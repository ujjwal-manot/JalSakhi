"""
JalSakhi - Ultimate Presentation Prep Guide PDF
10-minute presentation + 5-minute Q&A
World Water Day Ideation Challenge 2026 - Round 2
"""

from fpdf import FPDF
import os

class PrepPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 5, "JalSakhi | Round 2 Presentation Prep | World Water Day 2026", align="L")
            self.ln(2)
            self.set_draw_color(0, 168, 181)
            self.set_line_width(0.5)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title, r=13, g=43, b=69):
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(r, g, b)
        self.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(0, 168, 181)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(4)

    def sub_title(self, title, r=27, g=107, b=147):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(r, g, b)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def sub_sub_title(self, title, r=0, g=168, b=181):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(r, g, b)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text, bold=False):
        self.set_font("Helvetica", "B" if bold else "", 10)
        self.set_text_color(45, 45, 45)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def bullet(self, text, indent=15):
        x = self.get_x()
        self.set_font("Helvetica", "", 10)
        self.set_text_color(0, 168, 181)
        self.cell(indent, 5.5, "-")
        self.set_text_color(45, 45, 45)
        self.multi_cell(0, 5.5, text)
        self.ln(0.5)

    def script_line(self, timing, text):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(255, 107, 53)
        self.cell(18, 5.5, timing)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(45, 45, 45)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def highlight_box(self, text, r=255, g=243, b=224):
        self.set_fill_color(r, g, b)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(139, 69, 0)
        y_start = self.get_y()
        self.set_x(12)
        self.multi_cell(186, 6, text, fill=True)
        self.ln(2)

    def tip_box(self, text):
        self.set_fill_color(232, 244, 253)
        self.set_font("Helvetica", "BI", 10)
        self.set_text_color(27, 107, 147)
        self.set_x(12)
        self.multi_cell(186, 6, f"TIP: {text}", fill=True)
        self.ln(2)

    def warning_box(self, text):
        self.set_fill_color(253, 232, 232)
        self.set_font("Helvetica", "BI", 10)
        self.set_text_color(200, 50, 50)
        self.set_x(12)
        self.multi_cell(186, 6, f"WARNING: {text}", fill=True)
        self.ln(2)

    def qa_pair(self, question, answer):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(13, 43, 69)
        self.multi_cell(0, 5.5, f"Q: {question}")
        self.ln(1)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(45, 45, 45)
        self.multi_cell(0, 5.5, f"A: {answer}")
        self.ln(3)


# ── BUILD PDF ─────────────────────────────────────────────
pdf = PrepPDF()
pdf.alias_nb_pages()

# ══════════════════════════════════════════════════════════
# COVER PAGE
# ══════════════════════════════════════════════════════════
pdf.add_page()
pdf.ln(30)
pdf.set_font("Helvetica", "B", 36)
pdf.set_text_color(13, 43, 69)
pdf.cell(0, 15, "JalSakhi", align="C", new_x="LMARGIN", new_y="NEXT")

pdf.set_font("Helvetica", "", 14)
pdf.set_text_color(0, 168, 181)
pdf.cell(0, 8, "Ultimate Presentation Prep Guide", align="C", new_x="LMARGIN", new_y="NEXT")

pdf.ln(5)
pdf.set_draw_color(0, 168, 181)
pdf.set_line_width(1)
pdf.line(70, pdf.get_y(), 140, pdf.get_y())
pdf.ln(8)

pdf.set_font("Helvetica", "", 12)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 7, "World Water Day Ideation Challenge 2026 - Round 2", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 7, "L&T Construction Water & Effluent Treatment", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 7, 'Theme: "Water and Gender"', align="C", new_x="LMARGIN", new_y="NEXT")

pdf.ln(10)
pdf.set_font("Helvetica", "B", 12)
pdf.set_text_color(13, 43, 69)
pdf.cell(0, 7, "Team JalSakhi | Bennett University", align="C", new_x="LMARGIN", new_y="NEXT")

pdf.ln(5)
pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(255, 107, 53)
pdf.cell(0, 7, "10-Minute Presentation + 5-Minute Q&A", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 7, "Virtual Presentation: 17 March 2026", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 7, "Submission Deadline: 16 March 2026, 23:59", align="C", new_x="LMARGIN", new_y="NEXT")

pdf.ln(15)
pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(150, 150, 150)
pdf.cell(0, 6, "Contents: Full Script | Slide-by-Slide Speaker Notes | Q&A Preparation", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 6, "Judge Psychology | Do's & Don'ts | Last-Minute Checklist", align="C", new_x="LMARGIN", new_y="NEXT")


# ══════════════════════════════════════════════════════════
# TABLE OF CONTENTS
# ══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("Table of Contents")
pdf.ln(3)

toc = [
    "1. Presentation Overview & Timing",
    "2. Full Scripted Talk (10 Minutes)",
    "   Segment 1: The Hook (0:00 - 1:00)",
    "   Segment 2: The Problem (1:00 - 3:00)",
    "   Segment 3: The Solution (3:00 - 6:00)",
    "   Segment 4: The Platform & Deployment (6:00 - 8:00)",
    "   Segment 5: Results & Impact (8:00 - 9:00)",
    "   Segment 6: The Ask (9:00 - 10:00)",
    "3. Slide-by-Slide Speaker Notes",
    "4. Q&A Preparation (25 Questions)",
    "5. Judge Psychology & Strategy",
    "6. Presentation Do's & Don'ts",
    "7. Day-of Checklist",
    "8. Key Numbers to Memorize",
]

for item in toc:
    if item.startswith("   "):
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 6, item, new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(13, 43, 69)
        pdf.cell(0, 7, item, new_x="LMARGIN", new_y="NEXT")


