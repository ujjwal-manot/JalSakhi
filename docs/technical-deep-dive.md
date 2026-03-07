# Technical Deep Dive

## 1. Electrochemical Sensing — The Science

### Why Electrochemistry?

Electrochemistry is the gold standard for field-deployable water analysis because:
- **No reagent preparation** — the electrode IS the reagent
- **Multi-analyte from one scan** — different contaminants oxidize/reduce at different potentials
- **ppb-level sensitivity** — stripping voltammetry pre-concentrates analytes on the electrode
- **Miniaturizable** — the entire instrument is an analog circuit
- **Quantitative** — peak current is directly proportional to concentration (Randles-Sevcik equation)

### Voltammetric Techniques Used

#### Cyclic Voltammetry (CV)
- Sweep potential linearly from V1 → V2 → V1
- Measures oxidation and reduction currents
- Used for: qualitative identification, electrode characterization
- Scan rate: 50-100 mV/s

#### Differential Pulse Voltammetry (DPV)
- Staircase potential + small pulse at each step
- Measures difference current (pulse - baseline)
- **10-100x more sensitive than CV**
- Used for: heavy metals (Pb, As, Cd, Cu)
- Pulse amplitude: 50 mV, step: 4 mV, pulse width: 50 ms

#### Square Wave Voltammetry (SWV)
- Square wave superimposed on staircase
- Measures forward - reverse current
- Fastest technique, best signal-to-noise
- Used for: ammonia, nitrate, organic contaminants
- Frequency: 25 Hz, amplitude: 25 mV, step: 4 mV

#### Anodic Stripping Voltammetry (ASV)
- Pre-concentration: deposit metals on electrode at negative potential
- Stripping: sweep positive, metals oxidize sequentially
- Each metal has a characteristic stripping potential:
  - Zinc: -1.0 V
  - Cadmium: -0.6 V
  - Lead: -0.4 V
  - Copper: -0.1 V
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
              (to potentiostat)
```

- **WE (Working Electrode)**: Where the chemistry happens. Modified with nanomaterials.
- **CE (Counter Electrode)**: Completes the circuit. Carbon.
- **RE (Reference Electrode)**: Provides stable potential reference. Ag/AgCl.

Substrate: Ceramic (Al2O3) or PET plastic
Dimensions: 34mm x 10mm x 0.5mm (standard DropSens format)
Sample volume: 50-100 µL (one drop)

### Electrode Modifications — Recipe Book

#### For Ammonia (NH4+/NH3)
- **Modification**: Prussian Blue (PB) nanoparticles electrodeposited on carbon WE
- **Mechanism**: PB catalyzes ammonia oxidation at +0.2V vs Ag/AgCl
- **Procedure**: Cyclic voltammetry in 2mM K3[Fe(CN)6] + 2mM FeCl3 + 0.1M KCl + 0.01M HCl, 20 cycles, 50 mV/s
- **Detection range**: 0.05 - 50 mg/L
- **Reference**: Luo et al., Analytical Chemistry, 2019

#### For Lead (Pb2+)
- **Modification**: Bismuth film on carbon WE (in-situ plating)
- **Mechanism**: Bi and Pb co-deposit during preconcentration, strip sequentially
- **Procedure**: Add 400 ppb Bi3+ to sample, deposit at -1.2V for 120s, strip by DPV
- **Detection range**: 1 - 500 ppb
- **Reference**: Wang et al., Electroanalysis, 2005

#### For Arsenic (As3+)
- **Modification**: Gold nanoparticles on carbon WE
- **Mechanism**: As deposits on Au at -0.3V, strips at +0.1V
- **Procedure**: Electrodeposit Au from 1mM HAuCl4 in 0.5M H2SO4
- **Detection range**: 5 - 500 ppb
- **Reference**: Salimi et al., Analyst, 2008

#### For Nitrate (NO3-)
- **Modification**: Copper nanoparticles on carbon WE
- **Mechanism**: Cu catalyzes nitrate reduction at -0.8V
- **Procedure**: Electrodeposit Cu from 10mM CuSO4 in 0.1M H2SO4
- **Detection range**: 0.5 - 100 mg/L
- **Reference**: Ding et al., Talanta, 2019

---

## 2. Potentiostat Hardware Design

### Block Diagram

```
Smartphone (USB-C)
     │
     ▼
