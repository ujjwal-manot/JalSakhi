"""
JalSakhi — Physics-Based Synthetic Voltammogram Generator

Generates realistic Differential Pulse Voltammetry (DPV) data for training
the contaminant detection CNN. Uses Gaussian peak models with Randles-Sevcik
kinetics, electrode variability augmentation, and configurable noise.

Physics basis:
  - Peak potentials from published SPE literature
  - Current-concentration follows Randles-Sevcik: Ip ∝ n^(3/2) * D^(1/2) * C * v^(1/2)
  - Temperature dependence via Nernst equation (~59mV/n shift per decade)
  - Baseline modeled as exponential capacitive current

References:
  - Cui et al. (2015) Biosensors & Bioelectronics 63:276-286
  - Li et al. (2016) Analytical Chemistry 88(14):7267-7274
  - Valentini et al. (2014) Electroanalysis 26(9):2012-2019
"""

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class Contaminant:
    """Electrochemical properties of a detectable contaminant."""
    name: str
    symbol: str
    peak_potential_v: float       # Ep in volts vs Ag/AgCl
    peak_width_v: float           # Half-peak width (sigma of Gaussian)
    sensitivity: float            # μA per mg/L (or per ppb for metals)
    unit: str                     # 'mg/L' or 'ppb'
    who_limit: float              # WHO guideline value
    n_electrons: int              # Electrons transferred
    diffusion_coeff: float        # cm²/s (order of magnitude)
    temp_coeff: float             # Fractional change per °C


# Contaminant database — values from published SPE literature
CONTAMINANTS = (
    Contaminant("Ammonia",  "NH3", +0.25, 0.06, 0.80, "mg/L", 0.5,  2, 1.5e-5, 0.025),
    Contaminant("Lead",     "Pb",  -0.45, 0.04, 0.15, "ppb",  10.0, 2, 1.0e-5, 0.020),
    Contaminant("Arsenic",  "As",  -0.15, 0.05, 0.12, "ppb",  10.0, 3, 1.2e-5, 0.022),
    Contaminant("Nitrate",  "NO3", +0.45, 0.07, 0.50, "mg/L", 50.0, 2, 1.9e-5, 0.018),
    Contaminant("Iron",     "Fe",  +0.05, 0.05, 0.60, "mg/L", 0.3,  2, 0.7e-5, 0.030),
)

NUM_CONTAMINANTS = len(CONTAMINANTS)


@dataclass(frozen=True)
class GeneratorConfig:
    """Configuration for voltammogram generation."""
    num_points: int = 1000
    v_start: float = -0.8             # Start potential (V)
    v_end: float = 0.8                # End potential (V)
    snr_range: tuple[float, float] = (25.0, 50.0)  # dB
    baseline_scale_range: tuple[float, float] = (0.5, 3.0)
    peak_shift_mv: float = 15.0      # Max random Ep shift (mV)
    width_variation: float = 0.20     # Fractional sigma variation
    sensitivity_variation: float = 0.15
    temp_range: tuple[float, float] = (15.0, 40.0)  # °C
    temp_ref: float = 25.0            # Reference temperature (°C)
    ph_range: tuple[float, float] = (5.5, 8.5)
    tds_range: tuple[float, float] = (100.0, 1500.0)  # mg/L
    max_contaminants: int = 4         # Max simultaneous contaminants
    concentration_max_who_multiple: float = 5.0


@dataclass(frozen=True)
class VoltammogramSample:
    """A single generated voltammogram with labels and metadata."""
    voltages: NDArray[np.float32]           # (num_points,)
    currents: NDArray[np.float32]           # (num_points,) differential current
    labels_detection: NDArray[np.int8]      # (NUM_CONTAMINANTS,) binary
    labels_concentration: NDArray[np.float32]  # (NUM_CONTAMINANTS,) in native units
    metadata: NDArray[np.float32]           # (8,) [temp, ph, tds, snr, baseline, water_type, scan_rate, electrode_batch]


def _generate_baseline(
    voltages: NDArray[np.float32],
    scale: float,
    rng: np.random.Generator,
) -> NDArray[np.float32]:
    """Generate exponential capacitive baseline with slight curvature variation."""
    a = rng.uniform(0.3, 1.0) * scale
    b = rng.uniform(0.5, 2.0)
    offset = rng.uniform(-0.5, 0.5) * scale
    # Exponential baseline with slight polynomial drift
    baseline = a * np.exp(b * (voltages - voltages[0]) / (voltages[-1] - voltages[0]))
    drift = rng.uniform(-0.2, 0.2) * scale * voltages
    return (baseline + drift + offset).astype(np.float32)


def _gaussian_peak(
    voltages: NDArray[np.float32],
    center: float,
    sigma: float,
    amplitude: float,
) -> NDArray[np.float32]:
    """Single Gaussian peak representing a contaminant's DPV response."""
    return (amplitude * np.exp(-0.5 * ((voltages - center) / sigma) ** 2)).astype(np.float32)


