# -*- coding: utf-8 -*-
"""Builds the Ironman training folder skeleton, reference PDFs, Month 1 PDFs and a calendar event JSON."""
import os, json, datetime as dt
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

ROOT = r"C:\Users\rober\Documents\Triathlon Training"
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "month1_events.json")
WEEK1_MONDAY = dt.date(2026, 10, 5)
ACTIVITIES = ["Swim", "Bike", "Run", "Strength"]
TZ = "-04:00"  # America/Toronto, EDT through Oct 31 2026

# ---------------------------------------------------------------- styles
ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Title"], fontSize=20, leading=24, spaceAfter=4, alignment=0)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=13, leading=16, spaceBefore=10, spaceAfter=4)
BODY = ParagraphStyle("BODY", parent=ss["Normal"], fontSize=9.5, leading=12.5)
SMALL = ParagraphStyle("SMALL", parent=BODY, fontSize=8.5, leading=11, textColor=colors.HexColor("#444444"))
CELL = ParagraphStyle("CELL", parent=BODY, fontSize=9, leading=11.5)
CELLB = ParagraphStyle("CELLB", parent=CELL, fontName="Helvetica-Bold")
HDR = ParagraphStyle("HDR", parent=CELLB, textColor=colors.white)

COLORS = {
    "Swim": colors.HexColor("#1F6FB2"),
    "Bike": colors.HexColor("#2E8B57"),
    "Run": colors.HexColor("#D9711E"),
    "Strength": colors.HexColor("#6A3FA0"),
    "Plan": colors.HexColor("#333333"),
}

def P(t, st=CELL):
    return Paragraph(t, st)

def table(rows, widths, color=COLORS["Plan"]):
    data = [[P(c, HDR) for c in rows[0]]] + [[P(c) for c in r] for r in rows[1:]]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("BACKGROUND", (0, 0), (-1, 0), color),
    ]))
    return t

def build_pdf(path, story, title):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    doc = SimpleDocTemplate(path, pagesize=letter, leftMargin=0.7*inch, rightMargin=0.7*inch,
                            topMargin=0.6*inch, bottomMargin=0.6*inch, title=title, author="Ironman 12-Month Plan")
    def footer(canvas, d):
        canvas.saveState(); canvas.setFont("Helvetica", 7.5); canvas.setFillColor(colors.grey)
        canvas.drawString(0.7*inch, 0.4*inch, title)
        canvas.drawRightString(letter[0]-0.7*inch, 0.4*inch, "Page %d" % d.page)
        canvas.restoreState()
    doc.build(story, onFirstPage=footer, onLaterPages=footer)

def header_block(activity, title, subtitle):
    bar = Table([[P("<font color='white'><b>%s</b></font>" % activity.upper(), CELL)]], colWidths=[7.1*inch])
    bar.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), COLORS[activity]), ("LEFTPADDING", (0, 0), (-1, -1), 6)]))
    return [bar, Spacer(1, 4), Paragraph(title, H1), Paragraph(subtitle, SMALL), Spacer(1, 6)]

# ---------------------------------------------------------------- calendar of weeks
def week_monday(n):
    return WEEK1_MONDAY + dt.timedelta(days=7*(n-1))

def month_folders():
    months = []
    for n in range(1, 53):
        m = week_monday(n)
        key = (m.year, m.month)
        if not months or months[-1][0] != key:
            months.append([key, []])
        months[-1][1].append(n)
    out = []
    for i, (key, weeks) in enumerate(months, start=1):
        name = "Month %02d - %s" % (i, dt.date(key[0], key[1], 1).strftime("%B %Y"))
        out.append((i, name, weeks))
    return out

MONTHS = month_folders()
assert len(MONTHS) == 12 and sum(len(w) for _, _, w in MONTHS) == 52

def week_folder(activity, n):
    for i, name, weeks in MONTHS:
        if n in weeks:
            return os.path.join(ROOT, name, activity, "Week %02d" % n)
    raise ValueError(n)

def make_skeleton():
    os.makedirs(os.path.join(ROOT, "00 - Plan Overview"), exist_ok=True)
    for i, name, weeks in MONTHS:
        for a in ACTIVITIES:
            for n in weeks:
                os.makedirs(os.path.join(ROOT, name, a, "Week %02d" % n), exist_ok=True)

# ---------------------------------------------------------------- 12-month roadmap
PHASES = [
    ("Foundation", "Establish the weekly rhythm. Baseline tests: 20-min bike FTP test, 400 m swim time trial. Swim = body position and catch drills. Bike = Zone 2 with cadence work. Run = walk/run intervals on the treadmill, 2x per week. Strength 2x per week with Achilles and knee prehab.", "5.5 - 6.5"),
    ("Base 1", "Third swim added. Trainer rides stay Zone 2, cadence and single-leg work. Walk/run moves toward 3 min run / 2 min walk. Strength 2x per week, loads rise slowly.", "6.5 - 7.5"),
    ("Base 2", "Swim endurance sets around Critical Swim Speed (CSS). First sweet-spot intervals (88-93% FTP) on the trainer. Run intervals to 5 min run / 1 min walk. Keep the recovery week honest over the holidays.", "7 - 8"),
    ("Base 3", "Re-test FTP and CSS. Sweet-spot 2 x 15 min. Longest trainer ride reaches 2 h. Run: 20-25 min continuous if joints are quiet. Strength moves to heavier, lower-rep work.", "8 - 9"),
    ("Base 4", "Swim sessions reach 2.0-2.5 km. Long trainer ride 2.5 h. Run 30 min continuous, 3x per week only if pain-free. Introduce short brick (bike then 10 min run).", "8.5 - 9.5"),
    ("Build 1", "Bike threshold intervals. Swim 2.5-3 km with race-pace 100s. Run 40 min long run using run/walk. Weekly brick. Re-test at end of block.", "9 - 10"),
    ("Build 2", "Outdoor riding resumes. Long ride 3 h with aero position time. Run long 50 min. Open-water skills rehearsed in the pool (sighting, drafting, deck-ups).", "10 - 11"),
    ("Build 3", "Open water begins late May. Long ride 3.5-4 h with race-pace blocks. Long run 60-70 min. Half-distance rehearsal at month end: 1.9 km swim, 90 km ride, 10 km run/walk.", "11 - 12"),
    ("Ironman Specific 1", "Weekly open-water swim. Long ride 4-4.5 h with fuelling practice (60-90 g carbs/h). Long run 75-90 min run/walk. Race-day nutrition locked in.", "12 - 13"),
    ("Ironman Specific 2", "Optional 70.3 race mid-July as a dress rehearsal. Long ride 5 h. Long run 100 min. Swim 3.8 km continuous in open water.", "13 - 14"),
    ("Peak", "Longest ride 5.5-6 h plus 30 min run off the bike. Long run 2-2.5 h run/walk. Peak week around 15 h, then a full recovery week.", "13 - 15"),
    ("Taper and Race", "Volume drops 30%, 50%, then 70% while short race-pace touches remain. Race week: travel, bike check, course swim, race on Sunday 3 October 2027 (assumed; adjust to your actual event).", "10 down to 5"),
]