┌──────────────────────────────────────────┐
│  USB-C Interface                         │
│  (Power + Data via CDC/ACM serial)       │
├──────────────────────────────────────────┤
│  STM32L432KC (ARM Cortex-M4)            │
│  - Receives commands from phone          │
│  - Controls AD5940 via SPI               │
│  - Streams data to phone via USB serial  │
│  - 64KB RAM, 256KB Flash                 │
├────────────┬─────────────────────────────┤
│  SPI Bus   │                             │
│            ▼                             │
│  ┌────────────────────────────────┐      │
│  │  AD5940 Analog Front-End      │      │
│  │                                │      │
│  │  ┌──────────────────────────┐ │      │
│  │  │ Waveform Generator       │ │      │
│  │  │ - 12-bit DAC             │ │      │
│  │  │ - CV/DPV/SWV/EIS modes   │ │      │
│  │  └──────────┬───────────────┘ │      │
│  │             │                  │      │
│  │  ┌──────────▼───────────────┐ │      │
│  │  │ Potentiostat Circuit     │ │      │
│  │  │ - Control amp (OA)       │ │      │
│  │  │ - TIA (10Ω - 10MΩ)      │ │      │
│  │  │ - Voltage feedback loop  │ │      │
│  │  └──────────┬───────────────┘ │      │
│  │             │                  │      │
│  │  ┌──────────▼───────────────┐ │      │
│  │  │ Measurement              │ │      │
│  │  │ - 16-bit ADC, 200kSPS   │ │      │
│  │  │ - PGA (1x to 16x)       │ │      │
│  │  │ - DFT engine (for EIS)  │ │      │
│  │  └──────────────────────────┘ │      │
│  └────────────────────────────────┘      │
│                                          │
│  Electrode Connector (3-pin)             │
│  [WE] [RE] [CE]                          │
└──────────────────────────────────────────┘
     │     │     │
     ▼     ▼     ▼
  Screen-Printed Electrode
```

### Key Design Decisions

**Why AD5940 over discrete op-amps?**
- Integrated solution = smaller PCB, fewer components, lower noise
- Built-in waveform sequencer — runs experiments without CPU intervention
- DFT engine enables EIS (electrochemical impedance spectroscopy) as future feature
- Ultra-low power — entire dongle draws <5mA

**Why STM32L432 over ESP32?**
- USB device mode (ESP32 needs external USB-serial chip)
- Lower power consumption (40 uA/MHz vs 80 uA/MHz)
- Hardware SPI at 50 MHz (fast AD5940 communication)
- No WiFi needed — phone handles connectivity
- Smaller package (QFN-32, 5x5mm)

**Why USB-C over Bluetooth/WiFi?**
- Zero latency data streaming (voltammograms need real-time display)
- Phone powers the dongle (no battery needed)
- Simpler hardware, fewer failure modes
- Universal compatibility (USB CDC works on all Android/iOS)

### PCB Specifications

- **Size**: 30mm x 15mm x 5mm (size of a USB drive)
- **Layers**: 2 (top: signal, bottom: ground plane)
- **Impedance**: Controlled ground plane for analog noise reduction
- **Connector**: USB-C male (plugs directly into phone)
- **Electrode connector**: 3-pin edge connector (spring-loaded for SPE)
- **ESD protection**: TVS diodes on USB lines and electrode connections

---

## 3. Signal Processing Pipeline

### Raw Data → Clean Signal → Features → Classification

```
Raw Voltammogram
  │
  ▼
[Noise Reduction]
  - Moving average filter (window = 5)
  - Savitzky-Golay filter (order 3, window 15)
  │
  ▼
[Baseline Correction]
  - Asymmetric Least Squares (ALS) algorithm
  - Rubinstein-Russling method for CV
  - Iterative polynomial fitting
  │
  ▼
[Peak Detection]
  - First derivative zero-crossing
  - Second derivative local minima
  - Gaussian/Lorentzian peak fitting
  │
  ▼
[Feature Extraction]
  - Peak potential (Ep) ← identifies contaminant
  - Peak current (Ip) ← proportional to concentration
  - Half-peak width (W1/2)
  - Peak area (integral)
  - Peak shape descriptors
  - Full voltammogram embedding (for CNN)
  │
  ▼
[Classification & Quantification]
  - 1D-CNN for contaminant identification
  - Linear regression Ip vs concentration (calibration curve)
  - Confidence intervals from model uncertainty
