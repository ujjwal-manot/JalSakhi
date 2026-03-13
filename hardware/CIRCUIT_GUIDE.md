# JalSakhi DIY Potentiostat - Complete Circuit Build Guide

**Builder**: Ujjwal Manot, Bennett University
**Budget**: INR 1,840 (well within INR 4,000 hard limit)
**Build time**: ~2 hours for a first-time builder
**Difficulty**: Beginner-friendly (no soldering required)

> This guide walks you through building a 3-electrode potentiostat on a
> breadboard using an ESP32 and two LM358 op-amps. Every connection is
> spelled out. If you can push a wire into a breadboard hole, you can
> build this.

---

## Table of Contents

1. [Complete Circuit Schematic (ASCII Art)](#1-complete-circuit-schematic-ascii-art)
2. [Circuit Theory](#2-circuit-theory)
3. [Component List with Exact Values](#3-component-list-with-exact-values)
4. [ESP32 Pin Assignments](#4-esp32-pin-assignments)
5. [Breadboard Layout Guide](#5-breadboard-layout-guide)
6. [Electrode Preparation](#6-electrode-preparation)
7. [DPV Waveform Generation](#7-dpv-waveform-generation)
8. [Current Measurement](#8-current-measurement)
9. [Noise Reduction Tips](#9-noise-reduction-tips)
10. [Calibration Procedure](#10-calibration-procedure)
11. [Safety Notes](#11-safety-notes)
12. [Testing Procedure](#12-testing-procedure)
13. [Production Vision](#13-production-vision)

---

## 1. Complete Circuit Schematic (ASCII Art)

### Full System Block Diagram

```
                         JalSakhi Potentiostat - Full System
    ============================================================================

    ESP32 Dev Board                        Electrochemical Cell
    +--------------+                       (beaker with sample)
    |              |                        +-------------+
    | GPIO25 (DAC) |----> [CONTROL AMP] --> | CE (carbon) |
    |              |      (LM358 #1)        |             |
    | GPIO34 (ADC) |<---- [TIA]        <--- | WE (carbon) |
    |              |      (LM358 #2)        |             |
    | 3.3V         |--+                     | RE (Ag/AgCl)|--+
    | GND          |--+--[power rails]      +-------------+  |
    |              |  |                                       |
    | GPIO2 (LED)  |--+-[status LED]    RE sense line --------+
    +--------------+                         |
         |  BLE                              v
         v                            To LM358 #1 non-inv input
    [Flutter App]                      and LM358 #2 inv input
```

### Detailed Circuit Schematic

```
                        JalSakhi Potentiostat - Detailed Schematic
    ============================================================================

    POWER SUPPLY (from ESP32)
    =========================

    ESP32 3.3V ──────────┬──────────────┬──────────────┬────────── +3.3V rail
                         │              │              │
                      [100uF]        [100nF]        [100nF]
                      C1 elect.      C2 ceramic     C3 ceramic
                         │              │              │
    ESP32 GND ───────────┴──────────────┴──────────────┴────────── GND rail


    VIRTUAL GROUND (1.65V mid-rail reference)
    ==========================================

             +3.3V
               │
             [10k] R1
               │
               ├──────────────────────────────────────────── VREF (1.65V)
               │              │
             [10k] R2       [10uF]
               │            C4 ceramic
               │              │
              GND            GND

    Note: VREF = 3.3V x (R2 / (R1+R2)) = 3.3V x (10k/20k) = 1.65V
    This shifts our voltage range so we can generate both positive
    and negative potentials relative to the electrochemical cell.


    CONTROL AMPLIFIER (LM358 #1, Unit A - pins 1,2,3)
    ===================================================

    Purpose: Drives the Counter Electrode (CE) to maintain the desired
             potential between Working Electrode (WE) and Reference
             Electrode (RE).

                                    +3.3V (pin 8)
                                      │
                              ┌───────┴───────┐
                              │   LM358 #1    │
                              │               │
                              │     8   4     │
                              │   VCC  GND    │
                              │               │
    ESP32 GPIO25 ──[10k]──┬───│ 3+  1         │
    (DAC output)   R3     │   │      OUT──┬───│──────── to CE (Counter Electrode)
                          │   │ 2-        │   │
                        [100nF]│  ▲       │   │
                        C5    │  │        │   │
                          │   │  │      [1k]  │
                         GND  │  │      R4    │
                              │  │        │   │
                              │  └────────┘   │
                              │               │
    VREF (1.65V) ─────────────│ (bias)        │
                              │               │
    RE (Reference Electrode)──│──to pin 2     │
                              │  via R5 [10k] │
                              │               │
                              │     4         │
                              │   GND         │
                              └───────┬───────┘
                                      │
                                     GND

    Detailed pin connections for LM358 #1, Unit A:

        Pin 3 (+): ESP32 GPIO25 through R3 (10k) low-pass filtered
                   with C5 (100nF) to GND
        Pin 2 (-): Connected to RE through R5 (10k)
                   Also receives feedback from pin 1 through R4 (1k)
        Pin 1 (OUT): Connected to CE through R4 (1k) feedback to pin 2


    Actually, let me redraw this more carefully:

                              +3.3V (pin 8)
                                │
                        ┌───────┴───────┐
                        │   LM358 #1    │
                        │   Unit A      │
    DAC (GPIO25)        │               │
        │               │               │
      [10k] R3          │               │
        │               │               │
        ├───[100nF]──GND│               │
        │   C5          │               │
        │               │     ┌─OUT(1)──┼────[1k]────── to CE
        └───────────(+)3│     │         │     R4
                        │     │         │
    RE ──[10k]──┬───(-)2│     │         │
         R5     │       │     │         │
                │       └─────┼─────────┘
                │             │
                └─────────────┘  (feedback: OUT→R4→pin2)
                        │
                       GND (pin 4)


    TRANSIMPEDANCE AMPLIFIER (LM358 #1, Unit B - pins 5,6,7)
    ==========================================================

    Purpose: Converts the tiny current flowing through the Working
             Electrode (WE) into a measurable voltage for the ESP32 ADC.

                        ┌─────────────────────────┐
                        │   LM358 #1, Unit B      │
                        │                         │
                        │        Rf [100k]        │
                        │    ┌────/\/\/────┐      │
                        │    │             │      │
                        │    │  Cf [100pF] │      │
                        │    │  ───||───   │      │
                        │    │             │      │
    WE ────────────(-)6─┤────┘        OUT(7)──┬───┤──── to ESP32 GPIO34 (ADC)
                        │                     │   │
    VREF (1.65V)───(+)5─┤                     │   │
                        │                     │   │
                        └─────────────────────┘   │
                                                  │
                                              [10k] R7
                                                  │
                                                GND
                                        (voltage divider for
                                         ADC protection, optional)

    Pin connections for LM358 #1, Unit B:
        Pin 5 (+): VREF (1.65V)
        Pin 6 (-): Connected directly to WE (Working Electrode)
                   Feedback resistor Rf (100k) from pin 7 to pin 6
                   Feedback capacitor Cf (100pF) in parallel with Rf
        Pin 7 (OUT): Output voltage = VREF - (I_cell x Rf)
                     Connected to ESP32 GPIO34 through R7 (10k)


    COMPLETE CIRCUIT - ACTIVE COMPONENTS ONLY
    ==========================================

                    +3.3V
                      │
              ┌───────┴────────────────────────────┐
              │                LM358 #1             │
              │  (DIP-8 package)                    │
              │                                     │
              │  Pin 8 = VCC (+3.3V)                │
              │  Pin 4 = GND                        │
              │                                     │
              │  UNIT A (Control Amplifier):         │
              │    Pin 1 = Output A ──> to CE        │
              │    Pin 2 = Inv Input A (-)           │
              │    Pin 3 = Non-Inv Input A (+)       │
              │                                     │
              │  UNIT B (Transimpedance Amplifier):  │
              │    Pin 5 = Non-Inv Input B (+)       │
              │    Pin 6 = Inv Input B (-)           │
              │    Pin 7 = Output B ──> to ADC       │
              │                                     │
              └────────────────────────────────────┘


    LM358 DIP-8 PINOUT (top view, notch on left):
    ┌────────────────┐
    │  ●             │
    │ 1  OUT_A    8  │ VCC (+3.3V)
    │ 2  IN_A-   7  │ OUT_B      ──> to ESP32 GPIO34
    │ 3  IN_A+   6  │ IN_B-      <── from WE
    │ 4  GND     5  │ IN_B+      <── VREF (1.65V)
    └────────────────┘


    FULL WIRING SUMMARY
    ====================

    ESP32 GPIO25 (DAC) ──[10k R3]──┬──── LM358 pin 3 (+)
                                   │
                                [100nF C5]
                                   │
                                  GND

    LM358 pin 2 (-) ────┬──────── RE (Reference Electrode) via [10k R5]
                         │
                         └──────── LM358 pin 1 (OUT_A) via [1k R4] (feedback)

    LM358 pin 1 (OUT_A) ────────── CE (Counter Electrode)

    LM358 pin 5 (+) ────────────── VREF (1.65V from R1/R2 divider)

    LM358 pin 6 (-) ────┬──────── WE (Working Electrode)
                         │
                         ├──[100k Rf]── LM358 pin 7 (OUT_B)
                         │
                         └──[100pF Cf]─ LM358 pin 7 (OUT_B)
                              (in parallel with Rf)

    LM358 pin 7 (OUT_B) ────────── ESP32 GPIO34 (ADC input)

    LM358 pin 8 ────────────────── +3.3V
    LM358 pin 4 ────────────────── GND

    +3.3V ──[10k R1]──┬──[10k R2]── GND
                       │
                       └──[10uF C4]── GND
                       │
                       VREF (1.65V)

    ESP32 GPIO2 ──[220R R8]──[LED]── GND    (status indicator)
```

---

## 2. Circuit Theory

### How a 3-Electrode Potentiostat Works

A potentiostat is an electronic instrument that controls the voltage difference between a Working Electrode (WE) and a Reference Electrode (RE) while measuring the current flowing through the electrochemical cell. Here is why each electrode matters and why we need two op-amps.

### The Three Electrodes

```
    Beaker with water sample
    ┌─────────────────────────────┐
    │                             │
    │   CE          RE        WE  │
    │   │           │         │   │
    │   │  Counter  │  Ref    │   │
    │   │  Electrode│  Elect  │   │
    │   │  (carbon) │ (Ag/AgCl│   │
    │   │           │  wire)  │   │
    │   │           │         │   │
    │   └───────────┴─────────┘   │
    │        electrolyte          │
    └─────────────────────────────┘
```

**Working Electrode (WE)** -- This is where the electrochemistry happens. Contaminants in the water undergo oxidation or reduction reactions at the WE surface. The current flowing through WE tells us what contaminants are present and at what concentration.

- Material: Pencil graphite (carbon) rod
- Role: The sensing electrode
- Signal: Current flows through this electrode

**Reference Electrode (RE)** -- Provides a stable, known potential against which we measure the WE potential. The RE has a fixed electrochemical potential, so any voltage change we apply between WE and RE is entirely "seen" by the WE.

- Material: Silver wire coated with AgCl (Ag/AgCl)
- Role: Voltage reference point
- Current: Essentially zero current flows through RE (high impedance input)

**Counter Electrode (CE)** -- Completes the electrical circuit. All current that flows through the WE must return through the CE. The CE is driven by the control amplifier to maintain the correct WE-RE potential.

- Material: Pencil graphite (carbon) rod
- Role: Current return path
- Signal: The op-amp drives this electrode

### Why Not Just Two Electrodes?

In a two-electrode system, current flows through the reference electrode. This changes the RE potential (because of the voltage drop across the electrode-solution interface), ruining the voltage accuracy. The three-electrode design ensures the RE carries no current, maintaining a stable reference.

### The Two Op-Amps Explained

#### Op-Amp 1: Control Amplifier

```
    DAC voltage                          Electrochemical Cell
    (desired potential)                  ┌──────────────┐
         │                               │              │
         v            ┌─────┐            │              │
    ───>(+)──────────>│  A  │──OUT──────>│ CE           │
                      │     │            │              │
    ───>(-)──────────>│     │     RE ────│──> feedback  │
         ^            └─────┘            │              │
         │                               │    WE ──────│─> to TIA
         │            feedback loop      └──────────────┘
         └──────────── RE potential
```

The control amplifier works in a **negative feedback loop**:

1. The ESP32 DAC outputs a voltage on pin 3 (+) representing the desired WE-RE potential.
2. The RE voltage feeds back to pin 2 (-).
3. The op-amp adjusts its output (driving CE) until pin 2 equals pin 3.
4. This means: `V_RE = V_DAC`, so the WE-RE potential is exactly what the DAC commands.
5. If a reaction at WE changes the cell impedance, the op-amp automatically compensates by adjusting the CE drive voltage.

This is the core principle: **the control amplifier maintains the WE-RE potential by adjusting the CE voltage**. The feedback through RE ensures accuracy regardless of solution resistance or reaction kinetics.

#### Op-Amp 2: Transimpedance Amplifier (TIA)

```
                    Rf (100k)
              ┌────/\/\/────┐
              │             │
              │   Cf (100pF)│
              │   ──||──    │
              │             │
    WE ──────>(-)────────>OUT──── V_out to ADC
              │   ┌─────┐
    VREF ────>(+)─│  B  │
                  └─────┘

    V_out = VREF - (I_cell x Rf)
```

The TIA converts the tiny current flowing through WE into a voltage the ESP32 ADC can measure:

1. The WE is connected to the inverting input (-) of the op-amp.
2. The non-inverting input (+) is held at VREF (1.65V).
3. The feedback resistor Rf sets the gain (sensitivity).
4. The output voltage is: `V_out = VREF - (I_cell x Rf)`

For example, with Rf = 100k:
- If I_cell = +10 uA (oxidation): V_out = 1.65V - (10e-6 x 100e3) = 1.65V - 1.0V = 0.65V
- If I_cell = 0 uA (no reaction): V_out = 1.65V
- If I_cell = -10 uA (reduction): V_out = 1.65V + 1.0V = 2.65V

The feedback capacitor Cf (100pF) stabilizes the op-amp and filters high-frequency noise.

### Why We Need Both Op-Amps

| Op-Amp | Role | Analogy |
|--------|------|---------|
| Control Amp (Unit A) | Sets and maintains the electrode potential | Thermostat setting temperature |
| TIA (Unit B) | Measures the resulting current | Thermometer reading the actual temperature |

The control amplifier applies the stimulus (voltage). The TIA measures the response (current). Together, they form a complete potentiostat. The LM358 conveniently packages two op-amps in a single DIP-8 chip, so one LM358 gives us both amplifiers.

### The Voltage Offset Problem

The ESP32 DAC outputs 0V to 3.3V. But electrochemical experiments need both positive and negative potentials relative to the reference electrode (typically -1.2V to +0.6V for DPV scans).

**Solution**: The VREF voltage divider creates a 1.65V "virtual ground." All electrochemical potentials are measured relative to this point:

- DAC = 0V means V_cell = 0V - 1.65V = -1.65V (negative potential)
- DAC = 1.65V means V_cell = 1.65V - 1.65V = 0V
- DAC = 3.3V means V_cell = 3.3V - 1.65V = +1.65V (positive potential)

This maps the ESP32's 0-3.3V range onto a -1.65V to +1.65V electrochemical range, which is more than enough for DPV scans (-1.2V to +0.6V).

---

## 3. Component List with Exact Values

### Complete Bill of Materials

| Ref | Component | Value | Package | Qty | Purpose | E24 Standard? |
|-----|-----------|-------|---------|-----|---------|---------------|
| U1 | LM358N | Dual op-amp | DIP-8 | 1 | Control amp + TIA | - |
| R1 | Resistor | 10k ohm | 1/4W axial | 1 | VREF divider (top) | Yes (E24) |
| R2 | Resistor | 10k ohm | 1/4W axial | 1 | VREF divider (bottom) | Yes (E24) |
| R3 | Resistor | 10k ohm | 1/4W axial | 1 | DAC low-pass filter | Yes (E24) |
| R4 | Resistor | 1k ohm | 1/4W axial | 1 | Control amp feedback | Yes (E24) |
| R5 | Resistor | 10k ohm | 1/4W axial | 1 | RE input protection | Yes (E24) |
| Rf | Resistor | 100k ohm | 1/4W axial | 1 | TIA gain (default) | Yes (E24) |
| R7 | Resistor | 10k ohm | 1/4W axial | 1 | ADC input protection | Yes (E24) |
| R8 | Resistor | 220 ohm | 1/4W axial | 1 | LED current limiter | Yes (E24) |
| C1 | Capacitor | 100 uF, 10V | Electrolytic | 1 | Bulk power decoupling | - |
| C2 | Capacitor | 100 nF (0.1 uF) | Ceramic disc | 1 | HF power decoupling | - |
| C3 | Capacitor | 100 nF (0.1 uF) | Ceramic disc | 1 | HF power decoupling (near LM358) | - |
| C4 | Capacitor | 10 uF, 10V | Ceramic or electrolytic | 1 | VREF stabilization | - |
| C5 | Capacitor | 100 nF (0.1 uF) | Ceramic disc | 1 | DAC low-pass filter | - |
| Cf | Capacitor | 100 pF | Ceramic disc | 1 | TIA stability / HF filter | - |
| D1 | LED | Green, 3mm | Through-hole | 1 | Status indicator | - |
| - | Breadboard | 830 tie-point | Full-size | 1 | Circuit assembly | - |
| - | Jumper wire kit | M-M, M-F | Assorted | 1 | Connections | - |
| - | ESP32 DevKitC | 30-pin | Module | 1 | Controller | - |

**Total unique resistor values needed**: 4 (220R, 1k, 10k, 100k) -- all E24 standard
**Total unique capacitor values needed**: 4 (100pF, 100nF, 10uF, 100uF)

### Alternative TIA Gain Resistors (swap Rf for different current ranges)

| Rf Value | Current Range | Best For |
|----------|--------------|----------|
| 10k ohm | +/- 165 uA | High-concentration samples, CV scans |
| 100k ohm | +/- 16.5 uA | **Default -- use this first** |
| 1M ohm | +/- 1.65 uA | Trace-level detection (ppb metals) |

To calculate: `I_max = VREF / Rf = 1.65V / Rf`

Keep all three resistor values handy. Start with 100k. If the ADC reading is stuck near 0 or 3.3V (saturated), the current is too high -- switch to 10k. If the reading barely moves from 1.65V, the current is too low -- switch to 1M.

### LM358 Op-Amp Specifications (relevant to this circuit)

| Parameter | Value | Impact on Circuit |
|-----------|-------|-------------------|
| Supply voltage | 3V to 32V | Our 3.3V supply is right at the minimum. Works fine. |
| Input offset voltage | +/- 3 mV typical | Adds small offset to measurements. Calibration corrects this. |
| Input bias current | 20-45 nA | Negligible at our current ranges. |
| Gain-bandwidth product | 0.7 MHz | Limits maximum scan rate. Fine for DPV (slow scans). |
| Output swing (low) | ~0V | Can go to ground -- important for single-supply. |
| Output swing (high) | VCC - 1.5V | Maximum output is ~1.8V on 3.3V supply. **This is a limitation.** |
| Slew rate | 0.3 V/us | Adequate for DPV (mV/s scan rates). |

**Important limitation**: On a 3.3V supply, the LM358 output cannot swing above ~1.8V. This limits our effective electrochemical range. For this prototype, it is acceptable because:
- Most DPV scans for common contaminants operate within this range
- The VREF offset helps center the useful range
- The production design uses the AD5940 which has no such limitation

### Power Supply Considerations

The ESP32 3.3V pin can supply up to ~500 mA. Our circuit draws:
- LM358: ~1 mA quiescent
- Resistor divider (R1/R2): 0.165 mA
- LED: ~10 mA
- Total: ~12 mA (well within limits)

**Do not power the LM358 from 5V while connecting its output to ESP32 GPIO34.** The ESP32 ADC pins are rated for 0-3.3V maximum. Even though the LM358 can run on 5V, keep everything on the 3.3V rail for safety.

---

## 4. ESP32 Pin Assignments

### Pin Mapping Table

| ESP32 Pin | GPIO # | Function | Direction | Connected To | Notes |
|-----------|--------|----------|-----------|-------------|-------|
| D25 | GPIO25 | DAC Channel 1 | Output | R3 (10k) to LM358 pin 3 | Voltage sweep output (8-bit DAC) |
| VP | GPIO36 | ADC1_CH0 | Input | LM358 pin 7 (TIA output) | Current measurement (12-bit ADC) |
| D2 | GPIO2 | Digital Output | Output | R8 (220R) to LED | On-board LED / status indicator |
| D4 | GPIO4 | Digital Output | Output | (optional) External LED | Scan-in-progress indicator |
| 3V3 | - | Power | Output | +3.3V power rail | Powers entire analog circuit |
| GND | - | Ground | - | GND rail | Common ground |
| EN | - | Enable | - | - | Keep unconnected (has internal pull-up) |

### Why These Specific Pins?

**GPIO25 (DAC)**: The ESP32 has only two DAC outputs: GPIO25 (DAC1) and GPIO26 (DAC2). We use GPIO25 for the voltage sweep. GPIO26 is kept free as a spare.

**GPIO36 (ADC)**: This is one of the "input-only" pins (GPIO34, 35, 36, 39) which have no internal pull-up/pull-down resistors. This is ideal for analog measurement because there is no leakage current from pull resistors that would distort our reading. GPIO36 is ADC1_CH0 -- ADC1 is recommended because ADC2 cannot be used when WiFi is active (and we use BLE, which shares the radio).

**GPIO2 (LED)**: Connected to the on-board LED on most ESP32 dev boards. Useful for visual feedback during scans.

### Pins to Avoid

| Pin | Why Avoid |
|-----|-----------|
| GPIO0 | Boot mode selection. Pulling low enters flash mode. |
| GPIO1 (TX0) | UART TX -- used for serial monitor/debugging. |
| GPIO3 (RX0) | UART RX -- used for serial monitor/debugging. |
| GPIO6-11 | Connected to internal SPI flash. Never use these. |
| GPIO12 | Bootstrap pin (MTDI). Pulling high at boot can prevent startup. |
| GPIO15 | Outputs PWM at boot. Can interfere with analog signals. |
| ADC2 channels (GPIO0,2,4,12-15,25-27) | Cannot be used with WiFi/BLE active. |

### BLE Antenna Considerations

The ESP32 has an on-chip PCB antenna (on most dev boards). For reliable BLE communication with the Flutter app:

- Keep the antenna end of the ESP32 board at the edge of the breadboard, not buried in the middle.
- Do not place wires or metal objects directly over the antenna area (the end of the PCB opposite the USB connector).
- BLE range is typically 5-10 meters indoors, which is plenty for holding the phone near the device.
- The ESP32's BLE and ADC1 work simultaneously without issues.

### ESP32 Pin Diagram (30-pin DevKitC)

```
                    USB
                ┌────┴────┐
        3V3  ───┤ 1    30 ├─── GND
         EN  ───┤ 2    29 ├─── GPIO23
     GPIO36  ───┤ 3    28 ├─── GPIO22        GPIO36 = ADC input
     GPIO39  ───┤ 4    27 ├─── GPIO1  (TX)     (to TIA output)
     GPIO34  ───┤ 5    26 ├─── GPIO3  (RX)
     GPIO35  ───┤ 6    25 ├─── GPIO21
     GPIO32  ───┤ 7    24 ├─── GND
     GPIO33  ───┤ 8    23 ├─── GPIO19
     GPIO25  ───┤ 9    22 ├─── GPIO18        GPIO25 = DAC output
     GPIO26  ───┤10    21 ├─── GPIO5           (to control amp)
     GPIO27  ───┤11    20 ├─── GPIO17
     GPIO14  ───┤12    19 ├─── GPIO16
     GPIO12  ───┤13    18 ├─── GPIO4
         GND ───┤14    17 ├─── GPIO0
     GPIO13  ───┤15    16 ├─── GPIO2         GPIO2 = status LED
                └─────────┘
```

---

## 5. Breadboard Layout Guide

### Breadboard Orientation

Use a standard 830 tie-point breadboard (the full-size one, approximately 165mm x 55mm). Orient it with the long side horizontal, column numbers (1-63) going left to right, and row letters (a-e on top, f-j on bottom) visible.

```
    Power rails (top):     (+) ──────────────────────── (-)
    Rows a-e:              a  b  c  d  e
                           1  2  3  4  5 ... 60 61 62 63
    Center gap:            ─────────────────────────────────
    Rows f-j:              f  g  h  i  j
                           1  2  3  4  5 ... 60 61 62 63
    Power rails (bottom):  (+) ──────────────────────── (-)
```

### Wire Color Code

Use consistent colors to make debugging easier:

| Color | Purpose |
|-------|---------|
| **Red** | +3.3V power |
| **Black** | Ground (GND) |
| **Yellow** | Signal: DAC output (GPIO25 to control amp) |
| **Blue** | Signal: ADC input (TIA output to GPIO36) |
| **Green** | Signal: VREF (1.65V reference) |
| **White** | Electrode connections (WE, RE, CE) |
| **Orange** | Feedback connections (within op-amp circuits) |

### Step-by-Step Build Instructions

#### Step 0: Set Up Power Rails

1. Connect the top (+) rail to the bottom (+) rail with a red jumper (bridges both halves).
2. Connect the top (-) rail to the bottom (-) rail with a black jumper.
3. These are your +3.3V and GND rails respectively.
4. **Do not connect power yet.** We will power up only after all wiring is complete.

#### Step 1: Place the ESP32

1. Place the ESP32 dev board straddling the center gap of the breadboard.
2. Position it so pin 1 (3V3) is in column 1, and the USB connector hangs off the left edge.
3. The ESP32 pins go into rows `e` (top half) and `f` (bottom half).

```
    Columns:  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15
    Row e:   3V3  EN G36 G39 G34 G35 G32 G33 G25 G26 G27 G14 G12 GND G13
    Row f:   GND G23 G22  TX  RX G21 GND G19 G18  G5 G17 G16  G4  G0  G2
```

4. Connect ESP32 3V3 (column 1, row e) to the top (+) rail with a **red** wire.
5. Connect ESP32 GND (column 14, row e) to the top (-) rail with a **black** wire.
6. Also connect ESP32 GND (column 1, row f) to the bottom (-) rail with a **black** wire.

#### Step 2: Place the LM358

1. Place the LM358 DIP-8 straddling the center gap, starting at column 30.
2. Pin 1 goes in row e, column 30. Pin 8 goes in row f, column 30.
3. Verify orientation: the notch or dot on the LM358 should face LEFT (toward the ESP32).

```
    LM358 placement (columns 30-33):

    Row e:  pin1(OUT_A)  pin2(IN_A-)  pin3(IN_A+)  pin4(GND)
            col 30       col 31       col 32       col 33

    Row f:  pin8(VCC)    pin7(OUT_B)  pin6(IN_B-)  pin5(IN_B+)
            col 30       col 31       col 32       col 33
```

4. Connect LM358 pin 8 (VCC, row f, col 30) to (+) rail with a **red** wire.
5. Connect LM358 pin 4 (GND, row e, col 33) to (-) rail with a **black** wire.

#### Step 3: Build the VREF Voltage Divider (1.65V)

1. Insert R1 (10k) from the (+) rail to row a, column 40.
2. Insert R2 (10k) from row a, column 40 to the (-) rail.
3. Insert C4 (10 uF) from row a, column 40 to the (-) rail.
   - If electrolytic: long leg (+) in row a col 40, short leg (-) to GND rail.
4. The junction at row a, column 40 is now your VREF point (1.65V).
5. Run a **green** jumper from row a, col 40 to wherever VREF is needed.

```
    (+) rail ──── R1(10k) ──┬── R2(10k) ──── (-) rail
                            │
                            ├── C4 (10uF) ── (-) rail
                            │
                            VREF = 1.65V  (col 40, row a)
```

#### Step 4: Wire the DAC Low-Pass Filter

1. Insert R3 (10k) from row b, column 9 (same column as ESP32 GPIO25) to row b, column 25.
2. Insert C5 (100nF) from row b, column 25 to the (-) rail.
3. Run a **yellow** jumper from row b, col 25 to LM358 pin 3 (row d, col 32).

```
    ESP32 GPIO25 (col 9) ──[R3 10k]──┬── LM358 pin 3 (col 32)
                                      │      (yellow wire)
                                   [C5 100nF]
                                      │
                                     GND
```

This R-C filter smooths the DAC output (removes staircase steps from the 8-bit DAC).
Cutoff frequency: f = 1/(2 x pi x R3 x C5) = 1/(2 x 3.14 x 10000 x 0.0000001) = 159 Hz.
This is well above our DPV scan rate but removes DAC switching noise.

#### Step 5: Wire the Control Amplifier Feedback

1. Insert R4 (1k) from row d, column 30 (LM358 pin 1, OUT_A) to row c, column 31.
2. Run an **orange** jumper from row c, col 31 to row d, col 31 (connects to LM358 pin 2).
3. This creates the feedback path: Output A -> R4 -> Inv Input A.

```
    LM358 pin 1 (OUT_A) ──[R4 1k]──── LM358 pin 2 (IN_A-)
```

#### Step 6: Wire the Reference Electrode Input

1. Insert R5 (10k) from row c, column 31 (same node as R4 feedback) to row c, column 45.
2. Column 45 is your RE connection point. Attach a **white** jumper wire here that will connect to the reference electrode (Ag/AgCl).

```
    RE (col 45) ──[R5 10k]──── LM358 pin 2 (IN_A-)
                                     │
                               R4 feedback also here
```

#### Step 7: Wire the Counter Electrode Output

1. Run a **white** jumper from row d, column 30 (LM358 pin 1, OUT_A) to row c, column 50.
2. Column 50 is your CE connection point. Attach an alligator clip lead here to connect to the counter electrode (pencil graphite).

```
    LM358 pin 1 (OUT_A) ──────── CE (col 50)
```

#### Step 8: Wire the Transimpedance Amplifier (TIA)

1. Connect VREF to LM358 pin 5: Run a **green** jumper from row a, col 40 (VREF) to row g, col 33 (LM358 pin 5, IN_B+).
2. Insert Rf (100k) from row g, col 32 (LM358 pin 6, IN_B-) to row g, col 31 (LM358 pin 7, OUT_B).
3. Insert Cf (100pF) in parallel with Rf: from row h, col 32 to row h, col 31 (same nodes as Rf).
4. Run a **white** jumper from row g, col 32 (LM358 pin 6, IN_B-) to row c, column 55. Column 55 is your WE connection point.

```
    WE (col 55) ──── LM358 pin 6 (IN_B-)
                          │
                    ┌─[Rf 100k]──┐
                    │             │
                    ├─[Cf 100pF]─┤
                    │             │
                    └─────────── LM358 pin 7 (OUT_B)
```

#### Step 9: Wire the ADC Connection

1. Run a **blue** jumper from row g, col 31 (LM358 pin 7, OUT_B) to row a, col 3 (same column as ESP32 GPIO36).
2. Optionally, insert R7 (10k) in series as ADC protection: from row g, col 31 to row b, col 20, then a jumper from row b, col 20 to row a, col 3.

```
    LM358 pin 7 (OUT_B) ──[R7 10k (optional)]──── ESP32 GPIO36 (ADC)
```

#### Step 10: Add Power Decoupling Capacitors

1. Insert C1 (100 uF electrolytic) from the (+) rail to the (-) rail, near the ESP32 end.
   - Long leg (+) to (+) rail, short leg (-) to (-) rail.
2. Insert C2 (100 nF ceramic) from the (+) rail to the (-) rail, near the ESP32.
3. Insert C3 (100 nF ceramic) from the (+) rail to the (-) rail, near the LM358 (within 1-2 columns of LM358 pin 8).

#### Step 11: Add the Status LED

1. Insert R8 (220 ohm) from row a, col 15 (same column as ESP32 GPIO2) to row a, col 48.
2. Insert the LED: long leg (anode) in row b, col 48; short leg (cathode) to (-) rail.

```
    ESP32 GPIO2 ──[R8 220R]──[LED]──── GND
```

#### Step 12: Final Check Before Power-Up

Go through this checklist BEFORE connecting USB power:

- [ ] LM358 pin 8 connected to +3.3V? (red wire)
- [ ] LM358 pin 4 connected to GND? (black wire)
- [ ] No pins are shorted (visually inspect for bent pins)
- [ ] R1/R2 divider is between +3.3V and GND (not reversed)
- [ ] C1 electrolytic polarity is correct (+ to +3.3V, - to GND)
- [ ] C4 electrolytic polarity is correct (if electrolytic)
- [ ] ESP32 3V3 to (+) rail, GND to (-) rail
- [ ] DAC (GPIO25) goes to LM358 pin 3
- [ ] ADC (GPIO36) comes from LM358 pin 7
- [ ] Feedback resistor R4 goes from pin 1 to pin 2 (same chip)
- [ ] TIA Rf goes from pin 7 to pin 6 (same chip)
- [ ] RE, WE, CE connection points are NOT shorted together

### Common Mistakes to Avoid

| Mistake | Symptom | Fix |
|---------|---------|-----|
| LM358 inserted backwards | Circuit does not work at all. Chip may get warm. | Notch/dot faces LEFT. Pin 1 is top-left. |
| Electrolytic cap reversed | Cap may bulge, leak, or pop (unlikely at 3.3V but bad practice) | Long leg = +, short leg = - |
| Breadboard rows confused | Signals do not reach correct pins | Remember: each row (a-e or f-j) at a given column is one node. Top and bottom halves are separate. |
| Using GPIO34 instead of GPIO36 | Works but GPIO34 may have different noise characteristics | Either works. GPIO36 (VP) is slightly preferred for noise. |
| Forgetting the center gap | ESP32 shorts its own pins | The chip must straddle the gap. Each side goes into a separate half. |
| Too-long wires to electrodes | Excessive noise pickup | Keep electrode leads under 15cm. Twist them together if possible. |
| VREF node floating | Random voltage, unstable readings | Ensure R1 and R2 are both connected and C4 is in place. |
| Power rail break | Half the breadboard has no power | Many breadboards split the power rail in the middle. Bridge with a wire. |

---

## 6. Electrode Preparation

### 6.1 Working Electrode (WE) -- Pencil Graphite

**Material**: Mechanical pencil graphite lead, 0.5mm or 0.7mm diameter

**Pencil Grade Selection**:

| Grade | Carbon Content | Conductivity | Best For |
|-------|---------------|--------------|----------|
| HB | Medium | Medium | General purpose -- **use this** |
| 2B | Higher | Higher | Slightly better sensitivity |
| 4B | Highest | Highest | Soft, breaks easily -- avoid |

**Recommendation**: Use **HB or 2B** leads. They are the best balance of conductivity, availability, and mechanical strength.

**Preparation Steps**:

1. Take a mechanical pencil lead (0.5mm or 0.7mm, HB or 2B grade).
2. Cut it to approximately 3 cm length using wire cutters or sharp scissors.
3. Using fine sandpaper (400-grit or higher), gently polish one end of the lead to create a flat, clean surface. This is the sensing tip.
4. Wrap the other end with thin copper wire (from jumper wires -- strip the insulation). Wrap tightly for at least 5mm to ensure good electrical contact.
5. Alternatively, use a small alligator clip on the non-sensing end.
6. Apply a small amount of clear nail polish or epoxy around the wire-graphite junction to seal it, leaving only the polished tip exposed. Let it dry for 10 minutes.
7. The exposed sensing area should be approximately **3-5mm** of the graphite tip.

```
    ┌─── copper wire (to breadboard)
    │
    ├═══════╗
    │ wire  ║  nail polish seal
    │ wrap  ║
    ├═══════╝
    │
    ├─── exposed graphite (3-5mm) ← sensing surface
    │
    └─── polished flat tip
```

**Pre-treatment (improves sensitivity)**:
1. Dip the WE tip in a beaker of 0.1M KCl solution (dissolve 0.75g KCl in 100mL water -- pharmacy-grade table salt substitute works).
2. Apply +1.5V for 30 seconds, then -1.5V for 30 seconds using the potentiostat circuit.
3. This electrochemically activates the carbon surface, creating more reaction sites.
4. Rinse with distilled water and pat dry.

**Published reference**: Tavares & Barbeira (2008), "Influence of pencil graphite hardness on voltammetric response," *Electrochimica Acta* 53(27), pp. 8004-8010. Confirmed that HB and 2B pencil leads provide usable carbon electrode surfaces for voltammetric detection.

### 6.2 Counter Electrode (CE) -- Pencil Graphite

Prepare identically to the WE (steps 1-6 above). The CE does not need to be as carefully prepared because it does not sense anything -- it just provides a current return path.

- Use the same pencil grade (HB or 2B) for consistency.
- A slightly larger exposed area (5-8mm) is acceptable and beneficial (more surface area for current flow).
- No pre-treatment needed for the CE.

### 6.3 Reference Electrode (RE) -- Silver/Silver Chloride (Ag/AgCl)

A proper Ag/AgCl reference electrode provides a stable +0.222V potential (vs. Standard Hydrogen Electrode). This is the most important electrode for measurement accuracy.

**Materials**:
- Silver wire, 0.5mm diameter, ~3 cm length (available from jewellery supply stores or Amazon India, ~INR 200 for 5cm)
- Household bleach (sodium hypochlorite, NaOCl, ~4-6% concentration) -- any brand works (e.g., Domex, Robin Bleach)
- Small glass or plastic container
- Distilled water (available at medical shops for INR 20/L)

**Preparation Steps**:

1. **Clean the silver wire**: Polish the wire with fine sandpaper (400-grit) until it is bright and shiny. Wipe with a clean tissue.

2. **Prepare the bleach bath**: Pour ~50 mL of household bleach into a small glass container. Use full-strength bleach, do not dilute it.

3. **Coat with AgCl**: Immerse approximately 1.5-2 cm of the silver wire into the bleach solution. The chemical reaction is:
   ```
   2 Ag + NaOCl + H2O → 2 AgCl + NaOH
   ```
   The silver reacts with the hypochlorite to form a grey-purple AgCl coating.

4. **Duration**: Leave the wire in the bleach for **30-45 minutes**. Do not exceed 60 minutes (the coating becomes too thick and flaky).

5. **Verification**: After removing from bleach, the coated portion should appear:
   - **Grey to dark purple** in color (good)
   - NOT white and powdery (too long in bleach -- start over)
   - NOT still shiny silver (too short in bleach -- re-immerse)

6. **Rinse**: Gently rinse the coated wire with distilled water. Do not rub the coating.

7. **Conditioning**: Soak the coated wire in 0.1M KCl solution for at least 1 hour (overnight is better). This stabilizes the electrode potential.

8. **Connect**: Wrap copper wire around the uncoated end of the silver wire (the end that was NOT in bleach). Use an alligator clip or solder if possible.

```
    ┌─── copper wire (to breadboard)
    │
    ├─── uncoated silver wire (shiny)
    │
    ├━━━━━━━━━━━━━━━━━━━━━━━ junction
    │
    ├─── AgCl-coated region (grey-purple)
    │    (1.5-2 cm)
    │
    └─── tip submerged in sample
```

**Storage**: When not in use, store the Ag/AgCl electrode in 0.1M KCl solution (never let it dry out). It will remain usable for weeks. If the AgCl coating degrades (turns white or flakes off), re-coat with bleach.

**Published references**:
- Matsumoto et al. (2002), "A micro-planar reference electrode," *Sensors and Actuators B: Chemical* 83(1-3), pp. 174-178.
- An & Bhatt (2011), "A simple Ag/AgCl reference electrode," *Journal of Chemical Education* 88(6), pp. 837-838.
- Shinwari et al. (2010), "Microfabricated reference electrodes and their biosensing applications," *Sensors* 10(3), pp. 1679-1715.

### 6.4 Electrode Cell Setup

```
    Beaker (100mL or 250mL glass beaker)
    ┌─────────────────────────────────┐
    │                                 │
    │    CE        RE          WE     │
    │    │         │           │      │
    │    │  pencil │  Ag/AgCl  │  pencil
    │    │  graphite│  wire    │  graphite
    │    │         │           │      │
    │    │    ┌────┴────┐      │      │
    │    │    │ KCl salt│      │      │
    │    │    │ bridge  │      │      │
    │    │    │(optional│      │      │
    │    │    └─────────┘      │      │
    │    │                     │      │
    │    └─────────────────────┘      │
    │         water sample            │
    │         (50-100 mL)             │
    └─────────────────────────────────┘

    Spacing: keep electrodes 1-2 cm apart.
    Immersion depth: 1-2 cm of each electrode below water surface.
    Do NOT let electrodes touch each other.
```

**Simple setup**: Use a small binder clip or tape on the edge of the beaker to hold each electrode wire in position. Space them 1-2 cm apart. All three must be submerged in the same solution.

**Optional salt bridge**: For higher accuracy, dissolve 0.1M KCl (0.75g per 100mL) in the sample. This provides adequate ionic conductivity. For very dilute samples (like distilled water), this step is important -- pure water has very low conductivity and the potentiostat will struggle.

---

## 7. DPV Waveform Generation

### What is Differential Pulse Voltammetry (DPV)?

DPV is an electrochemical technique that applies a series of voltage pulses superimposed on a staircase ramp. It is highly sensitive to contaminant detection because it subtracts the background (capacitive) current, leaving only the faradaic current from electrochemical reactions.

```
    DPV Waveform:
    Voltage
    (applied
     to cell)
       │
       │              ┌──┐          ┌──┐          ┌──┐
       │              │  │          │  │          │  │
       │         ┌────┘  └────┐    │  └────┐    │  └────┐
       │         │             │   │        │   │        │
       │    ┌────┘             └───┘        └───┘        └───
       │    │
       │────┘
       │
       └───────────────────────────────────────────────── Time

    Parameters:
    - Step height (delta_E_s): 4 mV (voltage increment per step)
    - Pulse amplitude (delta_E_p): 50 mV (height of each pulse)
    - Pulse width (t_p): 50 ms (duration of each pulse)
    - Step period (T): 200 ms (time between steps)

    Measurement:
    - Sample current at end of pulse (i_1)
    - Sample current just before pulse (i_2)
    - Differential current: delta_i = i_1 - i_2
    - This subtraction removes capacitive background current
```

### ESP32 DAC Characteristics

| Parameter | Value | Notes |
|-----------|-------|-------|
| Resolution | 8-bit (256 steps) | Values 0-255 |
| Output voltage range | 0V to 3.3V | Linear within this range |
| Voltage per step | 3.3V / 255 = 12.94 mV | ~13 mV per DAC step |
| Update rate | Up to ~1 MHz | Far faster than we need |
| Output impedance | ~100 ohm | R3 (10k) isolates this |

### Mapping Electrochemical Voltage Range onto DAC Range

We need to scan from approximately -0.8V to +0.4V (vs. Ag/AgCl) for common contaminants. With our VREF at 1.65V, we translate:

```
    Electrochemical voltage (V_cell) = V_DAC - VREF
    V_cell = V_DAC - 1.65V

    So:
    V_cell = -0.8V  =>  V_DAC = -0.8 + 1.65 = 0.85V  =>  DAC value = 0.85/3.3 * 255 = 66
    V_cell = 0.0V   =>  V_DAC = 0.0 + 1.65  = 1.65V  =>  DAC value = 1.65/3.3 * 255 = 127
    V_cell = +0.4V  =>  V_DAC = 0.4 + 1.65  = 2.05V  =>  DAC value = 2.05/3.3 * 255 = 158

    Usable DAC range: 66 to 158 (93 steps)
    Voltage resolution: 1.2V / 93 steps = ~13 mV per step
```

Note: The LM358 output swing limitation (~1.8V max on 3.3V supply) means the control amplifier may clip above ~+0.15V vs. Ag/AgCl. This is acceptable for most DPV scans (the interesting peaks for ammonia, lead, arsenic, etc. occur at negative potentials).

### DPV Waveform Generation Code-Hardware Interface

```
    ESP32 Arduino Pseudocode:

    #define DAC_PIN       25    // GPIO25 = DAC Channel 1
    #define ADC_PIN       36    // GPIO36 = ADC input
    #define VREF_COUNTS   127   // DAC value for 0V cell potential
    #define MV_PER_COUNT  12.94 // millivolts per DAC step

    // DPV parameters
    #define STEP_MV       4     // step height in mV
    #define PULSE_MV      50    // pulse amplitude in mV
    #define PULSE_MS      50    // pulse duration in ms
    #define STEP_PERIOD   200   // total step period in ms
    #define START_MV     -800   // start potential in mV vs Ag/AgCl
    #define END_MV        400   // end potential in mV vs Ag/AgCl

    // Convert millivolts (vs Ag/AgCl) to DAC counts
    int mvToDac(float mv) {
        float dac_voltage = (mv / 1000.0) + 1.65;  // add VREF offset
        int dac_value = (int)(dac_voltage / 3.3 * 255.0);
        return constrain(dac_value, 0, 255);
    }

    // DPV scan
    void dpvScan() {
        for (float E = START_MV; E <= END_MV; E += STEP_MV) {
            // Step to base potential
            dacWrite(DAC_PIN, mvToDac(E));
            delay(STEP_PERIOD - PULSE_MS);

            // Measure current before pulse (i_2)
            int adc_before = analogRead(ADC_PIN);

            // Apply pulse
            dacWrite(DAC_PIN, mvToDac(E + PULSE_MV));
            delay(PULSE_MS);

            // Measure current at end of pulse (i_1)
            int adc_after = analogRead(ADC_PIN);

            // Differential current
            int delta_i = adc_after - adc_before;

            // Send data over BLE
            sendDataPoint(E, delta_i);

            // Return to base potential (next step starts here)
        }
    }
```

### Timing Diagram

```
    Time (ms): 0    150   200   350   400   550   600
               │     │     │     │     │     │     │
    DAC:   ────┤     ├─────┤     ├─────┤     ├─────
               │     │ ┌───┤     │ ┌───┤     │ ┌───
               │     │ │   │     │ │   │     │ │
               └─────┘ │   └─────┘ │   └─────┘ │
                       │           │           │
    Step 1:   E_base   E+50mV     E+4mV  E+54mV    ...
                       │           │
    Measure:      i_2──┘      i_1──┘
                  (before      (end of
                   pulse)       pulse)

    delta_i = i_1 - i_2  (the DPV differential current)
```

---

## 8. Current Measurement

### TIA Output Voltage

The transimpedance amplifier converts cell current to voltage:

```
    V_out = VREF - (I_cell x Rf)
    V_out = 1.65V - (I_cell x Rf)
```

| Rf (gain resistor) | I_cell = +1 uA | I_cell = +10 uA | I_cell = -10 uA | I_max measurable |
|---------------------|----------------|-----------------|-----------------|------------------|
| 10k | 1.64V | 1.55V | 1.75V | +/- 165 uA |
| 100k | 1.55V | 0.65V | 2.65V | +/- 16.5 uA |
| 1M | 0.65V | Saturated! | Saturated! | +/- 1.65 uA |

**Start with Rf = 100k.** This provides good sensitivity for typical water sample currents (0.1 to 10 uA).

### ESP32 ADC Characteristics

| Parameter | Value | Notes |
|-----------|-------|-------|
| Resolution | 12-bit (4096 steps) | Values 0-4095 |
| Input range (default) | 0V to 1.1V | Very limited! Must change attenuation. |
| Input range (11dB atten.) | 0V to 3.3V | **Use this setting** |
| Voltage per step (11dB) | 3.3V / 4095 = 0.806 mV | ~0.8 mV resolution |
| Sampling rate | Up to 200 kSPS | We sample at ~10 Hz, plenty fast |
| Non-linearity | Significant at edges | See calibration section below |

**ADC Configuration (Arduino)**:
```cpp
// Set 11dB attenuation for 0-3.3V range
analogSetAttenuation(ADC_11db);

// Set 12-bit resolution
analogSetWidth(12);

// Read ADC
int raw = analogRead(36);  // GPIO36
float voltage = raw * 3.3 / 4095.0;
```

### Converting ADC Reading to Current

```
    V_out = raw_adc * 3.3 / 4095.0       // ADC voltage
    I_cell = (VREF - V_out) / Rf          // Cell current in amps
    I_uA = I_cell * 1e6                   // Convert to microamps

    Example (Rf = 100k):
    ADC reads 2048 counts → V_out = 1.65V → I_cell = 0 uA (no current)
    ADC reads 1024 counts → V_out = 0.825V → I_cell = (1.65-0.825)/100000 = 8.25 uA
    ADC reads 3072 counts → V_out = 2.475V → I_cell = (1.65-2.475)/100000 = -8.25 uA
```

### ESP32 ADC Non-Linearity

The ESP32 ADC has a known non-linearity issue: readings near 0V and 3.3V are compressed. The middle range (0.5V to 2.5V) is reasonably linear.

```
    Ideal (linear):     ──────────────────────────
                       /
    Actual ESP32:     ╱
                     /   mostly linear region
                    ╱    (0.5V to 2.5V)
                   /
                  ╱     ← compressed at edges

    Voltage:  0V   0.5V         2.5V         3.3V
```

**Mitigations**:
1. Our VREF (1.65V) centers the TIA output in the linear ADC range.
2. Normal cell currents produce outputs between 0.5V and 2.8V -- within the good range.
3. Software calibration (polynomial correction) can further improve accuracy.
4. For competition purposes, relative measurements (peak heights) matter more than absolute accuracy.

### Expected Current Ranges for Water Samples

| Sample Type | Expected Current | Recommended Rf |
|-------------|-----------------|----------------|
| Distilled water (blank) | < 0.1 uA | 1M or 100k |
| Tap water | 0.1 - 1 uA | 100k |
| Ammonia spiked (1 mg/L) | 1 - 5 uA | 100k |
| Ammonia spiked (10 mg/L) | 5 - 20 uA | 100k or 10k |
| Lead spiked (50 ppb) | 0.5 - 2 uA | 100k |
| High-TDS groundwater | 5 - 50 uA | 10k |

---

## 9. Noise Reduction Tips

Electrochemical measurements deal with tiny currents (nanoamps to microamps). Noise is the primary enemy.

### 9.1 Hardware Noise Reduction

**Decoupling capacitors on power rails**:
- Already included: C1 (100uF bulk), C2 (100nF near ESP32), C3 (100nF near LM358).
- Place C3 as close to LM358 pins 4 and 8 as physically possible.
- Ceramic caps (C2, C3) filter high-frequency noise. Electrolytic (C1) provides bulk charge storage.

**Short wires to electrodes**:
- Keep the wires from the breadboard to the electrodes under 15 cm.
- Twist the three electrode wires together to reduce electromagnetic pickup.
- If using alligator clip leads, use the shortest ones you have.

**Faraday cage (optional but highly effective)**:
- Wrap a cardboard box (slightly larger than the beaker) with aluminum foil.
- Connect the foil to the GND rail with an alligator clip.
- Place the beaker with electrodes inside the foil box during measurements.
- This blocks 50 Hz mains interference and RF noise from phones/laptops.
- At a competition demo, even a simple foil-wrapped box dramatically reduces noise.

```
    ┌─────────────────────┐
    │  Aluminum foil box  │
    │  ┌───────────────┐  │
    │  │    Beaker      │  │
    │  │  CE  RE  WE    │  │
    │  │  │   │   │     │  │
    │  │  └───┴───┘     │  │
    │  └───────────────┘  │
    │       GND wire ──────┼──── to GND rail
    └─────────────────────┘
```

**Avoid noise sources**:
- Keep your phone at least 30 cm from the electrodes during measurement (phone RF creates interference).
- Keep the laptop charger/power supply away from the measurement area (50 Hz / switching noise).
- If possible, run the ESP32 from USB battery bank instead of laptop USB (eliminates ground loop through laptop charger).

### 9.2 Software Noise Reduction

**Averaging multiple ADC readings**:
```cpp
// Take 16 readings and average
int readADC_averaged(int pin, int samples) {
    long sum = 0;
    for (int i = 0; i < samples; i++) {
        sum += analogRead(pin);
        delayMicroseconds(100);  // small delay between samples
    }
    return sum / samples;
}

// Use 16-sample averaging (reduces noise by 4x = sqrt(16))
int adc_value = readADC_averaged(36, 16);
```

**Moving average filter**:
```cpp
// Circular buffer for moving average
#define WINDOW_SIZE 5
int buffer[WINDOW_SIZE];
int buf_index = 0;

int movingAverage(int new_value) {
    buffer[buf_index] = new_value;
    buf_index = (buf_index + 1) % WINDOW_SIZE;
    long sum = 0;
    for (int i = 0; i < WINDOW_SIZE; i++) {
        sum += buffer[i];
    }
    return sum / WINDOW_SIZE;
}
```

**Savitzky-Golay smoothing** (applied to the complete voltammogram after scan):
- This is a polynomial smoothing filter that preserves peak shape while removing noise.
- Apply on the Flutter app side after receiving the complete scan data.
- Use a 2nd order polynomial with a window of 7-15 points.
- See the JalSakhi signal processing module at `app/lib/signal/` for implementation.

### 9.3 Noise Budget

| Source | Magnitude | Mitigation |
|--------|-----------|------------|
| ESP32 ADC quantization | ~0.8 mV (12-bit) | Averaging improves effective resolution |
| LM358 input offset | +/- 3 mV | Calibration corrects this |
| 50 Hz mains pickup | 1-10 mV | Faraday cage, short wires |
| ESP32 switching noise | 5-20 mV on power rail | Decoupling caps C1/C2/C3 |
| Thermal noise (resistors) | ~0.1 mV (negligible) | N/A |
| RF interference (phone/WiFi) | Variable | Distance, Faraday cage |

---

## 10. Calibration Procedure

### Why Calibrate?

Every component in the signal chain adds small offsets and gain errors:
- ESP32 DAC output may not be exactly linear
- LM358 has input offset voltage (+/- 3 mV)
- ESP32 ADC has non-linearity
- Electrode surface area and condition vary

Calibration establishes a mapping between ADC readings and actual contaminant concentrations.

### Step 1: Zero Calibration (Blank)

1. Prepare a "blank" solution: distilled water with 0.1M KCl supporting electrolyte (0.75g KCl in 100mL distilled water).
2. Insert all three electrodes into the blank solution.
3. Run a complete DPV scan.
4. Record the voltammogram -- this is your **baseline**.
5. All subsequent measurements will have this baseline subtracted.

### Step 2: Standard Solutions

For ammonia detection (the primary demo contaminant):

1. Prepare stock solution: Dissolve the ammonia solution (from pharmacy) in distilled water to make a known concentration. For example, dilute to create:
   - Standard A: 0.5 mg/L NH3 (0.5 ppm)
   - Standard B: 1.0 mg/L NH3 (1 ppm)
   - Standard C: 5.0 mg/L NH3 (5 ppm)
   - Standard D: 10.0 mg/L NH3 (10 ppm)
   - Standard E: 25.0 mg/L NH3 (25 ppm)

2. For each standard:
   a. Rinse electrodes with distilled water
   b. Insert into the standard solution
   c. Run a DPV scan
   d. Record the peak current (Ip) at the ammonia oxidation potential

### Step 3: Build Calibration Curve

Plot peak current (Ip) vs. concentration:

```
    Ip (uA)
       │
    12 │                                    * E (25 ppm)
       │
    10 │                              *
       │                        D (10 ppm)
     8 │
       │
     6 │                  *
       │            C (5 ppm)
     4 │
       │
     2 │        *
       │  B (1 ppm)
     1 │  *
       │A(0.5)
     0 ├──┬──┬──┬──┬──┬──┬──┬──┬──┬──
       0  2  4  6  8 10 12 14 16 18 20 22 24 26
                      Concentration (mg/L)

    Fit: Ip = m * C + b  (linear regression)
    where: m = slope (sensitivity, uA per mg/L)
           b = intercept (ideally 0, offset from blank)
```

### Step 4: Store Calibration in ESP32 Flash

```cpp
#include <Preferences.h>
Preferences prefs;

// Store calibration
void storeCalibration(float slope, float intercept) {
    prefs.begin("cal", false);
    prefs.putFloat("slope", slope);
    prefs.putFloat("intercept", intercept);
    prefs.putULong("timestamp", millis());
    prefs.end();
}

// Read calibration
float getConcentration(float peak_current_uA) {
    prefs.begin("cal", true);
    float slope = prefs.getFloat("slope", 1.0);
    float intercept = prefs.getFloat("intercept", 0.0);
    prefs.end();
    return (peak_current_uA - intercept) / slope;
}
```

### When to Recalibrate

| Trigger | Action |
|---------|--------|
| New electrodes prepared | Full calibration (blank + standards) |
| Every 10 tests | Quick blank check (verify baseline) |
| After changing Rf (gain resistor) | Full calibration |
| After cleaning/polishing WE | Full calibration |
| Results seem inconsistent | Re-run blank, check electrode condition |
| Weekly (if electrodes stored properly) | Quick 2-point check (blank + one standard) |

---

## 11. Safety Notes

### Electrical Safety

This circuit operates at **3.3V DC** from the ESP32. This voltage is far below any dangerous threshold.

- 3.3V cannot cause electric shock through skin (minimum threshold is ~30V DC).
- Maximum current from ESP32 3.3V pin is ~500 mA (limited by onboard regulator).
- The breadboard circuit is inherently safe. There is no mains voltage anywhere.
- However, the USB cable connects to your laptop which IS connected to mains. Use a USB hub with proper isolation if concerned, or run from a USB battery bank.

### Chemical Safety

**Household bleach (NaOCl, 4-6%)** -- used for Ag/AgCl coating:
- Wear nitrile or rubber gloves.
- Work in a ventilated area (bleach fumes irritate the respiratory tract).
- Avoid contact with skin and eyes. If contact occurs, flush with water for 15 minutes.
- NEVER mix bleach with ammonia (produces toxic chloramine gas).
- NEVER mix bleach with acids (produces toxic chlorine gas).
- After use, dilute with water and pour down the drain. Rinse the container.

**Ammonia solution (NH3/NH4OH)** -- used for demo spiking:
- Wear gloves and work in a ventilated area.
- Ammonia fumes are irritating. Do not inhale directly from the bottle.
- Use dilute solutions (< 1% for demo purposes). Pharmacy ammonia is typically 2-5%.
- Dilute heavily before disposal (pour into a large volume of water, then down the drain).

**Potassium chloride (KCl)** -- used as supporting electrolyte:
- Food-grade KCl (sold as salt substitute) is safe to handle.
- No special precautions needed.
- Disposal: water-soluble, safe to pour down the drain.

### Lab Safety Basics

- Wear safety goggles when handling chemicals.
- Keep food and drinks away from the lab bench.
- Wash hands after handling chemicals, even benign ones like KCl.
- Label all solutions clearly (contents, concentration, date).
- Keep a beaker of clean distilled water nearby for rinsing electrodes between samples.
- If you break a glass beaker, do not pick up shards with bare hands -- use a dustpan and brush.

---

## 12. Testing Procedure

### Test 1: Verify Circuit Without Electrodes

**Goal**: Confirm the ESP32 DAC and ADC work, and the LM358 is alive.

**Procedure**:

1. Connect the ESP32 to your laptop via USB.
2. Upload a simple test sketch:

```cpp
#define DAC_PIN 25
#define ADC_PIN 36

void setup() {
    Serial.begin(115200);
    analogSetAttenuation(ADC_11db);
    analogSetWidth(12);
}

void loop() {
    // Sweep DAC from 0 to 255
    for (int i = 0; i <= 255; i += 10) {
        dacWrite(DAC_PIN, i);
        delay(100);
        int adc_raw = analogRead(ADC_PIN);
        float adc_v = adc_raw * 3.3 / 4095.0;
        float dac_v = i * 3.3 / 255.0;

        Serial.print("DAC=");
        Serial.print(dac_v, 3);
        Serial.print("V, ADC=");
        Serial.print(adc_v, 3);
        Serial.println("V");
    }
    delay(2000);
}
```

3. Open the Serial Monitor at 115200 baud.

**Expected results (no electrodes connected)**:

With no electrodes, the TIA has no input current. The output should sit near VREF (1.65V):

```
    DAC=0.000V, ADC=1.650V   (or close to it)
    DAC=0.130V, ADC=1.650V
    ...
    DAC=1.650V, ADC=1.650V
    ...
    DAC=3.300V, ADC=1.650V
```

- ADC should read approximately 1.65V (+/- 0.1V) at all DAC values.
- If ADC reads 0V: check the TIA wiring (VREF to pin 5, Rf connection).
- If ADC reads 3.3V: check the TIA wiring (pin 6 may be shorted to 3.3V).
- If ADC varies with DAC: there may be a wiring error connecting the control amp to the TIA.

**Also verify DAC output**: Use a multimeter on the DAC pin (GPIO25) to confirm it sweeps from ~0V to ~3.3V. If it does not change, the ESP32 DAC may need a different library or the pin may be damaged.

### Test 2: Verify VREF

1. Use a multimeter to measure the voltage at the VREF node (junction of R1 and R2).
2. Expected: 1.65V +/- 0.1V.
3. If significantly off:
   - Check R1 and R2 values (both should be 10k). If one is wrong, the voltage divider ratio changes.
   - Check that C4 is connected to GND (not floating).

### Test 3: Electrodes in Plain Water

**Goal**: Verify the potentiostat responds to the electrochemical cell.

**Procedure**:

1. Prepare 100 mL of 0.1M KCl solution (0.75g KCl in 100mL distilled water).
2. Connect the three electrodes to the breadboard (CE, RE, WE connection points).
3. Immerse all three electrodes in the KCl solution.
4. Run the DAC sweep test sketch from Test 1.

**Expected results**:

- ADC should now change as DAC sweeps. The exact values depend on electrode quality.
- You should see the ADC move away from 1.65V, indicating current flow through the cell.
- Typical range: ADC reads 1.0V to 2.3V across the sweep.

```
    DAC=0.000V, ADC=2.100V   (current flowing one direction)
    DAC=0.500V, ADC=1.900V
    DAC=1.000V, ADC=1.750V
    DAC=1.500V, ADC=1.650V   (near zero current)
    DAC=2.000V, ADC=1.500V
    DAC=2.500V, ADC=1.300V   (current flowing other direction)
    DAC=3.000V, ADC=1.100V
```

If the ADC reading does not change when electrodes are in solution:
- Check electrode connections (are they really making contact with the solution?)
- Check electrode connections to breadboard (are alligator clips secure?)
- Try wiggling the electrodes -- the reading should fluctuate
- Verify the control amplifier is working (measure LM358 pin 1 with multimeter -- it should change with DAC)

### Test 4: DPV Scan on Spiked Sample

**Goal**: Detect ammonia in a spiked water sample.

**Procedure**:

1. First, run a blank scan on plain KCl solution. Save this as baseline.
2. Add ammonia to make approximately 5-10 mg/L concentration:
   - If your ammonia solution is 2% (20,000 mg/L): add 50 uL (one drop) to 100 mL water = ~10 mg/L.
   - Use a dropper or syringe if available. Approximate is fine for a demo.
3. Stir gently. Wait 30 seconds for the solution to homogenize.
4. Run the DPV scan.

**Expected results**:

The DPV voltammogram (differential current vs. potential) should show a peak:

```
    delta_i (uA)
       │
     6 │
       │
     5 │             *
       │           *   *
     4 │         *       *
       │       *           *
     3 │     *               *
       │   *                   *
     2 │  *                     *
       │ *                       *
     1 │*                         *
       │                           *  *  *  *
     0 ├──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──
      -0.8 -0.6 -0.4 -0.2  0.0  0.2  0.4
                   Potential (V vs Ag/AgCl)

    Ammonia oxidation peak: approximately -0.2V to 0.0V vs Ag/AgCl
    Peak current should be proportional to ammonia concentration.
```

If no peak is visible:
- Increase ammonia concentration (add more drops)
- Check that the WE was pre-treated (Step 6.1, pre-treatment)
- Try a different gain resistor (switch from 100k to 10k if currents are very large, or to 1M if currents are very small)
- Ensure the Ag/AgCl reference electrode was properly prepared (grey-purple coating)

### Test 5: BLE Communication Test

**Goal**: Verify data transmission to the Flutter app.

1. Upload the BLE-enabled firmware (from `hardware/firmware/src/`).
2. Open the JalSakhi Flutter app on your phone.
3. Scan for BLE devices -- the ESP32 should appear as "JalSakhi".
4. Connect and trigger a DPV scan from the app.
5. The app should display the voltammogram in real time.

If BLE connection fails:
- Verify BLE is enabled in ESP32 partition scheme (use "Minimal SPIFFS" partition in Arduino IDE).
- Check that the antenna end of the ESP32 is not blocked by wires or metal.
- Restart both the ESP32 and the phone's Bluetooth.
- Ensure the phone is within 5 meters of the ESP32.

### Troubleshooting Guide

| Symptom | Possible Cause | Fix |
|---------|---------------|-----|
| ADC reads 0V constantly | TIA output shorted to GND | Check wiring around LM358 pin 7 |
| ADC reads 3.3V constantly | TIA output shorted to VCC, or TIA saturated | Check wiring; try smaller Rf |
| ADC reads 1.65V and never changes | No current flowing (electrodes disconnected or dry) | Check electrodes are in solution and connected |
| ADC fluctuates wildly | Noise pickup, loose connection | Add Faraday cage, check all connections, shorten wires |
| DAC output does not sweep | Wrong GPIO pin, or DAC not configured | Verify GPIO25, try `dacWrite(25, 128)` and measure with multimeter |
| LM358 gets hot | Shorted output, or pins wired wrong | Remove power immediately. Check pin assignments. |
| ESP32 resets during scan | Overcurrent on 3.3V rail | Check for shorts. Add bulk capacitor. Use external 3.3V supply. |
| No BLE connection | Partition scheme wrong, or antenna blocked | Use "Minimal SPIFFS" partition. Clear antenna area. |
| Baseline drift during scan | Electrode not stabilized, temperature change | Wait 2 minutes after immersing electrodes before scanning. |
| Peak appears at wrong potential | RE not properly prepared, or offset error | Re-prepare Ag/AgCl electrode. Recalibrate. |
| Peak too small to see | Concentration too low for current Rf | Increase concentration or use larger Rf (1M) |
| Peak too large (flat-topped) | ADC or TIA saturated | Use smaller Rf (10k) |
| Bubbles on electrodes | Electrolysis (voltage too high) | Reduce scan range. Ensure DAC is not outputting extreme values. |

---

## 13. Production Vision

### From Breadboard to Product

This section maps every breadboard component to its production equivalent in the final JalSakhi dongle design.

| Breadboard Prototype | Production Dongle | Why the Change |
|---------------------|-------------------|----------------|
| **ESP32 DevKitC** | **STM32L432KC** (ARM Cortex-M4, 80 MHz) | Lower power (2 uA sleep), USB-C native, deterministic timing with hardware timers, no WiFi overhead |
| **LM358 op-amps** (2 units in DIP-8) | **AD5940 AFE** (integrated potentiostat front-end) | 12-bit DAC, programmable TIA (200R-10M, 6 ranges with auto-switching), 16-bit ADC at 200 kSPS, integrated PGA (1x-9x), DFT engine for EIS, digital filters (Sinc2+Sinc3) -- all in one chip |
| **Pencil graphite electrodes** (DIY) | **Screen-Printed Electrodes** (SPEs) from DropSens/Zimmer&Peacock | Consistent surface area, pre-modified with target-specific nanomaterials (Prussian Blue, Bi film, Au NP), disposable (no cleaning/recalibration), INR 25 per strip |
| **Ag/AgCl wire** (DIY bleach coat) | **Ag/AgCl ink** (screen-printed on SPE) | Integrated into the disposable electrode strip, factory-calibrated, consistent potential |
| **Breadboard + jumper wires** | **4-layer PCB** (35mm x 18mm) | Signal/GND/Power/Digital layer stack, guard rings on high-impedance traces, ferrite bead isolation between analog and digital, stamped metal shielding can |
| **100nF/100uF caps** (through-hole) | **SMD decoupling** (100nF MLCC x6 + 10uF tantalum x2) + separate analog/digital LDO rails (MCP1700 x2) | Much lower ESR, shorter loop area, better HF filtering |
| **BLE wireless** (ESP32 onboard) | **USB-C** (direct to phone) | Lower latency, deterministic data transfer, phone powers the dongle (no battery needed), simpler protocol |
| **Manual gain switching** (swap resistor) | **Auto-range TIA** (AD5940 programmable R_TIA) | Firmware auto-selects gain before each scan based on pre-scan impedance check, 10 nA to 10 mA dynamic range |
| **Software peak detection** (on phone) | **On-device DSP** (on STM32 firmware) | Savitzky-Golay + ALS baseline + derivative peak detection runs on MCU before data reaches phone, deterministic timing |
| **No temperature compensation** | **TMP117 sensor** (+/- 0.1C) near electrode connector | Arrhenius-derived correction per contaminant: `I_corrected = I_measured / (1 + alpha * (T - T_ref))` |
| **No fault detection** | **Pre/post-scan fault checks** | Electrode presence, sample presence, contact impedance (<5 ohm), temperature range, ADC saturation, baseline anomaly |
| **No device authentication** | **Ed25519 key pair** per dongle (factory-provisioned) | Every test result cryptographically signed, tamper-resistant data for municipal dashboards |

### Cost Comparison

| | Prototype | Production (100 units) | Production (10,000 units) |
|---|-----------|----------------------|--------------------------|
| Electronics | INR 780 | INR 1,000 | INR 800 |
| Electrodes | INR 0 (DIY) | INR 25/test (SPE) | INR 15/test (SPE) |
| Enclosure | N/A (breadboard) | INR 100 (3D printed) | INR 35 (injection molded) |
| PCB | N/A (breadboard) | INR 200 (prototype PCB) | INR 50 (panel production) |
| Assembly | Self | INR 150 (manual) | INR 50 (pick-and-place) |
| **Total** | **INR ~1,840** | **INR ~1,500** | **INR ~1,200** |

### What the Prototype Proves

Even though the prototype uses cheaper components with worse specs, it demonstrates the core scientific principle:

1. **Voltage sweep generation** -- the ESP32 DAC generates the DPV waveform, proving that controlled electrochemical experiments can be driven by a microcontroller.
2. **Current measurement** -- the LM358 TIA converts picoamp-to-microamp cell currents into measurable voltages, proving that useful electrochemical signals can be captured with commodity op-amps.
3. **Contaminant detection** -- the DPV peak at a specific potential identifies ammonia (or other contaminants), proving that electrochemical fingerprinting works with pencil graphite electrodes.
4. **Wireless data transfer** -- BLE transmission to the Flutter app proves the smartphone-as-instrument concept.
5. **AI classification** -- the on-phone ML model interprets the voltammogram, proving that automated contaminant identification is feasible.

The production design replaces each component with a better version of the same function. The science does not change -- only the precision, reliability, and form factor improve.

### Upgrade Path

If you want to incrementally improve the prototype without jumping to full production:

| Upgrade | Cost | Benefit |
|---------|------|---------|
| Replace LM358 with MCP6002 (rail-to-rail) | INR 50 | Full 0-3.3V output swing, lower noise |
| Add ADS1115 external 16-bit ADC (I2C) | INR 200 | 16-bit resolution vs 12-bit ESP32 ADC, PGA built in |
| Use commercial SPEs instead of pencil graphite | INR 25/test | Consistent results, target-specific modifications |
| Add TMP36 temperature sensor | INR 50 | Basic temperature compensation |
| Switch from breadboard to perfboard (soldered) | INR 30 | More reliable connections, less noise |
| Add metal shielding (tin can over circuit) | INR 0 | Significant noise reduction |

---

## Quick Reference Card

Print this section and keep it next to your breadboard.

```
    ╔══════════════════════════════════════════════════════════╗
    ║           JalSakhi Potentiostat - Quick Reference        ║
    ╠══════════════════════════════════════════════════════════╣
    ║                                                          ║
    ║  ESP32 Pins:                                             ║
    ║    GPIO25 (DAC) → Control Amp (LM358 pin 3)             ║
    ║    GPIO36 (ADC) ← TIA output (LM358 pin 7)              ║
    ║    GPIO2        → Status LED (through 220R)              ║
    ║    3.3V         → Power rail (+)                         ║
    ║    GND          → Ground rail (-)                        ║
    ║                                                          ║
    ║  LM358 Pins:                                             ║
    ║    Pin 1 (OUT_A) → CE electrode                          ║
    ║    Pin 2 (IN_A-) ← RE electrode (through 10k)           ║
    ║                    + feedback from pin 1 (through 1k)    ║
    ║    Pin 3 (IN_A+) ← DAC (GPIO25, through 10k + 100nF)   ║
    ║    Pin 4 (GND)   → GND rail                              ║
    ║    Pin 5 (IN_B+) ← VREF (1.65V)                         ║
    ║    Pin 6 (IN_B-) ← WE electrode                          ║
    ║                    + Rf (100k) to pin 7                   ║
    ║                    + Cf (100pF) to pin 7                  ║
    ║    Pin 7 (OUT_B) → ADC (GPIO36)                          ║
    ║    Pin 8 (VCC)   → +3.3V rail                            ║
    ║                                                          ║
    ║  VREF: 10k + 10k divider = 1.65V (+ 10uF cap to GND)   ║
    ║                                                          ║
    ║  Electrodes:                                             ║
    ║    WE = Pencil graphite (HB/2B), 3-5mm exposed           ║
    ║    CE = Pencil graphite (HB/2B), 5-8mm exposed           ║
    ║    RE = Silver wire with AgCl coat (30-45 min in bleach) ║
    ║                                                          ║
    ║  TIA Gain:                                               ║
    ║    Rf = 10k   → +/- 165 uA range                        ║
    ║    Rf = 100k  → +/- 16.5 uA range  ★ START HERE         ║
    ║    Rf = 1M    → +/- 1.65 uA range                       ║
    ║                                                          ║
    ║  DPV Settings:                                           ║
    ║    Step: 4 mV | Pulse: 50 mV | Pulse width: 50 ms       ║
    ║    Step period: 200 ms | Range: -0.8V to +0.4V           ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
```

---

*Document version 1.0 | March 2026 | JalSakhi Project*
*World Water Day 2026 Competition Prototype*
*Bennett University*