def bullets(story, items):
    for r in items:
        story.append(Paragraph("&bull; " + r, BODY))

def roadmap_pdf():
    story = header_block("Plan", "12-Month Ironman Roadmap", "Week 1 starts Monday 5 October 2026. Week 52 ends Sunday 3 October 2027. Assumed race: Sunday 3 October 2027.")
    story.append(Paragraph("Athlete profile the plan is built around", H2))
    story.append(Paragraph("Swim: sustained 2:00/100 m, pool all year, open water late May to early October. "
        "Bike: road bike plus indoor trainer, power on both. Run: treadmill only until weight-loss goals are met, "
        "history of Achilles and knee pain, so running volume is gated by how the joints feel, never by the calendar. "
        "Start weight 207 lb. Strength and prehab are non-negotiable parts of the week.", BODY))
    story.append(Paragraph("Monthly progression", H2))
    rows = [["Month", "Weeks", "Phase", "What changes", "Hours / week"]]
    for (i, name, weeks), (phase, desc, hrs) in zip(MONTHS, PHASES):
        rows.append([name.replace("Month %02d - " % i, "%d. " % i), "%d-%d" % (weeks[0], weeks[-1]), phase, desc, hrs])
    story.append(table(rows, [1.15*inch, 0.55*inch, 1.0*inch, 3.7*inch, 0.7*inch]))
    story.append(Paragraph("Rules that never change", H2))
    bullets(story, [
        "Every month follows build-build-build-recover (5-week months add one more build week). Recovery weeks cut volume by 35-40% and are where adaptation happens.",
        "Run progression: increase weekly run minutes by no more than 10%. Pain above 3/10 during a run, or stiffness the next morning that lasts past the first 10 minutes, means repeat the previous week. Two repeats in a row means drop back one week and add a prehab session.",
        "Treadmill at 1% incline, run/walk from day one. Continuous running only arrives when a full month of intervals has been pain-free.",
        "Bike zones come from a 20-minute FTP test (FTP = 95% of the 20-min average power). Re-test in Months 4, 7 and 10.",
        "Swim pace comes from a 400 m time trial (Month 1) and a CSS test (400 m + 200 m) from Month 3 on. Re-test every 8 weeks.",
        "One full rest day per week (Monday is strength-only, no cardio). Sleep and body-weight trend are reviewed at each month boundary; the plan is adjusted before the next month is written.",
        "Strength never goes to failure. It is there to make tendons and knees robust, not to build a physique.",
    ])
    story.append(Paragraph("Training zones reference", H2))
    story.append(table([
        ["Zone", "Bike (% FTP)", "Run / Swim feel", "Talk test"],
        ["Z1 Recovery", "under 55%", "Very easy, walking-pace effort", "Full sentences easily"],
        ["Z2 Endurance", "56-75%", "All-day pace. Most of the year lives here", "Full sentences"],
        ["Z3 Tempo", "76-90%", "Comfortably hard, 70.3 race effort", "Short sentences"],
        ["Z4 Threshold", "91-105%", "Hard, 40-60 min race effort. CSS pace in the pool", "A few words"],
        ["Z5 VO2", "106-120%", "Very hard, 3-8 min efforts (rare in this plan)", "No talking"],
    ], [1.2*inch, 1.0*inch, 3.2*inch, 1.7*inch]))
    story.append(Paragraph("Folder structure", H2))
    story.append(Paragraph("Each month folder holds a Month Overview PDF plus four activity folders (Swim, Bike, Run, Strength). "
        "Each activity folder has one folder per week, and each week folder holds a single printable PDF with every session of "
        "that activity for the week. The Swim PDFs include cue cards for the drills used that week, so the sheet is all you need at the pool. "
        "Google Calendar events point back to the matching PDF.", BODY))
    build_pdf(os.path.join(ROOT, "00 - Plan Overview", "12-Month Ironman Roadmap.pdf"), story, "12-Month Ironman Roadmap")

