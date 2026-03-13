/*
 * ============================================================================
 *  JalSakhi — Smartphone-Based Electrochemical Water Forensics Platform
 * ============================================================================
 *
 *  Project     : JalSakhi (Hindi: "Water Friend")
 *  Competition : World Water Day 2026 — L&T Construction
 *  Team        : Ujjwal, Bennett University
 *  Repository  : https://github.com/ujjwal-manot/JalSakhi
 *  Budget      : INR 4,000 hard limit
 *
 *  Description:
 *    This firmware transforms an ESP32 + LM358 op-amp circuit into a
 *    Bluetooth Low Energy (BLE) potentiostat capable of performing
 *    Differential Pulse Voltammetry (DPV) on pencil graphite electrodes.
 *    It streams real-time voltammogram data to a Flutter smartphone app,
 *    enabling field-level detection of heavy metals and contaminants in
 *    drinking water — all for under INR 4,000.
 *
 *  Architecture:
 *    ESP32 (BLE Server)  <--BLE-->  Smartphone (Flutter App)
 *       |
 *       +-- DAC (GPIO25) --> LM358 Op-Amp Potentiostat --> Working Electrode
 *       +-- ADC (GPIO34) <-- Transimpedance Amplifier  <-- Current Response
 *       +-- ADC (GPIO35) <-- TMP36 Temperature Sensor
 *       +-- ADC (GPIO33) <-- Battery Voltage Divider
 *       +-- GPIO2        --> Status LED
 *       +-- GPIO32       --> Electrode Presence Detection
 *
 *  Technique — Differential Pulse Voltammetry (DPV):
 *    DPV superimposes small amplitude pulses on a linear potential ramp.
 *    The current is sampled twice: once just before the pulse (i1) and once
 *    at the end of the pulse (i2). The difference (i2 - i1) is plotted vs.
 *    the base potential. This differential measurement cancels capacitive
 *    (charging) current, yielding sharp Gaussian-shaped peaks whose
 *    position identifies the analyte and whose height/area gives
 *    concentration. DPV achieves detection limits in the low ppb range,
 *    making it ideal for heavy metal detection at WHO guideline levels.
 *
 *  Why DPV over other techniques?
 *    - Better sensitivity than cyclic voltammetry (CV)
 *    - Rejects capacitive background → cleaner peaks
 *    - Each metal oxidizes at a characteristic potential → identification
 *    - Pencil graphite electrodes are sufficient for ppb-level detection
 *    - Simple circuit: just need DAC + ADC + op-amp
 *
 * ============================================================================
 *  PIN ASSIGNMENTS
 * ============================================================================
 *
 *  GPIO25 (DAC1)  — Voltage output to potentiostat (0–3.3V → mapped to electrochemical window)
 *  GPIO34 (ADC6)  — Current measurement from transimpedance amplifier
 *  GPIO35 (ADC7)  — TMP36 temperature sensor input
 *  GPIO33 (ADC5)  — Battery voltage via voltage divider (2x 10kΩ)
 *  GPIO32         — Electrode presence detection (impedance check)
 *  GPIO2          — Built-in LED for status indication
 *
 * ============================================================================
 *  CIRCUIT DIAGRAM (ASCII Art)
 * ============================================================================
 *
 *  The potentiostat uses two LM358 op-amps in a single DIP-8 package:
 *    - OA1: Voltage follower / control amplifier (drives counter electrode)
 *    - OA2: Transimpedance amplifier (converts current to voltage)
 *
 *                          +5V (USB)
 *                           |
 *                    LM358 (DIP-8)
 *              +------+--------+------+
 *              |      |  Vcc   |      |
 *              |   +--+--+  +--+--+   |
 *              |   | OA1 |  | OA2 |   |
 *              |   +--+--+  +--+--+   |
 *              |      |  GND   |      |
 *              +------+--------+------+
 *
 *
 *   ESP32                    OA1 (Control Amplifier)
 *   GPIO25 ----[10kΩ]---+---(+)
 *   (DAC out)            |       \
 *                        |        >---+-------> Counter Electrode (CE)
 *              Vref -----|---(-)  /   |              |
 *             (1.65V)    |       /    |              |
 *              from      +------+     |         [Electrochemical
 *              divider                |           Cell / Beaker]
 *                                     |              |
 *                              Reference Electrode (RE)   |
 *                              (Ag/AgCl or pencil)        |
 *                                     |              |
 *                                     +--- to OA1(-) Working Electrode (WE)
 *                                          feedback       |
 *                                                         |
 *                                                    OA2 (Transimpedance Amp)
 *                              +-------[Rf = 100kΩ]------+
 *                              |                          |
 *                    (+)---+   |                     (-)--+
 *                          |   |                          |
 *              Vref -------+    \                         |
 *             (1.65V)            >----+---> GPIO34 (ADC)  |
 *                               /     |    (current       |
 *                         (-)--+      |     measurement)  |
 *                              |      |                   |
 *                              +------+                   |
 *                                                         |
 *                              Working Electrode (WE) ----+
 *                              (Pencil graphite, 2B)
 *
 *   Three-Electrode Configuration:
 *     WE  = Working Electrode  — pencil graphite lead (2B), where reaction occurs
 *     RE  = Reference Electrode — another pencil lead (provides stable potential reference)
 *     CE  = Counter Electrode  — pencil lead (completes circuit, carries current)
 *
 *   The potentiostat maintains the potential between WE and RE at the
 *   DAC-commanded value by adjusting the CE potential via feedback.
 *   The transimpedance amplifier (OA2) converts the tiny faradaic current
 *   (nA to µA range) flowing through WE into a measurable voltage.
 *
 *   Rf (feedback resistor) selection:
 *     Rf = 100kΩ → 1µA produces 100mV output
 *     For ppb-level heavy metals, currents are typically 0.1–10 µA
 *     This maps to 10mV – 1V at the ADC, well within ESP32's 12-bit range
 *
 *   Temperature Sensor (TMP36):
 *     TMP36 OUT ----> GPIO35
 *     Vout = 0.5V + 0.01V/°C  →  T(°C) = (Vout - 0.5) / 0.01
 *
 *   Battery Monitor:
 *     VBAT ---[10kΩ]---+---[10kΩ]--- GND
 *                       |
 *                       +---> GPIO33 (reads VBAT/2)
 *
 * ============================================================================
 *  BOM (Bill of Materials) — Total: ~INR 1,200
 * ============================================================================
 *
 *  1x ESP32 DevKit v1            — INR 450
 *  1x LM358 DIP-8 op-amp        — INR 15
 *  1x 100kΩ resistor (Rf)        — INR 2
 *  2x 10kΩ resistors (divider)   — INR 4
 *  1x TMP36 temperature sensor   — INR 80
 *  3x Pencil graphite leads (2B) — INR 10
 *  1x Mini breadboard            — INR 60
 *  Jumper wires                  — INR 30
 *  USB cable                     — INR 50
 *  Misc (capacitors, etc.)       — INR 20
 *                          Total ≈ INR 721
 *
 * ============================================================================
 *  DEPENDENCIES
 * ============================================================================
 *
 *  Board: ESP32 by Espressif Systems (Arduino Board Manager)
 *  Libraries: Built-in BLE (BLEDevice.h) — no external libraries needed
 *
 * ============================================================================
 *  LICENSE: MIT — Free for educational and competition use
 * ============================================================================
 */

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <math.h>
#include <driver/dac.h>
#include <driver/adc.h>

// ============================================================================
//  VERSION & IDENTIFICATION
// ============================================================================

#define FIRMWARE_VERSION    "1.4.0"
#define DEVICE_NAME         "JalSakhi-Potentiostat"
#define HARDWARE_REV        "BreadboardV1-LM358"

// ============================================================================
//  BLE UUIDs
// ============================================================================
//
//  We use standard NUS-like (Nordic UART Service) UUIDs for maximum
//  compatibility with generic BLE terminal apps during debugging,
//  plus a custom service UUID for the Flutter app.

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define TX_CHAR_UUID        "beb5483e-36e1-4688-b7f5-ea07361b26a8"   // Notify
#define RX_CHAR_UUID        "6e400002-b5a3-f393-e0a9-e50e24dcca9e"   // Write

// ============================================================================
//  PIN DEFINITIONS
// ============================================================================

#define PIN_DAC_OUT         25      // DAC Channel 1 — voltage output to potentiostat
#define PIN_ADC_CURRENT     34      // ADC1_CH6 — current measurement (from TIA)
#define PIN_ADC_TEMP        35      // ADC1_CH7 — TMP36 temperature sensor
#define PIN_ADC_BATTERY     33      // ADC1_CH5 — battery voltage divider
#define PIN_LED             2       // Built-in LED for status indication
#define PIN_ELECTRODE_DET   32      // Electrode presence detection (digital I/O)

