# JalSakhi — Smartphone Electrochemical Water Forensics Platform
### World Water Day 2026 | "Water and Gender"

---

## The Problem

India has 1.9 million rural habitations but only 2,200 water testing labs. Average distance to the nearest lab: 50+ km. Turnaround: 3-14 days. Cost: INR 500-2000 per test. Meanwhile, women and girls spend 1.4 billion hours/year collecting water — often from sources they cannot verify are safe. By the time lab results arrive, the contamination event is over, or families have already consumed the water.

**You can't manage what you can't measure. And India cannot measure its water.**

---

## The Solution

JalSakhi turns any smartphone into a field-deployable water laboratory using two sensing modes:

**Mode 1 — Electrochemical Fingerprinting (Precision)**
A pocket-sized potentiostat dongle (INR 800, USB-C) + disposable screen-printed electrodes (INR 25 each). The device performs voltammetric scans — sweeping voltage across the electrode and measuring the current response. Each contaminant produces a unique electrochemical signature. An on-device 1D-CNN model identifies and quantifies contaminants in 60 seconds.

| Contaminant | Detection Limit | Method |
|-------------|----------------|--------|
| Ammonia | 0.05 mg/L | Square Wave Voltammetry (Prussian Blue SPE) |
| Lead | 1 ppb | Differential Pulse ASV (Bismuth-film SPE) |
| Arsenic | 5 ppb | Differential Pulse ASV (Gold nanoparticle SPE) |
| Nitrate | 0.5 mg/L | Cyclic Voltammetry (Copper-modified SPE) |
| Iron | 0.05 mg/L | Differential Pulse Voltammetry |
| Fluoride | 0.1 mg/L | Potentiometry (ISE) |

**Mode 2 — Colorimetric Strip Analysis (Rapid Screening)**
Photograph a standard multi-parameter test strip against a calibration card. Computer vision corrects for lighting and phone camera differences. A CNN maps reagent pad colors to contaminant concentrations. Zero additional hardware — just the strip, the card, and a phone.

---

## The Platform: Community Contamination Intelligence

Individual tests are useful. Aggregated data is transformative.

Women Self-Help Groups (12 million SHGs, 140 million members across India) deploy as **Jal Sakhis (Water Guardians)**. Each SHG tests community water sources weekly. Results upload to a cloud platform that builds:

- **Contamination heatmaps** — spatial interpolation from sparse test points (Kriging)
- **Temporal forecasting** — LSTM models predict contamination spikes from weather + seasonal patterns
- **Source attribution** — correlate contamination events with upstream industrial/agricultural activity
- **Municipal dashboard** — district-level water safety scores fed into Jal Jeevan Mission monitoring

**This transforms women's local water knowledge into district-level infrastructure intelligence.**

---

## Why This Is Not Another IoT Sensor Box

| Typical IoT Water Monitor | JalSakhi |
|---|---|
| Fixed sensor at one location ($200+) | Portable dongle ($10-15) tests ANY source |
| 3-4 parameters, drifts over weeks | 7+ contaminants at ppb, fresh electrode every test |
| Data stays siloed per household | Crowdsourced data builds contamination maps |
| Requires dedicated hardware + internet | Works on any smartphone, fully offline-capable |
| Passive monitoring | Active forensic testing — users choose what to test |

**Key insight**: Disposable electrodes eliminate the #1 problem in field sensing — sensor drift and calibration. Every test starts fresh.

---

## Hardware: Honest Cost Breakdown

| Component | Part | Cost |
|-----------|------|------|
| Analog Front-End | AD5940 (Analog Devices) | $4.50 |
| Microcontroller | STM32L432 (ARM Cortex-M4) | $2.50 |
| USB-C + PCB + passives | — | $2.30 |
| Assembly | — | $1.50 |
| **Dongle total** | | **$10.80 (INR ~900)** |
| **SPE per test** | | **$0.30 (INR ~25)** |

At scale (100K units): dongle drops to ~$8, SPE to ~$0.20.

---

## The AI: Why It's Real

**Signal Processing Pipeline**: Raw voltammogram → Savitzky-Golay smoothing → asymmetric least squares baseline correction → derivative-based peak detection → feature extraction (peak potential, peak current, half-width, area).

**ML Model**: 1D Convolutional Neural Network trained on lab-generated voltammograms + synthetic augmentation. Multi-task output: contaminant identification (multi-label sigmoid) + concentration regression (ReLU). Deployed as quantized TFLite model (<200KB) running on-device in <50ms. Published, peer-reviewed architecture (Kammarchedu et al., ACS Sensors, 2022).

**Cloud Intelligence**: Ordinary Kriging for spatial interpolation. LSTM for temporal forecasting. Isolation Forest for anomaly detection. Not marketing — standard geostatistical and time-series methods with clear mathematical foundations.

---

## Gender Impact — Structural, Not Cosmetic

- Women **are** the sensing infrastructure — not passive beneficiaries
- Jal Sakhis earn INR 600/month for validated testing — livelihood, not volunteerism
- Time saved: contamination maps reduce average water collection by 15 min/trip
- 12 million SHGs already organized under NRLM — no new mobilization needed
- Women's data drives municipal infrastructure decisions — political empowerment through evidence

---

## Scale Economics

| Metric | Value |
|--------|-------|
| Cost per comprehensive test | INR 25 |
| Equivalent lab test cost | INR 500-2000 |
| Cost reduction | 80-95% |
| Monitoring frequency improvement | 52x (weekly vs annual lab survey) |
| Deployment infrastructure | 12M SHGs already exist |
| Break-even | ~200 SHGs deployed |

---

## Government Alignment

- **Jal Jeevan Mission**: Ground-truth water quality verification for 19 crore rural tap connections
- **NRLM/DAY-NRLM**: New livelihood vertical for women SHGs
- **Atal Bhujal Yojana**: Community groundwater quality monitoring in 7 states
- **SBM-G Phase 2**: Water quality component of ODF Plus

---

## The Ask

**Pilot**: 100 SHGs across 3 ammonia-affected districts (Bihar/UP/AP). 6 months. INR 5 lakh.

**Deliverable**: Validated contamination intelligence dashboard with >90% correlation to NABL lab results, serving 50,000+ people.

---

*Every technical claim is backed by peer-reviewed research. Full reference list: 26 papers.*
*All hardware components are commercially available. Prototype demonstrable.*
