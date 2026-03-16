# JalSakhi Interview Guide
## World Water Day 2026 | L&T Construction | March 17, 2026
## 10-min Presentation + 5-min Q&A | Category: Affordable Sensing & Filtration | Theme: "Water and Gender"

---

# PART 1: CODEBASE QUICK REFERENCE

## Project Structure (What's Where)

```
JalSakhi/
├── hardware/
│   ├── firmware/
│   │   ├── jalsakhi_ble/jalsakhi_ble.ino   # ESP32 BLE potentiostat firmware (DPV)
│   │   └── jalsakhi_web/index.html          # Web Bluetooth app (full UI)
│   └── CIRCUIT_GUIDE.md                     # Step-by-step breadboard build guide
├── docs/
│   ├── one-pager.md                         # Executive summary
│   ├── technical-deep-dive.md               # Full 22-subsystem engineering spec
│   ├── competition-brief.md                 # Category coverage + judge Q&A
│   ├── competition_strategy_final.md        # Round 2 strategy (judge psychology, weak spots)
│   ├── deployment-and-impact.md             # SHG model, gender impact, financials
│   ├── budget.md                            # INR 1,840 prototype BOM
│   └── references.md                        # 26 peer-reviewed references
├── presentation/
│   ├── slide_content_final.md               # Full slide-by-slide script
│   ├── gifs/                                # Animated GIFs for PPT
│   └── JalSakhi_Presentation_Prep_Guide.pdf
├── abstract.md                              # 300-word abstract
└── README.md                                # Full technical architecture
```

## Key Files to Know Cold

| If asked about... | Point to... |
|---|---|
| How the potentiostat works | `jalsakhi_ble.ino` — ESP32 DAC generates DPV waveform, ADC reads current via TIA |
| The app | `jalsakhi_web/index.html` — Web Bluetooth UI, real-time voltammogram, AI analysis |
| Circuit details | `CIRCUIT_GUIDE.md` — full breadboard layout, ESP32 pin assignments |
| Cost breakdown | `budget.md` — INR 1,840 total, every item listed |
| Scientific backing | `references.md` — 26 peer-reviewed papers |

---

# PART 2: HOW IT WORKS (End-to-End Flow)

## Electrochemical Mode (Precision)

```
Step 1: Dip pencil graphite electrodes into water sample
           ↓
Step 2: ESP32 generates DPV waveform via DAC (GPIO25)
        - Base potential sweeps from -0.8V to +0.8V
        - Superimposes 50mV pulses, 50ms width
           ↓
Step 3: LM358 op-amp potentiostat circuit
        - Op-amp A: Control amplifier (maintains WE-RE potential via CE)
        - Op-amp B: Transimpedance amplifier (converts cell current → voltage)
           ↓
Step 4: ESP32 ADC (GPIO34) reads TIA output
        - Samples current before pulse (i1) and at end of pulse (i2)
        - Differential current = i2 - i1 (cancels capacitive background)
           ↓
Step 5: Data sent via BLE to smartphone
        - Format: {voltage, differentialCurrent, temperature}
        - Real-time voltammogram plotted on phone
           ↓
Step 6: On-device AI analysis
        - Peak detection → each contaminant has unique peak potential
        - Lead: -0.45V, Arsenic: -0.15V, Ammonia: +0.25V, etc.
        - Peak height → concentration (quantitative)
           ↓
Step 7: Results displayed
        - Contaminant name + concentration + safety rating
        - Treatment advisory if needed
```

## Colorimetric Mode (Rapid Screening)

```
Step 1: Dip commercial test strip in water (30 sec)
           ↓
Step 2: Place strip on calibration card (ArUco markers)
           ↓
Step 3: Phone camera captures image
           ↓
Step 4: Computer vision pipeline:
        - ArUco marker detection → perspective correction
        - 10-patch color calibration (white balance + chromatic correction)
        - RGB → LAB color space conversion
        - ROI extraction for each reagent pad
           ↓
Step 5: CNN regression: LAB values → contaminant concentrations
           ↓
Step 6: Results in 30 seconds, ZERO extra hardware
```