// ============================================================================
//  DPV PARAMETERS
// ============================================================================
//
//  Differential Pulse Voltammetry waveform parameters:
//
//  The potential waveform looks like this:
//
//    Voltage
//      ^        ___         ___         ___
//      |       |   |       |   |       |   |
//      |    ___|   |___.___|   |___.___|   |___
//      |   /   ↑       ↑   ↑       ↑
//      |  /    i2      i1   i2      i1
//      | /     (pulse)      (pulse)
//      |/      (sample)     (sample)
//      +-----------------------------------------> Time
//
//  i1 = current sampled just BEFORE pulse (at base potential)
//  i2 = current sampled at END of pulse (base + pulse amplitude)
//  ΔI = i2 - i1  →  this is what we plot
//
//  Why these specific values?
//  - E_start = -1.2V: Catches lead (-0.55V) and other metals with negative potentials
//  - E_end   = +0.6V: Captures iron (+0.45V) and extends past for completeness
//  - E_step  = 4mV:   Standard resolution; finer steps = better peak shape
//  - Pulse amplitude = 50mV: Maximizes faradaic/capacitive ratio (Osteryoung)
//  - Pulse width = 50ms: Allows double-layer charging to decay (~5τ for RC circuit)
//  - Pulse period = 200ms: Gives adequate time for diffusion layer recovery

#define DPV_E_START         -1.2f   // Start potential (V vs pseudo-reference)
#define DPV_E_END           +0.6f   // End potential (V vs pseudo-reference)
#define DPV_E_STEP          0.004f  // Step potential (V) — 4 mV
#define DPV_PULSE_AMP       0.050f  // Pulse amplitude (V) — 50 mV
#define DPV_PULSE_WIDTH_MS  50      // Pulse width (ms) — duration of the pulse
#define DPV_PULSE_PERIOD_MS 200     // Pulse period (ms) — time between pulses

// Derived parameters
#define DPV_NUM_POINTS      ((int)((DPV_E_END - DPV_E_START) / DPV_E_STEP))   // 450 points
#define DPV_SCAN_TIME_S     (DPV_NUM_POINTS * DPV_PULSE_PERIOD_MS / 1000.0f)  // ~90 seconds

// ============================================================================
//  VOLTAGE MAPPING
// ============================================================================
//
//  The ESP32 DAC outputs 0–3.3V (8-bit: 0–255).
//  Our electrochemical window is -1.2V to +0.6V.
//  We use a virtual ground at Vcc/2 = 1.65V (set by the resistor divider
//  at the non-inverting input of OA1).
//
//  Mapping:
//    Electrochemical 0V  →  DAC outputs 1.65V  →  DAC value ~128
//    Electrochemical -1.2V → DAC outputs 1.65 - 1.2 = 0.45V → DAC value ~35
//    Electrochemical +0.6V → DAC outputs 1.65 + 0.6 = 2.25V → DAC value ~174
//
//  Formula: DAC_value = (V_electrochemical + 1.65) * 255 / 3.3

#define VREF_OFFSET         1.65f   // Virtual ground (Vcc/2)
#define DAC_MAX_VOLTAGE     3.3f    // ESP32 DAC full-scale voltage
#define DAC_RESOLUTION      255     // 8-bit DAC

// ============================================================================
//  ADC CONFIGURATION
// ============================================================================
//
//  ESP32 ADC1 is 12-bit (0–4095) with 0–3.3V range (with 11dB attenuation).
//  The transimpedance amplifier (TIA) outputs:
//    V_out = V_ref + I_cell × Rf
//  where V_ref = 1.65V and Rf = 100kΩ.
//
//  So: I_cell = (V_adc - 1.65V) / 100kΩ
//
//  At 12-bit resolution: 1 LSB ≈ 0.8mV → current resolution ≈ 8nA
//  This is sufficient for detecting heavy metals at ppb levels where
//  typical peak currents are 0.1–10 µA.

#define ADC_RESOLUTION      4095    // 12-bit ADC
#define ADC_VREF            3.3f    // ADC reference voltage (with 11dB atten)
#define TIA_RF              100000  // Transimpedance amplifier feedback resistor (Ω)
#define ADC_SAMPLES         16      // Number of ADC readings to average (for noise reduction)

// ============================================================================
//  CONTAMINANT DATABASE
// ============================================================================
//
//  Each contaminant oxidizes at a characteristic potential (vs Ag/AgCl or
//  pseudo-reference). The peak potential depends on the electrode material
//  and electrolyte; these values are calibrated for pencil graphite in
//  tap water / dilute acid supporting electrolyte.
//
//  The Gaussian peak model (Randles-Sevcik + DPV theory):
//    ΔI(E) = I_peak × exp(-0.5 × ((E - E_peak) / σ)²)
//  where:
//    E_peak = characteristic oxidation potential
//    σ = peak half-width (related to electron transfer kinetics)
//    I_peak = peak current (proportional to concentration via calibration)
//
//  Calibration curves (linear range, pencil graphite electrodes):
//    I_peak(µA) = slope × concentration + intercept
//  These are simplified linear models valid in the low-concentration regime
//  (Henry's law region of the Langmuir isotherm / dilute Nernst regime).

#define NUM_CONTAMINANTS    5

struct Contaminant {
    const char* name;       // Chemical name
    const char* symbol;     // Chemical symbol for display
    const char* unit;       // Concentration unit
    float peakPotential;    // E_peak in V vs pseudo-reference
    float sigma;            // Gaussian width parameter (V)
    float calSlope;         // Calibration slope (µA per unit concentration)
    float calIntercept;     // Calibration intercept (µA)
    float whoLimit;         // WHO guideline value
    float simConcentration; // Simulated concentration for demo mode
    float simPeakCurrent;   // Simulated peak current (µA) for demo
};

/*
 * Electrochemistry notes for each contaminant:
 *
 * Lead (Pb²⁺ → Pb⁰ at ~-0.55V):
 *   Pb²⁺ + 2e⁻ → Pb⁰  (stripping: Pb⁰ → Pb²⁺ + 2e⁻)
 *   WHO limit: 10 ppb. Our demo shows 15.2 ppb (above limit → flagged).
 *   Lead is one of the easiest metals to detect by ASV/DPV due to its
 *   well-defined, sharp stripping peak on carbon electrodes.
 *
 * Arsenic (As³⁺ at ~-0.15V):
 *   As³⁺ → As⁵⁺ + 2e⁻ (anodic oxidation in acidic media)
 *   WHO limit: 10 ppb. Demo: 8.1 ppb (below limit but concerning).
 *   Arsenic detection requires acidic conditions (HCl); broader peak than Pb.
 *
 * Ammonia (NH₃/NH₄⁺ at ~+0.05V):
 *   NH₃ → ½N₂ + 3H⁺ + 3e⁻ (electro-oxidation)
 *   Typical safe limit: 1.5 mg/L (WHO). Demo: 1.8 mg/L (slightly above).
 *   Broad peak due to multi-electron, multi-step mechanism.
 *
 * Nitrate (NO₃⁻ at ~+0.25V):
 *   NO₃⁻ + 2H⁺ + 2e⁻ → NO₂⁻ + H₂O (reduction, but we detect the
 *   reverse oxidation current in DPV setup with modified electrodes)
 *   WHO limit: 50 mg/L. Demo: 12.5 mg/L (safe).
 *
 * Iron (Fe²⁺/Fe³⁺ at ~+0.45V):
 *   Fe²⁺ → Fe³⁺ + e⁻ (anodic oxidation)
 *   WHO aesthetic limit: 0.3 mg/L (causes staining). Demo: 0.8 mg/L.
 *   Very clean, sharp peak on carbon electrodes.
 */

const Contaminant contaminants[NUM_CONTAMINANTS] = {
    // name       symbol   unit     E_peak   sigma  slope  intercept  WHO_limit  sim_conc  sim_peak_µA
    { "Lead",     "Pb",    "ppb",   -0.55f,  0.04f, 0.065f, 0.01f,   10.0f,     15.2f,    1.00f  },
    { "Arsenic",  "As",    "ppb",   -0.15f,  0.05f, 0.048f, 0.005f,  10.0f,     8.1f,     0.39f  },
    { "Ammonia",  "NH3",   "mg/L",  +0.05f,  0.06f, 0.52f,  0.02f,   1.5f,      1.8f,     0.96f  },
    { "Nitrate",  "NO3",   "mg/L",  +0.25f,  0.04f, 0.031f, 0.01f,   50.0f,     12.5f,    0.40f  },
    { "Iron",     "Fe",    "mg/L",  +0.45f,  0.05f, 1.15f,  0.03f,   0.3f,      0.8f,     0.95f  }
};

// ============================================================================
//  SAVITZKY-GOLAY COEFFICIENTS
// ============================================================================
//
//  Savitzky-Golay filter: polynomial smoothing that preserves peak shape
//  better than a moving average. We use a 5-point quadratic/cubic filter.
//
//  For a 5-point window (m=2), the normalized coefficients for smoothing are:
//    c = [-3, 12, 17, 12, -3] / 35
//
//  This is equivalent to fitting a 2nd-order polynomial to 5 points and
//  taking the fitted value at the center point. It smooths noise while
//  preserving peak height and width much better than a simple average.

#define SG_WINDOW           5
const float sgCoeffs[SG_WINDOW] = { -3.0f/35.0f, 12.0f/35.0f, 17.0f/35.0f, 12.0f/35.0f, -3.0f/35.0f };

