# Technical Deep Dive — Engineering Specification

## Table of Contents

1. [Electrochemical Sensing Science](#1-electrochemical-sensing--the-science)
2. [Potentiostat Hardware Architecture](#2-potentiostat-hardware-architecture)
3. [Auto-Range Current Measurement](#3-auto-range-current-measurement)
4. [Noise Control and Shielding](#4-noise-control-and-shielding)
5. [Temperature Compensation](#5-temperature-compensation)
6. [Electrode Contact Quality](#6-electrode-contact-quality)
7. [Calibration System](#7-calibration-system)
8. [Firmware: Deterministic Measurement Control](#8-firmware-deterministic-measurement-control)
9. [Firmware: On-Device Signal Conditioning](#9-firmware-on-device-signal-conditioning)
10. [Firmware: Fault Detection Logic](#10-firmware-fault-detection-logic)
11. [Firmware: Power Optimization](#11-firmware-power-optimization)
12. [App: Hardware Abstraction Layer](#12-app-hardware-abstraction-layer)
13. [App: Device Communication Protocol](#13-app-device-communication-protocol)
14. [App: Offline ML Inference](#14-app-offline-ml-inference)
15. [App: Model Confidence Scores](#15-app-model-confidence-scores)
16. [App: Interference Detection Model](#16-app-interference-detection-model)
17. [ML: Synthetic Voltammogram Generation](#17-ml-synthetic-voltammogram-generation)
18. [ML: Multi-Label Classification Architecture](#18-ml-multi-label-classification-architecture)
19. [ML: Domain Adaptation for Water Types](#19-ml-domain-adaptation-for-water-types)
20. [CV: Color Calibration System](#20-cv-color-calibration-system)
21. [CV: Lighting Correction Pipeline](#21-cv-lighting-correction-pipeline)
22. [Security: Device Authentication](#22-security-device-authentication)
23. [Security: Tamper Detection](#23-security-tamper-detection)
24. [Cloud Platform](#24-cloud-platform)

---

## 1. Electrochemical Sensing — The Science

### Why Electrochemistry?

Electrochemistry is the gold standard for field-deployable water analysis:
- **No reagent preparation** — the electrode IS the reagent
- **Multi-analyte from one scan** — different contaminants oxidize/reduce at different potentials
- **ppb-level sensitivity** — stripping voltammetry pre-concentrates analytes on the electrode
- **Miniaturizable** — the entire instrument is an analog circuit
- **Quantitative** — peak current is directly proportional to concentration (Randles-Sevcik equation)

### Voltammetric Techniques

#### Cyclic Voltammetry (CV)
- Sweep potential linearly: V1 → V2 → V1
- Measures oxidation and reduction currents
- Used for: qualitative identification, electrode characterization
- Scan rate: 50-100 mV/s

#### Differential Pulse Voltammetry (DPV)
- Staircase potential + small pulse at each step
- Measures difference current (pulse − baseline)
- **10-100x more sensitive than CV**
- Used for: heavy metals (Pb, As, Cd, Cu)
- Pulse amplitude: 50 mV, step: 4 mV, pulse width: 50 ms

#### Square Wave Voltammetry (SWV)
- Square wave superimposed on staircase
- Measures forward − reverse current
- Fastest technique, best signal-to-noise
- Used for: ammonia, nitrate, organic contaminants
- Frequency: 25 Hz, amplitude: 25 mV, step: 4 mV

#### Anodic Stripping Voltammetry (ASV)
- Pre-concentration: deposit metals at negative potential
- Stripping: sweep positive, metals oxidize sequentially
- Characteristic stripping potentials:
  - Zinc: −1.0 V
  - Cadmium: −0.6 V
  - Lead: −0.4 V
  - Copper: −0.1 V
  - Arsenic: +0.1 V (on gold electrode)
- **Detection limits: 0.1-10 ppb** — comparable to ICP-MS

### Screen-Printed Electrode (SPE) Design

Standard 3-electrode configuration:
```
    ┌─────────────────────────────────┐
    │                                 │
    │   ┌───┐   ┌───────┐   ┌───┐   │
    │   │ CE │   │  WE   │   │ RE│   │
    │   │Carb│   │ (mod) │   │Ag/│   │
    │   │ on │   │       │   │AgCl   │
    │   └─┬─┘   └───┬───┘   └─┬─┘   │
    │     │         │         │      │
    │     │    ┌────┴────┐    │      │
    │     │    │ Sample  │    │      │
    │     │    │  Drop   │    │      │
    │     │    │ (50 uL) │    │      │
    │     │    └─────────┘    │      │
    │     │                   │      │
    └─────┴──────────┬────────┴──────┘
                     │
              Contact Pads
         (gold-plated spring contacts)
```

- **WE (Working Electrode)**: Modified with target-specific nanomaterials
- **CE (Counter Electrode)**: Carbon, completes the circuit
- **RE (Reference Electrode)**: Ag/AgCl, stable potential reference
- Substrate: Ceramic (Al2O3) or PET plastic
- Dimensions: 34mm x 10mm x 0.5mm (standard DropSens format)
- Sample volume: 50-100 uL (one drop)

### Electrode Modifications — Recipe Book

#### Ammonia (NH4+/NH3)
- **Modification**: Prussian Blue nanoparticles electrodeposited on carbon WE
- **Mechanism**: PB catalyzes ammonia oxidation at +0.2V vs Ag/AgCl
- **Procedure**: CV in 2mM K3[Fe(CN)6] + 2mM FeCl3 + 0.1M KCl + 0.01M HCl, 20 cycles, 50 mV/s
- **Detection range**: 0.05 − 50 mg/L
- **Reference**: Luo et al., Analytical Chemistry, 2019

#### Lead (Pb2+)
- **Modification**: Bismuth film on carbon WE (in-situ plating)
- **Mechanism**: Bi and Pb co-deposit during preconcentration, strip sequentially
- **Procedure**: Add 400 ppb Bi3+ to sample, deposit at −1.2V for 120s, strip by DPV
- **Detection range**: 1 − 500 ppb
- **Reference**: Wang et al., Electroanalysis, 2005

#### Arsenic (As3+)
- **Modification**: Gold nanoparticles on carbon WE
- **Mechanism**: As deposits on Au at −0.3V, strips at +0.1V
- **Procedure**: Electrodeposit Au from 1mM HAuCl4 in 0.5M H2SO4
- **Detection range**: 5 − 500 ppb
- **Reference**: Salimi et al., Analyst, 2008

#### Nitrate (NO3-)
- **Modification**: Copper nanoparticles on carbon WE
- **Mechanism**: Cu catalyzes nitrate reduction at −0.8V
- **Procedure**: Electrodeposit Cu from 10mM CuSO4 in 0.1M H2SO4
- **Detection range**: 0.5 − 100 mg/L
- **Reference**: Ding et al., Talanta, 2019

---

## 2. Potentiostat Hardware Architecture

This is a real potentiostat, not a generic ADC board.

### Full Measurement Architecture

```
Smartphone (USB-C)
     │
     │  5V power + USB 2.0 FS data
     │
     ▼
┌────────────────────────────────────────────────────────┐
│                                                        │
│  ┌──────────────────────────────────────┐              │
│  │  USB-C Interface                     │              │
│  │  - ESD: USBLC6-2SC6 (TVS diodes)    │              │
│  │  - VBUS detection + CC resistors     │              │
│  │  - Ferrite bead on VBUS (EMI)        │              │
│  └──────────────┬───────────────────────┘              │
│                 │                                      │
│  ┌──────────────▼───────────────────────┐              │
│  │  Power Management                    │              │
│  │  - LDO: MCP1700 3.3V (low noise)    │              │
│  │  - Separate AVDD/DVDD rails          │              │
│  │  - Ferrite bead isolation            │              │
│  │  - Decoupling: 100nF + 10uF MLCC    │              │
│  │    per rail                          │              │
│  └──────────────┬───────────────────────┘              │
│                 │                                      │
│  ┌──────────────▼───────────────────────┐              │
│  │  STM32L432KC (ARM Cortex-M4, 80MHz) │              │
│  │                                      │              │
│  │  - USB 2.0 FS device (CDC/ACM)      │              │
│  │  - SPI master @ 20 MHz → AD5940     │              │
│  │  - TIM2: deterministic waveform      │              │
│  │    timing (1 us resolution)          │              │
│  │  - DMA: zero-copy SPI transfers     │              │
│  │  - I2C: temperature sensor           │              │
│  │  - Flash: 256KB (calibration data)   │              │
│  │  - RAM: 64KB (data buffers)          │              │
│  │  - GPIO: range switching, fault LED  │              │
│  │                                      │              │
│  └──────────────┬───────────────────────┘              │
│                 │                                      │
│          SPI Bus (20 MHz, Mode 0)                      │
│                 │                                      │
│  ┌──────────────▼───────────────────────┐              │
│  │  AD5940 Analog Front-End             │              │
│  │                                      │              │
│  │  ┌────────────────────────────────┐  │              │
│  │  │  DAC (Waveform Generator)      │  │              │
│  │  │  - 12-bit, 250 kSPS            │  │              │
│  │  │  - Voltage resolution: 0.8 mV  │  │              │
│  │  │  - CV/DPV/SWV/EIS waveforms    │  │              │
│  │  │  - Hardware sequencer (runs     │  │              │
│  │  │    without CPU intervention)    │  │              │
│  │  └──────────┬─────────────────────┘  │              │
│  │             │                         │              │
│  │  ┌──────────▼─────────────────────┐  │              │
│  │  │  Potentiostat Control Loop     │  │              │
│  │  │                                │  │              │
│  │  │  Control Amplifier (OA):       │  │              │
│  │  │   - Drives CE to maintain      │  │              │
│  │  │     WE-RE potential            │  │              │
│  │  │   - Unity-gain stable          │  │              │
│  │  │   - Bandwidth: 4 MHz           │  │              │
│  │  │                                │  │              │
│  │  │  Feedback Loop:                │  │              │
│  │  │   V_cell = V_DAC − V_RE        │  │              │
│  │  │   OA adjusts CE until:         │  │              │
│  │  │   V_WE − V_RE = V_set          │  │              │
│  │  └──────────┬─────────────────────┘  │              │
│  │             │                         │              │
│  │  ┌──────────▼─────────────────────┐  │              │
│  │  │  Transimpedance Amplifier      │  │              │
│  │  │  (TIA — Current Measurement)   │  │              │
│  │  │                                │  │              │
│  │  │  I_cell → TIA → V_out          │  │              │
│  │  │  V_out = I_cell × R_TIA        │  │              │
│  │  │                                │  │              │
│  │  │  Programmable R_TIA:           │  │              │
│  │  │   200 Ω  → 10 mA range        │  │              │
│  │  │   1 kΩ   → 2 mA range         │  │              │
│  │  │   10 kΩ  → 200 uA range       │  │              │
│  │  │   100 kΩ → 20 uA range        │  │              │
│  │  │   1 MΩ   → 2 uA range         │  │              │
│  │  │   10 MΩ  → 200 nA range       │  │              │
│  │  │                                │  │              │
│  │  │  (See Section 3: Auto-Range)   │  │              │
│  │  └──────────┬─────────────────────┘  │              │
│  │             │                         │              │
│  │  ┌──────────▼─────────────────────┐  │              │
│  │  │  ADC (Measurement)             │  │              │
│  │  │  - 16-bit SAR, 200 kSPS        │  │              │
│  │  │  - Current resolution: ≤10 nA  │  │              │
│  │  │  - Voltage resolution: ≤0.8 mV │  │              │
│  │  │  - PGA: 1x, 1.5x, 2x, 4x, 9x │  │              │
│  │  │  - Sinc2+Sinc3 digital filter  │  │              │
│  │  │  - DFT engine (for EIS mode)   │  │              │
│  │  └────────────────────────────────┘  │              │
│  └──────────────────────────────────────┘              │
│                                                        │
│  ┌──────────────────────────────────────┐              │
│  │  Temperature Sensor                  │              │
│  │  - TMP117 (I2C, ±0.1°C accuracy)    │              │
│  │  - Mounted near electrode connector  │              │
│  │  - Used for temperature compensation │              │
│  │  (See Section 5)                     │              │
│  └──────────────────────────────────────┘              │
│                                                        │
│  ┌──────────────────────────────────────┐              │
│  │  Electrode Connector                 │              │
│  │  - 3x gold-plated spring-loaded      │              │
│  │    pogo pins (Mill-Max 0906 series)  │              │
│  │  - Mechanical guide slot for SPE     │              │
│  │    alignment                         │              │
│  │  - Contact resistance: <1 Ω          │              │
│  │  - Variation: <5 Ω electrode-to-     │              │
│  │    electrode                         │              │
│  │  (See Section 6)                     │              │
│  │                                      │              │
│  │  [WE]  [RE]  [CE]                   │              │
│  └──────────────────────────────────────┘              │
│                                                        │
│  ┌──────────────────────────────────────┐              │
│  │  Status LED (RGB)                    │              │
│  │  - Blue: idle / connected            │              │
│  │  - Green pulse: scan in progress     │              │
│  │  - Red: fault detected               │              │
│  └──────────────────────────────────────┘              │
│                                                        │
│  PCB: 4-layer, 35mm x 18mm x 6mm                      │
│  Layer stack:                                          │
│    L1: Signal (analog traces)                          │
│    L2: Ground plane (continuous, unbroken)              │
│    L3: Power plane (split AVDD / DVDD)                 │
│    L4: Digital traces + USB                            │
│                                                        │
└────────────────────────────────────────────────────────┘
          │     │     │
          ▼     ▼     ▼
    Screen-Printed Electrode (disposable)
```

### Acceptance Criteria

| Parameter | Specification | Verification |
|-----------|--------------|--------------|
| Current resolution | ≤ 10 nA | Measure known 100 nA source |
| Voltage resolution | ≤ 1 mV (0.8 mV actual) | DAC step verification |
| Scan rate | 10 − 200 mV/s | Timer validation |
| Dynamic current range | 10 nA − 10 mA | Auto-range test |
| Voltage range | −0.6 V to +0.6 V (vs RE) | DAC output verification |
| SNR | > 40 dB | Noise floor measurement |
| Power (idle) | < 5 mA | Current measurement |
| Power (active scan) | < 30 mA | Current measurement |
| Sampling jitter | < 10 us | Oscilloscope verification |
| Temperature accuracy | ± 0.1°C | TMP117 spec |

### BOM (Updated, 4-Layer PCB)

| Component | Part Number | Qty | Unit Cost | Total |
|-----------|------------|-----|-----------|-------|
| Analog Front-End | AD5940BCBZ | 1 | $4.50 | $4.50 |
| MCU | STM32L432KCU6 | 1 | $2.50 | $2.50 |
| LDO (analog) | MCP1700-3302E | 1 | $0.25 | $0.25 |
| LDO (digital) | MCP1700-3302E | 1 | $0.25 | $0.25 |
| Temp sensor | TMP117AIDRVR | 1 | $1.20 | $1.20 |
| USB-C connector | USB4105-GF-A | 1 | $0.30 | $0.30 |
| ESD protection | USBLC6-2SC6 | 1 | $0.20 | $0.20 |
| Pogo pins | Mill-Max 0906 | 3 | $0.40 | $1.20 |
| Ferrite beads | BLM18PG221 | 3 | $0.05 | $0.15 |
| RGB LED | WS2812B-Mini | 1 | $0.10 | $0.10 |
| Decoupling caps | 100nF + 10uF MLCC | 8 | $0.03 | $0.24 |
| PCB | 4-layer, 35x18mm | 1 | $1.20 | $1.20 |
| Assembly | Pick-and-place | 1 | $1.50 | $1.50 |
| Shielding can | Stamped metal | 1 | $0.30 | $0.30 |
| Enclosure | Injection molded | 1 | $0.40 | $0.40 |
| **TOTAL** | | | | **$14.29** |

---

## 3. Auto-Range Current Measurement

Electrochemical currents vary from nanoamps (trace heavy metals in clean water) to milliamps (high-concentration ammonia). A fixed gain will either saturate or lose signal in noise.

### AD5940 Programmable TIA

The AD5940 has an internal programmable TIA with selectable feedback resistors:

| R_TIA | Current Range | Resolution (16-bit) | Use Case |
|-------|--------------|---------------------|----------|
| 200 Ω | ± 10 mA | 300 nA | High-concentration bulk electrolysis |
| 1 kΩ | ± 2 mA | 60 nA | Amperometry, CV at high concentrations |
| 10 kΩ | ± 200 uA | 6 nA | Standard CV, SWV for ammonia |
| 100 kΩ | ± 20 uA | 600 pA | DPV for moderate metal concentrations |
| 1 MΩ | ± 2 uA | 60 pA | DPV/ASV for low-ppb heavy metals |
| 10 MΩ | ± 200 nA | 6 pA | Ultra-trace detection |

### Auto-Range Algorithm

```c
typedef enum {
    RANGE_10MA   = 0,  // R_TIA = 200 Ohm
    RANGE_2MA    = 1,  // R_TIA = 1k
    RANGE_200UA  = 2,  // R_TIA = 10k
    RANGE_20UA   = 3,  // R_TIA = 100k
    RANGE_2UA    = 4,  // R_TIA = 1M
    RANGE_200NA  = 5,  // R_TIA = 10M
} current_range_t;

// Called after each ADC sample during a pre-scan
current_range_t auto_range(int16_t adc_raw, current_range_t current_range) {
    const int16_t ADC_MAX = 32767;
    const int16_t UPPER_THRESH = (int16_t)(ADC_MAX * 0.85);  // 85% of full scale
    const int16_t LOWER_THRESH = (int16_t)(ADC_MAX * 0.10);  // 10% of full scale

    int16_t abs_val = abs(adc_raw);

    if (abs_val > UPPER_THRESH && current_range > RANGE_10MA) {
        // Approaching saturation — decrease R_TIA (increase range)
        return (current_range_t)(current_range - 1);
    }
    if (abs_val < LOWER_THRESH && current_range < RANGE_200NA) {
        // Signal too small — increase R_TIA (decrease range)
        return (current_range_t)(current_range + 1);
    }
    return current_range;  // No change needed
}
```

### Ranging Strategy

1. **Pre-scan**: Before the actual measurement, run a quick 3-point voltage sweep (V_min, V_mid, V_max) at each range to find optimal R_TIA
2. **Fixed range during scan**: Lock the range for the entire voltammetric scan to avoid discontinuities
3. **Multi-range merge**: For wide-range samples, run two scans at different ranges and merge the data, stitching at the crossover point

---

## 4. Noise Control and Shielding

Electrochemical signals at ppb concentrations produce currents in the nanoamp range. At R_TIA = 10 MΩ, 1 nA produces only 10 mV — easily buried in noise.

### Noise Sources and Mitigations

| Noise Source | Magnitude | Mitigation |
|-------------|-----------|------------|
| USB 5V switching noise | 50-100 mVpp | Ferrite bead + dual LDO (analog/digital split) |
| Phone processor EMI | Broadband | Metal shielding can over AFE section |
| 50/60 Hz mains pickup | Variable | Sinc3 filter notch at 50/60 Hz (AD5940 built-in) |
| Electrode thermal noise | ~1 nA RMS | Bandwidth limiting via digital filter |
| PCB crosstalk | Variable | 4-layer PCB, continuous ground plane |
| TIA input bias current | ~100 pA | AD5940 spec, negligible vs signal |

### PCB Layout Rules

```
┌──────────────────────────────────────────────┐
│ LAYER 1 (TOP): Signal routing                │
│                                              │
│  ┌─────────────────────┐ ┌───────────────┐  │
│  │   ANALOG DOMAIN     │ │ DIGITAL DOMAIN│  │
│  │                     │ │               │  │
│  │  AD5940    TMP117   │ │  STM32L432    │  │
│  │  Electrode conn     │ │  USB-C        │  │
│  │  Analog LDO         │ │  Digital LDO  │  │
│  │                     │ │  LED          │  │
│  │  Guard ring around  │ │               │  │
│  │  WE/RE/CE traces    │ │               │  │
│  └─────────────────────┘ └───────────────┘  │
│           │                    │             │
│           │  SPI bridge zone   │             │
│           │  (short, straight) │             │
│           └────────────────────┘             │
│                                              │
│ LAYER 2: CONTINUOUS GROUND PLANE             │
│  - No splits under analog section            │
│  - Single point bridge between analog/digital│
│  - Via stitching around perimeter            │
│                                              │
│ LAYER 3: POWER PLANES                        │
│  - AVDD (analog 3.3V) — left half            │
│  - DVDD (digital 3.3V) — right half          │
│  - Connected via ferrite bead                │
│                                              │
│ LAYER 4 (BOTTOM): Digital traces + USB       │
│  - USB differential pair (90 Ω impedance)    │
│  - No analog signals on this layer           │
└──────────────────────────────────────────────┘
```

### Shielding

- **Stamped metal shielding can** over the analog section (AD5940 + TIA + electrode connector)
- Soldered to ground plane via castellated pads
- Provides >20 dB EMI attenuation above 100 MHz
- Cost: $0.30 at volume

### Analog Signal Integrity

- **Guard ring**: Driven guard trace around high-impedance WE/RE tracks, driven at the same potential as the inner conductor to eliminate leakage currents
- **Kelvin connection**: 4-wire sensing on the RE path (separate sense and force connections to the reference electrode) to eliminate IR drop in the connector
- **RC anti-aliasing filter**: First-order RC (10 kΩ + 1 nF = 16 kHz cutoff) before ADC input to prevent aliasing from signals above Nyquist

### Acceptance Target

| Parameter | Target | Measurement Method |
|-----------|--------|-------------------|
| Noise floor (10 MΩ TIA) | < 500 pA RMS | Short electrode leads, measure baseline |
| SNR at 100 nA signal | > 40 dB | Known current source via precision resistor |
| 50 Hz rejection | > 60 dB | Sinc3 filter at 50 Hz |
| Power supply rejection | > 40 dB | Inject 100 mV on VBUS, measure output |

---

## 5. Temperature Compensation

Electrochemical reaction kinetics are temperature-dependent. The Arrhenius equation governs reaction rates, and the Nernst equation shifts equilibrium potentials with temperature.

### Effects of Temperature on Measurements

| Parameter | Temperature Effect | Magnitude |
|-----------|-------------------|-----------|
| Peak current (Ip) | Increases with T (diffusion coefficient increases) | +1-3% per °C |
| Peak potential (Ep) | Shifts with T (Nernst equation) | -0.5 to -2 mV/°C |
| Solution resistance | Decreases with T (ion mobility increases) | -2% per °C |
| Reference electrode potential | Shifts with T | -0.7 mV/°C (Ag/AgCl) |

### Hardware

- **TMP117** digital temperature sensor (I2C)
- Accuracy: ±0.1°C (−20 to +50°C)
- Resolution: 0.0078°C
- Mounted on PCB near the electrode connector (within 5mm)
- Sampled at start and end of each scan

### Compensation Algorithm

```c
typedef struct {
    float alpha;    // temperature coefficient for peak current
    float beta;     // temperature coefficient for peak potential (mV/°C)
    float T_ref;    // reference temperature (typically 25.0 °C)
} temp_comp_params_t;

// Per-contaminant temperature coefficients (determined during factory calibration)
static const temp_comp_params_t temp_coefficients[] = {
    // {alpha,  beta,    T_ref}
    {0.020,  -0.59,   25.0},  // Ammonia (PB-SPE)
    {0.025,  -1.20,   25.0},  // Lead (Bi-SPE)
    {0.022,  -0.80,   25.0},  // Arsenic (Au-SPE)
    {0.018,  -1.00,   25.0},  // Nitrate (Cu-SPE)
    {0.020,  -0.70,   25.0},  // Iron (bare C)
    {0.015,   0.00,   25.0},  // Fluoride (ISE, Nernstian correction separate)
};

float compensate_current(float I_measured, float T_sample, int contaminant_id) {
    temp_comp_params_t p = temp_coefficients[contaminant_id];
    float I_corrected = I_measured / (1.0f + p.alpha * (T_sample - p.T_ref));
    return I_corrected;
}

float compensate_potential(float Ep_measured, float T_sample, int contaminant_id) {
    temp_comp_params_t p = temp_coefficients[contaminant_id];
    float Ep_corrected = Ep_measured - p.beta * (T_sample - p.T_ref) * 0.001f;
    return Ep_corrected;
}
```

### For Fluoride (ISE Mode)

Fluoride uses potentiometric detection with a Nernst-equation correction:

```
E = E0 + (R*T)/(n*F) * ln(a_F-)

At 25°C: slope = 59.16 mV/decade
At 35°C: slope = 61.14 mV/decade
```

The firmware recalculates the Nernstian slope using the measured temperature.

---

## 6. Electrode Contact Quality

SPE connections are the weakest physical link. Poor contact → unstable baseline → noisy peaks → wrong concentrations.

### Mechanical Design

```
Side view of electrode connector:

     ┌───────────────┐
     │  Dongle Body  │
     │               │
     │  ┌─┐  ┌─┐  ┌─┐   ← Gold-plated pogo pins
     │  │↕│  │↕│  │↕│      (spring-loaded, 100gf)
     │  └┬┘  └┬┘  └┬┘
     └───┼────┼────┼──┘
         │    │    │
    ═════╪════╪════╪═════  ← SPE slides into guide slot
    █████│████│████│█████     (0.5mm tolerance)
    █ WE █ RE █ CE █
    █████████████████████
    Screen-Printed Electrode
```

### Specifications

| Parameter | Specification |
|-----------|--------------|
| Pin type | Mill-Max 0906 series, gold-plated pogo |
| Spring force | 100 gf per pin |
| Contact material | Gold over nickel |
| Contact resistance | < 1 Ω per pin |
| Pin-to-pin variation | < 5 Ω across all 3 contacts |
| Insertion cycles | > 10,000 (rated life) |
| Alignment | Mechanical guide slot, ±0.25mm tolerance |
| Electrode detect | Impedance check before scan (see Section 10) |

### Guide Slot Design

- Injection-molded slot in dongle enclosure
- SPE slides in from the side (like inserting a SIM card)
- Positive click/detent when fully seated
- Prevents angular misalignment that causes inconsistent contact area

### Contact Verification

Before every scan, firmware runs a contact quality check:

```c
bool verify_electrode_contact(void) {
    // Apply 10 mV between WE and CE, measure impedance
    float Z = measure_impedance_at_1kHz(0.010);  // 10 mV excitation

    // Good contact: Z should be 100 Ohm - 10 kOhm (electrode + solution)
    if (Z < 50.0) {
        report_fault(FAULT_SHORT_CIRCUIT);
        return false;
    }
    if (Z > 100000.0) {
        report_fault(FAULT_NO_ELECTRODE);
        return false;
    }

    // Check stability: measure 10 times, compute variance
    float readings[10];
    for (int i = 0; i < 10; i++) {
        readings[i] = measure_impedance_at_1kHz(0.010);
        delay_ms(10);
    }
    float variance = compute_variance(readings, 10);

    if (variance > Z * 0.05) {  // >5% variation → bad contact
        report_fault(FAULT_UNSTABLE_CONTACT);
        return false;
    }

    return true;
}
```

---

## 7. Calibration System

Every serious analytical instrument requires calibration. JalSakhi uses two calibration modes.

### Mode 1: Factory Calibration

Performed during manufacturing with NIST-traceable standard solutions.

**Procedure:**
1. Run DPV/SWV with each electrode type in 5 standard concentrations
2. Record peak current (Ip) vs. known concentration for each contaminant
3. Fit linear calibration: `C = (Ip - offset) / sensitivity`
4. Store calibration coefficients in STM32 flash (last 16 KB sector)

**Stored data per electrode type:**

```c
typedef struct {
    uint8_t electrode_type;      // PB, Bi, Au, Cu, C, ISE
    float sensitivity;           // uA per (mg/L) or uA per ppb
    float offset;                // uA (baseline current)
    float r_squared;             // calibration linearity
    float LOD;                   // limit of detection (3*sigma/sensitivity)
    float LOQ;                   // limit of quantification (10*sigma/sensitivity)
    float temp_alpha;            // temperature coefficient
    uint32_t cal_date;           // Unix timestamp
    uint16_t cal_checksum;       // CRC-16 for integrity
} calibration_data_t;
```

### Mode 2: Field Calibration

User-initiated calibration using a known standard solution.

**Procedure:**
1. App prompts: "Insert calibration electrode, add 1 drop of standard solution"
2. Standard solutions provided in kit:
   - Ammonia: 1.0 mg/L
   - Lead: 50 ppb
   - pH 7.0 buffer
3. Device runs a standard scan, measures Ip
4. Compares with factory calibration
5. Computes correction factor: `K = Ip_expected / Ip_measured`
6. Stores K in flash for subsequent measurements

**Frequency**: Recommended every 50 tests or monthly, whichever comes first.

### Calibration Verification

```c
typedef struct {
    float correction_factor;    // K = expected/measured
    uint32_t field_cal_date;
    uint16_t tests_since_cal;
    bool cal_expired;           // true if >50 tests or >30 days
} field_cal_t;

float apply_calibration(float raw_concentration, field_cal_t* cal) {
    float corrected = raw_concentration * cal->correction_factor;
    cal->tests_since_cal++;

    if (cal->tests_since_cal > 50) {
        cal->cal_expired = true;
        // App shows "Calibration recommended" warning
    }
    return corrected;
}
```

### Acceptance Target

| Parameter | Target |
|-----------|--------|
| Calibration error | < 5% |
| Linearity (R²) | > 0.995 |
| LOD (ammonia) | 0.05 mg/L |
| LOD (lead) | 1 ppb |
| Field cal time | < 2 minutes |

---

## 8. Firmware: Deterministic Measurement Control

Voltammetry requires precise waveform timing. A jittery scan produces noisy, non-reproducible voltammograms.

### Timer-Based DAC Control

```c
// STM32 TIM2 configured for deterministic DAC stepping
// Example: CV scan at 50 mV/s, 1 mV steps → 20 ms per step

void configure_cv_scan(float V_start, float V_end, float scan_rate, float V_step) {
    // Calculate timing
    float step_time_s = V_step / scan_rate;              // 0.001 / 0.050 = 0.020 s
    uint32_t timer_period_us = (uint32_t)(step_time_s * 1e6);  // 20000 us

    // Calculate DAC values
    uint16_t dac_start = voltage_to_dac(V_start);
    uint16_t dac_end   = voltage_to_dac(V_end);
    int16_t  dac_step  = (V_end > V_start) ? 1 : -1;    // 1 DAC LSB ≈ 0.8 mV

    // Configure TIM2
    TIM2->PSC = 79;            // 80 MHz / 80 = 1 MHz timer clock
    TIM2->ARR = timer_period_us - 1;  // Period = 20000 us
    TIM2->DIER |= TIM_DIER_UIE;      // Enable update interrupt

    // Store scan parameters
    scan_ctx.dac_current = dac_start;
    scan_ctx.dac_end     = dac_end;
    scan_ctx.dac_step    = dac_step;
    scan_ctx.sample_index = 0;

    // Start scan
    TIM2->CR1 |= TIM_CR1_CEN;
}

// TIM2 ISR — fires every 20 ms (50 mV/s, 1 mV step)
void TIM2_IRQHandler(void) {
    TIM2->SR &= ~TIM_SR_UIF;  // Clear interrupt flag

    // 1. Set DAC voltage
    AD5940_SetDACVoltage(scan_ctx.dac_current);

    // 2. Wait settling time (50 us)
    delay_us(50);

    // 3. Read ADC (synchronized to DAC step)
    int32_t adc_raw = AD5940_ReadADC();

    // 4. Store data point
    scan_ctx.voltage_buf[scan_ctx.sample_index] = dac_to_voltage(scan_ctx.dac_current);
    scan_ctx.current_buf[scan_ctx.sample_index] = adc_to_current(adc_raw);
    scan_ctx.sample_index++;

    // 5. Step DAC
    scan_ctx.dac_current += scan_ctx.dac_step;

    // 6. Check if scan complete
    if (scan_ctx.dac_current == scan_ctx.dac_end) {
        TIM2->CR1 &= ~TIM_CR1_CEN;  // Stop timer
        scan_ctx.scan_complete = true;
    }
}
```

### Waveform Specifications

| Technique | V_start | V_end | V_step | Rate | Timing Source |
|-----------|---------|-------|--------|------|---------------|
| CV | −0.2 V | +0.8 V → −0.2 V | 1 mV | 50 mV/s | TIM2 (20 ms period) |
| DPV | −1.2 V | +0.2 V | 4 mV | N/A | TIM2 + pulse sequencer |
| SWV | −0.2 V | +0.8 V | 4 mV | N/A | TIM2 @ 25 Hz |
| ASV (deposition) | −1.2 V (fixed) | — | — | — | TIM2 (120 s total) |
| ASV (strip) | −1.2 V | +0.4 V | 4 mV | 50 mV/s | TIM2 |

### DPV Pulse Sequence

```
Voltage
  ^
  │     ┌──┐        ┌──┐        ┌──┐
  │     │  │ΔE_p    │  │        │  │
  │  ───┘  └──┐  ───┘  └──┐ ───┘  └──
  │           └──        └──
  │  E_step      E_step      E_step
  └──────────────────────────────────> Time

  ΔE_p = 50 mV (pulse amplitude)
  E_step = 4 mV (staircase step)
  t_pulse = 50 ms
  t_measure_1: sample current at end of pulse
  t_measure_2: sample current just before pulse
  ΔI = I_pulse - I_baseline (differential measurement)
```

### Acceptance Criteria

| Parameter | Specification |
|-----------|--------------|
| Sampling jitter | < 10 us (TIM2 hardware interrupt) |
| DAC settling time | < 50 us (verified by scope) |
| ADC-DAC synchronization | Hardware-triggered (no software delay) |
| Scan reproducibility | CV of K3[Fe(CN)6]: Ip RSD < 3% (n=10) |

---

## 9. Firmware: On-Device Signal Conditioning

Preprocessing on the MCU reduces data transfer and ML model complexity.

### Pipeline (runs on STM32 after scan completes)

```c
typedef struct {
    float voltage[MAX_POINTS];
    float current[MAX_POINTS];
    uint16_t n_points;
    float temperature;
    current_range_t range;
} raw_scan_t;

typedef struct {
    float voltage[MAX_POINTS];
    float current_smoothed[MAX_POINTS];
    float current_baseline_corrected[MAX_POINTS];
    uint16_t n_points;

    // Extracted features
    uint8_t n_peaks;
    float peak_potential[MAX_PEAKS];
    float peak_current[MAX_PEAKS];
    float peak_width[MAX_PEAKS];
    float peak_area[MAX_PEAKS];

    // Metadata
    float temperature;
    float baseline_noise_rms;
    uint8_t quality_flag;  // GOOD, MARGINAL, REJECT
} processed_scan_t;

processed_scan_t process_scan(raw_scan_t* raw) {
    processed_scan_t result;
    result.n_points = raw->n_points;
    result.temperature = raw->temperature;

    // Step 1: Copy voltage array
    memcpy(result.voltage, raw->voltage, raw->n_points * sizeof(float));

    // Step 2: Savitzky-Golay smoothing (order 3, window 15)
    savitzky_golay(raw->current, result.current_smoothed,
                   raw->n_points, 15, 3);

    // Step 3: Baseline correction (asymmetric least squares)
    float baseline[MAX_POINTS];
    als_baseline(result.current_smoothed, baseline,
                 raw->n_points, 1e6, 0.01, 10);  // lambda, p, iterations
    for (int i = 0; i < raw->n_points; i++) {
        result.current_baseline_corrected[i] =
            result.current_smoothed[i] - baseline[i];
    }

    // Step 4: Compute baseline noise RMS (first 50 points, before peaks)
    result.baseline_noise_rms = compute_rms(
        result.current_baseline_corrected, 50);

    // Step 5: Peak detection (first derivative zero-crossing)
    result.n_peaks = detect_peaks(
        result.voltage,
        result.current_baseline_corrected,
        raw->n_points,
        result.baseline_noise_rms * 5.0,  // threshold = 5x noise
        result.peak_potential,
        result.peak_current,
        result.peak_width,
        result.peak_area,
        MAX_PEAKS
    );

    // Step 6: Quality assessment
    if (result.baseline_noise_rms > NOISE_REJECT_THRESHOLD) {
        result.quality_flag = QUALITY_REJECT;
    } else if (result.baseline_noise_rms > NOISE_MARGINAL_THRESHOLD) {
        result.quality_flag = QUALITY_MARGINAL;
    } else {
        result.quality_flag = QUALITY_GOOD;
    }

    return result;
}
```

### Data Sent to Phone

Two modes:
1. **Full voltammogram** — for ML inference on phone (1000 floats = 4 KB)
2. **Feature vector only** — for simple threshold-based analysis (< 100 bytes)

The phone receives both; the feature vector is used for quick display while the full voltammogram feeds the CNN.

---

## 10. Firmware: Fault Detection Logic

Automatic detection of bad tests prevents false results.

### Fault Types and Detection

```c
typedef enum {
    FAULT_NONE              = 0x00,
    FAULT_NO_ELECTRODE      = 0x01,  // Open circuit detected
    FAULT_SHORT_CIRCUIT     = 0x02,  // Impedance too low
    FAULT_DRY_SAMPLE        = 0x04,  // No electrolyte (very high impedance)
    FAULT_UNSTABLE_CONTACT  = 0x08,  // Contact resistance fluctuating
    FAULT_ELECTRODE_DAMAGE  = 0x10,  // Abnormal baseline shape
    FAULT_SATURATION        = 0x20,  // ADC saturated during scan
    FAULT_TEMPERATURE_OOR   = 0x40,  // Temperature out of range
    FAULT_CAL_EXPIRED       = 0x80,  // Calibration needs refresh
} fault_flags_t;

fault_flags_t run_preflight_checks(void) {
    fault_flags_t faults = FAULT_NONE;

    // Check 1: Electrode presence (impedance at 1 kHz)
    float Z = measure_impedance_at_1kHz(0.010);
    if (Z > 1e6) faults |= FAULT_NO_ELECTRODE;
    if (Z < 10)  faults |= FAULT_SHORT_CIRCUIT;

    // Check 2: Sample presence (impedance should drop when wet)
    // Dry SPE: ~100 kOhm+, Wet SPE with water: 500-5000 Ohm
    if (Z > 50000 && !(faults & FAULT_NO_ELECTRODE)) {
        faults |= FAULT_DRY_SAMPLE;
    }

    // Check 3: Contact stability (10 readings, check variance)
    float z_readings[10];
    for (int i = 0; i < 10; i++) {
        z_readings[i] = measure_impedance_at_1kHz(0.010);
        delay_ms(10);
    }
    if (compute_cv_percent(z_readings, 10) > 5.0) {
        faults |= FAULT_UNSTABLE_CONTACT;
    }

    // Check 4: Temperature range (5-45 °C for reliable results)
    float temp = TMP117_ReadTemperature();
    if (temp < 5.0 || temp > 45.0) {
        faults |= FAULT_TEMPERATURE_OOR;
    }

    // Check 5: Calibration age
    if (get_tests_since_calibration() > 50 ||
        get_days_since_calibration() > 30) {
        faults |= FAULT_CAL_EXPIRED;
    }

    return faults;
}

// Post-scan fault detection
fault_flags_t check_scan_quality(processed_scan_t* scan) {
    fault_flags_t faults = FAULT_NONE;

    // Check for ADC saturation (any sample at ±full scale)
    for (int i = 0; i < scan->n_points; i++) {
        if (fabs(scan->current_smoothed[i]) > MAX_CURRENT_FOR_RANGE * 0.98) {
            faults |= FAULT_SATURATION;
            break;
        }
    }

    // Check baseline shape (should be relatively flat)
    // Large slope in baseline indicates electrode degradation
    float baseline_slope = linear_regression_slope(
        scan->voltage, scan->current_baseline_corrected, 50);
    if (fabs(baseline_slope) > BASELINE_SLOPE_THRESHOLD) {
        faults |= FAULT_ELECTRODE_DAMAGE;
    }

    return faults;
}
```

### User-Facing Fault Messages

| Fault | LED | App Message | Action |
|-------|-----|-------------|--------|
| No electrode | Red blink | "Insert electrode" | Wait for insertion |
| Dry sample | Red blink | "Add water sample (1 drop)" | Wait |
| Unstable contact | Red pulse | "Re-insert electrode, ensure it clicks" | Re-seat |
| Saturation | Red solid | "Signal too strong. Dilute sample or use different electrode." | Change electrode type |
| Electrode damage | Yellow | "Electrode may be damaged. Try a new one." | Replace SPE |
| Cal expired | Yellow | "Calibration recommended (50+ tests)" | Optional recalibration |
| Temperature OOR | Yellow | "Temperature outside 5-45°C range. Results may be less accurate." | Warning only |

---

## 11. Firmware: Power Optimization

The dongle draws power from the phone. Excessive draw heats the phone and drains battery.

### Power Budget

| State | Component | Current | Duration |
|-------|-----------|---------|----------|
| **Idle** | STM32 (Stop2 mode) | 1.0 uA | Continuous |
| | AD5940 (shutdown) | 0.5 uA | |
| | TMP117 (shutdown) | 0.25 uA | |
| | **Total idle** | **< 2 uA** | |
| **Pre-scan** | STM32 (active, 80 MHz) | 8 mA | 500 ms |
| | AD5940 (init + impedance check) | 3 mA | |
| | TMP117 (one-shot) | 0.25 mA | |
| | **Total pre-scan** | **~12 mA** | |
| **Active scan** | STM32 (active) | 8 mA | 20-120 s |
| | AD5940 (DAC + TIA + ADC active) | 12 mA | |
| | LED (pulse) | 5 mA avg | |
| | **Total scanning** | **~25 mA** | |
| **Data transfer** | STM32 (USB active) | 10 mA | 500 ms |
| | AD5940 (shutdown) | 0.5 uA | |
| | **Total transfer** | **~10 mA** | |

### Power State Machine

```
            USB plugged in
                 │
                 ▼
        ┌────────────────┐
        │  IDLE (Stop2)  │◄──────────────────┐
        │   < 2 uA       │                   │
        └───────┬────────┘                   │
                │ USB command: INIT           │
                ▼                             │
        ┌────────────────┐                   │
        │  PRE-SCAN      │                   │
        │  ~12 mA        │                   │
        │  - Impedance    │                   │
        │  - Temp read    │                   │
        │  - Fault check  │                   │
        └───────┬────────┘                   │
                │ START_SCAN                  │
                ▼                             │
        ┌────────────────┐                   │
        │  SCANNING      │                   │
        │  ~25 mA        │                   │
        │  - DAC sweep    │                   │
        │  - ADC sampling │                   │
        └───────┬────────┘                   │
                │ Scan complete               │
                ▼                             │
        ┌────────────────┐                   │
        │  PROCESSING    │                   │
        │  ~10 mA        │                   │
        │  - Smoothing    │                   │
        │  - Baseline     │                   │
        │  - Peak detect  │                   │
        └───────┬────────┘                   │
                │ Data ready                  │
                ▼                             │
        ┌────────────────┐                   │
        │  DATA TRANSFER │                   │
        │  ~10 mA        │                   │
        │  - USB stream   │───────────────────┘
        │  500 ms         │  → return to IDLE
        └────────────────┘
```

### Acceptance Criteria

| State | Target | Actual |
|-------|--------|--------|
| Idle | < 5 mA | < 2 uA |
| Active scan | < 30 mA | ~25 mA |
| Full test cycle energy | < 1 mAh | ~0.7 mAh (25 mA x 100s) |

A single test consumes ~0.7 mAh. A phone with 4000 mAh battery can power **5000+ tests** without noticeable battery impact.

---

## 12. App: Hardware Abstraction Layer

The app must survive hardware revisions without code changes.

### Architecture

```
┌─────────────────────────────────────────────┐
│                  UI LAYER                    │
│  Dashboard / Results / History / Map         │
├─────────────────────────────────────────────┤
│              ML INFERENCE LAYER              │
│  1D-CNN (TFLite) / Colorimetric CNN          │
├─────────────────────────────────────────────┤
│          SIGNAL PROCESSING LAYER             │
│  Savitzky-Golay / Baseline / Peak Detection  │
├─────────────────────────────────────────────┤
│            DEVICE DRIVER LAYER               │
│  Protocol parser / Data deserializer         │
│  Command builder / Response handler          │
├─────────────────────────────────────────────┤
│           HARDWARE ABSTRACT LAYER            │
│                                             │
│  ┌─────────────┐  ┌─────────────────────┐  │
│  │ USB Driver   │  │ BLE Driver (future) │  │
│  │ (usb_serial) │  │ (flutter_blue_plus) │  │
│  └──────┬──────┘  └──────────┬──────────┘  │
│         │                     │             │
│         └──────────┬──────────┘             │
│                    │                        │
│         ┌──────────▼──────────┐             │
│         │ DeviceInterface     │             │
│         │ (abstract class)    │             │
│         │                     │             │
│         │ + connect()         │             │
│         │ + disconnect()      │             │
│         │ + sendCommand()     │             │
│         │ + onDataReceived()  │             │
│         │ + getDeviceInfo()   │             │
│         └─────────────────────┘             │
│                                             │
└─────────────────────────────────────────────┘
```

### Dart Interface

```dart
abstract class DeviceInterface {
  Stream<ConnectionState> get connectionState;
  Stream<ScanData> get scanDataStream;

  Future<void> connect();
  Future<void> disconnect();
  Future<DeviceInfo> getDeviceInfo();
  Future<void> setScanParams(ScanParams params);
  Future<void> startScan();
  Future<void> stopScan();
  Future<CalibrationData> getCalibration();
  Future<void> runFieldCalibration(CalibrationType type);
}

class UsbPotentiostat implements DeviceInterface {
  // USB CDC/ACM implementation
}

class BlePotentiostat implements DeviceInterface {
  // BLE implementation (future hardware revision)
}
```

If hardware changes from USB to BLE, only the driver layer changes. Everything above remains untouched.

---

## 13. App: Device Communication Protocol

### Command Set

| Command | Code | Direction | Payload | Description |
|---------|------|-----------|---------|-------------|
| PING | 0x01 | App → Device | — | Check device alive |
| PONG | 0x81 | Device → App | firmware_version, device_id | Response to PING |
| GET_INFO | 0x02 | App → Device | — | Get device info + calibration status |
| INFO_RESP | 0x82 | Device → App | DeviceInfo struct | Device info response |
| SET_PARAMS | 0x03 | App → Device | ScanParams struct | Configure scan parameters |
| PARAMS_ACK | 0x83 | Device → App | status | Acknowledge parameters |
| START_SCAN | 0x04 | App → Device | — | Begin measurement |
| SCAN_DATA | 0x84 | Device → App | DataPacket[] | Stream of data points |
| SCAN_DONE | 0x85 | Device → App | ProcessedScan struct | Scan complete + features |
| STOP_SCAN | 0x05 | App → Device | — | Abort measurement |
| FAULT | 0x86 | Device → App | fault_flags | Fault notification |
| FIELD_CAL | 0x06 | App → Device | cal_type | Start field calibration |
| CAL_RESULT | 0x87 | Device → App | CalResult struct | Calibration result |

### Data Packet Format

```
┌──────────────────────────────────────────────────┐
│ HEADER (4 bytes)                                 │
│  [0xAA] [CMD] [LEN_H] [LEN_L]                   │
├──────────────────────────────────────────────────┤
│ PAYLOAD (variable)                               │
│                                                  │
│  For SCAN_DATA:                                  │
│  ┌──────────────────────────────────┐            │
│  │ timestamp_ms    : uint32 (4B)    │            │
│  │ voltage_mV      : int16  (2B)    │            │
│  │ current_nA      : int32  (4B)    │            │
│  │ temperature_C   : int16  (2B)    │  × N pts   │
│  │ range           : uint8  (1B)    │            │
│  │ quality_flag    : uint8  (1B)    │            │
│  └──────────────────────────────────┘            │
│  Total per point: 14 bytes                       │
│                                                  │
│  For SCAN_DONE:                                  │
│  ┌──────────────────────────────────┐            │
│  │ device_id       : uint32 (4B)    │            │
│  │ n_points        : uint16 (2B)    │            │
│  │ scan_type       : uint8  (1B)    │            │
│  │ temperature_avg : float  (4B)    │            │
│  │ baseline_noise  : float  (4B)    │            │
│  │ n_peaks         : uint8  (1B)    │            │
│  │ peak_data[n_peaks]:              │            │
│  │   Ep_mV         : int16  (2B)    │            │
│  │   Ip_nA         : int32  (4B)    │  × n_peaks │
│  │   width_mV      : uint16 (2B)    │            │
│  │   area          : float  (4B)    │            │
│  │ fault_flags     : uint8  (1B)    │            │
│  │ voltammogram[n_points]:          │            │
│  │   voltage_mV    : int16  (2B)    │  × n_pts   │
│  │   current_nA    : int32  (4B)    │            │
│  └──────────────────────────────────┘            │
│                                                  │
├──────────────────────────────────────────────────┤
│ FOOTER (3 bytes)                                 │
│  [CRC16_H] [CRC16_L] [0x55]                     │
└──────────────────────────────────────────────────┘
```

### Data Integrity

- CRC-16/CCITT on entire packet (header + payload)
- Device retransmits on NACK
- Sequence numbers for ordered delivery
- 115200 baud USB CDC (sufficient for 14 bytes × 200 SPS = 2.8 KB/s)

---

## 14. App: Offline ML Inference

All ML runs on-device. Cloud is never required for individual test results.

### TensorFlow Lite Deployment

```dart
class VoltammogramClassifier {
  late Interpreter _interpreter;
  static const String MODEL_PATH = 'assets/models/voltammogram_cnn_v1.tflite';

  Future<void> loadModel() async {
    _interpreter = await Interpreter.fromAsset(MODEL_PATH);
  }

  ClassificationResult classify(List<double> voltammogram) {
    // Input: normalized voltammogram [1000 points]
    var input = [voltammogram.map((v) => [v]).toList()];

    // Output: [1, 7] detection + [1, 7] concentration
    var detectionOutput = List.filled(7, 0.0).reshape([1, 7]);
    var concentrationOutput = List.filled(7, 0.0).reshape([1, 7]);

    _interpreter.runForMultipleInputs(
      [input],
      {0: detectionOutput, 1: concentrationOutput}
    );

    return ClassificationResult(
      contaminants: _parseDetections(detectionOutput[0]),
      concentrations: _parseConcentrations(concentrationOutput[0]),
    );
  }
}
```

### Model Specifications

| Property | Specification |
|----------|--------------|
| Framework | TensorFlow Lite (INT8 quantized) |
| Model size | < 200 KB |
| Input | 1000 x 1 (normalized voltammogram) |
| Output heads | 2: detection (sigmoid) + concentration (ReLU) |
| Inference time | < 50 ms on Snapdragon 665 |
| RAM usage | < 2 MB during inference |
| Offline | Yes, fully on-device |

### Alternative: ONNX Runtime Mobile

For devices where TFLite performs poorly:

```dart
// ONNX Runtime as fallback
class OnnxClassifier implements VoltammogramClassifier {
  // Same interface, different runtime
  // Model converted via tf2onnx
  // Typical inference: 30-80 ms
}
```

---

## 15. App: Model Confidence Scores

Every result must include uncertainty. A confident wrong answer is worse than an honest "I don't know."

### Confidence Computation

```dart
class ClassificationResult {
  final List<ContaminantResult> contaminants;

  // Each contaminant result includes:
  // - detected: bool (sigmoid > 0.5)
  // - probability: double (raw sigmoid output, 0.0 - 1.0)
  // - concentration: double (mg/L or ppb)
  // - confidence: ConfidenceLevel (HIGH / MEDIUM / LOW / RETEST)
  // - uncertainty: double (± range)
}

enum ConfidenceLevel { HIGH, MEDIUM, LOW, RETEST }

ConfidenceLevel computeConfidence(double probability, double concentration,
                                   double baselineNoise, int qualityFlag) {
  // Factor 1: Model confidence (sigmoid output distance from 0.5)
  double modelConf = (probability - 0.5).abs() * 2.0;  // 0.0 - 1.0

  // Factor 2: Signal-to-noise ratio
  // Higher concentration relative to noise = more confident
  double snr = concentration / (baselineNoise + 1e-10);

  // Factor 3: Scan quality
  double qualityPenalty = (qualityFlag == QUALITY_GOOD) ? 1.0 :
                          (qualityFlag == QUALITY_MARGINAL) ? 0.7 : 0.3;

  double overall = modelConf * 0.4 + min(snr / 10.0, 1.0) * 0.4 +
                   qualityPenalty * 0.2;

  if (overall > 0.8) return ConfidenceLevel.HIGH;
  if (overall > 0.6) return ConfidenceLevel.MEDIUM;
  if (overall > 0.4) return ConfidenceLevel.LOW;
  return ConfidenceLevel.RETEST;
}
```

### User-Facing Output Example

```
╔══════════════════════════════════════╗
║  WATER TEST RESULTS                 ║
║  Source: Community Well #3          ║
║  Time: 2026-03-07 14:30            ║
╠══════════════════════════════════════╣
║                                      ║
║  Ammonia:  1.8 mg/L ± 0.3           ║
║  ████████████░░░  HIGH CONFIDENCE    ║
║  ⚠ EXCEEDS WHO LIMIT (0.5 mg/L)     ║
║                                      ║
║  Lead:     < 1 ppb                   ║
║  ████████████████  NOT DETECTED      ║
║                                      ║
║  Arsenic:  8.2 ppb ± 2.1            ║
║  ██████████░░░░░  MEDIUM CONFIDENCE  ║
║  ⚠ NEAR WHO LIMIT (10 ppb)          ║
║  → Recommend retest to confirm       ║
║                                      ║
║  Nitrate:  22 mg/L ± 5              ║
║  ████████████░░░  HIGH CONFIDENCE    ║
║  ✓ Below WHO limit (50 mg/L)        ║
║                                      ║
╠══════════════════════════════════════╣
║  OVERALL: ⚠ UNSAFE                  ║
║  Action: Do not drink without        ║
║  treatment. See recommendations.     ║
╚══════════════════════════════════════╝
```

If confidence < MEDIUM for any detected contaminant → app recommends retest.

---

## 16. App: Interference Detection Model

Real water has matrix effects — substances that aren't contaminants but interfere with measurements. A model trained only on clean spiked water will produce wrong results on complex field samples.

### Approach: Autoencoder Anomaly Detection

Train an autoencoder on "normal" voltammograms (clean water + known single contaminants). If a field sample produces a voltammogram that the autoencoder can't reconstruct well, it flags potential interference.

```python
# Training (Python, offline)
def build_autoencoder(input_length=1000):
    encoder = tf.keras.Sequential([
        tf.keras.layers.Conv1D(32, 7, activation='relu', input_shape=(input_length, 1)),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Conv1D(16, 5, activation='relu'),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(32, activation='relu'),  # latent space
    ])

    decoder = tf.keras.Sequential([
        tf.keras.layers.Dense(16 * 250, activation='relu', input_shape=(32,)),
        tf.keras.layers.Reshape((250, 16)),
        tf.keras.layers.UpSampling1D(2),
        tf.keras.layers.Conv1D(32, 5, activation='relu', padding='same'),
        tf.keras.layers.UpSampling1D(2),
        tf.keras.layers.Conv1D(1, 7, activation='linear', padding='same'),
    ])

    autoencoder = tf.keras.Model(
        inputs=encoder.input,
        outputs=decoder(encoder.output)
    )
    autoencoder.compile(optimizer='adam', loss='mse')
    return autoencoder

# Inference (on device)
# reconstruction_error = MSE(input, reconstructed)
# if reconstruction_error > threshold → flag interference
```

### On-Device Inference

```dart
InterferenceResult checkInterference(List<double> voltammogram) {
  var reconstructed = _autoencoderInterpreter.run(voltammogram);
  double mse = _computeMSE(voltammogram, reconstructed);

  if (mse > INTERFERENCE_THRESHOLD_HIGH) {
    return InterferenceResult(
      detected: true,
      severity: 'HIGH',
      message: 'Significant interference detected. '
               'Results may be unreliable. '
               'Consider diluting sample or using colorimetric mode.',
    );
  }
  if (mse > INTERFERENCE_THRESHOLD_LOW) {
    return InterferenceResult(
      detected: true,
      severity: 'MODERATE',
      message: 'Possible matrix interference. '
               'Confidence scores adjusted downward.',
    );
  }
  return InterferenceResult(detected: false);
}
```

This prevents **false safety signals** — the most dangerous failure mode.

---

## 17. ML: Synthetic Voltammogram Generation

Real electrochemical training data is expensive to generate. Synthetic data augments the dataset by 10-50x.

### Physics-Based Simulation

Each contaminant peak follows a Gaussian or Lorentzian shape:

```python
import numpy as np

def generate_synthetic_voltammogram(
    contaminants: list,  # [(name, Ep, concentration), ...]
    noise_level: float = 0.01,
    baseline_slope: float = 0.0,
    electrode_area_factor: float = 1.0,
    temperature: float = 25.0
):
    """Generate a synthetic voltammogram from known peak parameters."""
    V = np.linspace(-0.6, 0.8, 1000)  # voltage sweep
    I = np.zeros_like(V)

    # Add capacitive baseline (linear + quadratic)
    I += baseline_slope * V + 0.001 * V**2

    for name, Ep, conc in contaminants:
        # Peak parameters from literature
        params = CONTAMINANT_PARAMS[name]

        # Randles-Sevcik: Ip proportional to concentration
        Ip = params['sensitivity'] * conc * electrode_area_factor

        # Temperature correction
        Ip *= (1 + params['alpha'] * (temperature - 25.0))
        Ep_shifted = Ep + params['beta'] * (temperature - 25.0) * 0.001

        # Gaussian peak shape
        sigma = params['half_width'] / 2.355  # FWHM to sigma
        peak = Ip * np.exp(-0.5 * ((V - Ep_shifted) / sigma)**2)
        I += peak

    # Add realistic noise
    I += np.random.normal(0, noise_level, len(V))

    # Add electrode-to-electrode variation (random baseline shift)
    I += np.random.normal(0, 0.005)

    return V, I

# Known parameters per contaminant (from published literature)
CONTAMINANT_PARAMS = {
    'ammonia':  {'sensitivity': 0.5,  'Ep': 0.20, 'half_width': 0.08, 'alpha': 0.020, 'beta': -0.59},
    'lead':     {'sensitivity': 2.0,  'Ep': -0.40, 'half_width': 0.05, 'alpha': 0.025, 'beta': -1.20},
    'arsenic':  {'sensitivity': 1.5,  'Ep': 0.10, 'half_width': 0.06, 'alpha': 0.022, 'beta': -0.80},
    'nitrate':  {'sensitivity': 0.3,  'Ep': -0.80, 'half_width': 0.10, 'alpha': 0.018, 'beta': -1.00},
    'iron':     {'sensitivity': 1.0,  'Ep': -0.15, 'half_width': 0.07, 'alpha': 0.020, 'beta': -0.70},
    'cadmium':  {'sensitivity': 1.8,  'Ep': -0.60, 'half_width': 0.05, 'alpha': 0.023, 'beta': -0.90},
}

# Generate training dataset
def generate_training_set(n_samples=10000):
    X, Y_detect, Y_conc = [], [], []

    for _ in range(n_samples):
        # Random selection of 0-3 contaminants
        n_contam = np.random.choice([0, 1, 2, 3], p=[0.2, 0.4, 0.3, 0.1])
        selected = np.random.choice(list(CONTAMINANT_PARAMS.keys()),
                                     n_contam, replace=False)

        contaminants = []
        detect_vec = np.zeros(len(CONTAMINANT_PARAMS))
        conc_vec = np.zeros(len(CONTAMINANT_PARAMS))

        for name in selected:
            idx = list(CONTAMINANT_PARAMS.keys()).index(name)
            # Random concentration within realistic range
            conc = np.random.lognormal(mean=1, sigma=1.5)
            contaminants.append((name, CONTAMINANT_PARAMS[name]['Ep'], conc))
            detect_vec[idx] = 1.0
            conc_vec[idx] = conc

        # Random noise, baseline, temperature variation
        noise = np.random.uniform(0.005, 0.05)
        baseline = np.random.uniform(-0.01, 0.01)
        temp = np.random.uniform(10, 40)
        area_factor = np.random.uniform(0.8, 1.2)

        V, I = generate_synthetic_voltammogram(
            contaminants, noise, baseline, area_factor, temp)

        X.append(I)
        Y_detect.append(detect_vec)
        Y_conc.append(conc_vec)

    return np.array(X), np.array(Y_detect), np.array(Y_conc)
```

### Augmentation Techniques

| Technique | Parameters | Simulates |
|-----------|-----------|-----------|
| Gaussian noise injection | sigma = 0.005 − 0.05 | Electronic noise |
| Baseline shift | offset = ±0.01 | Electrode variation |
| Baseline tilt | slope = ±0.01 | Reference electrode drift |
| Current scaling | factor = 0.8 − 1.2 | Electrode area variation |
| Peak broadening | width × 0.8 − 1.2 | Temperature, kinetics |
| Potential shift | Ep ± 10 mV | Reference electrode variation |
| Multi-contaminant mixing | 0-3 analytes | Real-world samples |

---

## 18. ML: Multi-Label Classification Architecture

Water samples typically contain multiple contaminants simultaneously. The model must handle this.

### Architecture

```
Input: Voltammogram [1000, 1]
  │
  ▼
Conv1D(32, k=7) → BatchNorm → ReLU → MaxPool(2)    [500, 32]
  │
  ▼
Conv1D(64, k=5) → BatchNorm → ReLU → MaxPool(2)    [250, 64]
  │
  ▼
Conv1D(128, k=3) → BatchNorm → ReLU → MaxPool(2)   [125, 128]
  │
  ▼
Conv1D(128, k=3) → BatchNorm → ReLU → GlobalAvgPool [128]
  │
  ▼
Dense(64) → ReLU → Dropout(0.3)                      [64]
  │
  ├──────────────────────────────┐
  │                              │
  ▼                              ▼
Dense(7) → Sigmoid           Dense(7) → ReLU
  │                              │
  ▼                              ▼
DETECTION HEAD               CONCENTRATION HEAD
[ammonia: 0.95]              [ammonia: 1.8 mg/L]
[lead:    0.02]              [lead:    0.0]
[arsenic: 0.87]              [arsenic: 8.2 ppb]
[nitrate: 0.78]              [nitrate: 22 mg/L]
[iron:    0.03]              [iron:    0.0]
[fluoride:0.01]              [fluoride:0.0]
[cadmium: 0.04]              [cadmium: 0.0]
```

### Loss Function

```python
# Multi-task loss with class weighting
def multi_task_loss(y_true_detect, y_pred_detect,
                    y_true_conc, y_pred_conc,
                    detect_weight=1.0, conc_weight=0.5):

    # Detection: weighted binary cross-entropy
    # Weight positive samples higher (contaminants are rare in training)
    pos_weight = 3.0  # 3:1 positive:negative weighting
    detect_loss = tf.nn.weighted_cross_entropy_with_logits(
        y_true_detect, y_pred_detect, pos_weight)

    # Concentration: MSE only where contaminant is present
    mask = tf.cast(y_true_detect > 0.5, tf.float32)
    conc_loss = tf.reduce_mean(
        mask * tf.square(y_true_conc - y_pred_conc))

    return detect_weight * detect_loss + conc_weight * conc_loss
```

### Handling Overlapping Peaks

When multiple metals are present (e.g., Pb at −0.4V and Cd at −0.6V), their peaks overlap. The CNN handles this because:

1. It learns the **full voltammogram shape**, not just individual peaks
2. Overlapping peaks produce characteristic deformed shapes that the CNN recognizes
3. Training on synthetic multi-contaminant data teaches the model to deconvolve peaks

---

## 19. ML: Domain Adaptation for Water Types

Water from different sources has different matrix compositions that affect electrochemical behavior.

### Water Types

| Type | TDS (ppm) | pH | Key Interferents |
|------|-----------|-----|-----------------|
| Groundwater (shallow) | 200-1000 | 6.5-8.0 | Iron, manganese, humic acids |
| Groundwater (deep) | 500-3000 | 7.0-8.5 | Fluoride, arsenic, high TDS |
| Surface water (river) | 100-500 | 6.5-8.5 | Organic matter, turbidity |
| Tap water (treated) | 100-300 | 6.5-7.5 | Chlorine residual |
| Industrial effluent | 1000-10000+ | Variable | Heavy metals, organics |

### Metadata-Conditioned Inference

```python
class DomainAdaptedModel(tf.keras.Model):
    def __init__(self, n_contaminants=7):
        super().__init__()

        # Voltammogram feature extractor (same as before)
        self.conv1 = tf.keras.layers.Conv1D(32, 7, activation='relu')
        self.bn1 = tf.keras.layers.BatchNormalization()
        self.pool1 = tf.keras.layers.MaxPooling1D(2)
        self.conv2 = tf.keras.layers.Conv1D(64, 5, activation='relu')
        self.bn2 = tf.keras.layers.BatchNormalization()
        self.pool2 = tf.keras.layers.MaxPooling1D(2)
        self.conv3 = tf.keras.layers.Conv1D(128, 3, activation='relu')
        self.bn3 = tf.keras.layers.BatchNormalization()
        self.gap = tf.keras.layers.GlobalAveragePooling1D()

        # Metadata encoder
        # Input: [TDS, pH, temperature, water_type_onehot(5)]
        self.meta_dense1 = tf.keras.layers.Dense(16, activation='relu')
        self.meta_dense2 = tf.keras.layers.Dense(16, activation='relu')

        # Combined head
        self.combined_dense = tf.keras.layers.Dense(64, activation='relu')
        self.dropout = tf.keras.layers.Dropout(0.3)

        # Output heads
        self.detection_head = tf.keras.layers.Dense(
            n_contaminants, activation='sigmoid')
        self.concentration_head = tf.keras.layers.Dense(
            n_contaminants, activation='relu')

    def call(self, inputs):
        voltammogram, metadata = inputs

        # Extract voltammogram features
        x = self.pool1(self.bn1(self.conv1(voltammogram)))
        x = self.pool2(self.bn2(self.conv2(x)))
        x = self.gap(self.bn3(self.conv3(x)))

        # Encode metadata
        m = self.meta_dense2(self.meta_dense1(metadata))

        # Concatenate and classify
        combined = tf.concat([x, m], axis=-1)  # [128 + 16 = 144]
        combined = self.dropout(self.combined_dense(combined))

        detection = self.detection_head(combined)
        concentration = self.concentration_head(combined)

        return detection, concentration
```

### How Metadata Is Obtained

1. **TDS**: From colorimetric strip (quick test) or user input
2. **pH**: From colorimetric strip or SPE measurement
3. **Temperature**: From TMP117 on dongle
4. **Water type**: User selects from app dropdown: {Well, Borewell, River, Tap, Other}

These metadata inputs cost nothing extra but significantly improve accuracy.

---

## 20. CV: Color Calibration System

Phone cameras differ wildly. An iPhone 15 and a Redmi Note 8 produce completely different RGB values for the same color.

### Calibration Card

```
┌───────────────────────────────────────────┐
│                                           │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐     │
│  │ W  │ │ L1 │ │ L2 │ │ L3 │ │ Bk │     │  ← Grayscale ramp
│  │255 │ │192 │ │128 │ │ 64 │ │  0 │     │    (for gamma correction)
│  └────┘ └────┘ └────┘ └────┘ └────┘     │
│                                           │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐     │
│  │ R  │ │ Y  │ │ G  │ │ C  │ │ B  │     │  ← Chromatic patches
│  │sRGB│ │sRGB│ │sRGB│ │sRGB│ │sRGB│     │    (known LAB values)
│  └────┘ └────┘ └────┘ └────┘ └────┘     │
│                                           │
│  ◆ ArUco #0              ◆ ArUco #1      │
│                                           │
│  ┌─────────────────────────────────────┐ │
│  │                                     │ │
│  │     TEST STRIP PLACEMENT ZONE       │ │
│  │                                     │ │
│  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐      │ │
│  │  │ pH │ │ NH3│ │ NO3│ │ Fe │      │ │  ← Reagent pads
│  │  └────┘ └────┘ └────┘ └────┘      │ │
│  │                                     │ │
│  └─────────────────────────────────────┘ │
│                                           │
│  ◆ ArUco #2              ◆ ArUco #3      │
│                                           │
└───────────────────────────────────────────┘
```

### Color Correction Algorithm

```python
class ColorCalibrator:
    """Corrects phone camera color response using calibration card."""

    # Known reference LAB values for each calibration patch
    REFERENCE_LAB = {
        'white':   (100.0,  0.0,   0.0),
        'light1':  (75.0,   0.0,   0.0),
        'light2':  (50.0,   0.0,   0.0),
        'dark':    (25.0,   0.0,   0.0),
        'black':   (0.0,    0.0,   0.0),
        'red':     (53.2,   80.1,  67.2),
        'yellow':  (97.1,  -21.6,  94.5),
        'green':   (87.7,  -86.2,  83.2),
        'cyan':    (91.1,  -48.1, -14.1),
        'blue':    (32.3,   79.2, -107.7),
    }

    def compute_correction_matrix(self, captured_patches: dict):
        """Compute 3x3 color correction matrix from captured vs reference."""
        # Convert captured RGB → LAB
        captured_lab = {k: rgb_to_lab(v) for k, v in captured_patches.items()}

        # Build system of equations: M * captured = reference
        # Solve using least squares
        A = np.array([captured_lab[k] for k in self.REFERENCE_LAB])
        B = np.array([self.REFERENCE_LAB[k] for k in self.REFERENCE_LAB])

        # Affine correction: LAB_corrected = M @ LAB_captured + offset
        # Solve with pseudo-inverse
        A_aug = np.hstack([A, np.ones((len(A), 1))])
        params, _, _, _ = np.linalg.lstsq(A_aug, B, rcond=None)

        self.M = params[:3, :]   # 3x3 rotation/scale
        self.offset = params[3, :]  # 1x3 offset

    def correct(self, lab_value):
        """Apply correction to a measured LAB value."""
        return self.M @ lab_value + self.offset
```

### Accuracy Target

| Metric | Target |
|--------|--------|
| Color error (deltaE) after correction | < 5 (imperceptible) |
| Concentration error from color analysis | < 10% |
| Cross-phone variability after correction | < 3% |

---

## 21. CV: Lighting Correction Pipeline

Even with a calibration card, extreme lighting conditions degrade results.

### Pipeline

```python
class LightingCorrector:
    def correct(self, image, aruco_corners):
        # Step 1: Perspective correction (using ArUco markers)
        warped = self.perspective_transform(image, aruco_corners)

        # Step 2: White balance correction
        # Use the white patch on calibration card as reference
        white_patch = self.extract_patch(warped, 'white')
        white_point = np.mean(white_patch, axis=(0, 1))  # [R, G, B]
        # Scale so white → [255, 255, 255]
        scale = np.array([255.0, 255.0, 255.0]) / (white_point + 1e-6)
        corrected = np.clip(warped * scale, 0, 255).astype(np.uint8)

        # Step 3: Histogram equalization (CLAHE)
        # Applied to L channel only (preserve color)
        lab = cv2.cvtColor(corrected, cv2.COLOR_RGB2LAB)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        corrected = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

        # Step 4: Shadow detection and removal
        # Compute illumination map from grayscale patches
        gray_values = [
            np.mean(self.extract_patch(corrected, p))
            for p in ['white', 'light1', 'light2', 'dark', 'black']
        ]
        expected_values = [255, 192, 128, 64, 0]
        # Fit gamma curve: pixel = 255 * (value/255)^gamma
        gamma = np.polyfit(
            np.log(np.array(gray_values[:-1]) + 1),
            np.log(np.array(expected_values[:-1]) + 1), 1)[0]
        # Apply inverse gamma correction
        corrected = np.clip(
            255 * (corrected / 255.0) ** (1.0 / gamma), 0, 255
        ).astype(np.uint8)

        return corrected
```

### Robustness Targets

| Condition | Target Accuracy |
|-----------|----------------|
| Indoor fluorescent lighting | Color error < 5% |
| Outdoor direct sunlight | Color error < 5% |
| Outdoor shade | Color error < 7% |
| Indoor warm LED (2700K) | Color error < 5% |
| Low light (< 100 lux) | App warns "Insufficient light" |

---

## 22. Security: Device Authentication

Crowdsourced data is only valuable if it's trustworthy. Fake data injection would corrupt the contamination maps.

### Device Key

Each potentiostat dongle has a unique identity:

```c
typedef struct {
    uint32_t device_id;           // Unique serial number
    uint8_t  device_key[32];      // Ed25519 private key (generated in factory)
    uint8_t  device_cert[64];     // Public key signed by JalSakhi root CA
} device_identity_t;

// Stored in STM32 option bytes (read-protected, cannot be extracted)
```

### Signed Data Packets

Every test result is cryptographically signed:

```c
typedef struct {
    uint32_t device_id;
    uint32_t timestamp;
    uint32_t test_sequence_number;
    float    results[7];          // concentrations
    uint8_t  fault_flags;
    float    temperature;
    float    gps_lat;             // from phone
    float    gps_lon;             // from phone
    uint8_t  signature[64];       // Ed25519 signature of all above fields
} signed_test_result_t;
```

### Verification

The cloud backend verifies:
1. Device ID exists in the registry
2. Signature is valid (Ed25519 verify with device's public key)
3. Timestamp is within acceptable range (±1 hour)
4. Sequence number is monotonically increasing (no replay)
5. GPS coordinates are consistent with device's registered region

---

## 23. Security: Tamper Detection

Even with authentic devices, users might submit bad data (intentionally or unintentionally).

### Statistical Tamper Checks

```python
class TamperDetector:
    """Server-side checks for suspicious data patterns."""

    def check(self, test_result, user_history, regional_data):
        flags = []

        # Check 1: Identical readings repeated
        # Same concentrations across multiple tests = likely fabricated
        recent = user_history[-10:]
        if len(recent) >= 3:
            concentrations = [r.results for r in recent]
            if self._all_identical(concentrations, tolerance=0.01):
                flags.append('IDENTICAL_READINGS')

        # Check 2: Impossible chemical combinations
        # High ammonia + very low pH is chemically unlikely
        nh3 = test_result.results[AMMONIA_IDX]
        ph = test_result.metadata.get('pH', 7.0)
        if nh3 > 5.0 and ph < 4.0:
            flags.append('IMPOSSIBLE_CHEMISTRY')

        # Check 3: Extreme outlier vs regional data
        # If all nearby devices show clean water but one shows extreme contamination
        regional_mean = np.mean([r.results for r in regional_data], axis=0)
        regional_std = np.std([r.results for r in regional_data], axis=0)
        z_scores = (test_result.results - regional_mean) / (regional_std + 1e-6)
        if np.any(np.abs(z_scores) > 5.0):
            flags.append('EXTREME_OUTLIER')

        # Check 4: Physically impossible values
        for i, conc in enumerate(test_result.results):
            if conc < 0 or conc > MAX_PHYSICAL_CONCENTRATION[i]:
                flags.append('IMPOSSIBLE_VALUE')

        # Check 5: Test frequency anomaly
        # User submitting 100 tests per hour = suspicious
        recent_hour = [r for r in user_history
                       if r.timestamp > time.time() - 3600]
        if len(recent_hour) > 20:
            flags.append('EXCESSIVE_FREQUENCY')

        return flags
```

### Response to Flags

| Flag | Action |
|------|--------|
| No flags | Data accepted, included in maps |
| 1 minor flag | Data accepted with quality marker |
| 2+ flags | Data quarantined, manual review |
| IMPOSSIBLE_VALUE | Data rejected automatically |
| IDENTICAL_READINGS (3+) | User flagged, data quarantined |

---

## 24. Cloud Platform

### Spatial Interpolation (Kriging)

```python
from pykrige.ok import OrdinaryKriging

class ContaminationMapper:
    def generate_heatmap(self, test_results, contaminant_idx, grid_resolution=100):
        lats = [r.gps_lat for r in test_results]
        lons = [r.gps_lon for r in test_results]
        values = [r.results[contaminant_idx] for r in test_results]

        OK = OrdinaryKriging(
            lons, lats, values,
            variogram_model='spherical',
            verbose=False,
            enable_plotting=False,
        )

        grid_lon = np.linspace(min(lons)-0.01, max(lons)+0.01, grid_resolution)
        grid_lat = np.linspace(min(lats)-0.01, max(lats)+0.01, grid_resolution)

        z, ss = OK.execute('grid', grid_lon, grid_lat)
        # z = interpolated values, ss = variance (uncertainty)

        return grid_lon, grid_lat, z, ss
```

### Temporal Forecasting (LSTM)

```python
class ContaminationForecaster:
    def build_model(self, lookback=30, n_features=7):
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(64, return_sequences=True,
                                  input_shape=(lookback, n_features)),
            tf.keras.layers.LSTM(32),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(n_features),  # predict next day's values
        ])
        model.compile(optimizer='adam', loss='mse')
        return model
```

### Anomaly Detection (Isolation Forest)

```python
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.05,  # expect 5% anomalies
            random_state=42
        )

    def fit(self, historical_data):
        self.model.fit(historical_data)

    def detect(self, new_reading):
        score = self.model.decision_function([new_reading])[0]
        is_anomaly = self.model.predict([new_reading])[0] == -1

        if is_anomaly:
            return {
                'anomaly': True,
                'score': score,
                'classification': self._classify_anomaly(new_reading)
            }
        return {'anomaly': False, 'score': score}

    def _classify_anomaly(self, reading):
        # Rule-based classification of anomaly type
        if reading[AMMONIA_IDX] > 2.0 and reading[NITRATE_IDX] > 20:
            return 'SEWAGE_CONTAMINATION'
        if reading[LEAD_IDX] > 10 or reading[CADMIUM_IDX] > 3:
            return 'INDUSTRIAL_DISCHARGE'
        if reading[NITRATE_IDX] > 50 and reading[AMMONIA_IDX] < 0.5:
            return 'AGRICULTURAL_RUNOFF'
        return 'UNKNOWN_ANOMALY'
```

### Municipal Dashboard

Web application (React + Leaflet.js) showing:
- Real-time contamination heatmaps per contaminant
- District/block/GP water safety scores
- Active alerts with source attribution
- Trending analysis (improving/worsening)
- Jal Sakhi network status (active testers, coverage)
- Compliance reports (exportable PDF for government)