## Key Technical Numbers to Remember

| Metric | Value | Why It Matters |
|--------|-------|----------------|
| Prototype cost | INR 1,840 | Well under INR 4,000 budget |
| Cost per test | INR 25 | vs INR 500-2,000 lab test (80x cheaper) |
| Detection time | 60 seconds | vs 3-14 days lab turnaround |
| Contaminants detected | 7+ | Ammonia, Lead, Arsenic, Nitrate, Iron, Fluoride, Chlorine |
| Lead detection limit | 1 ppb | Below WHO guideline (10 ppb) |
| Ammonia detection limit | 0.05 mg/L | 10x below WHO guideline (0.5 mg/L) |
| ML model size | < 200 KB | Runs fully offline on any smartphone |
| Inference time | < 50 ms | Real-time results |
| SHG network | 12 million | 140 million women, ready to deploy |

---

# PART 3: 2-MINUTE PITCH

> **Use this if asked "Tell us about your project" or for a quick elevator pitch.**

---

**[Hook — 15 sec]**

"A woman in rural Bihar suspects her borewell water is making her children sick. The nearest testing lab is 53 km away, costs 500 rupees, and takes 10 days. Her family drinks the water while they wait. Across India, 2,200 labs try to serve 1.9 million habitations. The math simply doesn't work."

**[Solution — 30 sec]**

"JalSakhi turns any smartphone into a water testing lab. In electrochemical mode, a pocket potentiostat built for under 2,000 rupees connects via Bluetooth. You dip a disposable electrode into water, and in 60 seconds, an on-device AI identifies and quantifies contaminants — ammonia, lead, arsenic, nitrate — at parts-per-billion sensitivity. In colorimetric mode, you just photograph a test strip against a calibration card. Zero extra hardware, 30-second results."

**[How — 20 sec]**

"The potentiostat performs Differential Pulse Voltammetry — a controlled voltage sweep that generates a unique electrochemical fingerprint for each contaminant. A 1D convolutional neural network, trained on thousands of voltammograms, reads these fingerprints on-device, fully offline. Every component is commercially available. Every claim is backed by peer-reviewed research."

**[Scale + Gender — 30 sec]**

"India already has 12 million women's Self-Help Groups under NRLM. JalSakhi taps into this existing infrastructure. Selected members become 'Jal Sakhis' — Water Guardians — testing community water weekly, earning micro-payments per test. Their data aggregates into district-level contamination heatmaps fed directly into Jal Jeevan Mission dashboards. Women aren't just end users — they become the sensing infrastructure of India's water system."

**[Close — 15 sec]**

"At 25 rupees per test versus 2,000 for lab work, we make weekly monitoring possible where annual testing was a luxury. A working prototype is here today. This is not a concept — it's built, it works, and it costs less than a movie ticket to test your water."

---

# PART 4: Q&A PREPARATION

## Category A: Technical Questions

**Q: How accurate is your electrochemical sensing vs a real lab?**
> Published literature shows DPV on screen-printed electrodes achieves >95% correlation with ICP-MS for heavy metals. Our prototype uses pencil graphite electrodes for the demo, which are less precise, but the production version with commercial SPEs at INR 25 each will match published accuracy. The key insight is that the electrode is disposable — fresh calibration every test, no drift.

**Q: Why not just use commercial test kits like Hach or LaMotte?**
> Those cost $500+ and measure one parameter at a time. We detect 7+ contaminants from one voltammetric scan for 25 rupees. More importantly, they don't aggregate data. JalSakhi doesn't just test water — it builds community intelligence.

**Q: Can an ESP32 really do accurate voltammetry?**
> The ESP32's 12-bit DAC gives ~0.8mV resolution — sufficient for DPV where 50mV pulses are standard. The real trick is the op-amp potentiostat circuit: one LM358 maintains the electrode potential, the other converts picoamp currents to measurable voltages. The ESP32 is just the controller and BLE radio. For production, an AD5940 analog front-end gives 16-bit resolution and 10nA current sensitivity.