// ============================================================================
//  STATE MACHINE
// ============================================================================

enum DeviceState {
    STATE_IDLE,             // Waiting for commands
    STATE_SCANNING,         // Performing DPV scan (real hardware)
    STATE_DEMO_CLEAN,       // Generating simulated clean water data
    STATE_DEMO_CONTAMINATED,// Generating simulated contaminated water data
    STATE_CALIBRATING,      // Running calibration routine
    STATE_ERROR             // Error state (recoverable)
};

const char* stateNames[] = {
    "IDLE", "SCANNING", "DEMO_CLEAN", "DEMO_CONTAMINATED", "CALIBRATING", "ERROR"
};

// ============================================================================
//  LED PATTERNS
// ============================================================================

enum LEDPattern {
    LED_OFF,                // LED off
    LED_SLOW_BLINK,         // 1 Hz — advertising, waiting for BLE connection
    LED_SOLID,              // Constant on — BLE connected, idle
    LED_FAST_BLINK,         // 4 Hz — scanning in progress
    LED_DOUBLE_BLINK        // Double pulse — error condition
};

// ============================================================================
//  GLOBAL VARIABLES
// ============================================================================

// BLE objects
BLEServer*         pServer         = nullptr;
BLECharacteristic* pTxCharacteristic = nullptr;
BLECharacteristic* pRxCharacteristic = nullptr;

// State
volatile DeviceState currentState  = STATE_IDLE;
volatile bool        deviceConnected = false;
volatile bool        oldDeviceConnected = false;
volatile bool        scanAborted    = false;

// LED control
LEDPattern currentLEDPattern       = LED_SLOW_BLINK;
unsigned long lastLEDToggle        = 0;
bool ledState                      = false;
int doubleBLinkPhase               = 0;

// Data buffers
//   We store the raw voltammogram and the processed (smoothed) version.
//   DPV_NUM_POINTS ≈ 450, so memory usage is modest (~3.6 KB per array).
float voltageArray[DPV_NUM_POINTS];   // Potential values (V)
float currentArray[DPV_NUM_POINTS];   // Raw differential current (µA)
float smoothedArray[DPV_NUM_POINTS];  // Savitzky-Golay smoothed current (µA)
float baselineArray[DPV_NUM_POINTS];  // Estimated baseline current (µA)
int   dataPointCount = 0;             // Number of valid data points

// Detected peaks
#define MAX_PEAKS 10
struct Peak {
    float potential;       // Peak potential (V)
    float current;         // Peak current (µA) — baseline-subtracted
    int   contaminantIdx;  // Index into contaminants[] or -1 if unidentified
    float concentration;   // Estimated concentration (in contaminant's unit)
};
Peak detectedPeaks[MAX_PEAKS];
int  numDetectedPeaks = 0;

// Sensor readings
float temperature      = 25.0f;     // °C (from TMP36 or simulated)
float batteryVoltage   = 3.7f;      // V (from divider or assumed)
bool  electrodePresent = false;     // Whether electrodes are detected

// Timing
unsigned long scanStartTime = 0;
unsigned long lastStatusSend = 0;

// ============================================================================
//  BLE CALLBACK CLASSES
// ============================================================================

/*
 * Server callbacks: track connection state.
 * When a client connects, we switch from advertising blink to solid LED.
 * When disconnected, we restart advertising automatically.
 */
class ServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) override {
        deviceConnected = true;
        currentLEDPattern = LED_SOLID;
        Serial.println("[BLE] Client connected");
    }

    void onDisconnect(BLEServer* pServer) override {
        deviceConnected = false;
        currentLEDPattern = LED_SLOW_BLINK;
        Serial.println("[BLE] Client disconnected");

        // If we were scanning, abort
        if (currentState == STATE_SCANNING ||
            currentState == STATE_DEMO_CLEAN ||
            currentState == STATE_DEMO_CONTAMINATED) {
            scanAborted = true;
            currentState = STATE_IDLE;
        }
    }
};

/*
 * RX Characteristic callback: handles incoming commands from the app.
 * Commands are simple ASCII strings for easy debugging with any BLE terminal.
 */
class RxCallbacks : public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic* pCharacteristic) override {
        String rxValue = pCharacteristic->getValue().c_str();
        rxValue.trim();

        if (rxValue.length() == 0) return;

        Serial.print("[BLE RX] Command: ");
        Serial.println(rxValue);

        // ---- Command Dispatch ----
        if (rxValue == "START_SCAN") {
            handleStartScan();
        }
        else if (rxValue == "DEMO_CLEAN") {
            handleDemoClean();
        }
        else if (rxValue == "DEMO_CONTAMINATED") {
            handleDemoContaminated();
        }
        else if (rxValue == "STOP") {
            handleStop();
        }
        else if (rxValue == "STATUS") {
            handleStatus();
        }
        else if (rxValue == "CALIBRATE") {
            handleCalibrate();
        }
        else {
            sendBLE("ERROR:Unknown command: " + rxValue + "\n");
        }
    }

    // ---- Command Handlers ----

    void handleStartScan() {
        if (currentState != STATE_IDLE) {
            sendBLE("ERROR:Device busy, current state=" + String(stateNames[currentState]) + "\n");
            return;
        }
        scanAborted = false;
        currentState = STATE_SCANNING;
        currentLEDPattern = LED_FAST_BLINK;
        sendBLE("STATUS:SCANNING\n");
        Serial.println("[SCAN] Starting real DPV scan...");
    }

    void handleDemoClean() {
        if (currentState != STATE_IDLE) {
            sendBLE("ERROR:Device busy\n");
            return;
        }
        scanAborted = false;
        currentState = STATE_DEMO_CLEAN;
        currentLEDPattern = LED_FAST_BLINK;
        sendBLE("STATUS:SCANNING\n");
        Serial.println("[DEMO] Generating clean water voltammogram...");
    }

    void handleDemoContaminated() {
        if (currentState != STATE_IDLE) {
            sendBLE("ERROR:Device busy\n");
            return;
        }
        scanAborted = false;
        currentState = STATE_DEMO_CONTAMINATED;
        currentLEDPattern = LED_FAST_BLINK;
        sendBLE("STATUS:SCANNING\n");
        Serial.println("[DEMO] Generating contaminated water voltammogram...");
    }

    void handleStop() {
        if (currentState == STATE_SCANNING ||
            currentState == STATE_DEMO_CLEAN ||
            currentState == STATE_DEMO_CONTAMINATED ||
            currentState == STATE_CALIBRATING) {
            scanAborted = true;
            sendBLE("STATUS:STOPPING\n");
            Serial.println("[CMD] Scan abort requested");
        } else {
            sendBLE("STATUS:IDLE\n");
        }
    }

    void handleStatus() {
        sendStatusReport();
    }

    void handleCalibrate() {
        if (currentState != STATE_IDLE) {
            sendBLE("ERROR:Device busy\n");
            return;
        }
        scanAborted = false;
        currentState = STATE_CALIBRATING;
        currentLEDPattern = LED_FAST_BLINK;
        sendBLE("STATUS:CALIBRATING\n");
        Serial.println("[CAL] Starting calibration...");
    }
};

// ============================================================================
//  BLE COMMUNICATION HELPER
// ============================================================================

/*
 * Send a string over BLE TX characteristic (notify).
 * BLE has a maximum payload size (typically 20 bytes for BLE 4.0, up to
 * 512 for BLE 4.2+ with MTU negotiation). We chunk if necessary.
 *
 * Also echoes to Serial for debugging without a phone.
 */
void sendBLE(const String& data) {
    if (!deviceConnected || pTxCharacteristic == nullptr) {
        Serial.print("[BLE TX - no client] ");
        Serial.print(data);
        return;
    }

    // BLE 4.2 typical MTU allows ~500 bytes, but we play safe with 20-byte chunks
    // to support all devices. ESP32 BLE stack handles fragmentation, but we keep
    // individual notify payloads small for reliability.
    const int CHUNK_SIZE = 20;
    int len = data.length();
    int offset = 0;

    while (offset < len) {
        int chunkLen = min(CHUNK_SIZE, len - offset);
        String chunk = data.substring(offset, offset + chunkLen);
        pTxCharacteristic->setValue(chunk.c_str());
        pTxCharacteristic->notify();
        offset += chunkLen;

        // Small delay between chunks to prevent BLE stack overflow.
        // The ESP32 BLE notify queue has limited depth.
        delay(10);
    }

    Serial.print("[BLE TX] ");
    Serial.print(data);
}

// ============================================================================
//  VOLTAGE CONVERSION FUNCTIONS
// ============================================================================

/*
 * Convert an electrochemical potential (V vs pseudo-reference) to a DAC value.
 *
 * The potentiostat applies the voltage between the working electrode (WE)
 * and the reference electrode (RE). The DAC drives the control amplifier
 * (OA1), which adjusts the counter electrode (CE) to maintain the desired
 * WE-RE potential through negative feedback.
 *
 * The virtual ground is at Vcc/2 = 1.65V (set by a resistor divider at
 * the non-inverting input of OA1). So:
 *   V_DAC = V_electrochemical + V_ref_offset
 *   DAC_value = V_DAC × 255 / 3.3
 */