# ---------------------------------------------------------------- swim drill glossary
DRILLS = {
    "Kick with board": "Board held at arm's length, face in the water, exhale, breathe forward or to the side. Kick comes from the hips with a soft knee, toes pointed, ankles loose. Small and fast beats big and slow. Purpose: leg endurance and ankle flexibility.",
    "Kick on side": "One arm extended in front, palm down, other arm on your hip. Ear rests on the extended arm, body rolled about 45 degrees, hips at the surface. Kick steadily; rotate the head to breathe without lifting it. Switch sides every 25. Purpose: balance and body line.",
    "6-3-6": "Six kicks on one side (as in Kick on side), three full strokes, six kicks on the other side. Keep the hips high and the extended arm still while kicking. Purpose: rotation, balance, and timing the arm switch with the hips.",
    "Catch-up": "Both arms start extended. One arm pulls and recovers while the other waits out front; the recovering hand touches the waiting hand before the next stroke starts. Purpose: long stroke, front-quadrant timing, patience in the glide.",
    "Fingertip drag": "Swim normally but during the recovery let the fingertips trail along the surface, elbow high and pointing to the ceiling. Purpose: relaxed, high-elbow recovery and shoulder rotation.",
    "Fist drill": "Swim freestyle with closed fists. You will feel the forearm doing the work. After 25 m of fists open the hands and notice the extra grip. Purpose: early vertical forearm and feel for the water.",
    "Sculling (front)": "Arms extended in front, elbows slightly bent, hands sweep in and out in small figure-8s with the palms angled like a windshield wiper. Head down, gentle kick or pull buoy. Move forward slowly. Purpose: feel for the water and catch pressure.",
    "Single-arm": "One arm swims, the other stays extended in front. Breathe to the side of the working arm. Focus on the catch: fingertips down, elbow high, press back not down. Switch arms every 25. Purpose: catch mechanics and rotation.",
    "Zipper": "During recovery, drag the thumb up the side of the body from hip to armpit before reaching forward. Purpose: high elbow recovery and body rotation.",
    "3-3-3 breathing": "25 m breathing to the left every stroke, 25 m to the right, 25 m bilateral (every 3rd stroke), then repeat. Exhale continuously through nose and mouth while the face is in the water. Purpose: symmetrical stroke and calm breathing for open water.",
    "Build 50": "Start the 50 easy and finish it fast, without letting the stroke shorten. Purpose: learning to raise speed by pressing harder on the water, not by spinning the arms.",
    "Stroke count": "Count strokes per 25 m (one arm = one stroke). Write down your normal count, then try to hold pace with one fewer. Purpose: efficiency and distance per stroke.",
    "Descend": "Each repeat in the set is slightly faster than the previous one. The first should feel too easy.",
    "Pull (buoy)": "Pull buoy between the thighs, no kick. Focus entirely on the arm stroke and on keeping the body long. Paddles are not used in Month 1.",
    "Sighting": "Every 6-8 strokes lift the eyes just above the surface (crocodile eyes) at the start of a breath, then turn the head to breathe. Practised from Month 4 for open water.",
}

def drill_cards(names, title="Drill cue cards for this week"):
    out = [Paragraph(title, H2)]
    rows = [["Drill", "How to do it and what it trains"]]
    for n in names:
        rows.append([n, DRILLS[n]])
    out.append(table(rows, [1.3*inch, 5.8*inch], color=COLORS["Swim"]))
    return out

def glossary_pdf():
    story = header_block("Swim", "Swim Drill Glossary", "Print once and keep it in your pool bag. Every drill used across the year is here.")
    story.append(Paragraph("Notation used in the swim sheets", H2))
    story.append(table([
        ["Term", "Meaning"],
        ["FS", "Freestyle"], ["WU / CD", "Warm-up / Cool-down"],
        ["4 x 50 r20", "Four repeats of 50 m, resting 20 seconds after each"],
        ["25 drill / 25 swim", "First length is the drill, second length is normal freestyle applying the feeling"],
        ["TT", "Time trial: maximal, evenly paced effort. Record the time"],
        ["CSS", "Critical Swim Speed: roughly your 1500 m race pace, from a 400 m and 200 m test"],
        ["Easy / Steady / Strong", "Easy = conversational. Steady = Zone 2, could hold for 30+ min. Strong = Zone 3-4, breathing hard"],
    ], [1.6*inch, 5.5*inch], color=COLORS["Swim"]))
    story += drill_cards(list(DRILLS.keys()), "All drills")
    story.append(Paragraph("Pool etiquette and safety notes", H2))
    story.append(Paragraph("Pick a lane matching your pace. Rest at the wall corners, not the middle. If a set feels wrong (shoulder pain, dizziness) stop the set and swim easy. Hydrate: a bottle at the end of the lane, sip every 400-500 m.", BODY))
    build_pdf(os.path.join(ROOT, "00 - Plan Overview", "Swim Drill Glossary.pdf"), story, "Swim Drill Glossary")

# ---------------------------------------------------------------- prehab guide
PREHAB = [
    ("Eccentric heel drops, straight knee (Alfredson)", "Stand on a step on the balls of both feet. Rise up on both, shift to the target leg, lower slowly over 3 seconds until the heel is below the step. Use both legs to come back up. 3 x 15. Mild discomfort is acceptable, sharp pain is not.", "Achilles tendon"),
    ("Eccentric heel drops, bent knee", "Same as above with the knee bent about 20 degrees. 3 x 15. Targets the soleus, the muscle that takes most of the load when running slowly.", "Achilles / soleus"),
    ("Seated or bent-knee calf raise", "Knee at 90 degrees, weight on the thigh (dumbbell or plate), raise heel slowly. 3 x 15. Build to heavy over the year.", "Soleus"),
    ("Tibialis raise", "Back against a wall, feet 30 cm out, lift toes toward shins. 3 x 20.", "Shin / ankle"),
    ("Single-leg balance", "Stand on one foot 30-45 s, eyes open then closed. Progress to standing on a folded towel.", "Ankle / knee control"),
    ("Glute bridge", "Lying on back, feet flat, drive hips up squeezing glutes, 2 s hold at top. 3 x 12. Progress to single leg.", "Hips / knee"),
    ("Clamshell with band", "Side-lying, knees bent, band above knees, open the top knee without rolling the pelvis back. 3 x 15 each side.", "Glute medius / knee tracking"),
    ("Monster walk", "Band above knees, quarter squat, step sideways 10 steps each direction x 3.", "Glute medius"),
    ("Step-down", "Stand on a low step (10-15 cm). Slowly lower the other heel to the floor, tap, return. Keep the knee over the second toe. 3 x 10 each side.", "Knee (patellofemoral)"),
    ("Wall sit", "Back to wall, thighs parallel-ish, 3 x 30-45 s. Progress duration, not depth.", "Quads / knee"),
    ("Terminal knee extension with band", "Band around the back of the knee anchored in front, straighten the knee against the band. 3 x 15.", "VMO / knee"),
    ("Calf stretch (gastroc and soleus)", "Straight-knee wall stretch 30 s, then bent-knee 30 s, each side. After sessions only.", "Achilles / calf"),
    ("Hip flexor stretch", "Half-kneeling, tuck the pelvis, lean forward slightly, 30-45 s each side.", "Hips / low back"),
    ("Foam roll", "Calves, quads, IT band region, glutes. 60 s each. Not on the Achilles tendon itself.", "Recovery"),
]