**Q: How do you handle electrode variability?**
> Two approaches: (1) Every electrode batch is characterized with known standards — a calibration factor stored in the app. (2) The ML model is trained on voltammograms from multiple electrode batches with augmented noise, so it's invariant to electrode-to-electrode variation. This is domain adaptation.

**Q: What's the ML model architecture?**
> 1D-CNN with 4 convolutional layers (32→64→128→128 filters), global average pooling, then dual output heads: sigmoid for multi-label detection (which contaminants are present) and ReLU for concentration regression. INT8 quantized TFLite, under 200 KB, runs in under 50ms on any smartphone.

**Q: What about interference from other chemicals in the water?**
> DPV's differential measurement inherently cancels capacitive background. Each contaminant has a distinct peak potential — lead at -0.45V, ammonia at +0.25V — so they're separable. For complex matrices, an autoencoder anomaly detector flags unusual voltammograms as "possible interference" and recommends retesting.

## Category B: Feasibility & Scale Questions

**Q: What's the business model?**
> Three revenue streams: (1) SPE consumables — recurring, 60-70% margin at scale. (2) Municipal dashboard subscriptions — INR 50,000/month per district. (3) Government contracts under Jal Jeevan Mission for continuous monitoring. Jal Sakhis earn INR 600/month for validated testing. Break-even at ~200 SHGs deployed.

**Q: Why women SHGs and not ASHA workers or Gram Panchayat staff?**
> ASHAs are overloaded — health surveys, immunization, maternal care. No bandwidth for water testing. Gram Panchayat staff are limited in number and face political dynamics. SHG women have smartphones (NRLM has digitized most SHGs), financial infrastructure (bank accounts), training channels, and more flexibility. They're already organized, trusted, and have a financial incentive.

**Q: How do you prevent fake or manipulated data?**
> Three layers: (1) Device-level: each dongle has a factory-provisioned Ed25519 key; every test result is cryptographically signed. (2) Statistical: server checks for identical readings, impossible chemistry, extreme outliers vs regional data. (3) Community: cross-validation between nearby testers. Suspicious data is quarantined automatically.

**Q: Can this really work without internet?**
> Yes. All sensing, signal processing, and ML inference happen on-device. Results are stored locally and synced when connectivity is available. The community heatmap is the only feature that needs internet, and it works with intermittent connectivity — batch upload when signal is found.

## Category C: Impact & Competition Questions

**Q: How is this different from WaterCanary / Lishtot / pHox?**
> Those are single-parameter or binary safe/unsafe indicators. We do quantitative multi-analyte forensics — actual concentrations in mg/L and ppb. Plus the platform layer — crowdsourced contamination mapping with municipal dashboards — doesn't exist anywhere.

**Q: What's the gender impact beyond women using the device?**
> Structural, not cosmetic. Women become the data infrastructure. Jal Sakhis earn income (INR 600/month). Contamination maps reduce water collection time — on average 15 minutes per trip, saving 450,000 hours annually for 5,000 households. Women's data drives municipal infrastructure decisions. They're not users — they're the system.

**Q: How does this help L&T specifically?**
> L&T builds water treatment plants — but where should they build them? JalSakhi provides the demand signal. Our contamination heatmaps are the data layer that makes L&T's infrastructure investments more targeted and effective. This is complementary to their core business.

**Q: What's the pilot plan?**
> 100 SHGs across 3 ammonia-affected districts (Bhagalpur Bihar, Unnao UP, Guntur AP — all documented ammonia hotspots). 6 months. INR 5 lakh. Deliverable: validated contamination dashboard with >90% correlation to NABL lab results.

## Category D: Tough / Skeptical Questions

**Q: This sounds too good to be true. What's the catch?**
> Fair question. Three honest limitations: (1) Pencil graphite electrodes in the prototype are less precise than commercial SPEs — production version needs proper screen-printed electrodes at INR 25 each. (2) The ML model is trained on synthetic data right now — real-world validation with NABL lab cross-checking is needed in the pilot phase. (3) BLE range is ~10 meters, so the phone needs to be nearby during scanning. None of these are fundamental barriers — they're engineering problems with clear solutions.