uint8_t electrochemicalToDAC(float eVoltage) {
    float vDAC = eVoltage + VREF_OFFSET;

    // Clamp to DAC range
    if (vDAC < 0.0f) vDAC = 0.0f;
    if (vDAC > DAC_MAX_VOLTAGE) vDAC = DAC_MAX_VOLTAGE;

    return (uint8_t)(vDAC * DAC_RESOLUTION / DAC_MAX_VOLTAGE);
}

/*
 * Convert an ADC reading to current (µA).
 *
 * The transimpedance amplifier (OA2) converts cell current to voltage:
 *   V_adc = V_ref + I_cell × Rf
 *   I_cell = (V_adc - V_ref) / Rf
 *
 * We return current in µA for convenient units in the ppb-level regime.
 */
float adcToCurrent(int adcValue) {
    float vADC = (float)adcValue * ADC_VREF / ADC_RESOLUTION;
    float currentA = (vADC - VREF_OFFSET) / TIA_RF;  // Amperes
    float currentUA = currentA * 1e6;                  // Microamperes
    return currentUA;
}

/*
 * Read ADC with oversampling for noise reduction.
 *
 * The ESP32 ADC is notoriously noisy (effective resolution ~9-10 bits).
 * Oversampling by N and averaging improves SNR by sqrt(N).
 * With 16 samples: improvement = 4x = +12dB, giving ~11 effective bits.
 */
int readADCOversampled(int pin) {
    long sum = 0;
    for (int i = 0; i < ADC_SAMPLES; i++) {
        sum += analogRead(pin);
        delayMicroseconds(100);  // Short delay between samples for ADC settling
    }
    return (int)(sum / ADC_SAMPLES);
}

// ============================================================================
//  SENSOR READING FUNCTIONS
// ============================================================================

/*
 * Read temperature from TMP36 sensor.
 *
 * TMP36 output: V = 0.5V + 0.01V/°C
 * At 25°C: V = 0.5 + 0.25 = 0.75V → ADC ≈ 930
 *
 * If no TMP36 is connected, the ADC will read noise near 0V or Vcc,
 * giving unreasonable temperatures. We detect this and fall back to
 * a default value.
 */
float readTemperature() {
    int adcVal = readADCOversampled(PIN_ADC_TEMP);
    float voltage = (float)adcVal * ADC_VREF / ADC_RESOLUTION;
    float tempC = (voltage - 0.5f) / 0.01f;

    // Sanity check: if outside -10 to 60°C, sensor probably not connected
    if (tempC < -10.0f || tempC > 60.0f) {
        return 25.0f;  // Default to room temperature
    }
    return tempC;
}

/*
 * Read battery voltage through voltage divider.
 *
 * Two equal 10kΩ resistors divide VBAT by 2.
 * V_adc = VBAT / 2  →  VBAT = V_adc × 2
 *
 * For a 3.7V LiPo: V_adc = 1.85V → ADC ≈ 2297
 * Full charge (4.2V): V_adc = 2.1V → ADC ≈ 2606
 * Empty (3.0V): V_adc = 1.5V → ADC ≈ 1862
 */
float readBatteryVoltage() {
    int adcVal = readADCOversampled(PIN_ADC_BATTERY);
    float voltage = (float)adcVal * ADC_VREF / ADC_RESOLUTION;
    float vbat = voltage * 2.0f;  // Undo the voltage divider

    // Sanity check: if unreasonable, assume USB-powered at 5V → regulated to 3.3V
    if (vbat < 2.5f || vbat > 5.5f) {
        return 3.7f;  // Default: assume nominal LiPo voltage
    }
    return vbat;
}

/*
 * Check if electrodes are present by measuring impedance.
 *
 * Method: briefly apply a known voltage through the DAC and measure the
 * ADC response. With electrodes immersed in water, there will be a
 * measurable current path. Without electrodes (open circuit), the ADC
 * will read near the bias voltage.
 *
 * This is a simplified check — not a full EIS (Electrochemical Impedance
 * Spectroscopy) measurement, but sufficient to detect if something is
 * connected.
 */
bool checkElectrodePresence() {
    // Apply a small test voltage (100mV above virtual ground)
    uint8_t testDAC = electrochemicalToDAC(0.1f);
    dacWrite(PIN_DAC_OUT, testDAC);
    delay(50);  // Allow settling

    int adcVal = readADCOversampled(PIN_ADC_CURRENT);
    float current = adcToCurrent(adcVal);

    // Reset DAC to virtual ground
    dacWrite(PIN_DAC_OUT, electrochemicalToDAC(0.0f));

    // If current > 0.05 µA, something is connected (electrodes in solution)
    // Open circuit would show essentially zero current (< 0.01 µA)
    bool present = (fabs(current) > 0.05f);

    Serial.print("[ELECTRODE] Test current: ");
    Serial.print(current, 4);
    Serial.print(" µA → ");
    Serial.println(present ? "PRESENT" : "NOT DETECTED");

    return present;
}

// ============================================================================
//  SEND STATUS REPORT
// ============================================================================

void sendStatusReport() {
    // Read sensors
    temperature = readTemperature();
    batteryVoltage = readBatteryVoltage();
    electrodePresent = checkElectrodePresence();

    // Calculate battery percentage (linear approximation: 3.0V=0%, 4.2V=100%)
    float battPct = constrain((batteryVoltage - 3.0f) / (4.2f - 3.0f) * 100.0f, 0.0f, 100.0f);

    // Build and send status message
    String status = "STATUS:" + String(stateNames[currentState]) + "\n";
    sendBLE(status);

    String meta = "META:temp=" + String(temperature, 1)
                + ",battery=" + String(batteryVoltage, 2)
                + ",battPct=" + String((int)battPct)
                + ",electrode=" + String(electrodePresent ? "YES" : "NO")
                + ",fw=" + String(FIRMWARE_VERSION)
                + ",hw=" + String(HARDWARE_REV)
                + "\n";
    sendBLE(meta);
}

// ============================================================================
//  PHYSICS-BASED SIMULATION ENGINE
// ============================================================================
//
//  When no electrodes are connected (or for demo purposes), we generate
//  realistic synthetic voltammograms based on electrochemical models.
//
//  The simulated DPV response consists of:
//  1. Baseline: exponential decay (capacitive current) + constant offset
//  2. Gaussian peaks: one per contaminant, centered at E_peak with width σ
//  3. Gaussian noise: random noise with specified SNR
//
//  This is physically motivated:
//  - The baseline represents non-faradaic (capacitive) current from the
//    electrochemical double layer. It's typically larger at negative
//    potentials and decays as the potential becomes more positive.
//  - The Gaussian peaks represent the faradaic current from each
//    electroactive species. DPV theory predicts symmetric peaks for
//    reversible systems (Gaussian is a good approximation).
//  - The noise represents electronic noise, thermal fluctuations,
//    and convective disturbances in the solution.

/*
 * Generate a pseudo-random number from a Gaussian distribution.
 * Uses the Box-Muller transform (pair generation method).
 *
 * We use the ESP32's hardware random number generator (esp_random())
 * for better randomness than rand().
 */
float gaussianRandom(float mean, float stddev) {
    // Box-Muller transform
    float u1 = (float)(esp_random() % 100000) / 100000.0f;
    float u2 = (float)(esp_random() % 100000) / 100000.0f;

    // Avoid log(0)
    if (u1 < 1e-10f) u1 = 1e-10f;

    float z = sqrtf(-2.0f * logf(u1)) * cosf(2.0f * M_PI * u2);
    return mean + stddev * z;
}

/*
 * Generate a simulated DPV voltammogram.
 *
 * Parameters:
 *   addContaminants - if true, add contaminant peaks; if false, clean water
 *
 * The simulation follows real electrochemistry:
 *
 * 1. Baseline (capacitive/charging current):
 *    I_baseline(E) = A × exp(-B × (E - E_start)) + C
 *    where A controls initial amplitude, B controls decay rate,
 *    C is the residual current at positive potentials.
 *    This models the charging current of the electrochemical double layer,
 *    which is largest when the potential changes rapidly and decays as the
 *    system reaches steady state.
 *
 * 2. Faradaic peaks (contaminant signals):
 *    I_peak(E) = I_max × exp(-0.5 × ((E - E_peak) / σ)²)
 *    This Gaussian shape comes from the DPV theory for reversible
 *    electron transfer (O'Dea, Osteryoung & Osteryoung, 1981).
 *    The peak current is proportional to concentration (Randles-Sevcik).
 *
 * 3. Noise:
 *    Gaussian random with σ_noise chosen for ~40 dB SNR.
 *    SNR = 20 × log10(I_peak / σ_noise)
 *    40 dB → I_peak / σ_noise = 100
 *    For I_peak ≈ 1 µA → σ_noise ≈ 0.01 µA
 */