# ══════════════════════════════════════════════════════════
# SECTION 1: OVERVIEW & TIMING
# ══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("1. Presentation Overview & Timing")

pdf.sub_title("Time Allocation")
pdf.body_text("Total time: 10 minutes presentation + 5 minutes Q&A")
pdf.body_text("You MUST finish at 10:00. Going over signals poor preparation and disrespects judges' time.")
pdf.ln(2)

timing_data = [
    ("0:00 - 1:00", "THE HOOK", "1 min", "Emotional story + problem scale"),
    ("1:00 - 3:00", "THE PROBLEM", "2 min", "Measurement gap + gender dimension"),
    ("3:00 - 6:00", "THE SOLUTION", "3 min", "Two modes + architecture + methodology"),
    ("6:00 - 8:00", "PLATFORM & DEPLOY", "2 min", "Community intelligence + SHG model"),
    ("8:00 - 9:00", "RESULTS & IMPACT", "1 min", "What's validated + impact numbers"),
    ("9:00 - 10:00", "THE ASK", "1 min", "Pilot proposal + closing"),
]

pdf.set_font("Helvetica", "B", 9)
pdf.set_fill_color(13, 43, 69)
pdf.set_text_color(255, 255, 255)
pdf.cell(30, 7, "Time", fill=True, border=1)
pdf.cell(35, 7, "Segment", fill=True, border=1)
pdf.cell(20, 7, "Duration", fill=True, border=1)
pdf.cell(0, 7, "Content", fill=True, border=1, new_x="LMARGIN", new_y="NEXT")

for i, (time, seg, dur, content) in enumerate(timing_data):
    if i % 2 == 0:
        pdf.set_fill_color(240, 248, 255)
    else:
        pdf.set_fill_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(255, 107, 53)
    pdf.cell(30, 7, time, fill=True, border=1)
    pdf.set_text_color(13, 43, 69)
    pdf.cell(35, 7, seg, fill=True, border=1)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(45, 45, 45)
    pdf.cell(20, 7, dur, fill=True, border=1)
    pdf.cell(0, 7, content, fill=True, border=1, new_x="LMARGIN", new_y="NEXT")

pdf.ln(5)
pdf.sub_title("Presentation Format")
pdf.bullet("Virtual presentation (meeting link will be shared)")
pdf.bullet("10-12 slides excluding title (you have 12)")
pdf.bullet("PPT must be submitted by 16 March 23:59 to krishmadhu@Lntecc.com")
pdf.bullet("File name: JalSakhi_Bennett University.pptx")
pdf.bullet("Idea presented by team lead and members (NOT mentors)")
pdf.bullet("Must be original and not published elsewhere")

pdf.ln(3)
pdf.warning_box("Presentations submitted after deadline will be DISQUALIFIED. Submit by 16 March 23:59 sharp.")


# ══════════════════════════════════════════════════════════
# SECTION 2: FULL SCRIPTED TALK
# ══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("2. Full Scripted Talk (10 Minutes)")
pdf.body_text("Below is a word-for-word script. You don't need to memorize it exactly, but practice it enough that you can deliver the key points naturally. The timing markers are critical.")

pdf.ln(3)
pdf.highlight_box("GOLDEN RULE: Every sentence must either (1) state the problem, (2) explain the solution, or (3) prove it works. Cut everything else.")

# ── SEGMENT 1: THE HOOK ──
pdf.ln(3)
pdf.sub_title("Segment 1: THE HOOK [0:00 - 1:00]")
pdf.sub_sub_title("Slide: Problem Statement")

pdf.body_text('[OPEN WITH STORY - speak slowly, let it land]', bold=True)
pdf.ln(1)

script_lines_1 = [
    ("0:00", '"Good morning/afternoon, everyone."'),
    ("0:05", '"Picture this. A woman in rural Bihar notices something off about her borewell water. It smells different. Her children have been complaining of stomach aches."'),
    ("0:18", '"The nearest accredited lab is 53 kilometers away. It costs 500 rupees. Results take 10 days."'),
    ("0:27", '"So what does she do? She does what 200 million rural women in India do. She gives the water to her family and hopes for the best."'),
    ("0:38", '"By the time results come back -- if they ever do -- her children have been drinking contaminated water for two weeks."'),
    ("0:48", '"This is not a hypothetical. This is the reality for 1.9 million rural habitations served by just 2,200 testing labs."'),
]

for timing, text in script_lines_1:
    pdf.script_line(timing, text)

pdf.tip_box("Pause after 'hopes for the best.' Let the silence do the work. Don't rush into the numbers.")

# ── SEGMENT 2: THE PROBLEM ──
pdf.add_page()
pdf.sub_title("Segment 2: THE PROBLEM [1:00 - 3:00]")
pdf.sub_sub_title("Slide: Problem Statement (continued)")

script_lines_2 = [
    ("1:00", '"Let me put this in perspective. India has 1.9 million rural habitations. We have 2,200 water testing labs. That is one lab for every 864 habitations."'),
    ("1:15", '"A single comprehensive test costs 500 to 2,000 rupees. Turnaround is 3 to 14 days. Most villages get tested once a year -- if at all."'),
    ("1:28", '"Meanwhile, women and girls spend 1.4 billion hours every year collecting water. That is 160,000 years of human life, every single year, walking to sources they cannot verify are safe."'),
    ("1:45", '[PAUSE] "The Jal Jeevan Mission is connecting taps to every household. But a tap connection is not the same as safe water. You need continuous monitoring. And right now, that monitoring infrastructure simply does not exist."'),
    ("2:05", '"You cannot manage what you cannot measure. And India -- with all its progress -- cannot measure its water."'),
    ("2:15", '[TRANSITION] "We built JalSakhi to close this gap. Not with another expensive lab. Not with another IoT sensor box. But by turning the device that 800 million Indians already carry -- their smartphone -- into a field water laboratory."'),
]