def prehab_pdf():
    story = header_block("Strength", "Achilles and Knee Prehab Guide", "The 15-minute routine attached to every run day, plus the load-management rules.")
    story.append(Paragraph("The run-day prehab routine (about 15 minutes)", H2))
    story.append(Paragraph("Do this after every treadmill session, and on Monday with Strength A. Order matters: heel drops first while the calves are warm.", BODY))
    rows = [["Exercise", "How", "Protects"]]
    for n, how, why in PREHAB:
        rows.append([n, how, why])
    story.append(table(rows, [1.7*inch, 4.2*inch, 1.2*inch], color=COLORS["Strength"]))
    story.append(Paragraph("Load-management rules for the run", H2))
    bullets(story, [
        "Treadmill only, 1% incline, cushioned deck. Shoes replaced every 500-600 km; note the start date on the sole.",
        "Run/walk from the first session. The walk breaks are the point: they let the tendon recover between loads.",
        "Rate pain 0-10 during and the morning after. 0-3 = continue as planned. 4-5 = repeat this week. 6+ = stop running for a week, keep swimming and cycling, do prehab daily, then restart one week back.",
        "Warm up the calves before every run: 5 min brisk walk, 20 slow calf raises, 10 leg swings each direction.",
        "Never run on consecutive days in Months 1-4.",
        "Body-weight check-in monthly. As weight drops, run volume can climb; the plan is re-written month by month with that in mind.",
    ])
    build_pdf(os.path.join(ROOT, "00 - Plan Overview", "Achilles and Knee Prehab Guide.pdf"), story, "Achilles and Knee Prehab Guide")

# ---------------------------------------------------------------- Month 1 sessions
def swim(day, title, focus, rows, drills, total, notes=""):
    return dict(activity="Swim", day=day, start="06:00", dur=50, title=title, focus=focus, rows=rows, drills=drills, total=total, notes=notes)
def bike(day, title, focus, rows, dur, notes="", start="06:00"):
    return dict(activity="Bike", day=day, start=start, dur=dur, title=title, focus=focus, rows=rows, notes=notes)
def run(day, title, focus, rows, dur, notes="", start="06:00"):
    return dict(activity="Run", day=day, start=start, dur=dur, title=title, focus=focus, rows=rows, notes=notes)
def strength(day, title, focus, rows, dur, notes="", start="06:00"):
    return dict(activity="Strength", day=day, start=start, dur=dur, title=title, focus=focus, rows=rows, notes=notes)

RUN_WU = ("Warm-up", "5 min brisk walk (5.5-6.0 km/h), 1% incline. 20 slow calf raises off the back of the treadmill, 10 leg swings each way.")
RUN_CD = ("Cool-down", "5 min walk, then the 15-minute prehab routine (see Achilles and Knee Prehab Guide).")
RUN_PACE = "Jog pace = a pace you could talk in full sentences at, likely 7.5-8.5 km/h. Walk = 5.5-6.0 km/h. Cadence 170+ steps/min: short, quick steps, land under the hips."

STR_A_EX = [
    ("Goblet squat", "3 x {a}", "Heels down, knees track over toes, depth only as far as pain-free"),
    ("Dumbbell Romanian deadlift", "3 x {a}", "Soft knees, hinge at the hip, flat back, feel the hamstrings"),
    ("Push-up (incline if needed)", "3 x {b}", "Body in one line, elbows at 45 degrees"),
    ("Single-arm dumbbell row", "3 x {a} each", "Pull the elbow to the hip, no torso twist"),
    ("Step-up to low box", "3 x {c} each", "Drive through the whole foot, control the descent"),
    ("Dead bug", "3 x {a} each side", "Low back stays glued to the floor"),
    ("Side plank", "3 x {d} s each", "Hips stacked, straight line ear to ankle"),
    ("Eccentric heel drops, straight and bent knee", "3 x 15 each", "From the prehab guide, slow 3 s lowering"),
]
STR_B_EX = [
    ("Glute bridge (progress to single leg)", "3 x {a}", "2 s squeeze at the top"),
    ("Clamshell with band", "3 x 15 each", "Pelvis does not roll back"),
    ("Monster walk", "3 x 10 steps each way", "Stay low, knees out"),
    ("Step-down from low step", "3 x {c} each", "Knee over second toe, slow"),
    ("Wall sit", "3 x {d} s", "Progress time, not depth"),
    ("Bent-knee calf raise (seated, weight on thigh)", "3 x 15", "Slow up, slow down"),
    ("Bird dog", "3 x {a} each side", "Hips level, reach long"),
    ("Pallof press (band)", "3 x {a} each side", "Resist the rotation"),
    ("Front plank", "3 x {d} s", "Squeeze glutes, breathe"),
    ("Single-leg balance", "3 x 30 s each", "Eyes closed if easy"),
]
STR_LEVELS = {1: dict(a=10, b=8, c=8, d=20), 2: dict(a=12, b=10, c=10, d=25), 3: dict(a=12, b=12, c=10, d=30), 4: dict(a=8, b=8, c=8, d=20)}

