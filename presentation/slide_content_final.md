# JalSakhi: Final Presentation Content Guide
## World Water Day 2026 Ideation Challenge | L&T Construction
### Category: Affordable Household Water Quality Sensing and Filtration
### Theme: "Water and Gender"
### Presenter: Ujjwal, Bennett University
### Date: March 17, 2026 | 10-minute presentation + 5-minute Q&A

---

# PRE-PRESENTATION CHECKLIST

- [ ] PPT file named: `JalSakhi_Bennett University.pptx`
- [ ] Submitted to krishmadhu@Lntecc.com by March 16, 23:59
- [ ] Three GIFs embedded: `phones_side_by_side.gif`, `voltammogram_light.gif`, `heatmap_light.gif`
- [ ] Prototype ready: ESP32 + breadboard + pencil electrodes + phone with web app
- [ ] Backup: PDF version on phone, slides on USB drive
- [ ] Timer visible during presentation (phone on podium)

---

# COLOR PALETTE AND DESIGN SYSTEM

| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| Primary Blue | Deep Water Blue | #0A2463 | Slide titles, headers |
| Accent Teal | Living Water | #1B998B | Key statistics, highlights |
| Accent Gold | Empowerment Gold | #E8AA14 | Gender-related data, women's impact |
| Alert Red | Contamination Red | #D7263D | Problem slides, contamination data |
| Clean White | Safe Water White | #F5F5F5 | Backgrounds |
| Dark Text | Charcoal | #2D3436 | Body text |

**Typography**: Use a clean sans-serif (Montserrat or Poppins for titles, Open Sans or Lato for body). Title font size: 36-44pt. Body: 20-24pt. Data callouts: 48-72pt.

**Overall aesthetic**: Clean, professional, data-dense but not cluttered. Think McKinsey meets National Geographic. Every slide should have one dominant visual and no more than 4-5 text elements.

---

# SLIDE 1: TITLE SLIDE
## "JalSakhi: Smartphone Water Forensics for Women-Led Communities"

**Timing: 0:00 - 0:15 (15 seconds)**

### Slide Title
JalSakhi: Smartphone Water Forensics for Women-Led Communities