**Q: Why hasn't anyone done this before?**
> They have — in labs. Published in journals since 2014. What nobody's done is: (1) packaged it at INR 1,200 instead of $500+, (2) added the community intelligence layer, (3) connected it to an existing deployment network of 12 million SHGs. The science exists. The platform didn't.

**Q: What if the prototype fails during the demo?**
> The colorimetric mode is independent — it just needs strips and a phone camera. If the potentiostat has issues, we switch to colorimetric demo instantly. We also have pre-recorded voltammograms from successful scans that show the full AI pipeline working. But the hardware has been tested and is working.

**Q: Isn't INR 25/test still expensive for rural families?**
> Not when it replaces a INR 2,000 lab test. And the Jal Sakhi model means individual families don't pay — the SHG does community testing funded by micro-payments from JJM/municipal contracts. The per-test cost is borne by the system, not the household.

---

# PART 5: DEMO FLOW (if live demo happens)

1. **Show the hardware** — ESP32 on breadboard, two LM358 op-amps, pencil graphite electrodes, jumper wires. "This entire setup costs INR 1,840."
2. **Open the web app** on phone — show Web Bluetooth connection screen
3. **Connect via BLE** — phone pairs with "JalSakhi-XXXX"
4. **Dip electrodes** in water sample (pre-prepared with ammonia spike if possible)
5. **Start DPV scan** — watch real-time voltammogram plot on phone
6. **AI results appear** — contaminant identified, concentration, safety rating, treatment advisory
7. **Show heatmap tab** — simulated multi-village contamination map
8. **Colorimetric backup** — photograph a test strip, show instant analysis

**Demo talking points while scanning (60 sec):**
- "What you're seeing is Differential Pulse Voltammetry — the same technique used in research labs, running on a 500-rupee microcontroller."
- "The voltage sweeps from -0.8V to +0.8V. Each contaminant produces a current peak at a specific voltage — that's its electrochemical fingerprint."
- "The AI model identifies the contaminant from the peak position and quantifies concentration from peak height."

---

# PART 6: NUMBERS CHEAT SHEET

Keep these at your fingertips:

| Stat | Number | Context |
|------|--------|---------|
| Rural habitations in India | 1.9 million | The scale of the problem |
| NABL water testing labs | 2,200 | Pathetically insufficient |
| Lab test cost | INR 500-2,000 | What we're replacing |
| Lab turnaround | 3-14 days | Unacceptable for safety |
| JalSakhi test cost | INR 25 | 80x cheaper |
| JalSakhi test time | 60 seconds | Real-time results |
| Prototype cost | INR 1,840 | Under INR 4,000 budget |
| Production dongle cost | INR 1,200 ($14.29) | Scalable |
| Women's water collection time | 1.4 billion hours/year | UNICEF stat |
| SHGs in India | 12 million | 140 million women |
| SHG coverage | 99% of blocks | Already everywhere |
| Jal Sakhi income | INR 600/month | Per water guardian |
| Contaminants detected | 7+ | Multi-analyte, not single |
| Lead detection limit | 1 ppb | Below WHO 10 ppb guideline |
| Ammonia detection limit | 0.05 mg/L | Below WHO 0.5 mg/L guideline |
| Peer-reviewed references | 26 | Every claim is backed |
| Pilot ask | INR 5 lakh | 100 SHGs, 3 districts, 6 months |

---

# PART 7: MINDSET REMINDERS

1. **You're not pitching a concept. You're showing something that works.** Lead with the demo.
2. **Judges are infrastructure engineers.** They respect specificity — part numbers, costs, detection limits. Not buzzwords.
3. **The L&T angle is your ace.** "This tells you WHERE to build treatment plants." That's their language.
4. **If you don't know something, say so honestly.** "That's a great question. In the current prototype, we haven't validated X, but the published literature shows Y, and our pilot plan specifically addresses this."
5. **The gender angle is structural, not decorative.** Women aren't just users. They're the sensing infrastructure. Their labor creates the data. Their data drives policy.
6. **End every answer by circling back to impact.** Numbers beat adjectives. "450,000 hours saved" beats "significant time savings."

---

**Good luck, Ujjwal. You've built something real. Now go show them.**