def str_rows(exs, level):
    return [(n, s.format(**STR_LEVELS[level]) + ". " + cue) for n, s, cue in exs]

def strength_pair(week, note_a, note_b):
    return [
        strength(0, "Strength A - Full-body foundation", "Movement quality, tendon loading, core", str_rows(STR_A_EX, week), 45,
                 "Warm up 5 min: easy bike or walk, then 10 bodyweight squats, 10 hip hinges, 10 arm circles. Rest 60-90 s between sets. " + note_a),
        strength(6, "Strength B - Hips, knees, core", "Glute medius, patellar tracking, trunk stability", str_rows(STR_B_EX, week), 30,
                 "Done straight after the Sunday treadmill session, which serves as the warm-up. " + note_b, start="08:35"),
    ]

M1 = {}

M1[1] = dict(
    theme="Foundation and testing",
    swim=[
        swim(1, "Swim A - Body position", "Balance, long body line, hips at the surface", [
            ("Warm-up", "200 easy FS, 100 kick with board"),
            ("Drills", "4 x 50 Kick on side (25 each side) r20<br/>4 x 50 6-3-6 r20<br/>4 x 50 Catch-up r20"),
            ("Main set", "6 x 100 FS easy r30. Focus: head down, hips up, long reach. Count strokes on the last 25 of each 100 and write it down."),
            ("Cool-down", "100 easy choice"),
        ], ["Kick with board", "Kick on side", "6-3-6", "Catch-up", "Stroke count"], 1500,
            "This is a technique session. If you finish with your usual stroke count and feel long and relaxed, it worked."),
        swim(4, "Swim B - 400 m baseline time trial", "Establish the swim pace the next 8 weeks are built on", [
            ("Warm-up", "200 easy FS, 100 kick with board, 4 x 50 Build r20"),
            ("Test", "400 m FS time trial from a push. Even pace, strong but controlled. Record total time and your per-100 average.<br/>Expected: around 8:00 (2:00/100). Write the time on this sheet."),
            ("Recovery", "200 very easy, mix of backstroke and FS"),
            ("Drills", "4 x 50 (25 Fist drill / 25 FS) r20<br/>4 x 50 (25 Fingertip drag / 25 FS) r20"),
            ("Cool-down", "100 easy"),
        ], ["Build 50", "Fist drill", "Fingertip drag"], 1500,
            "400 m time ________  Per-100 average ________  Training pace for Month 1 = 400 pace + 10 s per 100."),
    ],
    bike=[
        bike(2, "Trainer - 20-minute FTP test", "Set your power zones for the next 12 weeks", [
            ("Warm-up (20 min)", "10 min easy spin building to Zone 2. 3 x 1 min fast cadence (100+ rpm) with 1 min easy. 5 min at a hard-but-steady effort. 5 min easy."),
            ("Test (20 min)", "20 min at the highest power you can hold evenly. Start conservatively, the first 5 min should feel too easy. Note the 20-min average power."),
            ("Cool-down (10 min)", "Easy spin, cadence 85-90."),
            ("Result", "FTP = 20-min average x 0.95 = ________ W<br/>Z1 under 55%: ____ W &nbsp; Z2 56-75%: ____-____ W &nbsp; Z3 76-90%: ____-____ W &nbsp; Z4 91-105%: ____-____ W"),
        ], 60, "Fan on, bottle full, ERG mode off for the test. Enter FTP into your trainer app afterwards so ERG mode can drive the Zone 2 rides."),
        bike(5, "Long ride - Zone 2 endurance", "Aerobic base, comfortable position", [
            ("Warm-up", "10 min easy, cadence 85-95"),
            ("Main", "60 min Zone 2 (56-75% FTP). Every 10 min, 1 min at 100 rpm cadence to keep the legs light."),
            ("Cool-down", "5 min easy spin"),
        ], 75, "Outdoors if dry and above 8 C, otherwise trainer. Eat 30-40 g of carbs per hour after the first hour from now on so fuelling becomes habit.", start="08:00"),
    ],
    run=[
        run(3, "Treadmill walk/run 1:2", "First tendon loading. Easy is the whole point", [
            RUN_WU, ("Main", "6 x (1 min easy jog / 2 min walk) = 18 min. Total run time 6 min."), RUN_CD,
        ], 45, RUN_PACE),
        run(6, "Treadmill walk/run 1:2", "Same as Thursday. Then Strength B", [
            RUN_WU, ("Main", "6 x (1 min easy jog / 2 min walk) = 18 min. Total run time 6 min."), ("Cool-down", "5 min walk, then go straight into Strength B (the prehab is built into it)."),
        ], 30, RUN_PACE + " Pain during / next morning (0-10): ____ / ____", start="08:00"),
    ],
    strength=strength_pair(1, "Week 1: learn the movements with light dumbbells. Film one set of the squat and hinge from the side if you can.", "Bands: light and medium loop bands are all that is needed."),
)

