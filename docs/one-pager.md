# JalSakhi — Smartphone Electrochemical Water Forensics Platform
### World Water Day 2026 | "Water and Gender"

---

## The Problem

India has 1.9 million rural habitations but only 2,200 water testing labs. Turnaround: 3-14 days. Cost: INR 500-2000 per test. Women and girls spend 1.4 billion hours/year collecting water — often from sources they cannot verify are safe. By the time lab results arrive, families have already consumed the water.

**You can't manage what you can't measure. And India cannot measure its water.**

---

## The Solution

JalSakhi turns any smartphone into a field-deployable water laboratory.

**Mode 1 — Electrochemical Fingerprinting (Precision)**
A pocket-sized potentiostat dongle (INR 1,200) connects via USB-C. Disposable screen-printed electrodes (INR 25 each) dip into a water sample. The device performs voltammetric scans — a controlled voltage sweep while measuring picoamp-to-milliamp current response. Each contaminant produces a unique electrochemical signature. An on-device 1D-CNN identifies and quantifies contaminants in 60 seconds.

| Contaminant | Detection Limit | Method |
|-------------|----------------|--------|
| Ammonia | 0.05 mg/L | SWV (Prussian Blue SPE) |
| Lead | 1 ppb | DPASV (Bismuth-film SPE) |
| Arsenic | 5 ppb | DPASV (Gold nanoparticle SPE) |
| Nitrate | 0.5 mg/L | CV (Copper-modified SPE) |
| Iron | 0.05 mg/L | DPV (bare carbon) |
| Fluoride | 0.1 mg/L | Potentiometry (ISE) |

**Mode 2 — Colorimetric Strip Analysis (Rapid Screening)**
Photograph a test strip against a calibration card. Computer vision corrects for phone camera and lighting differences via ArUco marker detection + 10-patch color correction matrix. Zero hardware needed — just strips, card, and phone.

---

## Engineering Depth — Not a Generic ADC Board

**Potentiostat architecture** (AD5940 AFE + STM32L432):
- 12-bit DAC waveform generator (CV/DPV/SWV/ASV/EIS)
- Control amplifier maintains WE-RE potential via CE feedback loop
- Programmable TIA (200 Ω to 10 MΩ) with auto-range: 10 nA to 10 mA dynamic range
- 16-bit ADC at 200 kSPS, PGA 1x-9x, Sinc2+Sinc3 digital filtering
- Current resolution: ≤ 10 nA | Voltage resolution: ≤ 1 mV | SNR > 40 dB

**Noise control**: 4-layer PCB (signal/GND/power/digital split), separate analog/digital LDO rails, ferrite bead isolation, stamped metal shielding can, guard ring on high-impedance traces, RC anti-aliasing filter.

**Temperature compensation**: TMP117 sensor (±0.1°C) near electrode connector. Firmware corrects peak current and potential per contaminant using Arrhenius-derived coefficients: `I_corrected = I_measured / (1 + α(T − T_ref))`.

**Electrode contact**: Gold-plated Mill-Max pogo pins (100 gf spring force), mechanical guide slot (±0.25mm), contact impedance verified before every scan (< 5 Ω variation).

**Calibration**: Factory calibration stored in flash (sensitivity, offset, LOD, LOQ per electrode type). Field calibration via standard solution — correction factor applied until recalibration. Target: < 5% error.

**Deterministic waveform control**: TIM2 hardware interrupt drives DAC stepping with < 10 us jitter. DMA-based SPI transfers to AD5940. Synchronized ADC sampling.

**Fault detection**: Pre-scan checks (electrode presence, sample presence, contact stability, temperature range, calibration age). Post-scan checks (ADC saturation, baseline slope anomaly). Bad tests are rejected automatically with clear user guidance.

**Power**: Idle < 2 uA, active scan < 25 mA. Full test cycle: ~0.7 mAh. A 4000 mAh phone powers 5000+ tests.

---

## The AI: Why It's Real

**On-device signal processing**: Savitzky-Golay smoothing → ALS baseline correction → derivative peak detection → feature extraction (Ep, Ip, width, area). Runs on STM32 before data reaches the phone.

**ML model**: 1D-CNN (4 conv layers → GAP → shared dense → dual heads). Detection head (sigmoid, multi-label) + concentration head (ReLU, regression). INT8 quantized TFLite, < 200 KB, < 50 ms inference.

**Confidence scoring**: Combines model probability, signal-to-noise ratio, and scan quality flag. Output: HIGH / MEDIUM / LOW / RETEST. Low confidence → app recommends retest.

**Interference detection**: Autoencoder trained on "normal" voltammograms. High reconstruction error → "Possible matrix interference detected."

**Synthetic training data**: Physics-based voltammogram generator using Gaussian peak models + Randles-Sevcik kinetics. Augmented with noise, baseline, temperature, and electrode variation.

**Domain adaptation**: Model takes metadata input (TDS, pH, temperature, water type) to adapt predictions for groundwater vs. surface vs. tap water matrices.

**Cloud intelligence**: Ordinary Kriging for contamination heatmaps. LSTM for temporal forecasting. Isolation Forest for anomaly detection with source attribution (sewage/industrial/agricultural).

---

## Security and Data Integrity

**Device authentication**: Each dongle has a factory-provisioned Ed25519 key in read-protected flash. Every test result is cryptographically signed. Cloud verifies signature, timestamp, sequence number, and GPS consistency.

**Tamper detection**: Server-side statistical checks — identical readings, impossible chemical combinations, extreme outliers vs. regional data, physically impossible values, excessive test frequency. Suspicious data is quarantined.

---

## The Platform: Community Contamination Intelligence

Women Self-Help Groups (12M SHGs, 140M members) deploy as **Jal Sakhis (Water Guardians)**. Each SHG tests community water sources weekly. Aggregated data builds district-level contamination intelligence fed into Jal Jeevan Mission dashboards.

**Gender impact — structural**: Women are the sensing infrastructure. Jal Sakhis earn INR 600/month for validated testing. Contamination maps reduce water collection time. Women's data drives municipal infrastructure decisions.

---

## Honest Cost Breakdown

| Component | Cost |
|-----------|------|
| AD5940 AFE | $4.50 |
| STM32L432 MCU | $2.50 |
| TMP117 temp sensor | $1.20 |
| Pogo pins (3x Mill-Max) | $1.20 |
| LDOs, ferrites, caps, ESD | $0.85 |
| 4-layer PCB + shielding can | $1.50 |
| Assembly | $1.50 |
| Enclosure | $0.40 |
| **Dongle total** | **$14.29 (INR ~1,200)** |
| **SPE per test** | **$0.30 (INR ~25)** |

---

## The Ask

**Pilot**: 100 SHGs across 3 ammonia-affected districts. 6 months. INR 5 lakh.
**Deliverable**: Validated contamination intelligence dashboard with >90% correlation to NABL lab results.

*Every claim backed by 26 peer-reviewed references. All components commercially available. Prototype demonstrable.*