void generateSimulatedVoltammogram(bool addContaminants) {
    dataPointCount = 0;

    // Baseline parameters (physically motivated)
    float baselineAmplitude = 0.15f;    // µA — initial capacitive current
    float baselineDecay     = 1.2f;     // V⁻¹ — exponential decay constant
    float baselineOffset    = 0.02f;    // µA — residual background current

    // Noise level for ~40 dB SNR relative to 1 µA peak
    // SNR = 20 × log10(signal / noise) = 40 → signal/noise = 100
    // With max peak ≈ 1 µA: noise σ ≈ 0.01 µA
    float noiseStdDev = 0.01f;

    for (int i = 0; i < DPV_NUM_POINTS && !scanAborted; i++) {
        float E = DPV_E_START + i * DPV_E_STEP;

        // 1. Baseline: exponential decay modeling double-layer charging
        float baseline = baselineAmplitude * expf(-baselineDecay * (E - DPV_E_START)) + baselineOffset;

        // 2. Sum of Gaussian peaks (faradaic currents from each contaminant)
        float faradaic = 0.0f;
        if (addContaminants) {
            for (int c = 0; c < NUM_CONTAMINANTS; c++) {
                float dE = E - contaminants[c].peakPotential;
                float sigma = contaminants[c].sigma;
                float peakI = contaminants[c].simPeakCurrent;
                faradaic += peakI * expf(-0.5f * (dE * dE) / (sigma * sigma));
            }
        }

        // 3. Gaussian noise (electronic + thermal)
        float noise = gaussianRandom(0.0f, noiseStdDev);

        // Total DPV current
        float totalCurrent = baseline + faradaic + noise;

        // Store data
        voltageArray[i] = E;
        currentArray[i] = totalCurrent;
        dataPointCount = i + 1;

        // Stream data point over BLE
        // Format: "V:voltage,I:current\n"
        // Voltage in mV (integer) for compact transmission, current in µA
        String dataPoint = "V:" + String(E, 4) + ",I:" + String(totalCurrent, 4) + "\n";
        sendBLE(dataPoint);

        // Pace the data to simulate real scan timing
        // Real DPV takes ~90 seconds for 450 points; we speed up for demo
        // but keep it slow enough to look real (~100ms per point = 45 seconds total)
        delay(50);  // 50ms per point → ~22 seconds for full scan (demo-friendly)
    }
}

// ============================================================================
//  REAL DPV SCAN (HARDWARE MODE)
// ============================================================================
//
//  This function performs an actual DPV scan using the ESP32 DAC and ADC
//  through the LM358 potentiostat circuit.
//
//  DPV Waveform Generation:
//
//  For each step in the linear ramp:
//    1. Set DAC to base potential E_base
//    2. Wait for (pulse_period - pulse_width) → let current settle
//    3. Sample current → i1 (pre-pulse current)
//    4. Set DAC to (E_base + pulse_amplitude) → apply pulse
//    5. Wait for pulse_width → let pulse current develop
//    6. Sample current → i2 (pulse current)
//    7. Calculate ΔI = i2 - i1 → this is the DPV signal
//    8. Reset DAC to E_base
//    9. Increment E_base by E_step
//
//  The differential measurement (i2 - i1) is the key innovation of DPV:
//  it cancels out the large, slowly-varying capacitive current while
//  preserving the rapidly-changing faradaic current from redox reactions.

void performRealDPVScan() {
    Serial.println("[DPV] Starting real potentiostat scan");
    Serial.print("[DPV] E_start="); Serial.print(DPV_E_START);
    Serial.print("V, E_end="); Serial.print(DPV_E_END);
    Serial.print("V, Points="); Serial.println(DPV_NUM_POINTS);

    dataPointCount = 0;
    scanStartTime = millis();

    // Send metadata before scan
    temperature = readTemperature();
    String meta = "META:temp=" + String(temperature, 1)
                + ",technique=DPV"
                + ",E_start=" + String(DPV_E_START, 3)
                + ",E_end=" + String(DPV_E_END, 3)
                + ",E_step=" + String(DPV_E_STEP * 1000, 1) + "mV"
                + ",pulse=" + String(DPV_PULSE_AMP * 1000, 1) + "mV"
                + ",points=" + String(DPV_NUM_POINTS)
                + "\n";
    sendBLE(meta);

    // Conditioning step: hold at E_start for 2 seconds
    // This pre-conditions the electrode surface and stabilizes the double layer
    dacWrite(PIN_DAC_OUT, electrochemicalToDAC(DPV_E_START));
    Serial.println("[DPV] Conditioning at E_start for 2 seconds...");
    delay(2000);

    // Main DPV loop
    for (int i = 0; i < DPV_NUM_POINTS && !scanAborted; i++) {
        float E_base = DPV_E_START + i * DPV_E_STEP;

        // Step 1: Set base potential
        dacWrite(PIN_DAC_OUT, electrochemicalToDAC(E_base));

        // Step 2: Wait for settling (pulse_period - pulse_width)
        // During this time, the double-layer charges to the new base potential
        delay(DPV_PULSE_PERIOD_MS - DPV_PULSE_WIDTH_MS);

        // Step 3: Sample pre-pulse current (i1)
        // This captures the baseline (mostly capacitive) current at E_base
        int adc_i1 = readADCOversampled(PIN_ADC_CURRENT);
        float i1 = adcToCurrent(adc_i1);

        // Step 4: Apply pulse (E_base + pulse_amplitude)
        float E_pulse = E_base + DPV_PULSE_AMP;
        dacWrite(PIN_DAC_OUT, electrochemicalToDAC(E_pulse));

        // Step 5: Wait for pulse duration
        // The pulse must be long enough for the faradaic current to develop
        // but short enough that the capacitive current has largely decayed
        delay(DPV_PULSE_WIDTH_MS);

        // Step 6: Sample pulse current (i2)
        int adc_i2 = readADCOversampled(PIN_ADC_CURRENT);
        float i2 = adcToCurrent(adc_i2);

        // Step 7: Calculate differential current
        // ΔI = i2 - i1
        // This cancels the capacitive component (which is ~equal at both
        // sample times) and isolates the faradaic component (which increases
        // during the pulse due to higher overpotential driving the reaction)
        float deltaI = i2 - i1;

        // Step 8: Return to base potential for next step
        dacWrite(PIN_DAC_OUT, electrochemicalToDAC(E_base));

        // Store data
        voltageArray[i] = E_base;
        currentArray[i] = deltaI;
        dataPointCount = i + 1;

        // Stream data point
        String dataPoint = "V:" + String(E_base, 4) + ",I:" + String(deltaI, 4) + "\n";
        sendBLE(dataPoint);

        // Progress update every 50 points
        if (i > 0 && i % 50 == 0) {
            float progress = (float)i / DPV_NUM_POINTS * 100.0f;
            Serial.print("[DPV] Progress: ");
            Serial.print(progress, 0);
            Serial.println("%");
        }
    }

    // Reset DAC to 0V (virtual ground)
    dacWrite(PIN_DAC_OUT, electrochemicalToDAC(0.0f));

    float scanTime = (millis() - scanStartTime) / 1000.0f;
    Serial.print("[DPV] Scan complete in ");
    Serial.print(scanTime, 1);
    Serial.println(" seconds");
}

// ============================================================================
//  SIGNAL PROCESSING: SAVITZKY-GOLAY SMOOTHING
// ============================================================================
//
//  The Savitzky-Golay filter fits a low-degree polynomial to successive
//  sub-sets of adjacent data points by the method of linear least squares.
//  For DPV, this is superior to simple moving average because it:
//    1. Preserves peak height (no amplitude reduction at narrow peaks)
//    2. Preserves peak position (no phase shift)
//    3. Preserves peak shape (symmetry maintained)
//
//  We use a 5-point quadratic window: coefficients = [-3, 12, 17, 12, -3] / 35
//
//  The filter acts as a low-pass with a sharper cutoff than a moving average,
//  effectively removing high-frequency noise while keeping the Gaussian
//  peak shapes intact.

void applySavitzkyGolay() {
    int halfWindow = SG_WINDOW / 2;  // = 2 for 5-point window

    for (int i = 0; i < dataPointCount; i++) {
        if (i < halfWindow || i >= dataPointCount - halfWindow) {
            // Edge points: no filtering (would need asymmetric coefficients)
            smoothedArray[i] = currentArray[i];
        } else {
            float sum = 0.0f;
            for (int j = 0; j < SG_WINDOW; j++) {
                sum += sgCoeffs[j] * currentArray[i - halfWindow + j];
            }
            smoothedArray[i] = sum;
        }
    }

    Serial.println("[DSP] Savitzky-Golay smoothing applied (5-point quadratic)");
}

// ============================================================================
//  SIGNAL PROCESSING: BASELINE ESTIMATION AND SUBTRACTION
// ============================================================================
//
//  DPV data sits on top of a non-faradaic baseline (capacitive current,
//  oxygen reduction, solvent window effects). To accurately measure peak
//  heights, we must estimate and subtract this baseline.
//
//  Method: Iterative morphological approach (simplified).
//  We estimate the baseline by finding the local minima envelope of the
//  smoothed data using a wide sliding window, then interpolate between
//  the minimum points. This works because faradaic peaks are localized
//  but the baseline varies slowly.
//
//  For a competition prototype, we use a simpler approach: fit a line
//  through the first and last ~20 points (where no peaks should be present)
//  and use that as the baseline. This assumes a roughly linear baseline,
//  which is a reasonable first approximation for DPV.