for timing, text in script_lines_2:
    pdf.script_line(timing, text)

pdf.tip_box("The '1.4 billion hours' number is your emotional anchor. Say it slowly. Let judges absorb it.")

# ── SEGMENT 3: THE SOLUTION ──
pdf.sub_title("Segment 3: THE SOLUTION [3:00 - 6:00]")
pdf.sub_sub_title("Slides: Solution Overview + Architecture + Methodology")

script_lines_3a = [
    ("3:00", '"JalSakhi has two sensing modes."'),
    ("3:05", '"Mode one: electrochemical fingerprinting. A pocket-sized potentiostat dongle -- costing just 1,200 rupees -- connects to your phone via Bluetooth. You dip a disposable electrode into the water sample. The device runs a voltammetric scan -- a controlled voltage sweep -- and measures the current response."'),
    ("3:25", '"Each contaminant -- ammonia, lead, arsenic, nitrate, iron, fluoride -- produces a unique electrochemical signature. A 1D convolutional neural network on the phone reads these signatures and returns concentrations in under 60 seconds. No internet needed. Fully offline."'),
    ("3:48", '"Mode two: colorimetric strip analysis. For rapid screening, you photograph a commercial test strip against our calibration card. Computer vision corrects for your phone camera and lighting conditions. A trained model extracts concentrations. Zero additional hardware. Just strips and a phone."'),
    ("4:08", '[ADVANCE SLIDE to Architecture]'),
    ("4:10", '"The architecture has three layers. The sensing layer -- electrodes and strips. The edge AI layer -- signal processing and classification running entirely on the smartphone. And the cloud intelligence layer -- where individual tests from hundreds of women aggregate into district-level contamination maps."'),
]

for timing, text in script_lines_3a:
    pdf.script_line(timing, text)

pdf.add_page()
pdf.sub_sub_title("Methodology Deep-Dive [4:30 - 6:00]")

script_lines_3b = [
    ("4:30", '[ADVANCE to Methodology slide]'),
    ("4:32", '"Let me go deeper on the electrochemistry. This is not a generic ADC board. Our potentiostat implements proper three-electrode voltammetry -- working, reference, and counter electrodes. The signal processing pipeline runs Savitzky-Golay smoothing, asymmetric least squares baseline correction, and derivative-based peak detection before data even reaches the phone."'),
    ("4:55", '"Our detection limits are real. Ammonia at 0.05 milligrams per liter -- that is 10 times more sensitive than the WHO guideline. Lead at 1 part per billion. Arsenic at 5 parts per billion. These numbers come from published literature on screen-printed electrodes -- Ainla 2018, Nemiroski 2014, Cui 2015."'),
    ("5:20", '"The AI is also real. A 1D-CNN with dual heads -- one for multi-label detection, one for concentration regression. Less than 200 kilobytes. Less than 50 milliseconds inference. INT8 quantized TFLite. And a confidence scoring system that says RETEST when it is not sure, rather than giving a false safe reading."'),
    ("5:45", '[ADVANCE to Novelty slide]'),
    ("5:47", '"What makes this fundamentally different from existing IoT water sensors? Three things. One: disposable electrodes eliminate calibration drift entirely. Two: the smartphone is the instrument -- we leverage computing power the user already owns. Three: community intelligence -- one device tests hundreds of sources, and that data aggregates into contamination maps no lab network can provide."'),
]

for timing, text in script_lines_3b:
    pdf.script_line(timing, text)

pdf.tip_box("If running short on time, cut the methodology deep-dive (4:32-4:55) and jump straight to detection limits. The numbers are what judges remember.")

# ── SEGMENT 4: PLATFORM & DEPLOYMENT ──
pdf.add_page()
pdf.sub_title("Segment 4: PLATFORM & DEPLOYMENT [6:00 - 8:00]")
pdf.sub_sub_title("Slides: Categories + Deployment Model")

script_lines_4 = [
    ("6:00", '[ADVANCE to 5 Categories slide]'),
    ("6:02", '"One thing I want to highlight -- most teams in this competition address one category. JalSakhi covers all five. Ammonia mitigation through our Prussian Blue electrode. Water neutrality through community water budgeting. Smart distribution through crowdsourced contamination mapping. Affordable sensing -- that is our core. And AI water management through edge plus cloud intelligence."'),
    ("6:30", '[ADVANCE to Deployment slide]'),
    ("6:32", '"Now, the deployment model -- and this is where the gender argument becomes structural, not decorative."'),
    ("6:38", '"India has 12 million women Self-Help Groups under NRLM. 140 million members. Present in 99 percent of blocks. They already have bank accounts, smartphones, training infrastructure, and government linkages."'),
    ("6:55", '"We designate 2-3 women per SHG as Jal Sakhis -- Water Guardians. They test community water sources weekly. Results feed into village water registers, then district dashboards, then Jal Jeevan Mission systems."'),
    ("7:12", '"Jal Sakhis earn 10 to 20 rupees per validated test via UPI. This is not volunteer work. This is a livelihood. At scale, 1,000 Jal Sakhis put 72 lakh rupees per year into women\'s hands."'),
    ("7:30", '"The deployment happens in three phases. Phase one: 5 SHGs in one gram panchayat as proof of concept. Phase two: 100 SHGs across 3 blocks as a pilot. Phase three: 5,000 SHGs across one state."'),
    ("7:48", '"Women are not just end users of this system. They ARE the system. They are the sensing infrastructure of India\'s water quality network."'),
]

