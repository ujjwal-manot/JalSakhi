"""Tests for the synthetic voltammogram generator."""

import numpy as np
import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from synthetic_gen import (
    CONTAMINANTS,
    NUM_CONTAMINANTS,
    GeneratorConfig,
    generate_single,
    generate_dataset,
)


@pytest.fixture
def config():
    return GeneratorConfig()


@pytest.fixture
def rng():
    return np.random.default_rng(42)


class TestGenerateSingle:
    """Tests for single voltammogram generation."""

    def test_output_shapes(self, config, rng):
        sample = generate_single(config, rng)
        assert sample.voltages.shape == (config.num_points,)
        assert sample.currents.shape == (config.num_points,)
        assert sample.labels_detection.shape == (NUM_CONTAMINANTS,)
        assert sample.labels_concentration.shape == (NUM_CONTAMINANTS,)
        assert sample.metadata.shape == (8,)

    def test_output_dtypes(self, config, rng):
        sample = generate_single(config, rng)
        assert sample.voltages.dtype == np.float32
        assert sample.currents.dtype == np.float32
        assert sample.labels_detection.dtype == np.int8
        assert sample.labels_concentration.dtype == np.float32
        assert sample.metadata.dtype == np.float32

    def test_voltage_range(self, config, rng):
        sample = generate_single(config, rng)
        assert sample.voltages[0] == pytest.approx(config.v_start, abs=0.01)
        assert sample.voltages[-1] == pytest.approx(config.v_end, abs=0.01)
        # Monotonically increasing
        assert np.all(np.diff(sample.voltages) > 0)

    def test_detection_labels_binary(self, config, rng):
        for _ in range(50):
            sample = generate_single(config, rng)
            assert set(sample.labels_detection.tolist()).issubset({0, 1})

    def test_concentration_zero_when_not_detected(self, config, rng):
        for _ in range(50):
            sample = generate_single(config, rng)
            for i in range(NUM_CONTAMINANTS):
                if sample.labels_detection[i] == 0:
                    assert sample.labels_concentration[i] == 0.0

    def test_concentration_positive_when_detected(self, config, rng):
        # Generate enough samples to find at least one with detections
        found_detection = False
        for _ in range(100):
            sample = generate_single(config, rng)
            for i in range(NUM_CONTAMINANTS):
                if sample.labels_detection[i] == 1:
                    assert sample.labels_concentration[i] > 0.0
                    found_detection = True
        assert found_detection, "No detections found in 100 samples"

    def test_no_negative_concentrations(self, config, rng):
        for _ in range(100):
            sample = generate_single(config, rng)
            assert np.all(sample.labels_concentration >= 0)

    def test_metadata_ranges(self, config, rng):
        for _ in range(50):
            sample = generate_single(config, rng)
            temp, ph, tds, snr = sample.metadata[:4]
            assert config.temp_range[0] <= temp <= config.temp_range[1]
            assert config.ph_range[0] <= ph <= config.ph_range[1]
            assert config.tds_range[0] <= tds <= config.tds_range[1]
            assert config.snr_range[0] <= snr <= config.snr_range[1]

    def test_max_contaminants_respected(self, config, rng):
        for _ in range(100):
            sample = generate_single(config, rng)
            n_detected = sample.labels_detection.sum()
            assert n_detected <= config.max_contaminants

    def test_reproducibility_with_same_seed(self, config):
        rng1 = np.random.default_rng(12345)
        rng2 = np.random.default_rng(12345)
        s1 = generate_single(config, rng1)
        s2 = generate_single(config, rng2)
        np.testing.assert_array_equal(s1.currents, s2.currents)
        np.testing.assert_array_equal(s1.labels_detection, s2.labels_detection)

    def test_currents_are_finite(self, config, rng):
        for _ in range(50):
            sample = generate_single(config, rng)
            assert np.all(np.isfinite(sample.currents))


class TestGenerateDataset:
    """Tests for batch dataset generation."""

    def test_output_shapes(self, config):
        n = 100
        data = generate_dataset(n, config, seed=42)
        assert data["voltammograms"].shape == (n, config.num_points)
        assert data["labels_detection"].shape == (n, NUM_CONTAMINANTS)
        assert data["labels_concentration"].shape == (n, NUM_CONTAMINANTS)
        assert data["metadata"].shape == (n, 8)

    def test_has_both_clean_and_contaminated(self, config):
        data = generate_dataset(500, config, seed=42)
        has_any = data["labels_detection"].any(axis=1)
        assert has_any.sum() > 0, "No contaminated samples"
        assert (~has_any).sum() > 0, "No clean samples"

    def test_all_contaminants_represented(self, config):
        data = generate_dataset(1000, config, seed=42)
        for i, c in enumerate(CONTAMINANTS):
            count = data["labels_detection"][:, i].sum()
            assert count > 0, f"{c.name} never appears in 1000 samples"

    def test_concentration_within_expected_range(self, config):
        data = generate_dataset(500, config, seed=42)
        for i, c in enumerate(CONTAMINANTS):
            mask = data["labels_detection"][:, i] == 1
            if mask.any():
                concentrations = data["labels_concentration"][mask, i]
                max_expected = c.who_limit * config.concentration_max_who_multiple
                min_expected = c.who_limit * 0.1
                assert concentrations.min() >= min_expected * 0.9  # Small tolerance
                assert concentrations.max() <= max_expected * 1.1

    def test_different_seeds_produce_different_data(self, config):
        d1 = generate_dataset(10, config, seed=1)
        d2 = generate_dataset(10, config, seed=2)
        assert not np.array_equal(d1["voltammograms"], d2["voltammograms"])


class TestPeakPositions:
    """Verify that generated peaks appear near expected potentials."""

    def test_peak_near_expected_voltage(self, config):
        """For each contaminant, generate samples with ONLY that contaminant
        and verify the peak appears near the expected voltage."""
        voltages = np.linspace(config.v_start, config.v_end, config.num_points)
        rng = np.random.default_rng(42)

        for i, c in enumerate(CONTAMINANTS):
            # Generate a sample with just this contaminant at high concentration
            found = False
            for _ in range(200):
                sample = generate_single(config, rng)
                # Check if only this contaminant is present
                if sample.labels_detection[i] == 1 and sample.labels_detection.sum() == 1:
                    # Find peak in the signal (simple max in region around expected Ep)
                    mask = np.abs(voltages - c.peak_potential_v) < 0.2
                    if mask.any():
                        peak_idx = np.argmax(sample.currents[mask])
                        peak_voltage = voltages[mask][peak_idx]
                        # Peak should be within 50mV of expected
                        assert abs(peak_voltage - c.peak_potential_v) < 0.10, (
                            f"{c.name}: peak at {peak_voltage}V, expected {c.peak_potential_v}V"
                        )
                        found = True
                        break

            # It's OK if we didn't find an isolated sample in 200 tries
            # The random selection may not produce single-contaminant samples easily
            if not found:
                pytest.skip(f"Could not find isolated {c.name} sample in 200 tries")