void estimateBaseline() {
    // Use endpoints of the voltammogram (where peaks are unlikely) to
    // establish a linear baseline estimate.
    //
    // We average the first N and last N points to reduce noise influence.

    const int N = 20;  // Number of points to average at each end

    float sumStart = 0.0f, sumEnd = 0.0f;

    for (int i = 0; i < N && i < dataPointCount; i++) {
        sumStart += smoothedArray[i];
    }
    float meanStart = sumStart / N;

    for (int i = dataPointCount - N; i < dataPointCount; i++) {
        if (i >= 0) sumEnd += smoothedArray[i];
    }
    float meanEnd = sumEnd / N;

    // Linear interpolation between start and end baselines
    for (int i = 0; i < dataPointCount; i++) {
        float fraction = (float)i / (float)(dataPointCount - 1);
        baselineArray[i] = meanStart + fraction * (meanEnd - meanStart);
    }

    // Subtract baseline from smoothed data (in-place in smoothedArray)
    for (int i = 0; i < dataPointCount; i++) {
        smoothedArray[i] -= baselineArray[i];
    }

    Serial.println("[DSP] Linear baseline subtracted");
    Serial.print("[DSP] Baseline at start: ");
    Serial.print(meanStart, 4);
    Serial.print(" µA, at end: ");
    Serial.print(meanEnd, 4);
    Serial.println(" µA");
}

// ============================================================================
//  SIGNAL PROCESSING: PEAK DETECTION
// ============================================================================
//
//  After smoothing and baseline subtraction, we detect peaks in the
//  processed voltammogram. A peak is defined as a local maximum that:
//    1. Is above a minimum threshold (to reject noise)
//    2. Has sufficient prominence (height above surrounding valleys)
//    3. Can be matched to a known contaminant potential (±tolerance)
//
//  For each detected peak, we:
//    - Record the potential and current
//    - Match to the nearest known contaminant (within ±50mV tolerance)
//    - Estimate concentration using the linear calibration curve

void detectPeaks() {
    numDetectedPeaks = 0;

    // Minimum threshold: reject peaks below 3σ of the noise floor
    // Noise σ ≈ 0.01 µA → threshold ≈ 0.03 µA
    float threshold = 0.03f;

    // Peak matching tolerance: ±50mV
    // This accounts for shifts due to pH, temperature, and electrode variability
    float potentialTolerance = 0.05f;

    for (int i = 2; i < dataPointCount - 2 && numDetectedPeaks < MAX_PEAKS; i++) {
        // Check for local maximum: point higher than its 2 neighbors on each side
        if (smoothedArray[i] > smoothedArray[i-1] &&
            smoothedArray[i] > smoothedArray[i+1] &&
            smoothedArray[i] > smoothedArray[i-2] &&
            smoothedArray[i] > smoothedArray[i+2] &&
            smoothedArray[i] > threshold) {

            // Refine peak position using parabolic interpolation
            // (fits a parabola through 3 points for sub-step resolution)
            float yL = smoothedArray[i-1];
            float yC = smoothedArray[i];
            float yR = smoothedArray[i+1];
            float xOffset = 0.5f * (yL - yR) / (yL - 2.0f * yC + yR);

            // Guard against division instability
            if (isnan(xOffset) || isinf(xOffset)) xOffset = 0.0f;
            xOffset = constrain(xOffset, -0.5f, 0.5f);

            float peakPotential = voltageArray[i] + xOffset * DPV_E_STEP;
            float peakCurrent = yC;  // Baseline-subtracted peak height

            // Try to match this peak to a known contaminant
            int bestMatch = -1;
            float bestDistance = potentialTolerance;

            for (int c = 0; c < NUM_CONTAMINANTS; c++) {
                float distance = fabs(peakPotential - contaminants[c].peakPotential);
                if (distance < bestDistance) {
                    bestDistance = distance;
                    bestMatch = c;
                }
            }

            // Calculate concentration if matched
            float concentration = 0.0f;
            if (bestMatch >= 0) {
                // Linear calibration: I_peak = slope × concentration + intercept
                // → concentration = (I_peak - intercept) / slope
                concentration = (peakCurrent - contaminants[bestMatch].calIntercept)
                              / contaminants[bestMatch].calSlope;
                if (concentration < 0.0f) concentration = 0.0f;
            }

            // Store peak
            detectedPeaks[numDetectedPeaks].potential = peakPotential;
            detectedPeaks[numDetectedPeaks].current = peakCurrent;
            detectedPeaks[numDetectedPeaks].contaminantIdx = bestMatch;
            detectedPeaks[numDetectedPeaks].concentration = concentration;
            numDetectedPeaks++;

            // Skip ahead to avoid detecting the same peak multiple times
            i += 3;

            // Log detection
            if (bestMatch >= 0) {
                Serial.print("[PEAK] Found ");
                Serial.print(contaminants[bestMatch].name);
                Serial.print(" at ");
                Serial.print(peakPotential, 3);
                Serial.print("V, I=");
                Serial.print(peakCurrent, 4);
                Serial.print(" µA, conc=");
                Serial.print(concentration, 2);
                Serial.print(" ");
                Serial.println(contaminants[bestMatch].unit);
            } else {
                Serial.print("[PEAK] Unknown peak at ");
                Serial.print(peakPotential, 3);
                Serial.print("V, I=");
                Serial.print(peakCurrent, 4);
                Serial.println(" µA");
            }
        }
    }

    Serial.print("[PEAK] Total peaks detected: ");
    Serial.println(numDetectedPeaks);
}

// ============================================================================
//  RESULT REPORTING
// ============================================================================
//
//  After analysis, send a concise result string over BLE.
//  Format: "RESULT:Pb=15.2ppb,As=8.1ppb,NH3=1.8mg/L,NO3=12.5mg/L,Fe=0.8mg/L\n"
//
//  Also send WHO limit exceedances as warnings.

void sendResults() {
    // Build result string
    String result = "RESULT:";
    bool first = true;

    for (int i = 0; i < numDetectedPeaks; i++) {
        int ci = detectedPeaks[i].contaminantIdx;
        if (ci >= 0) {
            if (!first) result += ",";
            result += String(contaminants[ci].symbol)
                    + "=" + String(detectedPeaks[i].concentration, 1)
                    + String(contaminants[ci].unit);
            first = false;
        }
    }

    if (first) {
        // No contaminants detected
        result += "CLEAN";
    }
    result += "\n";
    sendBLE(result);

    // Send WHO limit warnings
    for (int i = 0; i < numDetectedPeaks; i++) {
        int ci = detectedPeaks[i].contaminantIdx;
        if (ci >= 0) {
            float ratio = detectedPeaks[i].concentration / contaminants[ci].whoLimit;
            if (ratio > 1.0f) {
                String warning = "WARNING:" + String(contaminants[ci].name)
                               + " at " + String(detectedPeaks[i].concentration, 1)
                               + " " + String(contaminants[ci].unit)
                               + " EXCEEDS WHO limit of "
                               + String(contaminants[ci].whoLimit, 1)
                               + " " + String(contaminants[ci].unit)
                               + " (" + String(ratio, 1) + "x)\n";
                sendBLE(warning);
            }
        }
    }
}

// ============================================================================
//  COMPLETE SCAN PIPELINE
// ============================================================================
//
//  The full analysis pipeline mirrors what a laboratory potentiostat does:
//    1. Acquire raw voltammogram (real or simulated)
//    2. Smooth the raw data (Savitzky-Golay)
//    3. Estimate and subtract baseline
//    4. Detect peaks (local maxima above threshold)
//    5. Identify contaminants (potential matching)
//    6. Quantify concentrations (calibration curves)
//    7. Report results

void runFullAnalysisPipeline() {
    Serial.println("[ANALYSIS] Running full signal processing pipeline...");
    Serial.print("[ANALYSIS] Data points: ");
    Serial.println(dataPointCount);

    if (dataPointCount < SG_WINDOW) {
        sendBLE("ERROR:Insufficient data points for analysis\n");
        return;
    }

    // Step 1: Savitzky-Golay smoothing
    applySavitzkyGolay();

    // Step 2: Baseline estimation and subtraction
    estimateBaseline();

    // Step 3: Peak detection, identification, and quantification
    detectPeaks();

    // Step 4: Send results
    sendResults();

    // Step 5: Send metadata with scan parameters
    temperature = readTemperature();
    String meta = "META:temp=" + String(temperature, 1)
                + ",ph=7.1"   // Placeholder — would need pH sensor for real value
                + ",tds=340"  // Placeholder — would need TDS sensor for real value
                + "\n";
    sendBLE(meta);
}