for timing, text in script_lines_4:
    pdf.script_line(timing, text)

pdf.highlight_box("KEY MOMENT: 'Women are not just end users. They ARE the system.' -- Deliver this with conviction. This is the line judges will remember from your entire presentation.")

# ── SEGMENT 5: RESULTS & IMPACT ──
pdf.sub_title("Segment 5: RESULTS & IMPACT [8:00 - 9:00]")
pdf.sub_sub_title("Slides: Results + Impact")

script_lines_5 = [
    ("8:00", '[ADVANCE to Results slide]'),
    ("8:02", '"What have we validated so far? Every technical claim is backed by 26 peer-reviewed references. All components are commercially available and sourced. Published DPV on screen-printed electrodes shows greater than 95 percent correlation with lab ICP-MS instruments."'),
    ("8:18", '"Our prototype uses an ESP32 with op-amps and DIY pencil graphite electrodes -- total cost under 2,000 rupees. At production scale, the full AD5940-based dongle costs 14 dollars -- about 1,200 rupees."'),
    ("8:32", '[ADVANCE to Impact slide]'),
    ("8:34", '"The impact maps directly to the problem. Health: 200 to 500 hospitalizations prevented per year from early contamination detection. Time: 450,000 hours of women\'s labor saved annually. Income: 72 lakh rupees per year into women\'s hands. And governance: 52x improvement in monitoring frequency -- weekly instead of annual."'),
]

for timing, text in script_lines_5:
    pdf.script_line(timing, text)

# ── SEGMENT 6: THE ASK ──
pdf.add_page()
pdf.sub_title("Segment 6: THE ASK [9:00 - 10:00]")
pdf.sub_sub_title("Slide: The Ask (closing slide)")

script_lines_6 = [
    ("9:00", '[ADVANCE to Ask slide - dark background, dramatic shift]'),
    ("9:02", '"So here is our ask."'),
    ("9:05", '"A pilot with 100 Self-Help Groups across 3 ammonia-affected districts. Bhagalpur in Bihar, Unnao in UP, and Guntur in Andhra Pradesh -- all with documented ammonia contamination."'),
    ("9:20", '"Duration: 6 months. Investment: 5 lakh rupees."'),
    ("9:28", '"The deliverable: a validated contamination intelligence dashboard with greater than 90 percent correlation to NABL lab results."'),
    ("9:38", '[PAUSE - look at camera]'),
    ("9:40", '"I want to close with one thought for L&T specifically. L&T builds water treatment plants. But where should you build them? Today, that decision relies on outdated, sparse lab data. JalSakhi gives you the demand signal -- real-time contamination intelligence at scale. We are not competing with your infrastructure business. We are making it smarter."'),
    ("9:58", '"Thank you."'),
]

for timing, text in script_lines_6:
    pdf.script_line(timing, text)

pdf.highlight_box("END EXACTLY AT 10:00. Do NOT say 'that is all' or 'I think that covers it.' Just: 'Thank you.' Then silence. Let them come to you.")

pdf.tip_box("The L&T angle in the close is CRITICAL. You are speaking to L&T judges. 'We make your business smarter' is what they want to hear.")


# ══════════════════════════════════════════════════════════
# SECTION 3: SLIDE-BY-SLIDE SPEAKER NOTES
# ══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("3. Slide-by-Slide Speaker Notes")

slides_notes = [
    ("Title Slide", "0:00", "Don't linger. Say your name, team, university. Move on in 10 seconds."),
    ("Slide 1: Problem Statement", "0:10 - 2:15", "This is your longest segment. Open with the Bihar woman story. Then hit the 4 stats. Then gender dimension. Close with the punchline. DO NOT rush the story."),
    ("Slide 2: Solution Overview", "2:15 - 3:48", "Two modes side by side. Point to each. Emphasize the zero-hardware colorimetric mode -- judges love low barrier to entry. Mention BLE, not USB-C."),
    ("Slide 3: Architecture", "3:48 - 4:30", "Three layers diagram. Don't read everything. Just: sensing, edge AI, cloud intelligence. Flow is bottom-up. Spend max 40 seconds here."),
    ("Slide 4: Electrochemical Methodology", "4:30 - 5:20", "This is your credibility slide. Mention three-electrode potentiostat (not generic ADC). Name-drop detection limits. Name-drop one reference. Show you know the science."),
    ("Slide 5: AI Pipeline", "5:20 - 5:47", "Four boxes. Hit the CNN architecture in one sentence. Emphasize <200KB, <50ms, offline. The confidence scoring (RETEST when unsure) is a differentiator."),
    ("Slide 6: Novelty", "5:47 - 6:02", "Comparison table. Don't read every row. Pick 2-3 most striking: cost ($14 vs $2000), disposable = no drift, one device tests hundreds of sources."),
    ("Slide 7: All 5 Categories", "6:02 - 6:30", "POWER SLIDE. 'Most teams pick one. We cover all five.' Run through quickly. This is a wow moment, not a deep dive."),
    ("Slide 8: Resources/Budget", "6:30 - 7:12", "Mention INR 4K prototype, then jump to scale economics. The INR 25 vs INR 2000 stat is your killer line. Say it once, clearly."),
    ("Slide 9: Results Achieved", "7:12 - 8:32", "Credibility: 26 references, >95% correlation published, all parts sourced. Don't oversell -- acknowledge this is a competition prototype. Honesty builds trust."),
    ("Slide 10: Deployment Model", "8:32 - 9:00", "SHG numbers are impressive. 12 million, 140 million members. This is not hypothetical infrastructure. Show the 3 phases quickly."),
    ("Slide 11: Impact / Key Inferences", "Covered in Seg 5", "4 impact cards. Read the big numbers only. Government alignment gives policy credibility. End with L&T angle."),
    ("Slide 12: The Ask", "9:00 - 10:00", "Dark slide. Dramatic shift. Three numbers: 100 SHGs, 6 months, 5 lakh. Deliverable. L&T close. Thank you. STOP."),
]