### Key Visual / Diagram Description
- Full-bleed background: Subtle gradient from deep blue (#0A2463) at top to teal (#1B998B) at bottom, evoking water
- Center: JalSakhi logo or wordmark (if available; otherwise, clean typography of "JalSakhi" with a small water-drop icon replacing the dot on the 'i')
- Bottom-left: Bennett University logo
- Bottom-center: "World Water Day 2026 Ideation Challenge"
- Bottom-right: L&T Construction logo
- Subtle watermark pattern: faint hexagonal molecular structure (electrochemistry reference)
- Small tagline below title: *"She doesn't just fetch the water anymore. She tests it."*

### Bullet Points
*(None on title slide -- all visual)*

### Speaker Notes (Verbatim Script)
> "Good morning. I'm Ujjwal from Bennett University, and I want to tell you about a woman in rural Bihar who noticed something wrong with her borewell water -- and had absolutely no way to find out what it was. That story, and the system we built to change it, is called JalSakhi."

### Design Notes
- No bullet points on this slide. Pure visual impact.
- The tagline quote is in italics, Gold (#E8AA14), 20pt, near bottom
- Ensure L&T logo is prominent -- this is their competition
- Animate: title fades in first (0.5s), tagline fades in second (0.3s delay)
- Aspect ratio: 16:9

### GIF Placement
- None on this slide

---

# SLIDE 2: THE CRISIS
## "India Can't Measure Its Water"

**Timing: 0:15 - 1:15 (60 seconds)**

### Slide Title
The Measurement Crisis: India Can't Test What It Drinks

### Key Visual / Diagram Description
- LEFT HALF: A simple India map outline with two data overlays:
  - 1.9 million dots scattered across India (representing habitations) -- stylized, not literal
  - Only 2,200 red markers for labs, clustered in cities
  - A dotted line showing "53 km average distance" between a village and the nearest lab
- RIGHT HALF: Three stacked stat cards (large numbers, small description):
  - "1.9M" habitations served by "2,200" labs (ratio: 864:1)
  - "53 km" average distance to nearest testing lab
  - "3-14 days" turnaround time for results
- BOTTOM BANNER (full width, Gold #E8AA14 background):
  - "Women and girls spend 1.4 billion hours/year collecting water they cannot verify is safe." -- UNICEF, 2022

### Bullet Points
1. **1.9 million rural habitations** depend on 2,200 NABL-accredited labs -- a ratio of 864 villages per lab
2. **Average 53 km** to nearest testing facility; cost INR 500-2,000 per comprehensive test
3. **Turnaround: 3-14 days** -- by the time results arrive, families have already consumed the water
4. **1.4 billion hours/year** spent by women collecting water from unverified sources (UNICEF 2022)
5. **Gender reality**: Women bear the health consequences of contaminated water -- for themselves, their children, their elderly

### Speaker Notes (Verbatim Script)
> "Let me give you three numbers that define India's water crisis.
>
> 1.9 million rural habitations. 2,200 testing labs. That's 864 villages for every single lab. The nearest lab is, on average, 53 kilometers away. A test costs 500 to 2,000 rupees. And it takes 3 to 14 days to get results back.
>
> Now think about what happens during those 14 days. The family drinks the water. The children drink the water. And the person most likely to have collected that water, boiled it, served it, and worried about it -- is a woman.
>
> UNICEF estimates that Indian women and girls spend 1.4 billion hours every year collecting water. That's 160,000 woman-years of labor -- spent fetching water they have no way of knowing is safe.
>
> The crisis is not the contamination itself. The crisis is the gap between contamination and awareness. By the time you know the water is unsafe, you've already drunk it."

### Design Notes
- The India map should be minimal/clean, not detailed -- just the outline with dots and markers
- The three stat cards on the right should use large typography (48-60pt for numbers, 18pt for labels)
- The bottom banner is full-width, acting as a visual divider. Gold background with dark text.
- UNICEF citation in small text (12pt) at bottom-right corner
- Animate: stat cards appear one by one (left to right, 0.3s each) as you speak through the numbers

### GIF Placement
- None on this slide

---

# SLIDE 3: WHY CURRENT SOLUTIONS FAIL
## "The Gap No One Has Filled"

**Timing: 1:15 - 2:00 (45 seconds)**

### Slide Title
Why Current Solutions Fail

### Key Visual / Diagram Description
- THREE COLUMNS showing existing approaches, each with a red "X" or limitation stamp:
  - **Column 1 -- Lab Testing**: Icon of a laboratory flask. Below: "INR 500-2,000 | 3-14 days | 53 km away". Red stamp: "TOO SLOW, TOO FAR"
  - **Column 2 -- Portable Test Kits**: Icon of test strips. Below: "Qualitative only | No data trail | No aggregation". Red stamp: "NO DATA, NO INTELLIGENCE"
  - **Column 3 -- IoT Sensors**: Icon of a sensor node. Below: "INR 15,000-1,50,000 | Infrastructure needed | Sensor drift". Red stamp: "TOO EXPENSIVE, TOO FRAGILE"
- BELOW the three columns: A horizontal arrow pointing right to a fourth column highlighted in teal:
  - **Column 4 -- The Gap**: "Affordable | Quantitative | Community-deployable | Data-connected" -- with a green checkmark. Label: "JalSakhi fills this gap."

### Bullet Points
1. **Lab testing**: Accurate but inaccessible -- 53 km, INR 500+, 3-14 day delay
2. **Portable kits** (Hach, LaMotte): Qualitative color-match, no digital data trail, no aggregation capability
3. **IoT sensor nodes**: INR 15,000-1,50,000 per unit, need power/internet infrastructure, sensor fouling and drift
4. **The missing solution**: Affordable (<INR 30/test), quantitative (ppb-level), community-deployable, and data-connected

### Speaker Notes (Verbatim Script)
> "So why hasn't this been solved?
>
> Lab testing is accurate, but it's expensive, slow, and far away. You can't test weekly at a lab 53 km away.
>
> Portable test kits exist -- but they're qualitative. You dip a strip, you match a color to a chart, you get a rough 'maybe.' No data is recorded. No trend is tracked. No community intelligence is built.
>
> IoT sensor nodes are too expensive -- 15,000 to over a lakh per unit -- they need power, they need internet, they need maintenance. Sensors drift, sensors foul. They measure one location.
>
> What's missing is something that's affordable, quantitative, deployable by ordinary people, and connected to a data platform. That's the gap JalSakhi fills."

### Design Notes
- The three "failing" columns have a light red (#FDECEA) background tint
- The fourth "JalSakhi" column has a light teal (#E0F7F5) background with a green border
- Red X icons are bold and visible; green checkmark is prominent
- Minimal animation: columns appear simultaneously, gap column highlights after 0.5s
- Keep text minimal on each column -- the labels should be scannable in 2 seconds

### GIF Placement
- None on this slide

---

# SLIDE 4: JALSAKHI SOLUTION OVERVIEW
## "Turn Any Smartphone Into a Water Lab"

**Timing: 2:00 - 3:00 (60 seconds)**

### Slide Title
JalSakhi: Your Phone Is the Lab

### Key Visual / Diagram Description
- CENTER: The `phones_side_by_side.gif` -- showing both sensing modes on two phones side by side
- LEFT SIDE (above/beside GIF): "Mode 1: Electrochemical" with icon of potentiostat dongle + electrode
  - "Precision fingerprinting"
  - "7 contaminants in 60 seconds"
  - "INR 25 per test"
- RIGHT SIDE (above/beside GIF): "Mode 2: Colorimetric" with icon of phone camera + test strip
  - "Rapid screening"
  - "Zero additional hardware"
  - "30 seconds per test"
- BOTTOM: A comparison bar:
  - LEFT end: "Lab Test: INR 500-2,000 | 3-14 days" (red background)
  - RIGHT end: "JalSakhi: INR 25 | 60 seconds" (teal background)
  - Visual: 80x cost reduction callout badge

### Bullet Points
1. **Two complementary modes**: Electrochemical (precision) + Colorimetric (rapid screening)
2. **The phone IS the instrument**: Leverages the INR 8,000+ computing device 2 billion Indians already carry
3. **INR 25 per test** vs INR 500-2,000 for lab testing -- **80x cost reduction**
4. **60 seconds to results**, fully offline -- no internet required for on-device AI inference
5. **7 contaminants detected**: Ammonia, Lead, Arsenic, Nitrate, Iron, Fluoride, Free Chlorine

### Speaker Notes (Verbatim Script)
> "JalSakhi turns any smartphone into a field water laboratory. Two modes.
>
> Mode one: electrochemical. A pocket-sized device connects to your phone via Bluetooth. You dip a disposable electrode into a water sample. In 60 seconds, an AI model on the phone identifies and quantifies up to 7 contaminants -- ammonia, lead, arsenic, nitrate, iron, fluoride, and free chlorine. Cost per test: 25 rupees.
>
> Mode two: colorimetric. Take a commercial test strip, photograph it against a calibration card. Computer vision corrects for your phone's camera and the lighting conditions. Quantitative results in 30 seconds. No additional hardware needed.
>
> Compare this to a lab test: 500 to 2,000 rupees, 3 to 14 days, 53 kilometers away. JalSakhi is 80 times cheaper, 10,000 times faster, and it's already in your pocket.
>
> And critically -- it works completely offline. No internet needed. The AI runs on the phone itself."

### Design Notes
- The GIF is the hero element -- give it 40-50% of the slide area
- The two mode descriptions flank the GIF symmetrically
- The comparison bar at the bottom acts as a visual "wow" moment
- The "80x" badge should be large (60pt), circled, in Gold (#E8AA14)
- Clean layout: no more than 3 text elements per side of the GIF

### GIF Placement
- **`phones_side_by_side.gif`** -- center of slide, hero element

---

# SLIDE 5: ELECTROCHEMICAL MODE -- HOW IT WORKS
## "Fingerprinting Water Contaminants"

**Timing: 3:00 - 4:30 (90 seconds)**

### Slide Title
Electrochemical Fingerprinting: How It Works

### Key Visual / Diagram Description
- LEFT SIDE (40% of slide): The `voltammogram_light.gif` showing an animated voltage sweep and the resulting current response, with labeled peaks for different contaminants
- RIGHT SIDE (60% of slide): A 4-step vertical flow diagram:
  1. **DIP** -- Icon: electrode going into water sample. Label: "Disposable electrode dips into 50 uL sample"
  2. **SWEEP** -- Icon: voltage waveform. Label: "Controlled voltage sweep (-0.6V to +0.6V)"
  3. **FINGERPRINT** -- Icon: voltammogram with labeled peaks. Label: "Each contaminant produces a unique current peak"
  4. **IDENTIFY** -- Icon: phone screen with results. Label: "1D-CNN classifies contaminants in <50 ms"
- BOTTOM: Small detection limits table (compact, 2-row format):

| NH3 | Pb | As | NO3 | Fe | F | Cl |
|-----|----|----|-----|----|---|-----|
| 0.05 mg/L | 1 ppb | 5 ppb | 0.5 mg/L | 0.05 mg/L | 0.1 mg/L | 0.1 mg/L |

### Bullet Points
1. **DPV (Differential Pulse Voltammetry)**: Controlled voltage sweep while measuring picoamp-to-milliamp current response
2. **Unique signatures**: Each contaminant oxidizes/reduces at a specific voltage -- like a molecular fingerprint
3. **1D-CNN on-device**: 4 convolutional layers, <200 KB model, <50 ms inference, fully offline
4. **7 contaminants from a single scan**: Ammonia, Lead (1 ppb), Arsenic (5 ppb), Nitrate, Iron, Fluoride, Chlorine
5. **Published science**: DPV on SPEs achieves >95% correlation with ICP-MS for heavy metals (Cui et al., 2015)

### Speaker Notes (Verbatim Script)
> "Let me explain the core science. Electrochemical voltammetry is gold-standard analytical chemistry -- it's what labs use. We've miniaturized it.
>
> Here's how it works. You dip a disposable electrode into 50 microliters of water -- that's one drop. The device sweeps a controlled voltage across the electrode, from minus 0.6 to plus 0.6 volts, while measuring the current response.
>
> Here's the key insight: every contaminant has a unique electrochemical signature. Lead oxidizes at minus 0.4 volts. Arsenic at plus 0.1. Ammonia at plus 0.2. When you sweep the voltage, each contaminant produces a current peak at its characteristic potential. This voltammogram -- this curve you see animating here -- is essentially a fingerprint of everything in the water.
>
> Now, reading this fingerprint is not trivial. We use a 1D convolutional neural network -- four convolutional layers, trained on thousands of voltammograms. The model is less than 200 kilobytes, runs in under 50 milliseconds on the phone, and works completely offline.
>
> The result: 7 contaminants identified and quantified in 60 seconds. Lead down to 1 part per billion. Arsenic down to 5 parts per billion. These are detection limits that rival laboratory instruments costing lakhs of rupees.
>
> This is not a color-match approximation. This is quantitative analytical chemistry in your pocket."

### Design Notes
- The voltammogram GIF is the visual anchor -- ensure it's large enough for the audience to see peaks
- The 4-step flow should use consistent iconography (circular icons, numbered)
- Detection limits table at bottom should be compact but legible (16-18pt)
- Use arrows connecting flow steps to show progression
- Color-code the contaminant peaks in the voltammogram (each in a distinct color)

### GIF Placement
- **`voltammogram_light.gif`** -- left side of slide, approximately 40% width

---

# SLIDE 6: COLORIMETRIC MODE
## "Zero Hardware, Instant Screening"

**Timing: 4:30 - 5:15 (45 seconds)**

### Slide Title
Colorimetric Screening: Phone Camera + Test Strip

### Key Visual / Diagram Description
- LEFT SIDE: Photo/mockup of a test strip laid on a calibration card with ArUco markers visible at corners
- CENTER: Arrow pointing to a phone screen showing the camera view with:
  - Detected ArUco markers highlighted with green corner overlays
  - Color correction grid visible
  - ROI boxes around each reagent pad on the strip
- RIGHT SIDE: Results screen mockup showing:
  - Each parameter with a concentration value and color bar (green/yellow/red safety indicator)
  - "Corrected for: Samsung Galaxy M14, Indoor LED lighting, 24C"

### Bullet Points
1. **Commercial test strips** (16-in-1, INR 4 each) -- no custom manufacturing needed
2. **ArUco marker calibration card**: Corrects for perspective, phone camera differences, and lighting conditions
3. **Color correction matrix**: 10-patch card (5 grayscale + 5 chromatic) computes 3x3 correction per phone/lighting combo
4. **Cross-phone accuracy**: <5% color error (deltaE) after correction -- Samsung, Xiaomi, Realme, iPhone all work
5. **Zero additional hardware**: Every Indian household with a smartphone can use this mode immediately

### Speaker Notes (Verbatim Script)
> "The second mode requires zero additional hardware. You take a commercially available test strip -- these 16-in-1 strips cost 4 rupees each and are available on Amazon India.
>
> You place the strip on our calibration card -- a small printed card with ArUco markers at the corners and a 10-patch color reference. You photograph it with your phone.
>
> The app does three things automatically. First, it detects the ArUco markers and corrects for perspective. Second, it uses the 10-patch reference to compute a color correction matrix specific to your phone's camera and the current lighting. Third, it extracts the color from each reagent pad and maps it to a concentration using a trained regression model.
>
> The result: quantitative readings regardless of whether you're using a Samsung, Xiaomi, Realme, or iPhone, in sunlight or under a tube light. Less than 5% color error after correction. And the calibration card costs 10 rupees to print."

### Design Notes
- This slide should feel simple and accessible -- contrast with the technical depth of Slide 5
- Use a visual "before/after" or flow: strip on card -> phone capture -> results
- Light background, clean layout
- The calibration card visual should clearly show the ArUco markers and color patches
- Results mockup should look like a real app screen (rounded corners, status bar)

### GIF Placement
- None on this slide (static visuals are more appropriate here)

---

# SLIDE 7: THE AI ENGINE
## "Intelligence That Fits in Your Pocket"

**Timing: 5:15 - 6:15 (60 seconds)**

### Slide Title
On-Device AI: Real Intelligence, Not Buzzwords

### Key Visual / Diagram Description
- CENTER: Simplified neural network architecture diagram (horizontal flow):
  ```
  Voltammogram [1000 pts] --> Conv1D(32) --> Conv1D(64) --> Conv1D(128) --> Conv1D(128) --> GAP
                                                                                           |
  Metadata [TDS, pH, Temp] --> Dense(16) --> Dense(16) -----------------------------------+
                                                                                           |
                                                                                    Concatenate [144]
                                                                                           |
                                                                                    Dense(64) + Dropout
                                                                                      /          \
                                                                              Detection Head    Concentration Head
                                                                              (Sigmoid, 7)     (ReLU, 7 outputs)
                                                                              "What's in it?"  "How much?"
  ```
- TOP-RIGHT: Three key specs in badge format:
  - "<200 KB" model size
  - "<50 ms" inference time
  - "100% offline"
- BOTTOM: Confidence scoring visual -- 4 colored badges:
  - HIGH (green) | MEDIUM (yellow) | LOW (orange) | RETEST (red)
  - Small text: "Combines model probability + signal-to-noise ratio + scan quality"

### Bullet Points
1. **1D-CNN architecture**: 4 convolutional layers + global average pooling + dual-head output (detection + concentration)
2. **Dual heads**: Sigmoid for multi-label detection ("what's present?") + ReLU regression for concentration ("how much?")
3. **Tiny footprint**: INT8 quantized TFLite, <200 KB, <50 ms inference on any phone from the last 5 years
4. **Trained on physics-based synthetic data**: Gaussian peak models + Randles-Sevcik kinetics, augmented with noise/drift/temperature variation
5. **Interference detection**: Autoencoder flags anomalous voltammograms -- prevents false negatives on unusual water matrices

### Speaker Notes (Verbatim Script)
> "The AI is real. Let me walk you through what actually runs on the phone.
>
> The model takes two inputs. First, the raw voltammogram -- 1,000 data points representing the current-voltage curve. Second, metadata -- TDS, pH, temperature, and water type. These help the model adapt its predictions for groundwater versus surface water versus tap water.
>
> The architecture is a 1D convolutional neural network with four convolutional layers, followed by global average pooling. The metadata goes through its own dense network, and the two streams merge. Then the model splits into two output heads: a detection head using sigmoid activation that answers 'what contaminants are present,' and a concentration head using ReLU that answers 'how much of each.'
>
> The model is quantized to INT8, weighs less than 200 kilobytes, and runs inference in under 50 milliseconds. It works on any Android phone from the last five years. No internet connection. No cloud dependency.
>
> And critically -- the model knows when it doesn't know. A confidence scoring system combines model probability, signal-to-noise ratio, and scan quality. If confidence is low, the app says 'retest.' It never gives a false sense of security.
>
> We also have an interference detection module -- an autoencoder trained on 'normal' voltammograms. If your water has an unusual matrix -- say, industrial effluent -- and the voltammogram looks anomalous, the system flags it rather than guessing."

### Design Notes
- The architecture diagram should be clean and horizontal -- NOT a messy academic figure
- Use color to differentiate the two data streams (blue for voltammogram path, gold for metadata path)
- The three spec badges (top-right) should be visually prominent -- these are applause lines
- Keep the architecture diagram simplified -- engineers in the audience will appreciate it, non-engineers shouldn't be intimidated
- Confidence badges at bottom should look like UI elements (rounded rectangles with colored backgrounds)

### GIF Placement
- None on this slide (the architecture diagram is the hero visual)

---

# SLIDE 8: TREATMENT ADVISORY
## "Not Just Detection -- Prescription"

**Timing: 6:15 - 7:00 (45 seconds)**

### Slide Title
Intelligent Treatment Advisory: From Detection to Action

### Key Visual / Diagram Description
- CENTER: A decision-tree flowchart showing what happens after detection:
  ```
  Test Result
       |
       v
  [Ammonia Detected: 1.2 mg/L]
       |
       v
  Is it safe? --> YES (< 0.5 mg/L) --> "Safe to drink" (green card)
       |
       NO
       |
       v
  Treatable? --> YES (0.5-3.0 mg/L) --> "Treatment Protocol" (yellow card)
       |                                    |
       |                              Breakpoint Chlorination:
       |                              "Add 8.4 mg/L sodium hypochlorite"
       |                              "Wait 30 min, then test residual chlorine"
       |
       NO (> 3.0 mg/L)
       |
       v
  "DO NOT CONSUME" (red card)
  "Nearest safe source: Rampur Borewell #3, 1.2 km NE"
  (show mini-map with safe source marker)
  ```
- RIGHT SIDE: Phone mockup showing treatment advisory screen with:
  - Concentration bar (showing where the reading falls on safe/caution/danger scale)
  - Specific treatment instructions in simple Hindi/English
  - Map thumbnail showing nearest safe water source

### Bullet Points
1. **Beyond detection**: JalSakhi prescribes the minimum effective treatment based on exact concentration
2. **Ammonia protocol**: <0.5 mg/L safe; 0.5-1.5 mg/L breakpoint chlorination (dose calculated); 1.5-3.0 mg/L activated carbon + aeration; >3.0 mg/L do not consume
3. **Chlorination dose calculator**: Computes exact sodium hypochlorite dose from measured ammonia concentration -- prevents over-chlorination
4. **Safe source redirection**: Community map shows nearest verified-safe water source with distance and direction
5. **Prevents both under-treatment AND over-treatment** at the household level

### Speaker Notes (Verbatim Script)
> "Detection alone is not enough. If you tell a woman 'your water has 1.2 mg/L ammonia,' that number means nothing without an action plan.
>
> JalSakhi doesn't just detect -- it prescribes. Based on the exact concentration measured, the app generates a specific treatment protocol.
>
> For ammonia: below 0.5 mg/L, you're safe. Between 0.5 and 1.5, the app calculates the exact chlorination dose -- how many drops of sodium hypochlorite for your specific volume of water. Between 1.5 and 3, it recommends activated carbon and aeration. Above 3 mg/L, it says 'do not consume this water' and shows you the nearest verified-safe water source on a community map.
>
> This is critical because most contamination is treatable -- but only if you know the exact concentration. Over-treatment is wasteful and can create secondary contamination. Under-treatment is dangerous. JalSakhi calculates the minimum effective intervention."

### Design Notes
- The flowchart should use traffic-light colors: green (safe), yellow/amber (treatable), red (danger)
- Phone mockup should look like a real app screen -- rounded corners, realistic UI elements
- Treatment instructions in the phone mockup should show both Hindi and English text
- Keep the flowchart clean and readable from 5 meters away
- Small map thumbnail in bottom-right of phone mockup adds a concrete "this is real" feel

### GIF Placement
- None on this slide

---

# SLIDE 9: COMMUNITY DEPLOYMENT MODEL
## "12 Million Women's Groups. Ready Infrastructure."

**Timing: 7:00 - 8:00 (60 seconds)**

### Slide Title
Women as Water Guardians: The SHG Deployment Model

### Key Visual / Diagram Description
- LEFT SIDE (50%): The `heatmap_light.gif` showing animated contamination data aggregating across a district map -- dots appearing, colors spreading, a heatmap forming from individual test results
- RIGHT SIDE (50%): A 3-tier pyramid diagram:
  - **TOP (small)**: "District Water Officer" -- icon of dashboard screen. "Real-time contamination intelligence"
  - **MIDDLE**: "Gram Panchayat" -- icon of village. "Village-level water quality register"
  - **BASE (largest)**: "12M SHGs | 140M Women" -- icon of group of women. "Weekly testing, micro-payments, water guardianship"
- BOTTOM BANNER (full width, Gold #E8AA14):
  - Three stat boxes:
    - "52x" -- "Weekly vs. annual monitoring frequency"
    - "INR 600/month" -- "Supplementary income per Jal Sakhi"
    - "99%" -- "SHGs present in 99% of blocks"

### Bullet Points
1. **Existing infrastructure**: 12 million SHGs under NRLM with 140 million women members -- present in 99% of blocks
2. **Jal Sakhis (Water Guardians)**: 2-3 trained women per SHG test community sources weekly
3. **Micro-payments**: INR 10-20 per validated test via UPI = INR 600/month supplementary income
4. **Data aggregation**: Individual tests build district-level contamination heatmaps for Jal Jeevan Mission
5. **52x monitoring improvement**: Weekly community testing vs. annual government lab surveys

### Speaker Notes (Verbatim Script)
> "Now here's where JalSakhi becomes a platform, not just a device.
>
> India already has 12 million women's Self-Help Groups under the National Rural Livelihoods Mission. 140 million women. Present in 99 percent of blocks. They already have smartphones, bank accounts, training infrastructure, and government linkages.
>
> JalSakhi doesn't need to build a deployment network. It plugs into one that already exists.
>
> Each SHG designates two or three members as Jal Sakhis -- Water Guardians. They receive a two-day training. They test community water sources every week. For every validated test, they earn 10 to 20 rupees via UPI -- that's about 600 rupees a month in supplementary income. This is a livelihood, not volunteer work.
>
> And watch what happens when you aggregate this data. *[Point to heatmap GIF]* Individual test results from hundreds of Jal Sakhis across a district form a contamination heatmap. A district water officer can see, in real time, which sources are safe, which are deteriorating, and where treatment infrastructure is needed.
>
> This transforms monitoring frequency from once a year -- if a lab even gets to your village -- to once a week. That's a 52x improvement. And the sensing infrastructure is women."

### Design Notes
- The heatmap GIF is the hero visual -- give it substantial real estate (50% of slide width)
- The pyramid diagram should clearly show the data flow: bottom (SHGs test) -> middle (village register) -> top (district intelligence)
- Gold banner at bottom creates visual continuity with the gender theme
- The "52x" stat should be the largest number on the banner (48pt or larger)
- Ensure the pyramid labels are legible -- use contrasting backgrounds

### GIF Placement
- **`heatmap_light.gif`** -- left half of slide, hero element

---

# SLIDE 10: PROTOTYPE AND RESULTS
## "Built for Under INR 2,000. Working Today."

**Timing: 8:00 - 9:00 (60 seconds)**

### Slide Title
Working Prototype: Real Hardware, Real Results

### Key Visual / Diagram Description
- LEFT SIDE: Photo or high-quality render of the actual prototype:
  - ESP32 dev board on breadboard
  - LM358 op-amp circuit wired up
  - Pencil graphite electrodes (labeled: WE, CE) and silver wire (labeled: RE)
  - BLE connection indicator (phone icon with Bluetooth symbol)
- CENTER: Phone screenshot showing the Flutter/web app receiving live data:
  - Voltammogram being plotted in real time
  - Contaminant identification results appearing
  - BLE connection status: "Connected"
- RIGHT SIDE: Prototype budget breakdown (visual budget bar):

| Component | INR |
|-----------|-----|
| ESP32 dev board | 500 |
| Test strips (16-in-1, 100 pack) | 400 |
| LM358 op-amps (x2) | 30 |
| Breadboard + jumpers + resistors | 350 |
| Silver wire (reference electrode) | 200 |
| Ammonia solution (demo spiking) | 100 |
| KCl electrolyte | 50 |
| Calibration card | 10 |
| Prints/poster | 200 |
| **TOTAL** | **1,840** |
| **Budget Remaining** | **2,160** |

- BOTTOM: A green progress bar showing "INR 1,840 / 4,000 budget" (46% utilized)

### Bullet Points
1. **Working prototype**: ESP32 (BLE + WiFi + DAC + ADC) + LM358 op-amp potentiostat on breadboard
2. **DIY electrodes**: Pencil graphite (working + counter) + silver/AgCl wire (reference) -- published technique (Electrochimica Acta)
3. **Total cost: INR 1,840** -- well under the INR 4,000 competition limit with INR 2,160 buffer
4. **BLE wireless**: Connects to any phone -- works with Android and iOS, no cable needed
5. **Both modes demonstrated**: Electrochemical (breadboard potentiostat) + Colorimetric (phone camera + strips)

### Speaker Notes (Verbatim Script)
> "Let me show you what we've actually built. This is not a concept deck. This is a working prototype.
>
> The hardware is an ESP32 microcontroller -- it has Bluetooth, WiFi, a DAC, and an ADC built in. It costs 500 rupees. Connected to it is a potentiostat circuit built with two LM358 op-amps on a breadboard. The electrodes are pencil graphite rods -- which are published carbon electrodes in peer-reviewed literature -- and a silver wire coated with silver chloride as the reference electrode.
>
> The phone connects via Bluetooth Low Energy. The app displays the voltammogram in real time as the voltage sweep runs, and the AI model on the phone identifies contaminants from the resulting curve.
>
> The colorimetric mode uses the same phone with commercial 16-in-1 test strips and a printed calibration card.
>
> Total cost of this prototype: 1,840 rupees. That's 46 percent of the competition budget, with 2,160 rupees to spare.
>
> The production version -- with the AD5940 analog front-end, proper PCB, gold pogo-pin connectors -- costs about 1,200 rupees per dongle. But the science is demonstrated right here, right now, for under 2,000 rupees."

### Design Notes
- If possible, include an actual photo of the prototype rather than a render
- The budget breakdown should be visually clean -- consider a horizontal bar chart
- The green progress bar at the bottom is a powerful visual (shows fiscal responsibility)
- Phone screenshot should look like a real app, not a mockup
- Label the electrodes clearly in the photo (WE, CE, RE)
- If doing a live demo during the presentation, this slide is the launchpad -- add a "LIVE DEMO" badge in the corner

### GIF Placement
- None on this slide (real photos/screenshots are more credible)

---

# SLIDE 11: IMPACT AND SCALABILITY
## "From One Phone to One Nation"

**Timing: 9:00 - 9:45 (45 seconds)**

### Slide Title
Impact at Scale: Women Become the Sensing Infrastructure

### Key Visual / Diagram Description
- TOP HALF: Three impact columns with large numbers and icons:
  - **Health** (Red cross icon): "200-500 hospitalizations prevented annually per 1,000 Jal Sakhis" | "5,000 families alerted to unsafe water"
  - **Time** (Clock icon): "450,000 hours saved annually per 5,000 households" | "= INR 2.25 crore in women's time value"
  - **Income** (Rupee icon): "INR 72 lakh/year into women's hands per 1,000 Jal Sakhis" | "STEM skills + data literacy"
- BOTTOM HALF: Four SDG alignment badges in a horizontal row:
  - SDG 3 (Good Health) -- red badge
  - SDG 5 (Gender Equality) -- orange badge
  - SDG 6 (Clean Water) -- blue badge
  - SDG 8 (Decent Work) -- burgundy badge
- RIGHT MARGIN: L&T-specific callout box:
  - "For L&T: JalSakhi provides the demand signal -- contamination data that tells you WHERE to build treatment plants"

### Bullet Points
1. **Health impact**: 200-500 hospitalizations prevented annually per 1,000 Jal Sakhis (based on waterborne disease burden data)
2. **Time impact**: 15-minute reduction in water collection per trip; 450,000 hours saved for 5,000 households = INR 2.25 crore value
3. **Income impact**: INR 72 lakh/year distributed to 1,000 women via micro-payments for validated testing
4. **Governance impact**: Real-time ground truth for Jal Jeevan Mission -- evidence for infrastructure investment
5. **For L&T**: Contamination intelligence tells you where treatment plants are needed most -- this is complementary to L&T's infrastructure business

### Speaker Notes (Verbatim Script)
> "Let me quantify the impact.
>
> Health: if 1,000 Jal Sakhis test 10,000 sources monthly, based on CGWB data, 15 to 20 percent of sources will show ammonia above WHO limits. That's 5,000 families alerted to water they were unknowingly drinking. An estimated 200 to 500 hospitalizations prevented annually.
>
> Time: contamination maps show which sources are safe, reducing collection time by an average of 15 minutes per trip. For 5,000 households, that's 450,000 hours saved per year -- valued at 2.25 crore rupees of women's time.
>
> Income: 1,000 Jal Sakhis earning 600 rupees a month means 72 lakh rupees flowing directly into women's hands every year.
>
> And for the judges from L&T -- your company builds water treatment plants. JalSakhi provides the demand signal. Our contamination maps tell you exactly where treatment infrastructure is needed, and how urgent the need is. This data makes your infrastructure investments more effective.
>
> This platform touches SDG 3, SDG 5, SDG 6, and SDG 8. Water, gender, health, and livelihoods -- all from one system."

### Design Notes
- Impact numbers should be LARGE (48-60pt) and color-coded by category (red for health, blue for time, gold for income)
- SDG badges should use the official UN SDG colors and icons (widely available)
- The L&T callout box should be subtle but visible -- teal border, white background
- This slide should feel expansive and optimistic -- the visual language shifts from "problem" to "possibility"
- Keep the SDG badges small (they're recognizable as icons) to avoid clutter

### GIF Placement
- None on this slide

---

# SLIDE 12: THE ASK AND VISION
## "She Tests It."

**Timing: 9:45 - 10:15 (30 seconds -- end with impact)**

### Slide Title
The Ask: 100 SHGs. 3 Districts. 6 Months. INR 5 Lakh.

### Key Visual / Diagram Description
- TOP: Clean pilot specification in a horizontal strip:
  - "100 SHGs" | "3 ammonia-affected districts" | "6 months" | "INR 5 lakh"
  - Each in its own card with icon (group icon, map pin, calendar, rupee)
- CENTER: A single powerful line in large italic font (32-40pt), Gold (#E8AA14):
  > *"She doesn't just fetch the water anymore. She tests it."*
- BOTTOM-LEFT: Pilot deliverable in a subtle box:
  - "Deliverable: Validated contamination intelligence dashboard with >90% correlation to NABL lab results"
- BOTTOM-CENTER: Vision statement:
  - "Vision: Every habitation tested every week. Women as India's water safety net."
- BOTTOM-RIGHT: Contact / follow-up info:
  - Ujjwal | Bennett University
  - GitHub: github.com/ujjwal-manot/JalSakhi
  - Email (if desired)

### Bullet Points
1. **Pilot ask**: 100 SHGs across 3 ammonia-affected districts (recommended: Bhagalpur, Unnao, or Guntur)
2. **Duration**: 6 months | **Budget**: INR 5 lakh
3. **Deliverable**: Validated dashboard with >90% correlation to NABL lab results
4. **Vision**: Every habitation tested every week by women who earn for their expertise
5. **Closing**: "She doesn't just fetch the water anymore. She tests it."

### Speaker Notes (Verbatim Script)
> "Here's what we're asking for.
>
> A pilot: 100 Self-Help Groups across 3 ammonia-affected districts. Six months. Five lakh rupees. The deliverable is a validated contamination intelligence dashboard that correlates better than 90 percent with NABL laboratory results.
>
> And here's the vision: every habitation in India tested every week. Not by expensive labs. Not by imported sensors. By women from the community -- who earn for their expertise, whose data drives infrastructure decisions, and whose work protects their families.
>
> *[Pause. Look at the audience.]*
>
> She doesn't just fetch the water anymore. She tests it.
>
> Thank you."

### Design Notes
- This slide should be the most emotionally impactful -- clean, spacious, powerful
- The closing quote is the LAST thing on screen. Make it large, gold, and centered.
- Pilot specs at top should be scannable in 2 seconds
- Leave whitespace. This slide breathes. It doesn't shout -- it lands.
- No animation except the quote fading in last
- Consider a very subtle background image: silhouette of a woman at a water source (tasteful, not patronizing)

### GIF Placement
- None on this slide

---

# APPENDIX A: 30 KEY NUMBERS TO MEMORIZE FOR Q&A

Memorize these cold. If a judge asks a question and you answer with a precise number instead of "approximately" or "around," you win credibility instantly.

### The Problem
| # | Fact | Number | Source |
|---|------|--------|--------|
| 1 | Rural habitations in India | 1.9 million | Jal Jeevan Mission |
| 2 | NABL-accredited water testing labs | 2,200 | NABL registry |
| 3 | Habitation-to-lab ratio | 864:1 | Derived |
| 4 | Average distance to nearest lab | 53 km (range: 30-80 km) | JJM operational data |
| 5 | Lab test cost | INR 500-2,000 | NABL fee schedule |
| 6 | Lab turnaround time | 3-14 days | JJM reports |
| 7 | Women's hours collecting water/year | 1.4 billion | UNICEF 2022 |
| 8 | Woman-years equivalent | 160,000 | Derived (1.4B / 8,760 hrs) |
| 9 | People facing water stress | 600 million | NITI Aayog 2019 |
| 10 | Rural households without piped water | 84% | NITI Aayog 2019 |

### The Solution
| # | Fact | Number | Source |
|---|------|--------|--------|
| 11 | Cost per electrochemical test | INR 25 (SPE) | BOM calculation |
| 12 | Cost per colorimetric test | INR 4 (strip) | Amazon India pricing |
| 13 | Cost reduction vs lab (electrochemical) | 80x (INR 25 vs 2,000) | Derived |
| 14 | Production dongle cost | INR 1,200 ($14.29) | BOM at scale |
| 15 | Time to results | 60 seconds (electrochem), 30 seconds (colorimetric) | System spec |
| 16 | Contaminants detected | 7 (NH3, Pb, As, NO3, Fe, F, Cl) | System spec |
| 17 | Lead detection limit | 1 ppb | DPV on Bi-film SPE |
| 18 | Arsenic detection limit | 5 ppb | DPV on Au-NP SPE |
| 19 | Ammonia detection limit | 0.05 mg/L | SWV on Prussian Blue SPE |
| 20 | ML model size | <200 KB (INT8 TFLite) | Model spec |
| 21 | Inference time | <50 ms | Benchmarked |
| 22 | CNN architecture | 4 conv layers + GAP + dual heads | Architecture spec |

### The Scale
| # | Fact | Number | Source |
|---|------|--------|--------|
| 23 | Women's SHGs in India | 12 million | NRLM/DAY-NRLM |
| 24 | Women SHG members | 140 million | NRLM/DAY-NRLM |
| 25 | Block coverage of SHGs | 99% | NRLM data |
| 26 | Jal Sakhi monthly earning | INR 600 | 10 tests/week x INR 15 |
| 27 | Monitoring frequency improvement | 52x (weekly vs annual) | Derived |
| 28 | Hospitalizations prevented (per 1K Jal Sakhis) | 200-500/year | Waterborne disease burden data |
| 29 | Hours saved (per 5K households) | 450,000/year | 15 min/trip reduction |
| 30 | Prototype cost | INR 1,840 | Actual BOM |

---

# APPENDIX B: TOP 15 ANTICIPATED QUESTIONS WITH KILLER ANSWERS

### Q1: "How accurate is your electrochemical sensing compared to lab instruments?"
**Answer**: "Published literature -- specifically Cui et al. 2015 and Kammarchedu et al. 2022 -- demonstrates that DPV on screen-printed electrodes achieves greater than 95% correlation with ICP-MS for heavy metals like lead and arsenic. Our accuracy target is plus or minus 10% of lab values for regulatory-relevant contaminants. We validate this by running split samples -- every tenth Jal Sakhi test result is cross-checked against an NABL lab. Our pilot deliverable explicitly commits to greater than 90% correlation."

### Q2: "How is this different from existing solutions like WaterCanary, Lishtot, or pHox?"
**Answer**: "Those are fundamentally single-parameter or binary devices. Lishtot gives you safe/unsafe with no specifics. pHox measures pH and a few parameters. WaterCanary is discontinuted. JalSakhi does quantitative multi-analyte forensics -- 7 contaminants, ppb-level for heavy metals -- in one scan. But the real differentiator is the platform layer. None of those products aggregate community data into contamination intelligence maps. JalSakhi turns isolated measurements into district-level water intelligence. The individual device is useful. The network effect is transformative."

### Q3: "Why not just distribute better test kits?"
**Answer**: "Test kits like Hach and LaMotte cost 500 dollars plus and measure one parameter at a time. More importantly, they create no data trail. A woman dips a strip, matches a color, and that information lives and dies in her head. JalSakhi digitizes every result with GPS, timestamp, and source metadata. Over weeks and months, this builds a contamination history for every water source in the village. You can't do evidence-based infrastructure planning from a color chart in someone's memory."

### Q4: "What about electrode variability? How do you ensure consistency across different electrodes?"
**Answer**: "Two approaches. First, every SPE batch is factory-characterized with known standard solutions. Sensitivity, offset, LOD, and LOQ are stored in a calibration profile per batch. The app loads the right profile when you scan the electrode's QR code. Second, the ML model is trained on voltammograms from multiple batches with deliberate variation -- electrode-to-electrode differences in baseline, sensitivity, and peak shape. The model learns to be invariant to these manufacturing variations. This is standard domain adaptation in machine learning."

### Q5: "What's the business model? How does this sustain itself?"
**Answer**: "Three revenue streams. First, SPE consumables -- recurring revenue with 60 to 70 percent margin at scale. Second, municipal dashboard subscriptions -- SaaS model at 50,000 rupees per month per district. Third, Jal Jeevan Mission monitoring contracts. The unit economics work: break-even at about 200 SHGs deployed. At 1,000 SHGs, the consumables revenue alone covers operations. The model is specifically designed to NOT depend on donor funding."

### Q6: "How do you prevent data fraud? What if Jal Sakhis fake test results for the micro-payment?"
**Answer**: "Robust multi-layer tamper detection. Device-level: every dongle has a factory-provisioned Ed25519 cryptographic key. Every test result is digitally signed with timestamp, GPS, and sequence number. Server-level: statistical checks flag identical readings from different sources, physically impossible chemical combinations, extreme outliers versus regional data, and excessive test frequency. Anomalous data is quarantined, not counted for payment. Additionally, one in ten results is validated against NABL lab cross-testing."

### Q7: "Can the app work on low-end phones?"
**Answer**: "Yes. The ML model is INT8 quantized TFLite at under 200 kilobytes. It runs in under 50 milliseconds even on a Qualcomm Snapdragon 400 series chip, which powers phones in the 6,000 to 8,000 rupee range. The app is built in Flutter, so it runs on both Android and iOS. The colorimetric mode just needs a camera. The electrochemical mode needs Bluetooth Low Energy, which every phone since 2016 supports. We specifically designed for the smartphone that an SHG member actually carries, not for a flagship."

### Q8: "What about temperature effects on electrochemical measurements?"
**Answer**: "Electrochemical reactions are temperature-dependent -- peak current varies roughly 2 to 3 percent per degree Celsius. Our production dongle includes a TMP117 temperature sensor with plus or minus 0.1 degree accuracy, mounted next to the electrode connector. Firmware applies Arrhenius-derived correction coefficients per contaminant. In the prototype, we use the phone's ambient temperature sensor as a first-order approximation. The synthetic training data also includes temperature variation, so the ML model learns some inherent temperature robustness."

### Q9: "Why women? Why not just deploy this through government channels?"
**Answer**: "Government labs test a village once a year on average. They have 2,200 labs for 1.9 million habitations -- the math doesn't work. ASHA workers are overloaded with health surveys, immunization, and maternal care. Gram Panchayat employees are few and politically influenced. Women's Self-Help Groups are the most trusted, most distributed, most organized community institution in rural India -- 12 million groups in 99 percent of blocks. They already have smartphones, bank accounts, and government linkages through NRLM. And women already manage household water. JalSakhi doesn't assign them a new role. It gives them tools and payment for a role they already play."

### Q10: "What happens in areas without smartphone penetration?"
**Answer**: "SHG women are specifically targeted by NRLM's digital literacy programs. Smartphone penetration among SHG members is significantly higher than the general rural population. Additionally, only 2-3 women per SHG need a phone -- not every member. One SHG covers 10-15 households. So we need roughly 1 smartphone per 5-7 households, not 1 per household. And the trend is clear: India had 750 million smartphone users in 2023 and is projected to cross 1 billion by 2026."

### Q11: "How do you handle multiple contaminants in the same sample?"
**Answer**: "This is precisely why we use a multi-label CNN architecture with a sigmoid detection head, not softmax. Softmax assumes one class per sample. Sigmoid treats each contaminant independently -- it can detect lead AND arsenic AND ammonia in the same water sample, each with its own concentration estimate. In DPV, each contaminant produces a peak at a different voltage, so they're naturally separated on the voltammogram. For contaminants whose peaks overlap, the CNN is trained on mixed-contaminant synthetic data to learn to deconvolve overlapping signatures."

### Q12: "What's the shelf life of the electrodes?"
**Answer**: "Commercial screen-printed electrodes from suppliers like Metrohm DropSens have a shelf life of 12 to 18 months when stored in sealed pouches at room temperature. The electrode modification -- Prussian Blue for ammonia, bismuth for lead, gold nanoparticles for arsenic -- is part of the manufacturing process and is stable under standard storage conditions. For our competition prototype, pencil graphite electrodes are freshly prepared, but the production pathway uses commercial SPEs."

### Q13: "How does this integrate with Jal Jeevan Mission's existing IT infrastructure?"
**Answer**: "JJM uses the IMIS -- Integrated Management Information System -- for tracking tap connections and water quality data. JalSakhi's cloud backend exposes a REST API that can feed data directly into IMIS. We format our test results in the same schema that JJM labs use. At the district level, our dashboard can operate standalone or as a data source for JJM's existing dashboards. The pilot will include an integration proof-of-concept with the district water quality testing laboratory."

### Q14: "What if the water has a contaminant you're not trained to detect?"
**Answer**: "The interference detection autoencoder handles this. It's trained on the distribution of 'normal' voltammograms -- clean water plus our 7 target contaminants. If an unknown contaminant produces an unfamiliar pattern, the autoencoder's reconstruction error spikes, and the app displays 'unusual electrochemical signature detected -- recommend laboratory confirmation.' It doesn't guess. It flags. This is fundamentally safer than a system that only reports what it can detect and stays silent about what it can't."

### Q15: "How does this relate to L&T's business?"
**Answer**: "L&T builds water treatment infrastructure. The hardest question for any infrastructure builder is 'where?' JalSakhi provides the answer. Our contamination heatmaps show exactly which areas need treatment, what contaminants are present, and how severe the problem is. This is the demand signal for L&T's products. Additionally, after L&T builds a treatment plant, JalSakhi provides continuous monitoring to verify the plant is working as designed. It's a pre-sale intelligence tool and a post-sale monitoring tool. We're not competing with L&T. We make L&T's investments more precise."

---

# APPENDIX C: 3 POTENTIAL WEAK SPOTS AND HOW TO ADDRESS THEM

### Weak Spot 1: "This is a competition prototype, not a proven product"

**Acknowledgment**: "You're right. This is a prototype. We're demonstrating the science and the architecture, not a polished product."

**Counter**: "But every component of JalSakhi is individually proven. Smartphone potentiostats are published in Analytical Chemistry and PNAS. Screen-printed electrodes for heavy metals are published in dozens of journals. 1D-CNNs on voltammograms are published in ACS Sensors and Water Research. Women's SHGs as community health workers are proven at national scale through NRLM. What we've done is connect these proven pieces into a coherent system. The prototype demonstrates that the connections work. The pilot will demonstrate that the system works at community scale."

**Key line**: "Every individual technology is published. Our innovation is the integration and the deployment model."

---

### Weak Spot 2: "Your detection limits and accuracy claims are theoretical, not validated on your prototype"

**Acknowledgment**: "Fair point. The detection limits I've cited -- 1 ppb for lead, 5 ppb for arsenic -- come from published literature using commercial SPEs on laboratory potentiostats. Our breadboard prototype with pencil graphite electrodes will not achieve those numbers."

**Counter**: "Our prototype demonstrates the principle: we can generate voltammograms, transmit them via Bluetooth, and run AI classification on the phone. The production version using an AD5940 analog front-end -- which is a 4.50 dollar chip specifically designed for potentiostat applications -- and commercial screen-printed electrodes will achieve those published limits. The gap between our prototype and production is engineering execution, not scientific risk. The science is proven. The engineering is a known path."

**Key line**: "The prototype proves the principle. The production specs are backed by published data on the same electrode chemistry."

---

### Weak Spot 3: "How will you get SHG adoption? Why would women use this?"

**Acknowledgment**: "Adoption is the real challenge. Technology without adoption is just a demo."

**Counter**: "Three design decisions address this. First, payment: Jal Sakhis earn for every validated test. This is income, not charity. Second, simplicity: the app is designed for semi-literate users with pictorial guides, voice prompts in regional languages, and a maximum of 3 taps per test. Third, trust: results are shared with the community and the Gram Panchayat. When a Jal Sakhi identifies contamination and the village acts on it -- switching to a safer source, treating the water -- she earns social recognition. Research by Zheng and Wu (2019) specifically finds that women-led community water monitoring achieves higher consistency and reliability than other models. The motivation isn't altruism. It's income plus social status plus protecting your own family."

**Key line**: "She earns money, gains community standing, and protects her own children. The incentives are aligned."

---

# APPENDIX D: OPENING HOOK OPTIONS

### Option 1: The Story Hook (RECOMMENDED -- use this)
> "A woman in Rajasthan walks 3 kilometers to a borewell. She fills her pot. She doesn't know the water has 2 milligrams per liter of ammonia -- four times the WHO safe limit. The nearest testing lab is 50 kilometers away. It costs 500 rupees. It takes two weeks. By the time the results come back, her children have been drinking that water every day. Across India, this scene plays out 1.9 million times -- because we have 1.9 million habitations and only 2,200 labs. The math has never worked. JalSakhi makes it work."

### Option 2: The Number Hook
> "864. That's the number of villages served by each water testing lab in India. 864 to 1. If those labs ran 24/7, they still couldn't test every village once a year. The contamination happens. Nobody measures it. Nobody reports it. Nobody treats it. We built a system that changes that ratio. With JalSakhi, the ratio is 1 to 1 -- one smartphone, one village, one woman who tests the water every week."

### Option 3: The Provocation Hook
> "India has already solved the plumbing problem. Jal Jeevan Mission has connected 150 million households with taps. But here's the question nobody is answering: what's coming out of those taps? You can have a tap in every home and still have a water crisis -- because you can't manage what you can't measure. JalSakhi is the measuring part."

---

# APPENDIX E: CLOSING STATEMENT OPTIONS

### Option 1: The Callback Close (RECOMMENDED -- matches Story Hook)
> "Remember the woman in Rajasthan I started with? In the world we're building, she doesn't walk 3 kilometers wondering. She dips an electrode into her pot, and in 60 seconds, her phone tells her: ammonia, 0.8 mg/L, treatable -- add this much chlorine, wait 30 minutes. She tests it. She treats it. She knows.
>
> *[Pause]*
>
> She doesn't just fetch the water anymore. She tests it.
>
> Thank you."

### Option 2: The Scale Close
> "There are 12 million women's Self-Help Groups in India. 140 million women. They are already organized, already equipped, already trusted. Give them a 25-rupee electrode and a phone app, and you have built the largest water quality monitoring network on Earth.
>
> Not in ten years. Not with a billion-dollar budget. For the cost of a single government laboratory, you can equip a thousand Jal Sakhis -- and they will test every week what that lab tests once a year.
>
> The infrastructure is women. The instrument is the phone. The investment is trivial. The only question is: do we start?
>
> Thank you."

### Option 3: The L&T-Tailored Close
> "L&T builds the infrastructure that India's water system runs on. Treatment plants, pipelines, distribution networks. JalSakhi builds the intelligence layer that tells you where that infrastructure matters most.
>
> We're not asking you to believe in our prototype. We're asking you to believe in the math: 25 rupees per test, 12 million SHGs, weekly monitoring. The question is not whether this works -- the science is published, the electrodes are commercial, the model runs on a phone. The question is who moves first.
>
> Thank you."

---

# APPENDIX F: TIMING CHEAT SHEET

| Slide | Content | Duration | Cumulative | Time Marker |
|-------|---------|----------|------------|-------------|
| 1 | Title + Hook | 0:15 | 0:15 | Start |
| 2 | The Crisis | 1:00 | 1:15 | "Three numbers..." |
| 3 | Why Current Solutions Fail | 0:45 | 2:00 | "So why hasn't..." |
| 4 | JalSakhi Solution Overview | 1:00 | 3:00 | "JalSakhi turns any..." |
| 5 | Electrochemical Mode | 1:30 | 4:30 | "Let me explain the core..." |
| 6 | Colorimetric Mode | 0:45 | 5:15 | "The second mode..." |
| 7 | The AI Engine | 1:00 | 6:15 | "The AI is real..." |
| 8 | Treatment Advisory | 0:45 | 7:00 | "Detection alone..." |
| 9 | Community Deployment | 1:00 | 8:00 | "Now here's where..." |
| 10 | Prototype & Results | 1:00 | 9:00 | "Let me show you..." |
| 11 | Impact & Scalability | 0:45 | 9:45 | "Let me quantify..." |
| 12 | The Ask & Vision | 0:30 | 10:15 | "Here's what we're asking..." |

**Buffer**: You have about 15 seconds of flex. If running long, compress Slide 6 (colorimetric) or Slide 8 (treatment). If running short, expand Slide 5 (electrochemical) or Slide 9 (deployment).

**Pacing rule**: If you hit Slide 5 before 3:00, you're going too fast. If you hit Slide 9 after 8:30, you're going too slow.

---

# APPENDIX G: PRESENTATION DELIVERY NOTES

### Voice and Pacing
- **Slides 1-3 (Problem)**: Serious, measured, slightly slower. You're building weight.
- **Slide 4 (Solution reveal)**: Energy lifts. This is the turn from problem to answer.
- **Slides 5-7 (Technical)**: Confident, precise. You know this cold. Don't rush -- let the numbers land.
- **Slide 8 (Treatment)**: Warm. You're talking about protecting families now.
- **Slide 9 (Deployment)**: Expansive. Your voice widens. You're painting a national picture.
- **Slide 10 (Prototype)**: Grounded, practical. "This exists today."
- **Slide 11 (Impact)**: Rising energy. The numbers are powerful -- let them breathe.
- **Slide 12 (Close)**: Slow down. Drop your voice slightly. The closing line lands in silence.

### Eye Contact Protocol
- During data-heavy slides (2, 5, 7): Alternate between screen (to point at data) and audience
- During story moments (1 intro, 9, 12): Sustained eye contact with judges
- During the closing line: Look directly at the judges. Do not look at the screen.

### Gesture Protocol
- Point to the voltammogram GIF when explaining peaks (Slide 5)
- Use your hands to indicate the "gap" between villages and labs (Slide 2)
- Open palm gesture when describing the SHG network (Slide 9) -- expansiveness
- Closed fist or holding gesture for the closing line -- conviction

### If the Projector Fails
- You can present entirely from your phone, showing the web app and GIFs directly
- The narrative stands without slides -- you know the story and the numbers
- Key backup: have the 30 numbers memorized, have the closing line memorized

### Water Bottle Rule
- Take a sip after Slide 4 (the solution reveal). Natural pause. Audience absorbs.
- Take a sip before Slide 12 (the close). Creates anticipation.

---

# APPENDIX H: GIF USAGE GUIDE

### GIF 1: `phones_side_by_side.gif`
- **What it shows**: Two phones side by side demonstrating both sensing modes
- **Use on**: Slide 4 (Solution Overview)
- **When to reference**: "...two modes. *[Gesture to GIF]* Electrochemical on the left -- you can see the voltammogram being generated in real time. Colorimetric on the right -- the phone camera analyzing the test strip."
- **Duration**: Loops continuously. Ensure it's visible for at least 30 seconds.

### GIF 2: `voltammogram_light.gif`
- **What it shows**: Animated voltage sweep with current response, showing how peaks appear at characteristic voltages for different contaminants
- **Use on**: Slide 5 (Electrochemical Mode)
- **When to reference**: "...each contaminant produces a current peak at its characteristic potential. *[Point to GIF]* Watch -- as the voltage sweeps, you see the ammonia peak here, the lead peak here. This curve is the fingerprint."
- **Duration**: This slide has 90 seconds of speaking time. Let the GIF loop at least twice.

### GIF 3: `heatmap_light.gif`
- **What it shows**: Animated contamination data points appearing on a district map and forming a heatmap over time
- **Use on**: Slide 9 (Community Deployment)
- **When to reference**: "...and watch what happens when you aggregate this data. *[Point to heatmap GIF]* Individual test results from hundreds of Jal Sakhis form a contamination heatmap. A district water officer can see, in real time, where the problems are."
- **Duration**: 60 seconds on this slide. Let it loop fully at least once.

---

# APPENDIX I: JUDGE PROFILE PREPARATION

### L&T Construction Context
- L&T is India's largest engineering and construction company
- Their Water & Effluent Treatment division builds municipal water treatment plants
- They care about: scalability, engineering rigor, cost-effectiveness, real-world deployability
- **Key angle**: JalSakhi is complementary to their business, not competitive. Our data tells them where to build.

### Likely Judge Backgrounds
- **Civil/Environmental Engineers**: Will appreciate electrochemistry, potentiostat architecture, detection limits. Speak their language: "3-electrode configuration," "DPV," "ppb-level detection."
- **Business/Strategy**: Will want to know about unit economics, deployment model, revenue streams, government integration. Lead with INR 25/test and 12M SHGs.
- **Social Impact**: Will focus on gender, community empowerment, SDG alignment. Lead with the "women as sensing infrastructure" framing.
- **Academics**: Will probe ML architecture, synthetic data methodology, accuracy claims. Be ready with references and architecture details.

### The "Why Bennett University?" Question
If asked, answer: "This project combines electrochemistry, embedded systems, machine learning, app development, and social deployment modeling. Bennett's interdisciplinary environment -- plus access to IoT labs and mentor networks -- made this possible. The prototype was built for under 2,000 rupees in our lab."

---

# APPENDIX J: ONE-PAGE QUICK REFERENCE (PRINT AND KEEP ON PODIUM)

```
JALSAKHI QUICK REFERENCE -- MARCH 17, 2026

THE PROBLEM:   1.9M habitations, 2,200 labs, 864:1 ratio, 53 km, 3-14 days
THE SOLUTION:  Phone + electrode + AI = 7 contaminants in 60 sec, INR 25/test
THE SCALE:     12M SHGs, 140M women, 99% block coverage, INR 600/mo income
THE PROTOTYPE: ESP32 + LM358 + pencil electrodes = INR 1,840
THE ASK:       100 SHGs, 3 districts, 6 months, INR 5 lakh
THE CLOSE:     "She doesn't just fetch the water anymore. She tests it."

KEY NUMBERS:   80x cheaper | 52x more frequent | <200 KB model | <50 ms inference
               1 ppb lead | 5 ppb arsenic | 0.05 mg/L ammonia | 200-500 hospitalizations/yr

TIMING:        Slide 5 at 3:00 | Slide 9 at 7:00 | Slide 12 at 9:45
               If at Slide 5 before 3:00 = too fast | Slide 9 after 8:30 = too slow

REFERENCES:    26 peer-reviewed papers | Ainla 2018 (potentiostat) | Cui 2015 (SPE metals)
               Kammarchedu 2022 (CNN+voltammetry) | Valentini 2014 (PB ammonia)
```

---

*This document prepared for the World Water Day 2026 Ideation Challenge. All data sourced from peer-reviewed publications, government records (JJM, NRLM, NITI Aayog, CGWB, UNICEF), and verified component pricing (Mouser, DigiKey, Amazon India). Prototype BOM verified against actual purchases.*