M1[2] = dict(
    theme="Kick, balance and feel for the water",
    swim=[
        swim(1, "Swim A - Kick and balance", "Hip-driven kick, rotation from the core", [
            ("Warm-up", "200 easy FS, 100 kick with board"),
            ("Kick set", "6 x 50 Kick with board r20 (small, fast, from the hips)"),
            ("Drills", "4 x 50 Kick on side r20<br/>4 x 50 6-3-6 r20<br/>4 x 50 Catch-up r20"),
            ("Main set", "4 x 150 FS steady r30 at training pace (400 pace + 10 s/100). Stroke count on the last 25 of each."),
            ("Cool-down", "100 easy"),
        ], ["Kick with board", "Kick on side", "6-3-6", "Catch-up", "Stroke count"], 1800),
        swim(4, "Swim B - The catch", "High elbow, forearm pressing back", [
            ("Warm-up", "200 easy FS, 4 x 50 Build r20"),
            ("Drills", "4 x 50 (25 Sculling / 25 FS) r20<br/>4 x 50 (25 Fist / 25 FS) r20<br/>4 x 50 (25 Single-arm right / 25 Single-arm left) r20<br/>4 x 50 (25 Fingertip drag / 25 FS) r20"),
            ("Main set", "8 x 75 FS steady r20. Think: fingertips down early, elbow high, press the water back toward your feet."),
            ("Cool-down", "100 easy"),
        ], ["Build 50", "Sculling (front)", "Fist drill", "Single-arm", "Fingertip drag"], 1900),
    ],
    bike=[
        bike(2, "Trainer - Zone 2 with cadence ladders", "Smooth pedalling, aerobic base", [
            ("Warm-up", "10 min easy building into Zone 2"),
            ("Main", "4 x (5 min Zone 2 at 95-100 rpm / 3 min Zone 2 at 80-85 rpm). Watch for bouncing in the saddle at high cadence; if it starts, back off 5 rpm."),
            ("Single-leg", "4 x (30 s left leg / 30 s right leg / 1 min both), easy gear. Unclip the resting foot or rest it on the trainer frame."),
            ("Cool-down", "8 min easy"),
        ], 60),
        bike(5, "Long ride - Zone 2 endurance", "Aerobic base, 90 minutes", [
            ("Warm-up", "10 min easy"),
            ("Main", "75 min Zone 2. Include 2 x 10 min in the upper half of Zone 2 (70-75% FTP), 10 min easy between."),
            ("Cool-down", "5 min easy"),
        ], 90, "Fuel: 40 g carbs per hour. Practise drinking every 15 min.", start="08:00"),
    ],
    run=[
        run(3, "Treadmill walk/run 1.5:2", "Run minutes up 50%, tendon still protected by the walks", [
            RUN_WU, ("Main", "6 x (1.5 min easy jog / 2 min walk) = 21 min. Total run time 9 min."), RUN_CD,
        ], 45, RUN_PACE + " Only progress if last week scored 0-3 on pain."),
        run(6, "Treadmill walk/run 1.5:2", "Repeat of Thursday, then Strength B", [
            RUN_WU, ("Main", "6 x (1.5 min easy jog / 2 min walk) = 21 min. Total run time 9 min."), ("Cool-down", "5 min walk, then Strength B."),
        ], 30, "Pain during / next morning (0-10): ____ / ____", start="08:00"),
    ],
    strength=strength_pair(2, "Week 2: add 1-2 reps per set. Choose a weight where the last rep is still clean.", "Add a light band to the glute bridge if it feels easy."),
)

M1[3] = dict(
    theme="Breathing, rhythm and the first longer efforts",
    swim=[
        swim(1, "Swim A - Breathing and rhythm", "Calm exhale, symmetrical stroke", [
            ("Warm-up", "200 easy FS, 100 kick with board"),
            ("Drills", "4 x 50 3-3-3 breathing r20<br/>4 x 50 (25 Zipper / 25 FS) r20<br/>4 x 50 6-3-6 r20"),
            ("Main set", "4 x 200 FS steady r40 at training pace. Breathe every 3rd stroke on the odd 200s, every 2nd on the even 200s."),
            ("Cool-down", "100 easy"),
        ], ["3-3-3 breathing", "Zipper", "6-3-6"], 1800, "If bilateral breathing feels air-starved, breathe every 2 strokes and alternate sides each length instead."),
        swim(4, "Swim B - Endurance with drill reminders", "Holding form as the distance grows", [
            ("Warm-up", "200 easy FS, 4 x 50 Build r20"),
            ("Main set", "4 x (100 drill of your choice from this month + 200 FS steady) r30 after the drill, r40 after the swim. Pick the drill that fixes your weakest link."),
            ("Kick", "4 x 50 Kick with board r20"),
            ("Cool-down", "100 easy"),
        ], ["Build 50", "Catch-up", "Fist drill", "Single-arm", "Kick with board"], 2000, "Longest swim of the month. Note how the last 200 felt compared with the first."),
    ],
    bike=[
        bike(2, "Trainer - Tempo introduction", "A first taste of Zone 3, still mostly Zone 2", [
            ("Warm-up", "10 min easy building into Zone 2, 3 x 30 s at 100 rpm"),
            ("Main", "3 x 8 min Zone 3 (76-85% FTP) at 85-90 rpm / 4 min Zone 1 easy between"),
            ("Cool-down", "10 min easy"),
        ], 60, "Tempo should feel purposeful, not hard. If breathing becomes ragged, the power is too high."),
        bike(5, "Long ride - Zone 2 endurance", "Longest ride of the month, 105 minutes", [
            ("Warm-up", "10 min easy"),
            ("Main", "90 min Zone 2 with 3 x 10 min at 72-78% FTP (upper Z2 / low Z3), 10 min easy between."),
            ("Cool-down", "5 min easy"),
        ], 105, "Fuel 40-50 g carbs per hour. This is the ride to check saddle and hand comfort; note anything that hurts after 90 min.", start="08:00"),
    ],
    run=[
        run(3, "Treadmill walk/run 2:2", "Equal run and walk for the first time", [
            RUN_WU, ("Main", "6 x (2 min easy jog / 2 min walk) = 24 min. Total run time 12 min."), RUN_CD,
        ], 50, RUN_PACE + " Progress only if Week 2 scored 0-3 on pain."),
        run(6, "Treadmill walk/run 2:2", "Repeat of Thursday, then Strength B", [
            RUN_WU, ("Main", "6 x (2 min easy jog / 2 min walk) = 24 min. Total run time 12 min."), ("Cool-down", "5 min walk, then Strength B."),
        ], 35, "Pain during / next morning (0-10): ____ / ____", start="08:00"),
    ],
    strength=strength_pair(3, "Week 3: heaviest week of the month. Add weight to squat, hinge and row if the last two weeks felt clean.", "Try single-leg glute bridges for the first set."),
)