```

### Signal Processing Code Structure

```python
class VoltammogramProcessor:
    def __init__(self, technique: str):
        self.technique = technique  # 'CV', 'DPV', 'SWV', 'ASV'

    def preprocess(self, voltage, current):
        current = self.savitzky_golay(current, window=15, order=3)
        baseline = self.als_baseline(current, lam=1e6, p=0.01)
        current_corrected = current - baseline
        return voltage, current_corrected

    def detect_peaks(self, voltage, current):
        # First derivative method
        di_dv = np.gradient(current, voltage)
        zero_crossings = np.where(np.diff(np.sign(di_dv)))[0]
        # Filter by peak prominence
        peaks = [(voltage[i], current[i]) for i in zero_crossings
                 if current[i] > self.noise_threshold]
        return peaks

    def extract_features(self, voltage, current, peaks):
        features = {}
        for i, (ep, ip) in enumerate(peaks):
            features[f'peak_{i}_potential'] = ep
            features[f'peak_{i}_current'] = ip
            features[f'peak_{i}_width'] = self.half_peak_width(voltage, current, ep)
            features[f'peak_{i}_area'] = self.peak_area(voltage, current, ep)
        return features

    def quantify(self, ip, calibration_curve):
        # Randles-Sevcik: Ip = 2.69e5 * n^1.5 * A * D^0.5 * C * v^0.5
        # Simplified: C = Ip / sensitivity
        concentration = calibration_curve.predict(ip)
        return concentration
```

---

## 4. ML Model Details

### Training Data Generation

Since we can't collect thousands of field samples immediately, we use a hybrid approach:

1. **Lab-generated voltammograms** (primary)
   - Prepare standard solutions of each contaminant at 10 concentration levels
   - Run 5 replicates per concentration per electrode
   - Use multiple SPE batches for electrode variability
   - Total: ~500 real voltammograms per contaminant

2. **Synthetic augmentation** (expand dataset 10x)
   - Add Gaussian noise (simulating different electrodes)
   - Shift baseline (simulating temperature effects)
   - Scale current (simulating electrode area variation)
   - Mix contaminant voltammograms (simulating real water with multiple contaminants)

3. **Published datasets** (validation)
   - Use voltammograms from published literature as external validation
   - Ensures model generalizes beyond our lab conditions

### Model Training Pipeline

```python
# Pseudocode for training
import tensorflow as tf

