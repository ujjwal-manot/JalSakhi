# JalSakhi - AI-Powered Affordable Water Quality Monitor

## Competition: World Water Day 2026 - "Water and Gender"

### Theme
"Water is Life!" — Access to safe water is essential for healthy communities. Women and girls are primarily responsible for collecting and managing water in many parts of the world. Limited access to safe water and sanitation affects their health, education, and opportunities.

---

## Problem Statement Categories

| # | Category | Selected |
|---|----------|----------|
| 1 | Mitigations/offset strategies for Ammonia in drinking water | Integrated |
| 2 | Technologies for Water Neutrality in household | Integrated |
| 3 | Integrating smart technologies in water distribution and carrier systems | Integrated |
| 4 | Affordable household water quality sensing and filtration | Primary |
| 5 | AI Driven Water management | Primary |

**Our approach combines Categories 4 + 5 as primary focus, integrating elements from 1, 2, and 3.**

---

## Our Solution: JalSakhi

**"JalSakhi"** (meaning "Water Friend" in Hindi) — An AI-Powered Affordable Water Quality Monitor designed for women-led households.

### Core Concept
- A low-cost IoT sensor kit (< $5 per unit at scale) that tests water for ammonia, pH, TDS, and turbidity
- Connected to a mobile app (works on basic smartphones) with AI-driven insights in local languages
- Specifically designed for women as primary water managers — simple UI, voice alerts, community sharing
- AI predicts contamination patterns using crowdsourced data from multiple households

### Why This Wins
1. **Gender angle is baked in** — women collect/manage water; this tool empowers them with data
2. **Technically feasible** — Arduino/ESP32 + cheap sensors + a simple ML model
3. **Demonstrable** — working prototype can be shown
4. **Scalable** — cloud-based AI improves with more users
5. **Multi-category coverage** — sensing, filtration guidance, AI, ammonia detection

---

## Hardware Components

| Component | Technology | Approx. Cost |
|-----------|-----------|-------------|
| Microcontroller | ESP32 | ~$3 |
| pH Sensor | Analog pH module | ~$2 |
| TDS Sensor | TDS meter probe | ~$1.50 |
| Turbidity Sensor | Infrared turbidity module | ~$2 |
| Ammonia Detection | MQ-137 gas sensor or colorimetric strip reader | ~$3 |
| **Total per unit** | | **~$11.50** |

## Software Stack

| Component | Technology |
|-----------|-----------|
| Firmware | Arduino C++ (ESP32) |
| Mobile App | Flutter / React Native |
| Backend API | Python (FastAPI) |
| AI/ML Model | TensorFlow Lite / Anomaly Detection |
| Database | Firebase / PostgreSQL |
| Cloud | AWS IoT / Google Cloud IoT |

---

## Key Features

### 1. Real-Time Water Quality Monitoring
- Continuous monitoring of pH, TDS, turbidity, and ammonia levels
- Instant alerts when parameters exceed safe limits (WHO/BIS standards)

### 2. AI-Driven Insights
- Predictive contamination alerts based on historical data patterns
- Seasonal trend analysis (monsoon contamination spikes, etc.)
- Community-level heatmaps showing water quality across regions

### 3. Women-Centric Design
- Voice-based alerts in local languages (Hindi, Tamil, Bengali, etc.)
- Simple color-coded UI (Green/Yellow/Red) for quick understanding
- Community sharing — women can share water quality data with neighbors
- Educational tips on water purification methods

### 4. Ammonia Mitigation (Category 1)
- Real-time ammonia level detection in drinking water
- AI-suggested mitigation strategies (boiling, chlorination dosage, activated carbon)
- Alert system when ammonia exceeds 0.5 mg/L (WHO guideline)

### 5. Water Neutrality Tracking (Category 2)
- Tracks household water consumption vs. recycled/harvested water
- Gamification — earn "water credits" for conservation
- Tips for greywater reuse and rainwater harvesting

### 6. Smart Distribution Insights (Category 3)
- Crowdsourced data creates a water quality map for the community
- Identifies optimal water sources for collection
- Reduces time women spend collecting water by routing to nearest safe source

---

## Architecture

```
[Sensors] --> [ESP32] --> [WiFi/BLE] --> [Mobile App]
                                             |
                                             v
                                      [Cloud Backend]
                                             |
                                             v
                                      [AI/ML Pipeline]
                                             |
                                             v
                                    [Predictions & Alerts]
```

---

## Project Structure

```
JalSakhi/
├── README.md                 # This file
├── docs/                     # Documentation and research
│   └── competition-brief.md  # Competition details
├── hardware/                 # Hardware schematics and firmware
│   ├── schematics/           # Circuit diagrams
│   └── firmware/             # ESP32 Arduino code
├── app/                      # Mobile application
│   ├── android/
│   └── ios/
├── backend/                  # Backend API server
│   ├── api/
│   └── ml/                   # AI/ML models
├── data/                     # Sample/training data
└── presentation/             # Pitch deck and demo materials
```

---

## Development Roadmap

### Phase 1: Prototype (Week 1-2)
- [ ] Assemble sensor hardware on breadboard
- [ ] Write ESP32 firmware for sensor data collection
- [ ] Basic mobile app with real-time data display
- [ ] Simple threshold-based alerts

### Phase 2: AI Integration (Week 3)
- [ ] Collect/generate training data
- [ ] Build anomaly detection model
- [ ] Integrate ML predictions into app
- [ ] Add voice alerts in local languages

### Phase 3: Polish & Present (Week 4)
- [ ] Design pitch deck
- [ ] Record demo video
- [ ] Prepare documentation
- [ ] Practice presentation

---

## Team

- **Project Lead**: Ujjwal

---

## License

MIT License