def _add_noise(
    signal: NDArray[np.float32],
    snr_db: float,
    rng: np.random.Generator,
) -> NDArray[np.float32]:
    """Add white Gaussian noise at specified SNR."""
    signal_power = np.mean(signal ** 2)
    noise_power = signal_power / (10 ** (snr_db / 10))
    noise_std = np.sqrt(max(noise_power, 1e-12))
    noise = rng.normal(0, noise_std, signal.shape).astype(np.float32)
    return signal + noise


def generate_single(
    config: GeneratorConfig = GeneratorConfig(),
    rng: Optional[np.random.Generator] = None,
) -> VoltammogramSample:
    """Generate a single synthetic voltammogram with random contaminants."""
    if rng is None:
        rng = np.random.default_rng()

    voltages = np.linspace(config.v_start, config.v_end, config.num_points, dtype=np.float32)

    # Random environmental conditions
    temperature = rng.uniform(*config.temp_range)
    ph = rng.uniform(*config.ph_range)
    tds = rng.uniform(*config.tds_range)
    snr_db = rng.uniform(*config.snr_range)
    baseline_scale = rng.uniform(*config.baseline_scale_range)
    water_type = rng.integers(0, 4)  # 0=tap, 1=borewell, 2=open well, 3=river
    scan_rate = rng.choice([10.0, 20.0, 50.0, 100.0])
    electrode_batch = rng.integers(0, 10)

    # Generate baseline
    signal = _generate_baseline(voltages, baseline_scale, rng)

    # Decide which contaminants are present (0 to max_contaminants)
    num_present = rng.integers(0, config.max_contaminants + 1)
    present_indices = rng.choice(NUM_CONTAMINANTS, size=num_present, replace=False) if num_present > 0 else np.array([], dtype=int)

    labels_detection = np.zeros(NUM_CONTAMINANTS, dtype=np.int8)
    labels_concentration = np.zeros(NUM_CONTAMINANTS, dtype=np.float32)

    for idx in present_indices:
        contam = CONTAMINANTS[idx]
        labels_detection[idx] = 1

        # Random concentration: 0.1x to concentration_max_who_multiple * WHO limit
        max_conc = contam.who_limit * config.concentration_max_who_multiple
        min_conc = contam.who_limit * 0.1
        concentration = rng.uniform(min_conc, max_conc)
        labels_concentration[idx] = concentration

        # Temperature correction (Arrhenius-like)
        temp_factor = 1.0 + contam.temp_coeff * (temperature - config.temp_ref)

        # Electrode variability
        ep_shift = rng.normal(0, config.peak_shift_mv / 1000.0)
        width_factor = rng.uniform(1.0 - config.width_variation, 1.0 + config.width_variation)
        sens_factor = rng.uniform(1.0 - config.sensitivity_variation, 1.0 + config.sensitivity_variation)

        # Randles-Sevcik: Ip ∝ n^1.5 * D^0.5 * C * v^0.5
        n_factor = contam.n_electrons ** 1.5
        d_factor = np.sqrt(contam.diffusion_coeff * 1e5)  # scale for reasonable amplitudes
        v_factor = np.sqrt(scan_rate / 50.0)  # normalized to 50 mV/s

        amplitude = (
            contam.sensitivity
            * concentration
            * temp_factor
            * sens_factor
            * n_factor
            * d_factor
            * v_factor
        )

        peak_center = contam.peak_potential_v + ep_shift
        peak_sigma = contam.peak_width_v * width_factor

        signal += _gaussian_peak(voltages, peak_center, peak_sigma, amplitude)

    # Add noise
    signal = _add_noise(signal, snr_db, rng)

    metadata = np.array([
        temperature, ph, tds, snr_db,
        baseline_scale, float(water_type), scan_rate, float(electrode_batch),
    ], dtype=np.float32)

    return VoltammogramSample(
        voltages=voltages,
        currents=signal,
        labels_detection=labels_detection,
        labels_concentration=labels_concentration,
        metadata=metadata,
    )


def generate_dataset(
    n_samples: int,
    config: GeneratorConfig = GeneratorConfig(),
    seed: int = 42,
) -> dict[str, NDArray]:
    """
    Generate a full dataset of synthetic voltammograms.

    Returns dict with keys:
      - voltammograms: (n_samples, num_points) float32
      - labels_detection: (n_samples, NUM_CONTAMINANTS) int8
      - labels_concentration: (n_samples, NUM_CONTAMINANTS) float32
      - metadata: (n_samples, 8) float32
    """
    rng = np.random.default_rng(seed)

    voltammograms = np.empty((n_samples, config.num_points), dtype=np.float32)
    labels_det = np.empty((n_samples, NUM_CONTAMINANTS), dtype=np.int8)
    labels_conc = np.empty((n_samples, NUM_CONTAMINANTS), dtype=np.float32)
    meta = np.empty((n_samples, 8), dtype=np.float32)

    for i in range(n_samples):
        sample = generate_single(config, rng)
        voltammograms[i] = sample.currents
        labels_det[i] = sample.labels_detection
        labels_conc[i] = sample.labels_concentration
        meta[i] = sample.metadata

    return {
        "voltammograms": voltammograms,
        "labels_detection": labels_det,
        "labels_concentration": labels_conc,
        "metadata": meta,
    }