def build_voltammogram_cnn(input_length=1000, n_contaminants=7):
    model = tf.keras.Sequential([
        # Feature extraction
        tf.keras.layers.Conv1D(32, 7, activation='relu',
                               input_shape=(input_length, 1)),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling1D(2),

        tf.keras.layers.Conv1D(64, 5, activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling1D(2),

        tf.keras.layers.Conv1D(128, 3, activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.GlobalAveragePooling1D(),

        # Shared representation
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.3),
    ])

    # Multi-task output
    input_layer = model.input
    shared = model.output

    # Task 1: Contaminant detection (multi-label classification)
    detection = tf.keras.layers.Dense(
        n_contaminants, activation='sigmoid', name='detection'
    )(shared)

    # Task 2: Concentration estimation (regression)
    concentration = tf.keras.layers.Dense(
        n_contaminants, activation='relu', name='concentration'
    )(shared)

    multi_task_model = tf.keras.Model(
        inputs=input_layer,
        outputs=[detection, concentration]
    )

    multi_task_model.compile(
        optimizer='adam',
        loss={
            'detection': 'binary_crossentropy',
            'concentration': 'mse'
        },
        loss_weights={'detection': 1.0, 'concentration': 0.5},
        metrics={
            'detection': 'accuracy',
            'concentration': 'mae'
        }
    )
    return multi_task_model
```

### Edge Deployment

- Convert to TensorFlow Lite (quantized INT8)
- Model size: ~200 KB (fits on any phone)
- Inference time: <50ms on mid-range Android
- Works completely offline

---

## 5. Colorimetric Analysis System

### Calibration Card Design

```
┌─────────────────────────────────┐
│                                 │
│  ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐    │
│  │W │ │Bk│ │R │ │G │ │B │    │  ← Known color patches
│  │  │ │  │ │  │ │  │ │  │    │    (for color correction)
│  └──┘ └──┘ └──┘ └──┘ └──┘    │
│                                 │
│  ◆ ArUco                ◆ ArUco│  ← Markers for
│  Marker 1               Marker 2│   perspective correction
│                                 │
│  ┌────────────────────────────┐ │
│  │    Test Strip Placement    │ │
│  │    ┌──┐┌──┐┌──┐┌──┐┌──┐  │ │
│  │    │pH││NH││NO││Fe││Cl│  │ │  ← Reagent pads
│  │    │  ││3 ││3 ││  ││  │  │ │
│  │    └──┘└──┘└──┘└──┘└──┘  │ │
│  └────────────────────────────┘ │
│                                 │
│  ◆ ArUco                ◆ ArUco│
│  Marker 3               Marker 4│
│                                 │
└─────────────────────────────────┘
```

### Computer Vision Pipeline

```python
class StripAnalyzer:
    def analyze(self, image):
        # 1. Detect ArUco markers
        markers = self.detect_aruco(image)

        # 2. Perspective transform to canonical view
        warped = self.perspective_transform(image, markers)

        # 3. Color correction using known patches
        corrected = self.color_correct(warped, self.reference_colors)

        # 4. Extract ROIs for each reagent pad
        pads = self.extract_pads(corrected, self.pad_positions)

        # 5. Convert to LAB color space
        lab_values = [self.rgb_to_lab(pad) for pad in pads]

        # 6. Map LAB values to concentrations
        results = {}
        for pad_name, lab in zip(self.pad_names, lab_values):
            results[pad_name] = self.calibration_model.predict(lab)

        return results
```

---

## 6. Cloud Platform: Contamination Intelligence

### Spatial Interpolation

With sparse test points (one per village/well), we estimate contamination across the region using **Ordinary Kriging**:

- Assumes spatial autocorrelation (nearby sources have similar quality)
- Fits a variogram model to observed data
- Produces interpolated heatmap with uncertainty estimates
- Uncertainty drives **where to test next** (active sampling)

### Temporal Forecasting

For sources tested repeatedly over time:
- **Seasonal decomposition** (STL) to separate trend, seasonal, residual
- **LSTM network** trained on: historical readings + rainfall + temperature + upstream data
- Predicts: probability of contamination exceedance in next 7 days
- Generates proactive alerts

### Anomaly Detection

- **Isolation Forest** on multi-parameter water quality vectors
- Detects unusual combinations even if individual parameters are in range
- Example: pH normal + TDS normal + turbidity spike + ammonia spike → likely sewage event
- Alert classification: {natural variation, industrial discharge, agricultural runoff, sewage}

### Municipal Dashboard

```
┌──────────────────────────────────────────────────┐
│  DISTRICT WATER INTELLIGENCE DASHBOARD            │
├──────────────────────────────────────────────────┤
│                                                    │
│  ┌─────────────────────┐  ┌──────────────────┐   │
│  │   CONTAMINATION      │  │  WATER SAFETY    │   │
│  │   HEATMAP            │  │  SCORE           │   │
│  │                      │  │                  │   │
│  │  [Leaflet.js map     │  │  District: 72%   │   │
│  │   with colored       │  │  Block A:  85%   │   │
│  │   regions showing    │  │  Block B:  61%   │   │
│  │   contamination      │  │  Block C:  70%   │   │
│  │   levels]            │  │                  │   │
│  │                      │  │  Trend: ↑ 3%     │   │
│  └─────────────────────┘  └──────────────────┘   │
│                                                    │
│  ┌─────────────────────┐  ┌──────────────────┐   │
│  │  ACTIVE ALERTS       │  │  TOP CONTAMINANTS│   │
│  │                      │  │                  │   │
│  │  ! Ammonia spike     │  │  1. Ammonia 34%  │   │
│  │    Gram Panchayat X  │  │  2. Iron    28%  │   │
│  │    2.3 mg/L (4.6x)  │  │  3. Nitrate 18%  │   │
│  │                      │  │  4. TDS     12%  │   │
│  │  ! Lead detected     │  │  5. Lead     8%  │   │
│  │    Ward 7, Borewell  │  │                  │   │
│  │    45 ppb            │  │                  │   │
│  └─────────────────────┘  └──────────────────┘   │
│                                                    │
│  ┌────────────────────────────────────────────┐   │
│  │  TESTS THIS MONTH                          │   │
│  │  Total: 1,247 | Safe: 891 | Unsafe: 356   │   │
│  │  Active Jal Sakhis: 89 | SHGs: 34         │   │
│  └────────────────────────────────────────────┘   │
│                                                    │
└──────────────────────────────────────────────────┘
```