// ============================================================================
//  CALIBRATION ROUTINE
// ============================================================================
//
//  Calibration in a full system would involve:
//  1. Running a blank (clean water) to establish baseline
//  2. Running standards of known concentration for each analyte
//  3. Constructing calibration curves (current vs concentration)
//
//  For this competition prototype, we perform a simplified calibration:
//  - Run a quick scan to check noise floor
//  - Verify DAC/ADC linearity
//  - Check electrode condition
//  - Report system health

void performCalibration() {
    Serial.println("[CAL] Starting calibration routine...");

    sendBLE("CAL:Starting calibration...\n");

    // Step 1: DAC/ADC linearity check
    // Sweep DAC across range and verify ADC follows
    sendBLE("CAL:Checking DAC/ADC linearity...\n");

    int linErrors = 0;
    for (int dacVal = 50; dacVal <= 200 && !scanAborted; dacVal += 30) {
        dacWrite(PIN_DAC_OUT, dacVal);
        delay(50);

        int adcVal = readADCOversampled(PIN_ADC_CURRENT);
        float expectedV = (float)dacVal * DAC_MAX_VOLTAGE / DAC_RESOLUTION;
        float measuredV = (float)adcVal * ADC_VREF / ADC_RESOLUTION;

        // In a potentiostat circuit, the relationship between DAC and ADC
        // is not direct (it goes through the electrochemical cell), but
        // without electrodes, the TIA output should be near Vref
        Serial.print("[CAL] DAC=");
        Serial.print(dacVal);
        Serial.print(" (");
        Serial.print(expectedV, 2);
        Serial.print("V), ADC=");
        Serial.print(adcVal);
        Serial.print(" (");
        Serial.print(measuredV, 2);
        Serial.println("V)");

        String calPoint = "CAL:DAC=" + String(dacVal)
                        + ",ADC=" + String(adcVal)
                        + "\n";
        sendBLE(calPoint);

        delay(100);
    }

    // Reset DAC
    dacWrite(PIN_DAC_OUT, electrochemicalToDAC(0.0f));

    // Step 2: Noise floor measurement
    sendBLE("CAL:Measuring noise floor...\n");
    Serial.println("[CAL] Measuring noise floor at Vref...");

    dacWrite(PIN_DAC_OUT, electrochemicalToDAC(0.0f));
    delay(200);

    float noiseSum = 0.0f;
    float noiseSumSq = 0.0f;
    const int NOISE_SAMPLES = 100;

    for (int i = 0; i < NOISE_SAMPLES && !scanAborted; i++) {
        int adcVal = readADCOversampled(PIN_ADC_CURRENT);
        float current = adcToCurrent(adcVal);
        noiseSum += current;
        noiseSumSq += current * current;
        delay(10);
    }

    float noiseMean = noiseSum / NOISE_SAMPLES;
    float noiseVar = (noiseSumSq / NOISE_SAMPLES) - (noiseMean * noiseMean);
    float noiseStd = sqrtf(fabs(noiseVar));

    Serial.print("[CAL] Noise floor: mean=");
    Serial.print(noiseMean, 4);
    Serial.print(" µA, σ=");
    Serial.print(noiseStd, 4);
    Serial.println(" µA");

    String noiseResult = "CAL:noise_mean=" + String(noiseMean, 4)
                       + ",noise_std=" + String(noiseStd, 4)
                       + " µA\n";
    sendBLE(noiseResult);

    // Step 3: Electrode check
    sendBLE("CAL:Checking electrodes...\n");
    electrodePresent = checkElectrodePresence();

    String electrodeResult = "CAL:electrode=" + String(electrodePresent ? "PRESENT" : "NOT_FOUND") + "\n";
    sendBLE(electrodeResult);

    // Step 4: Temperature
    temperature = readTemperature();
    String tempResult = "CAL:temperature=" + String(temperature, 1) + "°C\n";
    sendBLE(tempResult);

    // Final calibration report
    String calSummary = "CAL:COMPLETE";
    calSummary += ",noise=" + String(noiseStd, 4);
    calSummary += ",electrode=" + String(electrodePresent ? "OK" : "MISSING");
    calSummary += ",temp=" + String(temperature, 1);
    calSummary += ",status=" + String(noiseStd < 0.05f ? "PASS" : "NOISE_HIGH");
    calSummary += "\n";
    sendBLE(calSummary);

    Serial.println("[CAL] Calibration complete");
}

// ============================================================================
//  LED MANAGEMENT
// ============================================================================
//
//  Non-blocking LED patterns using millis() instead of delay().
//  This ensures BLE communication isn't blocked by LED animation.
//
//  Patterns:
//    SLOW_BLINK:   500ms on, 500ms off (1 Hz) — waiting for connection
//    SOLID:        Always on — connected and idle
//    FAST_BLINK:   125ms on, 125ms off (4 Hz) — scanning
//    DOUBLE_BLINK: Two quick flashes, then pause — error

void updateLED() {
    unsigned long now = millis();

    switch (currentLEDPattern) {
        case LED_OFF:
            digitalWrite(PIN_LED, LOW);
            break;

        case LED_SLOW_BLINK:
            // 1 Hz blink (500ms period)
            if (now - lastLEDToggle >= 500) {
                ledState = !ledState;
                digitalWrite(PIN_LED, ledState ? HIGH : LOW);
                lastLEDToggle = now;
            }
            break;

        case LED_SOLID:
            digitalWrite(PIN_LED, HIGH);
            break;

        case LED_FAST_BLINK:
            // 4 Hz blink (125ms period)
            if (now - lastLEDToggle >= 125) {
                ledState = !ledState;
                digitalWrite(PIN_LED, ledState ? HIGH : LOW);
                lastLEDToggle = now;
            }
            break;

        case LED_DOUBLE_BLINK:
            // Double blink pattern: ON-OFF-ON-OFF----ON-OFF-ON-OFF----
            // Phase 0: ON (100ms)  Phase 1: OFF (100ms)
            // Phase 2: ON (100ms)  Phase 3: OFF (600ms) → repeat
            if (now - lastLEDToggle >= (doubleBLinkPhase == 3 ? 600 : 100)) {
                doubleBLinkPhase = (doubleBLinkPhase + 1) % 4;
                bool on = (doubleBLinkPhase == 0 || doubleBLinkPhase == 2);
                digitalWrite(PIN_LED, on ? HIGH : LOW);
                lastLEDToggle = now;
            }
            break;
    }
}

// ============================================================================
//  BLE RECONNECTION HANDLING
// ============================================================================
//
//  When a client disconnects, we need to restart BLE advertising so
//  the device becomes discoverable again. The ESP32 BLE stack requires
//  a short delay after disconnect before restarting advertising.

void handleBLEReconnection() {
    // Client just disconnected
    if (!deviceConnected && oldDeviceConnected) {
        delay(500);  // Give the BLE stack time to clean up
        pServer->startAdvertising();
        Serial.println("[BLE] Restarted advertising after disconnect");
        oldDeviceConnected = false;
    }

    // Client just connected
    if (deviceConnected && !oldDeviceConnected) {
        oldDeviceConnected = true;
        Serial.println("[BLE] New client session established");

        // Send welcome message with device info
        String welcome = "STATUS:IDLE\n";
        sendBLE(welcome);
        sendStatusReport();
    }
}

// ============================================================================
//  STATE MACHINE EXECUTION
// ============================================================================
//
//  The main state machine processes the current state each loop iteration.
//  Scan operations run to completion (they have their own internal loops
//  with abort checks), then return to IDLE.

void processStateMachine() {
    switch (currentState) {
        case STATE_IDLE:
            // Nothing to do — waiting for BLE commands
            break;

        case STATE_SCANNING:
            // Real DPV scan using hardware DAC/ADC
            Serial.println("[SM] Entering SCANNING state");
            performRealDPVScan();

            if (!scanAborted) {
                // Run signal processing pipeline
                runFullAnalysisPipeline();
                sendBLE("SCAN_COMPLETE\n");
                Serial.println("[SM] Scan completed successfully");
            } else {
                sendBLE("STATUS:ABORTED\n");
                Serial.println("[SM] Scan was aborted");
            }

            currentState = STATE_IDLE;
            currentLEDPattern = deviceConnected ? LED_SOLID : LED_SLOW_BLINK;
            break;

        case STATE_DEMO_CLEAN:
            // Simulated clean water voltammogram
            Serial.println("[SM] Entering DEMO_CLEAN state");
            sendBLE("META:mode=DEMO_CLEAN,sample=Clean_Water\n");
            generateSimulatedVoltammogram(false);  // No contaminant peaks

            if (!scanAborted) {
                runFullAnalysisPipeline();
                sendBLE("SCAN_COMPLETE\n");
                Serial.println("[SM] Demo clean scan completed");
            } else {
                sendBLE("STATUS:ABORTED\n");
            }

            currentState = STATE_IDLE;
            currentLEDPattern = deviceConnected ? LED_SOLID : LED_SLOW_BLINK;
            break;

        case STATE_DEMO_CONTAMINATED:
            // Simulated contaminated water voltammogram
            Serial.println("[SM] Entering DEMO_CONTAMINATED state");
            sendBLE("META:mode=DEMO_CONTAMINATED,sample=Contaminated_Water\n");
            generateSimulatedVoltammogram(true);  // With contaminant peaks

            if (!scanAborted) {
                runFullAnalysisPipeline();
                sendBLE("SCAN_COMPLETE\n");
                Serial.println("[SM] Demo contaminated scan completed");
            } else {
                sendBLE("STATUS:ABORTED\n");
            }

            currentState = STATE_IDLE;
            currentLEDPattern = deviceConnected ? LED_SOLID : LED_SLOW_BLINK;
            break;

        case STATE_CALIBRATING:
            Serial.println("[SM] Entering CALIBRATING state");
            performCalibration();

            if (!scanAborted) {
                sendBLE("STATUS:IDLE\n");
                Serial.println("[SM] Calibration completed");
            } else {
                sendBLE("STATUS:ABORTED\n");
            }

            currentState = STATE_IDLE;
            currentLEDPattern = deviceConnected ? LED_SOLID : LED_SLOW_BLINK;
            break;

        case STATE_ERROR:
            // Error state — set LED pattern and wait for user to send a command
            currentLEDPattern = LED_DOUBLE_BLINK;

            // Auto-recover after 10 seconds
            static unsigned long errorStartTime = 0;
            if (errorStartTime == 0) errorStartTime = millis();
            if (millis() - errorStartTime > 10000) {
                currentState = STATE_IDLE;
                currentLEDPattern = deviceConnected ? LED_SOLID : LED_SLOW_BLINK;
                errorStartTime = 0;
                Serial.println("[SM] Auto-recovered from error state");
                sendBLE("STATUS:IDLE\n");
            }
            break;
    }
}

