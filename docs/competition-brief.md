# Competition Strategy

## Event: World Water Day 2026 Challenge
## Theme: "Water and Gender"

---

## How We Cover ALL 5 Categories

Most teams pick one category. We cover all five with one unified platform.

### Category 1: Ammonia Mitigation
- **Our answer**: Electrochemical detection via SWV on Prussian Blue-modified SPE
- Detection limit: 0.05 mg/L (10x more sensitive than WHO guideline of 0.5 mg/L)
- AI-generated mitigation protocol based on concentration level:
  - < 0.5 mg/L → safe, no action
  - 0.5-1.5 mg/L → breakpoint chlorination (dosage calculated from exact concentration)
  - 1.5-3.0 mg/L → activated carbon + aeration
  - > 3.0 mg/L → do not consume, alert community, notify municipality
- Ammonia source attribution from spatial mapping (agricultural runoff vs sewage vs industrial)

### Category 2: Water Neutrality
- Community-level water budgeting from consumption surveys + rainfall data
- Track conservation impact: how much contaminated water was AVOIDED by informed source selection
- Water savings quantified per SHG (equivalent to X hours of women's labor saved)

### Category 3: Smart Distribution
- Crowdsourced contamination data maps the entire distribution network
- Identifies which pipeline segments introduce contamination
- Leak-related contamination detection (chlorine residual drops = potential intrusion)
- Optimal collection routing: shortest path to safest water source

### Category 4: Affordable Sensing & Filtration
- $10-15 reusable potentiostat dongle + $0.30 disposable electrodes
- Detects 7+ contaminants including heavy metals at ppb
- Colorimetric strip mode requires ZERO hardware (just phone + strips)
- Orders of magnitude cheaper than lab testing

### Category 5: AI Water Management
- Edge AI: 1D-CNN classifies voltammograms on-device
- Cloud AI: Spatial interpolation (Kriging), temporal forecasting (LSTM), anomaly detection
- Municipal decision support dashboard
- Contamination prediction from weather + historical patterns

---

## Scoring Strategy

| Category (20% each) | Our Score Target | How |
|---------------------|-----------------|-----|
| Problem Relevance | 9.5/10 | Jal Jeevan Mission gap + 1.4B hours women's labor |
| Technical Feasibility | 9/10 | Every component exists, published research backs it |
| Innovation | 9.5/10 | Smartphone potentiostat + crowdsourced forensics |
| Impact | 9.5/10 | 12M SHGs, municipal integration, income for women |
| Prototype | 9/10 | Live voltammetry demo + real-time classification |

**Target overall: 9.3/10**

---

## What Judges Will Remember

1. **Live demo** — dip electrode in water, show voltammogram on phone, AI identifies ammonia in 60 seconds
2. **The number** — INR 25 per test vs INR 2000 lab test = 80x cheaper
3. **The scale** — 12 million SHGs = ready deployment network
4. **The framing** — "Women become the sensing infrastructure of India's water system"
5. **The L&T angle** — "This platform tells you WHERE to build treatment plants"

---

## Presentation Flow (10 min)

1. **Hook** (1 min): "A woman in Rajasthan walks 3 km for water. She doesn't know it has 2 mg/L ammonia. The nearest lab is 50 km away. By the time results come back, her children have been drinking it for 2 weeks."

2. **Problem** (2 min): The measurement gap. 1.9M habitations, 2,200 labs. The math doesn't work.

3. **Solution** (3 min): Smartphone + potentiostat + disposable electrode + edge AI. Live demo here.

4. **Platform** (2 min): Community intelligence. Show contamination heatmap. Municipal dashboard.

5. **Deployment** (1 min): SHG model. 12 million groups. Women as Water Guardians.

6. **Ask** (1 min): Pilot with 100 SHGs across 3 districts. INR 5 lakh investment. 6-month proof of value.

---

## Potential Judge Questions & Answers

**Q: How accurate is electrochemical sensing vs lab instruments?**
A: Published literature shows DPV on SPEs achieves >95% correlation with ICP-MS for heavy metals. Our accuracy target is ±10% of lab values for regulatory-relevant contaminants.

**Q: Why not just use commercial test kits?**
A: Commercial kits (Hach, LaMotte) cost $500+ and measure one parameter at a time. We detect 7+ contaminants from one voltammetric scan. More importantly, they don't aggregate data — we build community intelligence.

**Q: How do you handle electrode variability?**
A: Every SPE batch is characterized with known standards. The ML model is trained on voltammograms from multiple batches, learning to be invariant to electrode-to-electrode variation. This is called domain adaptation.

**Q: What's the business model?**
A: Three revenue streams: (1) SPE consumables (recurring), (2) Municipal dashboard subscriptions (SaaS), (3) Contamination intelligence reports for water utilities. Women testers earn per validated test.

**Q: How is this different from WaterCanary / Lishtot / pHox?**
A: Those are single-parameter or binary (safe/unsafe) indicators. We do quantitative multi-analyte forensics + community intelligence. The platform layer — crowdsourced contamination mapping — doesn't exist anywhere.