for title, timing, note in slides_notes:
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(13, 43, 69)
    pdf.cell(70, 6, title)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(255, 107, 53)
    pdf.cell(0, 6, f"[{timing}]", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 5.5, note)
    pdf.ln(2)


# ══════════════════════════════════════════════════════════
# SECTION 4: Q&A PREPARATION
# ══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("4. Q&A Preparation (25 Questions)")
pdf.body_text("You have 5 minutes of Q&A. Expect 3-5 questions. Here are 25 likely questions with tight answers. Practice saying each answer in under 45 seconds.")

pdf.ln(2)
pdf.sub_title("Technical Questions")

pdf.qa_pair(
    "How accurate is electrochemical sensing vs lab instruments?",
    "Published literature shows DPV on screen-printed electrodes achieves greater than 95% correlation with ICP-MS for heavy metals. Our accuracy target is plus-minus 10% of lab values for regulatory-relevant contaminants. We validate this through the pilot by sending split samples to NABL labs."
)

pdf.qa_pair(
    "Why not just use commercial test kits like Hach or LaMotte?",
    "Commercial kits cost $500+ and measure one parameter at a time. We detect 7+ contaminants from one voltammetric scan. More importantly, they don't aggregate data. Individual test results are useful, but the real value is community intelligence -- contamination maps that no kit can provide."
)

pdf.qa_pair(
    "How do you handle electrode variability between batches?",
    "Two mechanisms. First, every SPE batch is characterized with known standards. Second, the ML model is trained on voltammograms from multiple batches, learning to be invariant to electrode-to-electrode variation. This is called domain adaptation. The metadata input -- TDS, pH, temperature -- further corrects for environmental variation."
)

pdf.qa_pair(
    "What happens if the ML model gives a wrong reading?",
    "Our confidence scoring system combines model probability, signal-to-noise ratio, and scan quality. If any of these are low, the app shows RETEST rather than a potentially wrong result. We also have an autoencoder anomaly detector that flags unusual voltammograms as possible matrix interference. We would rather say 'we are not sure, test again' than give a false safe reading."
)

pdf.qa_pair(
    "Can this work without internet?",
    "Yes. Both the signal processing and ML classification run entirely on the smartphone. The TFLite model is less than 200 kilobytes and runs in under 50 milliseconds. Results sync to the cloud when connectivity is available, but the core detection is fully offline."
)

pdf.qa_pair(
    "Why ESP32 and not Arduino or Raspberry Pi?",
    "ESP32 has built-in BLE, WiFi, DAC, and 12-bit ADC in a single $5 chip. Arduino lacks BLE and adequate ADC resolution. Raspberry Pi is overkill -- too expensive, too power-hungry, and unnecessary for this application. At production scale, we move to the AD5940 dedicated electrochemical AFE plus STM32, which gives us 16-bit resolution and proper potentiostat control."
)

pdf.qa_pair(
    "How do pencil graphite electrodes compare to commercial SPEs?",
    "Pencil graphite is a well-published working electrode material -- there are papers in Electrochimica Acta validating this. For the prototype, it demonstrates the principle. For production, we use proper screen-printed electrodes with target-specific modifications -- Prussian Blue for ammonia, bismuth film for lead, gold nanoparticles for arsenic. The electrode material does not change the fundamental approach."
)

pdf.add_page()
pdf.sub_title("Business & Deployment Questions")

pdf.qa_pair(
    "What is the business model?",
    "Three revenue streams. First: SPE consumables -- recurring revenue, 60-70% margin at scale. Second: municipal dashboard subscriptions -- SaaS model, 50,000 rupees per district per month. Third: contamination intelligence data for water utilities, real estate, and insurance. Women testers earn per validated test -- this is a livelihood, not volunteer work."
)

pdf.qa_pair(
    "Why women Self-Help Groups specifically?",
    "Three reasons. One: infrastructure already exists -- 12 million SHGs, 140 million members, 99% block coverage, smartphones, bank accounts. Two: women manage household water -- this formalizes their existing expertise. Three: SHGs are permanent community institutions, unlike project-based NGOs. We are not building new infrastructure. We are activating what already exists."
)

pdf.qa_pair(
    "How do you ensure data quality from community testers?",
    "Multiple layers. Device-level: each dongle has an Ed25519 cryptographic key. Every test result is signed. Server-side: statistical checks flag identical readings, impossible chemistry, extreme outliers, and excessive test frequency. Suspicious data is quarantined. Split-sample verification against NABL labs during the pilot validates the whole chain."
)

pdf.qa_pair(
    "What if SHG women cannot use the technology?",
    "The app is designed for minimal literacy. Pictorial guides, voice prompts in local languages. The testing protocol is physically simple -- dip electrode, wait, read result on screen. NRLM already trains SHG women on smartphone-based financial apps. A 2-day training protocol covers water testing. We are not the first to trust rural women with technology -- UPI proved they can adopt it."
)

pdf.qa_pair(
    "How do you scale electrode manufacturing?",
    "Screen-printed electrodes are manufactured using standard thick-film printing -- the same process used for printed circuit boards and solar cells. At 100,000 kit scale, SPE cost drops to $0.20 each. We partner with existing SPE manufacturers like Metrohm DropSens or Zimmer and Peacock, or set up local screen printing in India."
)