// ============================================================================
//  ARDUINO SETUP
// ============================================================================

void setup() {
    // ---- Serial for debugging ----
    Serial.begin(115200);
    delay(500);

    Serial.println();
    Serial.println("============================================");
    Serial.println("  JalSakhi — Water Forensics Potentiostat  ");
    Serial.println("============================================");
    Serial.print("  Firmware: v");
    Serial.println(FIRMWARE_VERSION);
    Serial.print("  Hardware: ");
    Serial.println(HARDWARE_REV);
    Serial.print("  DPV Points: ");
    Serial.println(DPV_NUM_POINTS);
    Serial.print("  Scan Time (real): ~");
    Serial.print(DPV_SCAN_TIME_S, 0);
    Serial.println(" seconds");
    Serial.print("  Free heap: ");
    Serial.print(ESP.getFreeHeap());
    Serial.println(" bytes");
    Serial.println("============================================");
    Serial.println();

    // ---- GPIO setup ----
    pinMode(PIN_LED, OUTPUT);
    digitalWrite(PIN_LED, LOW);
    pinMode(PIN_ELECTRODE_DET, INPUT_PULLUP);

    // ---- ADC Configuration ----
    // Set ADC resolution to 12 bits (0–4095)
    analogReadResolution(12);
    // Set ADC attenuation to 11dB for full 0–3.3V range
    // (default is 0dB which only reads 0–1.1V)
    analogSetAttenuation(ADC_11db);

    // ---- DAC Configuration ----
    // Initialize DAC to virtual ground (1.65V = 0V electrochemical)
    dacWrite(PIN_DAC_OUT, electrochemicalToDAC(0.0f));
    Serial.print("[INIT] DAC set to virtual ground (");
    Serial.print(electrochemicalToDAC(0.0f));
    Serial.println("/255)");

    // ---- Initial sensor readings ----
    temperature = readTemperature();
    batteryVoltage = readBatteryVoltage();
    electrodePresent = checkElectrodePresence();

    Serial.print("[INIT] Temperature: ");
    Serial.print(temperature, 1);
    Serial.println(" °C");
    Serial.print("[INIT] Battery: ");
    Serial.print(batteryVoltage, 2);
    Serial.println(" V");
    Serial.print("[INIT] Electrodes: ");
    Serial.println(electrodePresent ? "DETECTED" : "NOT DETECTED");

    // ---- BLE Initialization ----
    Serial.println("[BLE] Initializing Bluetooth Low Energy...");

    BLEDevice::init(DEVICE_NAME);

    // Create BLE Server
    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new ServerCallbacks());

    // Create BLE Service
    BLEService* pService = pServer->createService(SERVICE_UUID);

    // Create TX Characteristic (for sending data to phone)
    // Properties: NOTIFY — the phone subscribes and we push data
    pTxCharacteristic = pService->createCharacteristic(
        TX_CHAR_UUID,
        BLECharacteristic::PROPERTY_NOTIFY
    );
    // Add Client Characteristic Configuration Descriptor (CCCD)
    // This is required for NOTIFY to work — the client enables/disables
    // notifications by writing to this descriptor
    pTxCharacteristic->addDescriptor(new BLE2902());

    // Create RX Characteristic (for receiving commands from phone)
    // Properties: WRITE — the phone sends commands as writes
    pRxCharacteristic = pService->createCharacteristic(
        RX_CHAR_UUID,
        BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR
    );
    pRxCharacteristic->setCallbacks(new RxCallbacks());

    // Start the service
    pService->start();

    // Start advertising
    BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->setScanResponse(true);
    // These settings help with iPhone connectivity:
    pAdvertising->setMinPreferred(0x06);  // Functions that help with iPhone connections
    pAdvertising->setMinPreferred(0x12);
    BLEDevice::startAdvertising();

    Serial.println("[BLE] Advertising started as \"" DEVICE_NAME "\"");
    Serial.println("[BLE] Service UUID: " SERVICE_UUID);
    Serial.println("[BLE] TX UUID:      " TX_CHAR_UUID);
    Serial.println("[BLE] RX UUID:      " RX_CHAR_UUID);
    Serial.println();
    Serial.println("[READY] JalSakhi potentiostat ready. Waiting for BLE connection...");
    Serial.println("[READY] Commands: START_SCAN | DEMO_CLEAN | DEMO_CONTAMINATED | STOP | STATUS | CALIBRATE");
    Serial.println();

    // Start with slow blink (advertising)
    currentLEDPattern = LED_SLOW_BLINK;
}

// ============================================================================
//  ARDUINO MAIN LOOP
// ============================================================================
//
//  The main loop handles three things:
//    1. LED animation (non-blocking pattern updates)
//    2. BLE reconnection (restart advertising after disconnect)
//    3. State machine execution (process commands and run scans)
//
//  The loop runs at ~100 Hz when idle (10ms delay), which is fast enough
//  for responsive BLE communication and smooth LED animation.

void loop() {
    // ---- 1. Update LED pattern ----
    updateLED();

    // ---- 2. Handle BLE connection changes ----
    handleBLEReconnection();

    // ---- 3. Process state machine ----
    // This is where the actual work happens.
    // When idle, this is a no-op and returns immediately.
    // When scanning, this blocks until the scan completes or is aborted.
    processStateMachine();

    // ---- 4. Periodic status (every 30 seconds while idle) ----
    if (currentState == STATE_IDLE && deviceConnected) {
        if (millis() - lastStatusSend > 30000) {
            // Send periodic heartbeat so the app knows we're still alive
            sendBLE("STATUS:IDLE\n");
            lastStatusSend = millis();
        }
    }

    // Small delay to prevent WDT (watchdog timer) reset
    // The ESP32 has a task watchdog that triggers if the main loop doesn't
    // yield. This delay also prevents excessive CPU usage when idle.
    delay(10);
}

// ============================================================================
//  END OF FIRMWARE
// ============================================================================
//
//  Summary of what this firmware does:
//
//  1. Boots up, initializes BLE as "JalSakhi-Potentiostat"
//  2. Blinks LED slowly while waiting for a phone to connect
//  3. On connection: LED goes solid, sends welcome + status
//  4. Accepts commands over BLE:
//     - START_SCAN:         Real DPV using hardware DAC/ADC
//     - DEMO_CLEAN:         Simulated clean water (no peaks)
//     - DEMO_CONTAMINATED:  Simulated dirty water (5 peaks)
//     - STOP:               Abort current operation
//     - STATUS:             Report device status
//     - CALIBRATE:          Check DAC/ADC + noise + electrodes
//  5. During scan: streams V,I data points over BLE in real-time
//  6. After scan: runs signal processing pipeline
//     - Savitzky-Golay smoothing (preserves peak shape)
//     - Linear baseline subtraction
//     - Peak detection (local maxima above threshold)
//     - Contaminant identification (potential matching ±50mV)
//     - Concentration estimation (linear calibration curves)
//  7. Sends results: concentrations + WHO limit warnings
//  8. Returns to idle, ready for next scan
//
//  Total code size: fits well within ESP32's 4MB flash
//  RAM usage: ~20 KB for data buffers (out of 320 KB available)
//
//  For the competition demo:
//    - Use DEMO_CONTAMINATED to show impressive real-time voltammogram
//    - Use DEMO_CLEAN to show what clean water looks like
//    - Use START_SCAN with actual electrodes in water for live demo
//    - The Flutter app renders the voltammogram as data streams in
//
// ============================================================================