M1[4] = dict(
    theme="Recovery week: absorb the work",
    swim=[
        swim(1, "Swim A - Easy technique", "Short, relaxed, drill-heavy", [
            ("Warm-up", "200 easy FS"),
            ("Drills", "8 x 50 drill mix r20: 2 x Kick on side, 2 x Catch-up, 2 x Fist/FS, 2 x Fingertip drag/FS"),
            ("Main set", "4 x 100 FS easy r30, focus on your best stroke count of the month"),
            ("Cool-down", "100 easy"),
        ], ["Kick on side", "Catch-up", "Fist drill", "Fingertip drag", "Stroke count"], 1100),
        swim(4, "Swim B - Easy steady", "Consolidate, no clock pressure", [
            ("Warm-up", "200 easy FS, 4 x 50 Build r20"),
            ("Drills", "4 x 50 (25 Single-arm / 25 FS) r20"),
            ("Main set", "6 x 100 FS steady r30 at training pace, relaxed"),
            ("Cool-down", "100 easy"),
        ], ["Build 50", "Single-arm"], 1400, "Month-end check: does 2:00/100 feel easier than it did on 5 October? Write a sentence about it here."),
    ],
    bike=[
        bike(2, "Trainer - Easy spin and single-leg", "Recovery, pedalling skill", [
            ("Warm-up", "10 min easy"),
            ("Main", "20 min Zone 1-2 at 90-95 rpm<br/>4 x (30 s left / 30 s right / 1 min both) single-leg"),
            ("Cool-down", "8 min easy"),
        ], 45),
        bike(5, "Endurance ride - short Zone 2", "Keep the rhythm, cut the volume", [
            ("Warm-up", "10 min easy"),
            ("Main", "45 min Zone 2, no surges"),
            ("Cool-down", "5 min easy"),
        ], 60, start="08:00"),
    ],
    run=[
        run(3, "Treadmill walk/run 1.5:2 (recovery)", "Step back so the tendons catch up", [
            RUN_WU, ("Main", "5 x (1.5 min easy jog / 2 min walk) = 17.5 min. Total run time 7.5 min."), RUN_CD,
        ], 40, RUN_PACE),
        run(6, "Treadmill walk/run 1.5:2 (recovery)", "Repeat of Thursday, then Strength B (light)", [
            RUN_WU, ("Main", "5 x (1.5 min easy jog / 2 min walk) = 17.5 min. Total run time 7.5 min."), ("Cool-down", "5 min walk, then Strength B."),
        ], 30, "Month-end: total pain-free run sessions this month ____ of 8. If 7 or more, Month 2 progresses; if fewer, Month 2 repeats Weeks 2-3.", start="08:00"),
    ],
    strength=strength_pair(4, "Week 4: reduce weight by 20-30% and reps to the listed numbers. Move well, leave the gym fresh.", "Light week. Keep the heel drops and calf raises at full volume; those are the ones that matter most."),
)

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def week_dates(n):
    m = week_monday(n)
    return m, m + dt.timedelta(days=6)

def activity_week_pdf(activity, n, sessions):
    mon, sun = week_dates(n)
    sub = "Week %d of 52 &nbsp;|&nbsp; %s to %s &nbsp;|&nbsp; Month 1: %s" % (n, mon.strftime("%a %d %b %Y"), sun.strftime("%a %d %b %Y"), M1[n]["theme"])
    story = header_block(activity, "Week %02d %s" % (n, activity), sub)
    for s in sessions:
        d = mon + dt.timedelta(days=s["day"])
        block = [Paragraph("%s, %s &nbsp; %s &nbsp; (%d min)" % (DAY_NAMES[s["day"]], d.strftime("%d %b"), s["title"], s["dur"]), H2),
                 Paragraph("<b>Focus:</b> " + s["focus"], BODY), Spacer(1, 3)]
        rows = [["Section", "Details"]] + [[a, b] for a, b in s["rows"]]
        block.append(table(rows, [1.3*inch, 5.8*inch], color=COLORS[activity]))
        if s.get("total"):
            block.append(Paragraph("<b>Total:</b> about %d m" % s["total"], BODY))
        if s.get("notes"):
            block.append(Paragraph("<b>Notes:</b> " + s["notes"], BODY))
        block.append(Spacer(1, 6))
        story.append(KeepTogether(block))
    if activity == "Swim":
        names = []
        for s in sessions:
            for dname in s["drills"]:
                if dname not in names:
                    names.append(dname)
        story += drill_cards(names)
    if activity == "Run":
        story.append(Paragraph("Pain log", H2))
        story.append(table([["Session", "Pain during (0-10)", "Next morning (0-10)", "Notes"],
                            ["Thursday", "", "", ""], ["Sunday", "", "", ""]], [1.2*inch, 1.5*inch, 1.5*inch, 2.9*inch], color=COLORS["Run"]))
    path = os.path.join(week_folder(activity, n), "Week %02d %s.pdf" % (n, activity))
    build_pdf(path, story, "Week %02d %s" % (n, activity))
    return path