pdf.qa_pair(
    "What is the regulatory pathway?",
    "For community-level screening, we do not need medical device approval since we are testing water, not humans. We align with BIS standards for water quality (IS 10500). The pilot will benchmark against NABL lab results to establish equivalence. For integration with Jal Jeevan Mission, we work through the state NRLM offices which already govern SHG activities."
)

pdf.add_page()
pdf.sub_title("Competition-Specific Questions")

pdf.qa_pair(
    "How is this different from WaterCanary, Lishtot, or pHox?",
    "Those are single-parameter or binary safe-unsafe indicators. We do quantitative multi-analyte forensics -- 7 contaminants with specific concentrations. More importantly, the platform layer -- crowdsourced contamination mapping from thousands of community testers building district-level intelligence -- does not exist anywhere. We are not just a sensor. We are an intelligence system."
)

pdf.qa_pair(
    "You claim to cover all 5 categories. Is that realistic?",
    "The platform architecture inherently covers all five. Ammonia detection is one of our 7 contaminants. Water neutrality comes from tracking consumption patterns. Smart distribution comes from mapping contamination across pipeline networks. Affordable sensing is our core value proposition. And AI management is our edge plus cloud intelligence stack. One platform, five applications."
)

pdf.qa_pair(
    "How does this help L&T specifically?",
    "L&T builds water treatment infrastructure. The biggest question in infrastructure investment is WHERE. Today, that decision relies on sparse, outdated lab data. JalSakhi provides real-time contamination intelligence at scale -- the demand signal for where to build, what to treat, and whether existing plants are working. We are complementary to L&T's infrastructure business, not competing with it."
)

pdf.qa_pair(
    "What is your unfair advantage?",
    "Three things. First, the electrode chemistry -- published, validated, specific to Indian water contaminants. Second, the deployment channel -- 12 million SHGs that no startup can replicate. Third, the data network effect -- every test makes the contamination map more valuable. The more women test, the smarter the system gets. This is a moat that grows with usage."
)

pdf.qa_pair(
    "What are the biggest risks?",
    "Honest answer: electrode performance in real-world conditions with complex water matrices. That is exactly what the pilot is designed to validate. The science works in published lab conditions. We need to prove it works in Bihar borewell water. Second risk: adoption friction with SHG women. We mitigate this through the financial incentive -- 600 rupees per month is meaningful supplementary income."
)

pdf.qa_pair(
    "Why should we fund this over a simpler solution?",
    "Simpler solutions exist -- commercial test strips for example. But they do not aggregate. They do not build intelligence. They do not scale. India's water problem is not sensing -- it is the gap between individual measurements and system-level understanding. JalSakhi bridges that gap. The potentiostat is the tool. The intelligence platform is the product."
)

pdf.add_page()
pdf.sub_title("Curveball Questions")

pdf.qa_pair(
    "Do you have any actual test results from real water samples?",
    "The prototype demonstrates the sensing principle with known standard solutions. For real-world validation with actual contaminated water samples, that is precisely what Phase 1 of the pilot is designed for -- 5 SHGs, 30 water sources, 360 data points, benchmarked against NABL lab results. We are transparent about this: we have validated the science from published literature, and now we need field validation."
)

pdf.qa_pair(
    "Is the AI actually necessary? Could you just use threshold-based detection?",
    "For simple cases, yes. But real water is a complex matrix. Multiple contaminants create overlapping peaks in voltammograms. Temperature, pH, and dissolved solids shift peak positions. The CNN handles this multivariate complexity in a way that fixed thresholds cannot. The confidence scoring is also AI-driven -- it knows when it does not know, which is more important than being right."
)

pdf.qa_pair(
    "How do you prevent gaming or fake test results?",
    "Cryptographic signing at the hardware level -- each dongle has a unique Ed25519 key. Server-side statistical checks catch impossible chemistry, identical sequential readings, GPS inconsistencies, and excessive test frequency. During the pilot, 10% of tests get split-sample verification against NABL labs. The incentive structure also helps -- payment is per validated test, not per test submitted."
)

pdf.qa_pair(
    "What if someone copies your approach?",
    "The hardware design is replicable -- and that is fine. Our moat is the data network. Once 1,000 SHGs are testing weekly, we have a contamination dataset that no competitor can replicate without the same deployment infrastructure. The SHG relationships, the municipal dashboard contracts, and the growing intelligence platform create switching costs. First-mover advantage in community deployment is real."
)

pdf.qa_pair(
    "What is your team's qualification for this?",
    "[ADAPT THIS TO YOUR ACTUAL TEAM] We are engineering students at Bennett University with backgrounds in electronics, signal processing, and machine learning. What we bring is not decades of water chemistry experience -- we bring first-principles engineering thinking and the ability to integrate published science into a deployable system. Every technical claim in our presentation is backed by peer-reviewed research."
)

pdf.qa_pair(
    "How do you handle the cold-start problem -- no data initially?",
    "Two approaches. First: synthetic training data from physics-based voltammogram generators. Gaussian peak models combined with Randles-Sevcik kinetics create realistic training sets before real data exists. Second: during the pilot, every test is cross-validated against lab results, which builds the real-world training dataset rapidly. 360 validated data points in Phase 1 alone."
)

pdf.qa_pair(
    "What happens when SPEs expire or get wet?",
    "SPEs are individually sealed in foil pouches with desiccant -- standard practice from manufacturers. Shelf life is typically 12-18 months. Each SPE is used once and discarded. There is no degradation concern during use because the test takes 60 seconds. If an electrode is visibly damaged or wet before use, the fault detection system catches it -- impedance check before scan."
)


