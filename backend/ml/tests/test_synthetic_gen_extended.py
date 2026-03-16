"""
Extended tests for synthetic_gen.py — covering gaps identified in TDD review.

Covers:
  - generate_single with no rng argument (line 127 default path)
  - _generate_baseline internal behavior via observable outputs
  - _gaussian_peak shape and amplitude properties
  - _add_noise SNR fidelity
  - GeneratorConfig immutability (frozen dataclass)
  - Contaminant dataclass field correctness
  - Edge: zero contaminants (clean sample), all contaminants simultaneously
  - Edge: single-point dataset (n=1)
  - Edge: extreme GeneratorConfig values
  - Water type and scan rate discrete distributions
  - Metadata field order and electrode batch range
"""

import numpy as np
import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from synthetic_gen import (
    CONTAMINANTS,
    NUM_CONTAMINANTS,
    GeneratorConfig,
    VoltammogramSample,
    generate_single,
    generate_dataset,
    _generate_baseline,
    _gaussian_peak,
    _add_noise,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_rng(seed: int = 0) -> np.random.Generator:
    return np.random.default_rng(seed)


# ---------------------------------------------------------------------------
# Test _generate_baseline
# ---------------------------------------------------------------------------

class TestGenerateBaseline:
    """Unit tests for the baseline generation helper."""

    def test_output_shape_matches_input(self):
        voltages = np.linspace(-0.8, 0.8, 1000, dtype=np.float32)
        rng = _make_rng(0)
        baseline = _generate_baseline(voltages, scale=1.0, rng=rng)
        assert baseline.shape == voltages.shape

    def test_output_dtype_is_float32(self):
        voltages = np.linspace(-0.8, 0.8, 500, dtype=np.float32)
        rng = _make_rng(1)
        baseline = _generate_baseline(voltages, scale=1.0, rng=rng)
        assert baseline.dtype == np.float32

    def test_baseline_is_finite(self):
        voltages = np.linspace(-0.8, 0.8, 1000, dtype=np.float32)
        rng = _make_rng(2)
        for _ in range(20):
            baseline = _generate_baseline(voltages, scale=rng.uniform(0.1, 5.0), rng=rng)
            assert np.all(np.isfinite(baseline)), "Baseline contains non-finite values"

    def test_scale_zero_produces_near_zero_baseline(self):
        voltages = np.linspace(-0.8, 0.8, 100, dtype=np.float32)
        rng = _make_rng(3)
        baseline = _generate_baseline(voltages, scale=0.0, rng=rng)
        # With scale=0, amplitude a=0, drift=0, offset=0 -> all zeros
        np.testing.assert_allclose(baseline, 0.0, atol=1e-6)

    def test_larger_scale_produces_larger_magnitude(self):
        voltages = np.linspace(-0.8, 0.8, 1000, dtype=np.float32)
        rng_a = _make_rng(10)
        rng_b = _make_rng(10)
        small = _generate_baseline(voltages, scale=0.1, rng=rng_a)
        large = _generate_baseline(voltages, scale=10.0, rng=rng_b)
        assert np.abs(large).max() > np.abs(small).max()


# ---------------------------------------------------------------------------
# Test _gaussian_peak
# ---------------------------------------------------------------------------

class TestGaussianPeak:
    """Unit tests for the Gaussian peak helper."""

    def test_output_shape(self):
        voltages = np.linspace(-0.8, 0.8, 1000, dtype=np.float32)
        peak = _gaussian_peak(voltages, center=0.0, sigma=0.05, amplitude=1.0)
        assert peak.shape == voltages.shape

    def test_output_dtype(self):
        voltages = np.linspace(-0.8, 0.8, 1000, dtype=np.float32)
        peak = _gaussian_peak(voltages, center=0.0, sigma=0.05, amplitude=1.0)
        assert peak.dtype == np.float32

    def test_peak_maximum_at_center(self):
        voltages = np.linspace(-0.8, 0.8, 1000, dtype=np.float32)
        center = 0.25
        peak = _gaussian_peak(voltages, center=center, sigma=0.05, amplitude=2.0)
        peak_idx = np.argmax(peak)
        # The argmax voltage should be within one sample of center
        step = voltages[1] - voltages[0]
        assert abs(voltages[peak_idx] - center) <= 2 * step

    def test_amplitude_scales_peak_height(self):
        voltages = np.linspace(-0.8, 0.8, 1000, dtype=np.float32)
        p1 = _gaussian_peak(voltages, center=0.0, sigma=0.05, amplitude=1.0)
        p3 = _gaussian_peak(voltages, center=0.0, sigma=0.05, amplitude=3.0)
        assert pytest.approx(p3.max() / p1.max(), rel=1e-4) == 3.0

    def test_zero_amplitude_gives_zero_peak(self):
        voltages = np.linspace(-0.8, 0.8, 200, dtype=np.float32)
        peak = _gaussian_peak(voltages, center=0.0, sigma=0.05, amplitude=0.0)
        np.testing.assert_array_equal(peak, 0.0)

    def test_peak_values_are_non_negative_for_positive_amplitude(self):
        voltages = np.linspace(-0.8, 0.8, 1000, dtype=np.float32)
        peak = _gaussian_peak(voltages, center=0.0, sigma=0.05, amplitude=5.0)
        assert np.all(peak >= 0.0)

    def test_wider_sigma_produces_broader_peak(self):
        """Wider sigma means more area under the curve (integral ∝ sigma * amplitude)."""
        voltages = np.linspace(-0.8, 0.8, 1000, dtype=np.float32)
        narrow = _gaussian_peak(voltages, center=0.0, sigma=0.02, amplitude=1.0)
        wide = _gaussian_peak(voltages, center=0.0, sigma=0.10, amplitude=1.0)
        # Wider peak has five times the area (sigma ratio = 5)
        assert wide.sum() > narrow.sum() * 4.0, (
            "Wide peak should have substantially more integrated area than narrow peak"
        )


# ---------------------------------------------------------------------------
# Test _add_noise
# ---------------------------------------------------------------------------

class TestAddNoise:
    """Unit tests for the noise addition helper."""

    def test_output_shape_preserved(self):
        signal = np.ones(1000, dtype=np.float32)
        noisy = _add_noise(signal, snr_db=30.0, rng=_make_rng(0))
        assert noisy.shape == signal.shape

    def test_output_is_finite(self):
        signal = np.ones(500, dtype=np.float32) * 2.0
        noisy = _add_noise(signal, snr_db=20.0, rng=_make_rng(1))
        assert np.all(np.isfinite(noisy))

    def test_high_snr_preserves_signal_closely(self):
        signal = np.sin(np.linspace(0, np.pi, 1000)).astype(np.float32)
        noisy = _add_noise(signal, snr_db=60.0, rng=_make_rng(2))
        # At 60 dB SNR, RMS error should be tiny relative to signal power
        rms_error = np.sqrt(np.mean((noisy - signal) ** 2))
        signal_rms = np.sqrt(np.mean(signal ** 2))
        assert rms_error / signal_rms < 0.01, f"RMS error ratio too high: {rms_error / signal_rms:.4f}"

    def test_low_snr_adds_visible_noise(self):
        rng = _make_rng(3)
        signal = np.ones(1000, dtype=np.float32)
        noisy = _add_noise(signal, snr_db=5.0, rng=rng)
        # At 5 dB the signal should be noticeably degraded
        rms_error = np.sqrt(np.mean((noisy - signal) ** 2))
        signal_rms = np.sqrt(np.mean(signal ** 2))
        assert rms_error / signal_rms > 0.01

    def test_zero_signal_does_not_crash(self):
        signal = np.zeros(100, dtype=np.float32)
        # Should not raise even with zero power signal
        noisy = _add_noise(signal, snr_db=30.0, rng=_make_rng(4))
        assert noisy.shape == signal.shape
        assert np.all(np.isfinite(noisy))


# ---------------------------------------------------------------------------
# Test GeneratorConfig immutability
# ---------------------------------------------------------------------------

class TestGeneratorConfigImmutability:
    """GeneratorConfig is a frozen dataclass — mutation must raise."""

    def test_cannot_set_attribute(self):
        config = GeneratorConfig()
        with pytest.raises((AttributeError, TypeError)):
            config.num_points = 500  # type: ignore[misc]

    def test_cannot_delete_attribute(self):
        config = GeneratorConfig()
        with pytest.raises((AttributeError, TypeError)):
            del config.num_points  # type: ignore[misc]

    def test_two_default_configs_are_equal(self):
        assert GeneratorConfig() == GeneratorConfig()

    def test_different_configs_are_not_equal(self):
        c1 = GeneratorConfig(num_points=100)
        c2 = GeneratorConfig(num_points=200)
        assert c1 != c2


# ---------------------------------------------------------------------------
# Test Contaminant dataclass
# ---------------------------------------------------------------------------

class TestContaminantData:
    """Verify the CONTAMINANTS registry has physically plausible values."""

    def test_num_contaminants_is_five(self):
        assert NUM_CONTAMINANTS == 5

    def test_all_peak_potentials_in_valid_range(self):
        for c in CONTAMINANTS:
            assert -1.5 <= c.peak_potential_v <= 1.5, (
                f"{c.name}: peak_potential_v={c.peak_potential_v} outside [-1.5, 1.5] V"
            )

    def test_all_who_limits_positive(self):
        for c in CONTAMINANTS:
            assert c.who_limit > 0, f"{c.name}: WHO limit must be positive"

    def test_all_sensitivities_positive(self):
        for c in CONTAMINANTS:
            assert c.sensitivity > 0, f"{c.name}: sensitivity must be positive"

    def test_all_n_electrons_at_least_one(self):
        for c in CONTAMINANTS:
            assert c.n_electrons >= 1, f"{c.name}: must transfer at least 1 electron"

    def test_all_diffusion_coefficients_in_physical_range(self):
        for c in CONTAMINANTS:
            # Typical D for small ions in water: 1e-6 to 1e-4 cm²/s
            assert 1e-7 <= c.diffusion_coeff <= 1e-4, (
                f"{c.name}: diffusion_coeff={c.diffusion_coeff} outside physical range"
            )

    def test_contaminant_names_are_unique(self):
        names = [c.name for c in CONTAMINANTS]
        assert len(names) == len(set(names)), "Duplicate contaminant names"

    def test_contaminant_symbols_are_unique(self):
        symbols = [c.symbol for c in CONTAMINANTS]
        assert len(symbols) == len(set(symbols)), "Duplicate contaminant symbols"


# ---------------------------------------------------------------------------
# Test generate_single edge cases
# ---------------------------------------------------------------------------

class TestGenerateSingleEdgeCases:
    """Edge cases not covered by the primary test suite."""

    def test_no_rng_argument_uses_default(self):
        """Line 127: the rng=None default path must execute without error."""
        config = GeneratorConfig()
        sample = generate_single(config)  # no rng arg
        assert sample.voltages.shape == (config.num_points,)
        assert np.all(np.isfinite(sample.currents))

    def test_max_contaminants_zero_always_clean(self):
        config = GeneratorConfig(max_contaminants=0)
        rng = _make_rng(42)
        for _ in range(20):
            sample = generate_single(config, rng)
            assert sample.labels_detection.sum() == 0, "Expected clean sample with max_contaminants=0"
            assert np.all(sample.labels_concentration == 0.0)

    def test_max_contaminants_equals_num_contaminants(self):
        """Should never crash and must cap at NUM_CONTAMINANTS."""
        config = GeneratorConfig(max_contaminants=NUM_CONTAMINANTS)
        rng = _make_rng(7)
        for _ in range(20):
            sample = generate_single(config, rng)
            assert sample.labels_detection.sum() <= NUM_CONTAMINANTS

    def test_very_short_voltammogram(self):
        config = GeneratorConfig(num_points=10)
        rng = _make_rng(99)
        sample = generate_single(config, rng)
        assert sample.voltages.shape == (10,)
        assert sample.currents.shape == (10,)
        assert np.all(np.isfinite(sample.currents))

    def test_very_narrow_voltage_window(self):
        config = GeneratorConfig(v_start=-0.1, v_end=0.1)
        rng = _make_rng(11)
        sample = generate_single(config, rng)
        assert sample.voltages[0] == pytest.approx(-0.1, abs=0.001)
        assert sample.voltages[-1] == pytest.approx(0.1, abs=0.001)

    def test_very_high_snr_range(self):
        config = GeneratorConfig(snr_range=(80.0, 100.0))
        rng = _make_rng(13)
        sample = generate_single(config, rng)
        assert np.all(np.isfinite(sample.currents))

    def test_very_low_snr_range(self):
        config = GeneratorConfig(snr_range=(1.0, 5.0))
        rng = _make_rng(14)
        sample = generate_single(config, rng)
        assert np.all(np.isfinite(sample.currents))

    def test_metadata_water_type_in_valid_set(self):
        """water_type should be 0, 1, 2, or 3."""
        config = GeneratorConfig()
        rng = _make_rng(15)
        water_types_seen = set()
        for _ in range(200):
            sample = generate_single(config, rng)
            wt = int(sample.metadata[5])
            assert wt in {0, 1, 2, 3}, f"Invalid water_type: {wt}"
            water_types_seen.add(wt)
        assert water_types_seen == {0, 1, 2, 3}, "Not all water types observed in 200 samples"

    def test_metadata_scan_rate_in_valid_set(self):
        """scan_rate should be one of {10, 20, 50, 100}."""
        config = GeneratorConfig()
        rng = _make_rng(16)
        valid_rates = {10.0, 20.0, 50.0, 100.0}
        for _ in range(100):
            sample = generate_single(config, rng)
            sr = float(sample.metadata[6])
            assert sr in valid_rates, f"Invalid scan_rate: {sr}"

    def test_metadata_electrode_batch_in_range(self):
        """electrode_batch should be in [0, 9]."""
        config = GeneratorConfig()
        rng = _make_rng(17)
        for _ in range(100):
            sample = generate_single(config, rng)
            eb = int(sample.metadata[7])
            assert 0 <= eb <= 9, f"electrode_batch out of range: {eb}"

    def test_signal_amplitude_increases_with_concentration_on_average(self):
        """Higher concentration should produce higher amplitude peaks on average."""
        low_config = GeneratorConfig(
            max_contaminants=1,
            concentration_max_who_multiple=0.5,  # low concentration ceiling
        )
        high_config = GeneratorConfig(
            max_contaminants=1,
            concentration_max_who_multiple=10.0,  # high concentration ceiling
        )
        rng_low = _make_rng(20)
        rng_high = _make_rng(20)

        low_peaks = []
        high_peaks = []
        for _ in range(100):
            sl = generate_single(low_config, rng_low)
            sh = generate_single(high_config, rng_high)
            if sl.labels_detection.sum() > 0:
                low_peaks.append(sl.currents.max())
            if sh.labels_detection.sum() > 0:
                high_peaks.append(sh.currents.max())

        if low_peaks and high_peaks:
            assert np.mean(high_peaks) > np.mean(low_peaks), (
                "Higher concentration ceiling should produce higher average peak amplitudes"
            )


# ---------------------------------------------------------------------------
# Test generate_dataset edge cases
# ---------------------------------------------------------------------------

class TestGenerateDatasetEdgeCases:
    """Edge cases for generate_dataset not covered in the primary suite."""

    def test_single_sample_dataset(self):
        config = GeneratorConfig()
        data = generate_dataset(1, config, seed=0)
        assert data["voltammograms"].shape == (1, config.num_points)
        assert data["labels_detection"].shape == (1, NUM_CONTAMINANTS)
        assert data["labels_concentration"].shape == (1, NUM_CONTAMINANTS)
        assert data["metadata"].shape == (1, 8)

    def test_all_arrays_have_consistent_first_dimension(self):
        n = 37  # Odd number to catch off-by-one errors
        config = GeneratorConfig()
        data = generate_dataset(n, config, seed=5)
        for key, arr in data.items():
            assert arr.shape[0] == n, f"Array '{key}' has wrong first dimension: {arr.shape[0]}"

    def test_no_nan_or_inf_in_dataset(self):
        data = generate_dataset(200, GeneratorConfig(), seed=99)
        for key, arr in data.items():
            if np.issubdtype(arr.dtype, np.floating):
                assert np.all(np.isfinite(arr)), f"Non-finite values found in '{key}'"

    def test_labels_detection_dtype_is_int8(self):
        data = generate_dataset(50, GeneratorConfig(), seed=1)
        assert data["labels_detection"].dtype == np.int8

    def test_labels_detection_only_contains_zero_and_one(self):
        data = generate_dataset(200, GeneratorConfig(), seed=2)
        unique_vals = np.unique(data["labels_detection"])
        assert set(unique_vals.tolist()).issubset({0, 1})

    def test_voltammograms_dtype_is_float32(self):
        data = generate_dataset(50, GeneratorConfig(), seed=3)
        assert data["voltammograms"].dtype == np.float32

    def test_metadata_dtype_is_float32(self):
        data = generate_dataset(50, GeneratorConfig(), seed=4)
        assert data["metadata"].dtype == np.float32

    def test_same_seed_is_fully_reproducible_across_calls(self):
        config = GeneratorConfig()
        d1 = generate_dataset(50, config, seed=777)
        d2 = generate_dataset(50, config, seed=777)
        for key in d1:
            np.testing.assert_array_equal(d1[key], d2[key], err_msg=f"Mismatch in '{key}'")

    def test_concentration_zero_iff_not_detected(self):
        data = generate_dataset(300, GeneratorConfig(), seed=6)
        det = data["labels_detection"]
        conc = data["labels_concentration"]
        # Where not detected, concentration must be exactly 0
        not_detected_mask = det == 0
        assert np.all(conc[not_detected_mask] == 0.0), (
            "Non-zero concentration found for undetected contaminant"
        )

    def test_concentration_positive_where_detected(self):
        data = generate_dataset(300, GeneratorConfig(), seed=6)
        det = data["labels_detection"]
        conc = data["labels_concentration"]
        detected_mask = det == 1
        if detected_mask.any():
            assert np.all(conc[detected_mask] > 0.0), (
                "Zero or negative concentration found for detected contaminant"
            )

    def test_max_contaminants_per_sample_never_exceeded(self):
        config = GeneratorConfig(max_contaminants=2)
        data = generate_dataset(500, config, seed=8)
        n_per_sample = data["labels_detection"].sum(axis=1)
        assert np.all(n_per_sample <= 2), (
            f"max_contaminants=2 violated: max found = {n_per_sample.max()}"
        )