def month1_overview_pdf():
    name = MONTHS[0][1]
    story = header_block("Plan", "Month 1 Overview - October 2026", "Weeks 1-4 &nbsp;|&nbsp; Phase: Foundation &nbsp;|&nbsp; 5 October to 1 November 2026")
    story.append(Paragraph("Goals for the month", H2))
    bullets(story, ["Make the seven-session week a habit before adding any volume.",
              "Bike: FTP test in Week 1, then Zone 2 base with cadence work. Longest ride 105 min.",
              "Swim: 400 m baseline, then body position, kick, catch and breathing drills. Two swims per week, 1,100-2,000 m each.",
              "Run: treadmill walk/run twice per week, from 6 to 12 minutes of total running per session. Zero pain is the target, not pace.",
              "Strength: two sessions per week. Achilles heel drops and knee prehab on every run day."])
    story.append(Paragraph("Weekly template", H2))
    story.append(table([
        ["Day", "Session", "Time", "Duration"],
        ["Monday", "Strength A - full-body foundation", "6:00 AM", "45 min"],
        ["Tuesday", "Swim A - technique", "6:00 AM", "50 min"],
        ["Wednesday", "Bike - trainer (test / cadence / tempo)", "6:00 AM", "45-60 min"],
        ["Thursday", "Run - treadmill walk/run + prehab", "6:00 AM", "40-50 min"],
        ["Friday", "Swim B - test / catch / endurance", "6:00 AM", "50 min"],
        ["Saturday", "Bike - long Zone 2 (outdoor if weather allows)", "8:00 AM", "60-105 min"],
        ["Sunday", "Run - treadmill walk/run, then Strength B", "8:00 AM", "60-65 min"],
    ], [1.0*inch, 3.4*inch, 1.0*inch, 1.7*inch]))
    story.append(Paragraph("Week by week", H2))
    rows = [["Week", "Dates", "Theme", "Swim", "Bike", "Run (run minutes per session)", "Hours"]]
    hrs = {1: "6.0", 2: "6.3", 3: "6.8", 4: "4.7"}
    runs = {1: "6 x 1:00 / 2:00 (6 min)", 2: "6 x 1:30 / 2:00 (9 min)", 3: "6 x 2:00 / 2:00 (12 min)", 4: "5 x 1:30 / 2:00 (7.5 min)"}
    for n in range(1, 5):
        mon, sun = week_dates(n)
        w = M1[n]
        rows.append([str(n), "%s - %s" % (mon.strftime("%d %b"), sun.strftime("%d %b")), w["theme"],
                     " / ".join("%d m" % s["total"] for s in w["swim"]),
                     " / ".join("%d min" % s["dur"] for s in w["bike"]), runs[n], hrs[n]])
    story.append(table(rows, [0.45*inch, 0.95*inch, 1.5*inch, 1.0*inch, 0.9*inch, 1.7*inch, 0.6*inch]))
    story.append(Paragraph("End-of-month checkpoint (fill in before Month 2 is written)", H2))
    story.append(table([
        ["Measure", "Start of month", "End of month"],
        ["Body weight (lb)", "207", ""], ["FTP (W)", "", "n/a until Month 4"], ["400 m swim time", "", "n/a until Month 3"],
        ["Pain-free run sessions", "", "____ of 8"], ["Sessions completed", "", "____ of 28"], ["Average sleep (h)", "", ""],
    ], [2.3*inch, 2.4*inch, 2.4*inch]))
    story.append(Paragraph("Where the printouts live", H2))
    story.append(Paragraph("%s\\Swim\\Week 01 ... Week 04, and the same for Bike, Run and Strength. Reference sheets (drill glossary, prehab guide, 12-month roadmap) are in 00 - Plan Overview." % name, BODY))
    build_pdf(os.path.join(ROOT, name, "Month 01 Overview.pdf"), story, "Month 01 Overview")

# ---------------------------------------------------------------- calendar events
COLOR_IDS = {"Swim": "9", "Bike": "10", "Run": "6", "Strength": "3"}

def strip_tags(s):
    return s.replace("<br/>", "\n").replace("&lt;", "<").replace("&gt;", ">").replace("&nbsp;", " ").replace("<b>", "").replace("</b>", "")

def events_for_month1():
    events = []
    for n in range(1, 5):
        mon, _ = week_dates(n)
        for act in ["swim", "bike", "run", "strength"]:
            for s in M1[n][act]:
                d = mon + dt.timedelta(days=s["day"])
                h, m = s["start"].split(":")
                start = dt.datetime(d.year, d.month, d.day, int(h), int(m))
                end = start + dt.timedelta(minutes=s["dur"])
                lines = ["Week %d of 52 - %s" % (n, M1[n]["theme"]), "Focus: " + s["focus"], ""]
                for a, b in s["rows"]:
                    lines.append("%s: %s" % (a, strip_tags(b)))
                if s.get("total"):
                    lines.append("Total: about %d m" % s["total"])
                if s.get("notes"):
                    lines += ["", "Notes: " + strip_tags(s["notes"])]
                pdf = os.path.join(week_folder(s["activity"], n), "Week %02d %s.pdf" % (n, s["activity"]))
                lines += ["", "Printout: " + pdf]
                events.append(dict(summary="%s: %s" % (s["activity"], s["title"]),
                                   startTime=start.strftime("%Y-%m-%dT%H:%M:00") + TZ,
                                   endTime=end.strftime("%Y-%m-%dT%H:%M:00") + TZ,
                                   description="\n".join(lines), colorId=COLOR_IDS[s["activity"]]))
    return events

if __name__ == "__main__":
    make_skeleton()
    roadmap_pdf(); glossary_pdf(); prehab_pdf(); month1_overview_pdf()
    made = []
    for n in range(1, 5):
        for act, key in zip(ACTIVITIES, ["swim", "bike", "run", "strength"]):
            made.append(activity_week_pdf(act, n, M1[n][key]))
    ev = events_for_month1()
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(ev, f, indent=1)
    print("Months:", [(i, name, weeks[0], weeks[-1]) for i, name, weeks in MONTHS])
    print("PDFs:", len(made) + 4, "Events:", len(ev))