# ══════════════════════════════════════════════════════════
# SECTION 5: JUDGE PSYCHOLOGY
# ══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("5. Judge Psychology & Strategy")

pdf.sub_title("Who Are Your Judges?")
pdf.body_text("L&T Construction Water & Effluent Treatment Domestic SBG + L&T EduTech. These are engineers and infrastructure professionals. They understand:")
pdf.bullet("Large-scale project execution and deployment challenges")
pdf.bullet("Real engineering vs. handwaving (they will spot fake technical depth)")
pdf.bullet("Cost structures and scale economics")
pdf.bullet("Government project integration (Jal Jeevan Mission, etc.)")
pdf.bullet("Business viability -- they think in terms of contracts and revenue")

pdf.ln(3)
pdf.sub_title("What Judges Want to See")

judge_wants = [
    ("REAL ENGINEERING", "Not 'we will use AI.' Specific: 1D-CNN, Conv1D(32,k=7), TFLite INT8, <200KB. Name-drop one paper. Show you understand the science, not just the buzzwords."),
    ("HONEST NUMBERS", "INR 25/test is powerful BECAUSE it is specific. Vague claims ('very cheap') are worthless. Every number should be traceable to a source."),
    ("FEASIBILITY", "Can this actually be built? You have a BOM with part numbers. You have published references. You have a prototype under INR 2,000. This is credible."),
    ("SCALE PATH", "12 million SHGs is not your invention -- it is existing infrastructure. This makes the scale argument believable. 'We deploy through what already exists.'"),
    ("L&T RELEVANCE", "They build treatment plants. You provide demand intelligence. This is complementary. Make them see JalSakhi as a tool that makes THEIR business better."),
]

for title, desc in judge_wants:
    pdf.sub_sub_title(title)
    pdf.body_text(desc)
    pdf.ln(1)

pdf.sub_title("What Judges Do NOT Want")
pdf.bullet("Long introductions about yourself or your university")
pdf.bullet("Slides full of text that you read verbatim")
pdf.bullet("Vague claims: 'revolutionary', 'game-changing', 'cutting-edge'")
pdf.bullet("Overselling: 'this will solve India's water crisis'")
pdf.bullet("Ignoring limitations or pretending you have no risks")

pdf.ln(3)
pdf.highlight_box("THE HONESTY PRINCIPLE: Judges trust teams that acknowledge limitations. Saying 'we need field validation -- that is what the pilot is for' is MORE credible than claiming everything already works perfectly.")


# ══════════════════════════════════════════════════════════
# SECTION 6: DO'S & DON'TS
# ══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("6. Presentation Do's & Don'ts")

pdf.sub_title("DO")
pdf.bullet("Maintain eye contact with the camera (virtual presentation)")
pdf.bullet("Speak at a measured pace -- slower than you think is necessary")
pdf.bullet("Pause after key numbers (let them land)")
pdf.bullet("Use your hands when explaining architecture (even on video)")
pdf.bullet("Have a glass of water nearby")
pdf.bullet("Test your microphone, camera, and screen sharing 30 minutes before")
pdf.bullet("Have the PPT open in presentation mode before you join")
pdf.bullet("End at exactly 10 minutes -- set a timer visible to you")
pdf.bullet("Thank the judges by name if possible")
pdf.bullet("If you don't know an answer in Q&A: 'That is an excellent question. We plan to address this in the pilot phase by...'")

pdf.ln(3)
pdf.sub_title("DON'T")
pdf.bullet("Don't read slides -- judges can read faster than you can speak")
pdf.bullet("Don't start with 'Good morning, my name is X and I'm from Y and today I'm going to talk about...' -- that wastes 30 seconds")
pdf.bullet("Don't use jargon without explanation (assume judges are engineers, not electrochemists)")
pdf.bullet("Don't say 'Um', 'So', 'Basically', 'Actually' as filler words")
pdf.bullet("Don't show excitement about your own slides ('This is really cool!')")
pdf.bullet("Don't argue with judges during Q&A -- acknowledge their point, then add your perspective")
pdf.bullet("Don't go over 10 minutes under ANY circumstances")
pdf.bullet("Don't apologize ('Sorry this slide is hard to read') -- fix it instead")
pdf.bullet("Don't mention competitors by name negatively")
pdf.bullet("Don't end with 'That's all' or 'I think that covers it' -- just say 'Thank you'")


# ══════════════════════════════════════════════════════════
# SECTION 7: DAY-OF CHECKLIST
# ══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("7. Day-of Checklist (17 March 2026)")

pdf.sub_title("Before Submission (16 March)")
pdf.bullet("PPT finalized and saved as: JalSakhi_Bennett University.pptx")
pdf.bullet("Email sent to krishmadhu@Lntecc.com before 23:59")
pdf.bullet("If file too large, upload to OneDrive/SharePoint and share access")
pdf.bullet("Confirm email was received (check sent folder)")

pdf.ln(3)
pdf.sub_title("Morning of Presentation (17 March)")
pdf.bullet("Charge laptop to 100%")
pdf.bullet("Close all unnecessary apps and browser tabs")
pdf.bullet("Turn off all notifications (phone, desktop, email)")
pdf.bullet("Have backup internet ready (mobile hotspot)")
pdf.bullet("Open PPT in presentation mode")
pdf.bullet("Test camera and microphone")
pdf.bullet("Have a plain, uncluttered background")
pdf.bullet("Good lighting on your face (light source in front, not behind)")
pdf.bullet("Glass of water within reach")
pdf.bullet("Print this prep guide for quick reference during Q&A")
pdf.bullet("Set a 9-minute timer (start when you begin speaking)")

