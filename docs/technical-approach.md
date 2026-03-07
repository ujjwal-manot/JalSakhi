# Technical Approach

## System Overview

JalSakhi is an end-to-end water quality monitoring system with three main components:
1. **IoT Sensor Node** — hardware that measures water quality
2. **Mobile Application** — user interface for women/household users
3. **AI Backend** — cloud-based intelligence layer

---

## 1. IoT Sensor Node (ESP32-based)

### Sensors
| Parameter | Sensor | Range | Accuracy | Interface |
|-----------|--------|-------|----------|-----------|
| pH | SEN0161 (DFRobot) | 0-14 | +/- 0.1 | Analog |
| TDS | SEN0244 (DFRobot) | 0-1000 ppm | +/- 10% | Analog |
| Turbidity | SEN0189 (DFRobot) | 0-3000 NTU | +/- 5% | Analog |
| Ammonia | MQ-137 | 5-200 ppm | +/- 10% | Analog |
| Temperature | DS18B20 | -55 to 125C | +/- 0.5C | Digital |

### Communication
- **WiFi** (primary) — ESP32 built-in WiFi for home networks
- **BLE** (fallback) — Bluetooth Low Energy for direct phone connection
- Data is sent every 30 seconds during active monitoring

### Power
- USB-C powered (5V, 500mA)
- Optional: 18650 Li-ion battery for portable use
- Deep sleep mode when not actively testing (~10uA)

### Enclosure
- 3D-printed waterproof case
- Probe-style sensor assembly that dips into water
- LED indicator (RGB) for quick status: Green/Yellow/Red

---

## 2. Mobile Application

### Tech Stack
- **Framework**: Flutter (cross-platform Android + iOS)
- **State Management**: Provider / Riverpod
- **Local DB**: SQLite (offline data storage)
- **Charts**: fl_chart package
- **BLE**: flutter_blue_plus
- **Voice/TTS**: flutter_tts (local language support)

### Key Screens
1. **Dashboard** — Current water quality with color-coded indicators
2. **History** — Trends over time with graphs
3. **Alerts** — Push notifications for unsafe water
4. **Community Map** — Crowdsourced water quality heatmap
5. **Learn** — Educational content on water safety
6. **Water Tracker** — Household water consumption tracking

### Offline Support
- App works offline via BLE connection to sensor
- Data syncs to cloud when internet is available
- Critical alerts work without internet

### Accessibility
- Large, clear icons and color codes
- Voice alerts in 8+ Indian languages
- Minimal text — relies on visual indicators
- Works on Android 8+ (covers 95%+ of devices in India)

---

## 3. AI/ML Backend

### Tech Stack
- **API**: FastAPI (Python)
- **ML Framework**: scikit-learn + TensorFlow Lite
- **Database**: PostgreSQL + TimescaleDB (time-series)
- **Message Queue**: Redis
- **Deployment**: Docker + AWS/GCP

### ML Models

#### Model 1: Anomaly Detection
- **Purpose**: Detect unusual water quality readings
- **Algorithm**: Isolation Forest / Local Outlier Factor
- **Input**: pH, TDS, turbidity, ammonia, temperature
- **Output**: Anomaly score (0-1) + alert flag
- **Training**: Historical water quality data + synthetic contamination events

#### Model 2: Contamination Prediction
- **Purpose**: Predict future contamination based on trends
- **Algorithm**: LSTM / Prophet time-series forecasting
- **Input**: 7-day historical readings + weather data + seasonal patterns
- **Output**: Predicted contamination probability for next 24-48 hours
- **Use case**: "Ammonia levels may rise tomorrow due to upstream activity"

#### Model 3: Source Quality Ranking
- **Purpose**: Rank water sources by safety for community routing
- **Algorithm**: Multi-criteria scoring + collaborative filtering
- **Input**: Crowdsourced quality data from multiple users
- **Output**: Ranked list of safe water sources nearby
- **Use case**: "Nearest safe water source is 200m north at community well"

### Data Pipeline
```
Sensor Data --> API Gateway --> Validation --> TimescaleDB
                                    |
                                    v
                              ML Pipeline
                                    |
                            +---------+---------+
                            |         |         |
                         Anomaly  Prediction  Ranking
                            |         |         |
                            v         v         v
                              Alert Engine
                                    |
                                    v
                            Push Notifications
```

---

## 4. Water Quality Standards Reference

| Parameter | WHO Guideline | BIS (India) | Our Alert Threshold |
|-----------|--------------|-------------|-------------------|
| pH | 6.5 - 8.5 | 6.5 - 8.5 | < 6.5 or > 8.5 |
| TDS | < 600 ppm | < 500 ppm | > 500 ppm |
| Turbidity | < 4 NTU | < 5 NTU | > 4 NTU |
| Ammonia | < 0.5 mg/L | < 0.5 mg/L | > 0.3 mg/L (early warning) |
| Temperature | - | - | > 30C (bacterial growth risk) |

---

## 5. Ammonia Mitigation Strategies (Category 1)

When ammonia is detected above threshold, JalSakhi recommends:

1. **Immediate** (< 1 mg/L):
   - Boil water for 5 minutes
   - Use activated carbon filter

2. **Moderate** (1-3 mg/L):
   - Breakpoint chlorination (dosage calculated by AI based on ammonia level)
   - Ion exchange filtration
   - Do not use for drinking without treatment

3. **Severe** (> 3 mg/L):
   - Do NOT consume
   - Alert community and local authorities
   - Suggest alternative safe water sources from community map

---

## 6. Water Neutrality Tracking (Category 2)

### How it works
- User logs daily water consumption (with smart estimation)
- App tracks water-saving actions:
  - Rainwater harvested (estimated from roof area + rainfall data)
  - Greywater reused
  - Water-efficient practices
- **Water Neutrality Score** = Water Offset / Water Consumed x 100%
- Gamification: badges, streaks, community leaderboard

---

## 7. Cost Analysis at Scale

| Component | Unit Cost (prototype) | Unit Cost (1000 units) |
|-----------|----------------------|----------------------|
| ESP32 | $3.00 | $1.50 |
| pH Sensor | $2.00 | $1.00 |
| TDS Sensor | $1.50 | $0.80 |
| Turbidity | $2.00 | $1.00 |
| Ammonia | $3.00 | $1.50 |
| PCB + Assembly | $2.00 | $0.50 |
| Enclosure | $1.50 | $0.30 |
| **Total** | **$15.00** | **$6.60** |

Target retail price at scale: **< INR 500 (~$6)**