pdf.ln(3)
pdf.sub_title("30 Minutes Before")
pdf.bullet("Join the meeting link early if possible")
pdf.bullet("Verify screen sharing works")
pdf.bullet("Do one final run-through of your opening line out loud")
pdf.bullet("Take 5 deep breaths")

pdf.ln(3)
pdf.sub_title("During Presentation")
pdf.bullet("Start the timer when you say your first word")
pdf.bullet("Glance at timer at 3:00, 6:00, and 8:00 marks")
pdf.bullet("If behind: cut methodology deep-dive, keep numbers")
pdf.bullet("If ahead: slow down, add pauses, let numbers breathe")
pdf.bullet("End with 'Thank you' and STOP talking")

pdf.ln(3)
pdf.sub_title("During Q&A")
pdf.bullet("Listen to the FULL question before answering")
pdf.bullet("Pause 2 seconds before responding (shows you are thinking)")
pdf.bullet("Keep answers under 45 seconds each")
pdf.bullet("If unsure: 'Great question. Our pilot is specifically designed to answer that.'")
pdf.bullet("If the question is about team qualifications, pivot to: 'Every claim is backed by peer-reviewed research'")


# ══════════════════════════════════════════════════════════
# SECTION 8: KEY NUMBERS TO MEMORIZE
# ══════════════════════════════════════════════════════════
pdf.add_page()
pdf.section_title("8. Key Numbers to Memorize")
pdf.body_text("These are the numbers judges will remember. Know them cold.")

pdf.ln(3)

numbers = [
    ("1.9 million", "Rural habitations in India"),
    ("2,200", "NABL-accredited water testing labs"),
    ("1.4 billion hours/year", "Women and girls spend collecting water"),
    ("INR 500-2,000", "Cost per lab test"),
    ("3-14 days", "Lab turnaround time"),
    ("7+", "Contaminants detected by JalSakhi"),
    ("0.05 mg/L", "Ammonia detection limit (10x WHO)"),
    ("1 ppb", "Lead detection limit"),
    ("60 seconds", "Time to get results"),
    ("INR 1,200 (~$14)", "Production dongle cost"),
    ("INR 25 (~$0.30)", "Cost per test (SPE)"),
    ("<200 KB", "ML model size (TFLite)"),
    ("<50 ms", "ML inference time"),
    ("12 million", "Women SHGs in India (NRLM)"),
    ("140 million", "Women SHG members"),
    ("99%", "Block coverage of SHGs"),
    ("INR 600/month", "Jal Sakhi supplementary income"),
    ("INR 72 lakh/year", "Total income for 1,000 Jal Sakhis"),
    ("450,000 hours/year", "Women's labor saved"),
    ("52x", "Monitoring frequency improvement"),
    ("200-500", "Hospitalizations prevented per year"),
    ("26", "Peer-reviewed references backing claims"),
    (">95%", "Published SPE-to-lab correlation"),
    (">90%", "Pilot target: lab correlation"),
    ("100 SHGs", "Pilot scale"),
    ("INR 5 lakh", "Pilot investment ask"),
    ("6 months", "Pilot duration"),
    ("80-95%", "Cost reduction vs lab testing"),
    ("INR 4,000", "Competition prototype budget"),
    ("INR 1,840", "Actual prototype cost"),
]

pdf.set_font("Helvetica", "B", 9)
pdf.set_fill_color(13, 43, 69)
pdf.set_text_color(255, 255, 255)
pdf.cell(45, 7, "Number", fill=True, border=1)
pdf.cell(0, 7, "What It Represents", fill=True, border=1, new_x="LMARGIN", new_y="NEXT")

for i, (num, desc) in enumerate(numbers):
    if i % 2 == 0:
        pdf.set_fill_color(240, 248, 255)
    else:
        pdf.set_fill_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(255, 107, 53)
    pdf.cell(45, 6, num, fill=True, border=1)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(45, 45, 45)
    pdf.cell(0, 6, desc, fill=True, border=1, new_x="LMARGIN", new_y="NEXT")


# ── FINAL PAGE ────────────────────────────────────────────
pdf.add_page()
pdf.ln(30)
pdf.set_font("Helvetica", "B", 24)
pdf.set_text_color(13, 43, 69)
pdf.cell(0, 12, "You've Got This.", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)

pdf.set_font("Helvetica", "", 14)
pdf.set_text_color(100, 100, 100)
pdf.multi_cell(0, 7, "You have real science, real engineering, real numbers, and a real deployment channel.\nMost teams don't have any of these.\n\nTrust your preparation. Deliver with conviction.\nLet the numbers speak for themselves.", align="C")

pdf.ln(10)
pdf.set_font("Helvetica", "B", 16)
pdf.set_text_color(0, 168, 181)
pdf.cell(0, 10, '"Women become the sensing infrastructure', align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 10, "of India's water system.\"", align="C", new_x="LMARGIN", new_y="NEXT")

pdf.ln(10)
pdf.set_font("Helvetica", "I", 11)
pdf.set_text_color(150, 150, 150)
pdf.cell(0, 7, "Grand Ceremony: L&T Chennai HQ, 20 March 2026", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 7, "See you there.", align="C", new_x="LMARGIN", new_y="NEXT")


# ── SAVE ──────────────────────────────────────────────────
output_path = "C:/Users/Ujjwal/JalSakhi/presentation/JalSakhi_Presentation_Prep_Guide.pdf"
pdf.output(output_path)
print(f"PDF saved to: {output_path}")
print(f"Pages: {pdf.page_no()}")
