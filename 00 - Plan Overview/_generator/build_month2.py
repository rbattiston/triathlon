# -*- coding: utf-8 -*-
"""Month 2 (November 2026, Weeks 5-9): keto-adaptation block. Builds PDFs and the calendar event JSON.
Run from this folder: python build_month2.py"""
import os, json, datetime as dt
from build_plan import (ROOT, MONTHS, ACTIVITIES, COLORS, H2, BODY, inch, Paragraph, Spacer, KeepTogether,
                        table, build_pdf, header_block, bullets, week_folder, week_monday, week_dates, DAY_NAMES,
                        bike, run, strength, strip_tags, COLOR_IDS)

TZ = "-05:00"  # America/Toronto is on EST from 1 Nov 2026
MONTH = 2
MONTH_NAME = MONTHS[MONTH - 1][1]          # "Month 02 - November 2026"
WEEKS = MONTHS[MONTH - 1][2]               # [5, 6, 7, 8, 9]
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "month2_events.json")

# Provisional zones from hour-long outdoor rides at 160-180 W average. Re-test when keto adaptation has settled.
FTP = 190
Z = dict(z1="under 105 W", z2="105-140 W", z2hi="130-140 W", z3="145-170 W")

def cross(day, title, focus, rows, dur, notes="", start="06:00"):
    return dict(activity="Run", day=day, start=start, dur=dur, title=title, focus=focus, rows=rows, notes=notes, optional=True)

RUN_WU = ("Warm-up", "5 min brisk walk (3.5-3.8 mph), 1% incline. 20 slow calf raises off the back of the treadmill, 10 leg swings each way.")
RUN_CD = ("Cool-down", "5 min walk, then the 15-minute prehab routine (Achilles and Knee Prehab Guide). Heel drops first.")
RUN_RULES = ("Jog = 6.5-7.0 mph (8:35-9:15 per mile), walk = 3.5-3.8 mph. The cap is deliberate: speed is what loads the Achilles. "
             "Fast feet = cadence, not speed: on the marked reps hold 180 steps per minute at the same jog speed, shorter and quicker steps, "
             "landing under the hips. Pain scale 0 = no pain, 10 = worst pain; write it in the planner note.")
PREHAB_ROW = ("Prehab", "Eccentric heel drops straight and bent knee 3 x 15, step-downs 2 x 10 each, single-leg balance 2 x 30 s, calf stretch.")

def walkrun(day, reps, jog, walk, fast_reps, dur, extra="", start="06:00", label=None):
    total_jog = reps * jog
    main = "%d x (%s jog / %s walk). Reps %s at 180 steps per minute (fast feet, same speed). Total jog time %s." % (
        reps, _mmss(jog), _mmss(walk), fast_reps, _mmss(total_jog))
    t = label or "Treadmill walk/run %s:%s" % (_short(jog), _short(walk))
    rows = [RUN_WU, ("Main", main), RUN_CD]
    return run(day, t, "Aerobic, tendon-safe, cadence for the fast-legs feel", rows, dur, RUN_RULES + (" " + extra if extra else ""), start=start)

def _mmss(m):
    s = int(round(m * 60)); return "%d:%02d" % (s // 60, s % 60)
def _short(m):
    return ("%g" % m)

STR_A = [
    ("Goblet squat", "3 x {a} at 70 lb (Week 8 target 75 lb)", "Heels down, knees over toes, depth only as far as pain-free"),
    ("Dumbbell Romanian deadlift", "3 x {a} at 55 lb (Week 8 target 60 lb)", "Soft knees, hinge at the hip, flat back"),
    ("Push-up, or dumbbell floor press if the shoulder objects", "3 x {b}", "Pain-free only. Body in one line, elbows at 45 degrees"),
    ("Single-arm dumbbell row", "3 x {a} each at 70-75 lb", "Pull the elbow to the hip, no torso twist. Rows are the safe direction for the shoulder"),
    ("Low box jump or step-up", "3 x {c}", "Soft, quiet landings. Skip the jump on any day the Achilles is above 2/10"),
    ("Dead bug", "3 x {a} each side", "Low back glued to the floor"),
    ("Side plank", "3 x {d} s each", "Hips stacked"),
    ("Eccentric heel drops, straight and bent knee", "3 x 12-15 each at 90 lb", "Slow 3 s lowering. This is the most important exercise in the session"),
]
STR_B = [
    ("Machine glute thrust (replaces glute bridge)", "3 x {a} starting at 150 lb", "Your Sep 20 top was 250 lb; start light and leave 3 reps in reserve, add 10-20 lb per week"),
    ("Clamshell with band", "3 x 15 each", "Pelvis does not roll back"),
    ("Monster walk", "3 x 10 steps each way", "Stay low, knees out"),
    ("Step-down from low step", "3 x {s} each", "Knee over second toe, slow. Watch the knee the next morning"),
    ("Wall sit", "3 x {d} s", "Progress time, not depth"),
    ("Bent-knee calf raise (seated, weight on thigh)", "3 x 15 at 90 lb (Week 8 target 100 lb)", "Slow up, slow down"),
    ("Bird dog", "3 x {a} each side", "Hips level, reach long"),
    ("Pallof press (band)", "3 x {a} each side", "Resist the rotation"),
    ("Front plank", "3 x {d} s", "Squeeze glutes, breathe. Count 10-second blocks out loud"),
    ("Single-leg balance", "3 x 30 s each", "Eyes closed if easy"),
]
LEVELS = {5: dict(a=10, b=10, c=8, d=30, s=12), 6: dict(a=12, b=12, c=10, d=40, s=15), 7: dict(a=12, b=12, c=10, d=45, s=15),
          8: dict(a=12, b=14, c=10, d=45, s=15), 9: dict(a=8, b=8, c=6, d=30, s=10)}

def str_rows(exs, n):
    return [(name, s.format(**LEVELS[n]) + ". " + cue) for name, s, cue in exs]

def strength_pair(n, note_a, note_b):
    return [
        strength(0, "Strength A - Full-body foundation", "Movement quality, tendon loading, core", str_rows(STR_A, n), 45,
                 "Warm up 5 min easy, then 10 bodyweight squats, 10 hinges, 10 arm circles. Rest 60-90 s. Fasted is fine at this length. " + note_a),
        strength(4, "Strength B - Hips, knees, core", "Glute medius, patellar tracking, trunk stability. Now on its own day, no run before it.", str_rows(STR_B, n), 35,
                 "Warm up 5 min walk or easy spin. " + note_b),
    ]

def trainer(n, title, focus, rows, dur, notes=""):
    return bike(1, title, focus, rows, dur, notes + " Fan on, bottle with electrolytes. ERG mode at the stated watts (provisional FTP %d W)." % FTP)

def weekend(n, title, focus, rows, dur, notes=""):
    return bike(5, title, focus, rows, dur, notes + " Outdoors if 5 C or warmer and dry; otherwise the trainer version in the second row.", start="08:00")

def elliptical(n, dur):
    return cross(3, "Optional - Elliptical Zone 2", "Low-impact aerobic time, zero tendon cost. Skip it freely", [
        ("Main", "%d min at a conversational effort (heart rate under about 140). No intervals today." % dur),
    ], dur, "Only if the week feels good and the shoulder and legs are quiet. This is the first session to drop when life is busy.")

M2 = {}

M2[5] = dict(theme="Keto adaptation 1: settle in", bike=[
    trainer(5, "Trainer - Zone 2 with spin-ups", "Aerobic base, fast legs without metabolic cost", [
        ("Warm-up", "10 min building from %s to %s, cadence 85-90" % (Z["z1"], Z["z2"])),
        ("Main", "25 min at 115-130 W. Every 4 min: 30 s spin-up to 110+ rpm at the same watts (6 total). Sit tall, no bouncing."),
        ("Cool-down", "10 min easy, %s" % Z["z1"]),
    ], 45, "First week of the block. Heart rate will run high for the watts; that is adaptation, not a problem."),
    weekend(5, "Weekend ride - Zone 2", "60 minutes aerobic", [
        ("Outdoors", "60 min easy on the Tay loop or similar. Keep the effort to full-sentence conversation, avoid chasing the hills."),
        ("Trainer version", "10 min warm-up, 40 min at 115-135 W with 3 x 5 min at 95 rpm, 10 min cool-down."),
    ], 60)],
    run=[walkrun(2, 6, 1.5, 2.0, "5 and 6", 45), elliptical(5, 30), walkrun(6, 6, 1.5, 2.0, "5 and 6", 40, start="08:00")],
    strength=strength_pair(5, "Week 5: hold the Oct 8 loads. Push-ups only if the shoulder is at 0-1/10.", "First week with the machine glute thrust: 150 lb, 3 reps in reserve."))

M2[6] = dict(theme="Keto adaptation 2: one more rep", bike=[
    trainer(6, "Trainer - Zone 2, spin-ups and single-leg", "Pedalling skill while the engine adapts", [
        ("Warm-up", "10 min building to %s" % Z["z2"]),
        ("Main", "30 min at 115-135 W. Every 4 min: 30 s spin-up to 110+ rpm (8 total). Then 4 x (30 s left / 30 s right / 1 min both) single-leg in an easy gear."),
        ("Cool-down", "8 min easy"),
    ], 50),
    weekend(6, "Weekend ride - Zone 2", "75 minutes aerobic", [
        ("Outdoors", "75 min easy. Add 4 x 1 min at 100 rpm on the flats to keep it interesting."),
        ("Trainer version", "10 min warm-up, 55 min at 115-135 W with 2 x 10 min at 95 rpm, 10 min cool-down."),
    ], 75, "Carry water with sodium even if you eat nothing.")],
    run=[walkrun(2, 7, 1.5, 2.0, "6 and 7", 50), elliptical(6, 35), walkrun(6, 7, 1.5, 2.0, "6 and 7", 45, start="08:00")],
    strength=strength_pair(6, "Week 6: add 1-2 reps per set, same weights.", "Glute thrust +10-20 lb if Week 5 felt easy."))

M2[7] = dict(theme="Adaptation easing: a little more time at the top of Zone 2", bike=[
    trainer(7, "Trainer - upper Zone 2 blocks", "Sustained aerobic work at a brisk cadence", [
        ("Warm-up", "10 min building to %s, with 3 x 30 s spin-ups" % Z["z2"]),
        ("Main", "3 x 8 min at %s at 95 rpm / 4 min easy at %s between" % (Z["z2hi"], Z["z1"])),
        ("Cool-down", "10 min easy"),
    ], 60, "If breathing turns ragged in the blocks, drop 10 W rather than quitting the block."),
    weekend(7, "Weekend ride - Zone 2 with two lifts", "90 minutes, the longest of the block", [
        ("Outdoors", "90 min easy with 2 x 10 min at a brisk-but-conversational effort (upper Zone 2), 10 min easy between."),
        ("Trainer version", "10 min warm-up, 70 min at 115-135 W with 2 x 10 min at %s, 10 min cool-down." % Z["z2hi"]),
    ], 90, "Electrolytes in the bottle. Note how the last 20 min feel compared with Week 5.")],
    run=[walkrun(2, 6, 2.0, 2.0, "5 and 6", 50), elliptical(7, 40), walkrun(6, 6, 2.0, 2.0, "5 and 6", 45, start="08:00")],
    strength=strength_pair(7, "Week 7: heaviest week of the block. Goblet squat 75 lb, RDL 60 lb if the last two weeks were clean.", "Glute thrust to about 180 lb. Calf raise to 100 lb."))

M2[8] = dict(theme="Consolidate", bike=[
    trainer(8, "Trainer - upper Zone 2 blocks, lower cadence", "Same work, more torque", [
        ("Warm-up", "10 min building to %s, with 3 x 30 s spin-ups" % Z["z2"]),
        ("Main", "4 x 6 min at %s at 85-90 rpm / 3 min easy between" % Z["z2hi"]),
        ("Cool-down", "10 min easy"),
    ], 60),
    weekend(8, "Weekend ride - steady Zone 2", "90 minutes, no surges", [
        ("Outdoors", "90 min steady, full-sentence effort throughout. The goal is a flat heart rate line."),
        ("Trainer version", "10 min warm-up, 70 min at 120-135 W at 90 rpm, 10 min cool-down."),
    ], 90, "Compare average heart rate with Week 7. Lower at the same watts means adaptation is landing.")],
    run=[walkrun(2, 7, 2.0, 2.0, "6 and 7", 55), elliptical(8, 40), walkrun(6, 7, 2.0, 2.0, "6 and 7", 50, start="08:00")],
    strength=strength_pair(8, "Week 8: hold Week 7 loads, add a rep where it is clean.", "Hold Week 7 loads. Plank and wall sit to 45 s."))

M2[9] = dict(theme="Recovery week and checkpoint", bike=[
    trainer(9, "Trainer - easy spin", "Recovery", [
        ("Warm-up", "10 min easy"),
        ("Main", "20 min at 105-120 W at 90-95 rpm, 4 x 30 s spin-ups"),
        ("Cool-down", "10 min easy"),
    ], 40),
    bike(5, "Checkpoint ride - FTP test if adapted, otherwise easy", "Decide on the day", [
        ("If the 70% feeling has lifted", "20-minute FTP test on the trainer: 20 min warm-up (3 x 1 min at 100 rpm, 5 min hard-but-steady, 5 min easy), 20 min at the highest even power you can hold, 10 min cool-down. FTP = 20-min average x 0.95 = ________ W. Replace the provisional 190 W everywhere."),
        ("If not yet", "60 min easy Zone 2, outdoors or trainer. Test in Week 10 or 11 instead. Nothing is lost by waiting."),
    ], 60, "Either way, weigh in this week and write the number in the Month 2 reflection.", start="08:00")],
    run=[walkrun(2, 5, 1.5, 2.0, "4 and 5", 40), elliptical(9, 30), walkrun(6, 5, 1.5, 2.0, "4 and 5", 35, start="08:00")],
    strength=strength_pair(9, "Week 9: light. Weights down 20-30%, reps as listed.", "Light. Keep heel drops and calf raises at full volume."))

RUN_SUMMARY = {5: "6 x 1:30 / 2:00 (9 min jog)", 6: "7 x 1:30 / 2:00 (10.5 min)", 7: "6 x 2:00 / 2:00 (12 min)", 8: "7 x 2:00 / 2:00 (14 min)", 9: "5 x 1:30 / 2:00 (7.5 min)"}
HOURS = {5: "4.5 (+0.5 optional)", 6: "5.1 (+0.6)", 7: "5.6 (+0.7)", 8: "5.6 (+0.7)", 9: "4.1 (+0.5)"}

def activity_week_pdf(activity, n, sessions):
    mon, sun = week_dates(n)
    sub = "Week %d of 52 &nbsp;|&nbsp; %s to %s &nbsp;|&nbsp; Month %d: %s" % (n, mon.strftime("%a %d %b %Y"), sun.strftime("%a %d %b %Y"), MONTH, M2[n]["theme"])
    story = header_block(activity, "Week %02d %s" % (n, activity), sub)
    for s in sessions:
        d = mon + dt.timedelta(days=s["day"])
        block = [Paragraph("%s, %s &nbsp; %s &nbsp; (%d min)" % (DAY_NAMES[s["day"]], d.strftime("%d %b"), s["title"], s["dur"]), H2),
                 Paragraph("<b>Focus:</b> " + s["focus"], BODY), Spacer(1, 3)]
        rows = [["Section", "Details"]] + [[a, b] for a, b in s["rows"]]
        block.append(table(rows, [1.3*inch, 5.8*inch], color=COLORS[activity]))
        if s.get("notes"):
            block.append(Paragraph("<b>Notes:</b> " + s["notes"], BODY))
        block.append(Spacer(1, 6))
        story.append(KeepTogether(block))
    if activity == "Bike":
        story.append(Paragraph("Provisional power zones (FTP %d W, from your hour-long outdoor rides)" % FTP, H2))
        story.append(table([["Zone 1 recovery", "Zone 2 endurance", "Upper Zone 2", "Zone 3 tempo (not this month)"],
                            [Z["z1"], Z["z2"], Z["z2hi"], Z["z3"]]], [1.7*inch]*4, color=COLORS["Bike"]))
    if activity == "Run":
        story.append(Paragraph("Pain log (0 = no pain, 10 = worst pain)", H2))
        story.append(table([["Session", "During", "Next morning", "Jog speed used", "Notes"],
                            ["Wednesday", "", "", "", ""], ["Sunday", "", "", "", ""]], [1.1*inch, 0.9*inch, 1.1*inch, 1.2*inch, 2.8*inch], color=COLORS["Run"]))
    path = os.path.join(week_folder(activity, n), "Week %02d %s.pdf" % (n, activity))
    build_pdf(path, story, "Week %02d %s" % (n, activity))
    return path

def swim_note_pdf(n):
    story = header_block("Swim", "Week %02d Swim - paused" % n, "No swim is scheduled this week.")
    story.append(Paragraph("Why", H2))
    story.append(Paragraph("Shoulder recovery. Swimming resumes after two weeks of pain-free pressing (push-ups, floor press) and daily life. "
        "When that day comes, the first session is 20 minutes: 200 easy, 6 x 50 kick with board, 4 x 50 kick on side, 4 x 50 catch-up, 100 easy. No pulling sets, no paddles. "
        "If you swim this week on your own, write it in the next reflection. The Swim Drill Glossary in 00 - Plan Overview is still the pool sheet.", BODY))
    path = os.path.join(week_folder("Swim", n), "Week %02d Swim.pdf" % n)
    build_pdf(path, story, "Week %02d Swim" % n)

def overview_pdf():
    story = header_block("Plan", "Month 2 Overview - November 2026", "Weeks 5-9 &nbsp;|&nbsp; Phase: Keto-adaptation block &nbsp;|&nbsp; 2 November to 6 December 2026")
    story.append(Paragraph("What changed from Month 1, and why", H2))
    bullets(story, [
        "Built from the 13 Sep to 13 Oct reflection and your comments on it (Reflections folder).",
        "No swim scheduled: shoulder recovery. Return criteria are in each Swim week sheet.",
        "Everything aerobic stays in Zone 1-2 while the body learns to run on ketones (self-rated 70% on 15 Oct). Fast legs come from cadence: 30 s spin-ups on the trainer, 180 steps per minute on marked jog reps.",
        "No FTP test until the adaptation feeling lifts. Provisional FTP 190 W; checkpoint ride in Week 9 decides.",
        "Jog capped at 6.5-7.0 mph. Your 8.6 mph intervals felt fine, and the cap is still there because speed is the Achilles load. It rises in Month 3 if November is pain-free.",
        "Strength B moved to Friday: the Sunday run + strength brick was too hard on keto. Glute bridge replaced by machine glute thrust.",
        "Thursday is an optional elliptical session. First thing to drop in a busy week.",
    ])
    story.append(Paragraph("Weekly template", H2))
    story.append(table([
        ["Day", "Session", "Time", "Duration"],
        ["Monday", "Strength A - full-body foundation", "12:00 PM", "45 min"],
        ["Tuesday", "Bike - trainer, ERG, Zone 2 with spin-ups", "12:00 PM", "40-60 min"],
        ["Wednesday", "Run - treadmill walk/run + prehab", "12:00 PM", "40-55 min"],
        ["Thursday", "Optional - elliptical Zone 2", "12:00 PM", "30-40 min"],
        ["Friday", "Strength B - hips, knees, core", "12:00 PM", "35 min"],
        ["Saturday", "Bike - weekend ride (outdoor if 5 C+ and dry)", "10:00 AM", "60-90 min"],
        ["Sunday", "Run - treadmill walk/run (no strength after)", "10:00 AM", "35-50 min"],
    ], [1.0*inch, 3.4*inch, 1.0*inch, 1.7*inch]))
    story.append(Paragraph("Calendar slots are placeholders for a mid-day session; drag them to the real time on the day. Every event's single reminder fires at 8:00 AM, nothing earlier.", BODY))
    story.append(Paragraph("Week by week", H2))
    rows = [["Week", "Dates", "Theme", "Trainer", "Weekend ride", "Walk/run (x2)", "Hours"]]
    for n in WEEKS:
        mon, sun = week_dates(n)
        w = M2[n]
        rows.append([str(n), "%s - %s" % (mon.strftime("%d %b"), sun.strftime("%d %b")), w["theme"], "%d min" % w["bike"][0]["dur"], "%d min" % w["bike"][1]["dur"], RUN_SUMMARY[n], HOURS[n]])
    story.append(table(rows, [0.45*inch, 0.95*inch, 1.7*inch, 0.7*inch, 0.9*inch, 1.6*inch, 0.8*inch]))
    story.append(Paragraph("Fuelling on keto and modified OMAD", H2))
    bullets(story, [
        "Sessions up to 60 min: fasted is fine. Water.",
        "75-90 min rides: water with electrolytes (sodium first, then potassium and magnesium), even with no food. Many keto athletes need 1-2 g sodium per training hour in the first months.",
        "If a session falls apart in the second half (shaky, dizzy, power collapses), stop, walk, and note it. That is useful data, not a failure.",
    ])
    story.append(Paragraph("End-of-month checkpoint", H2))
    story.append(table([
        ["Measure", "Mid-Oct", "End of Month 2"],
        ["Body weight (lb)", "just under 200", ""], ["Provisional / tested FTP (W)", "190 (provisional)", ""], ["Walk/run pain scores at or under 3 (0 = no pain)", "", "____ of 10 sessions"],
        ["Shoulder: pain-free pressing for 2 weeks?", "improving", ""], ["Sessions completed", "", "____ of 30 (+5 optional)"], ["Average Garmin sleep score", "80-91", ""],
    ], [2.6*inch, 2.2*inch, 2.3*inch]))
    build_pdf(os.path.join(ROOT, MONTH_NAME, "Month 02 Overview.pdf"), story, "Month 02 Overview")

# Calendar slots and reminders (agreed 15 Oct 2026): Roberto trains mid-day and wants the ONE notification at 8:00 AM,
# never a 6 AM buzz. Weekdays start 12:00 with a 240-min popup; weekends start 10:00 with a 120-min popup. Both fire at 8:00.
SLOT = {"06:00": ("12:00", 240), "08:00": ("10:00", 120), "08:35": ("10:35", 155)}

def events():
    out = []
    for n in WEEKS:
        mon, _ = week_dates(n)
        for key in ["bike", "run", "strength"]:
            for s in M2[n][key]:
                d = mon + dt.timedelta(days=s["day"])
                slot, reminder = SLOT.get(s["start"], (s["start"], 240))
                h, m = slot.split(":")
                start = dt.datetime(d.year, d.month, d.day, int(h), int(m)); end = start + dt.timedelta(minutes=s["dur"])
                lines = ["Week %d of 52 - Month 2: %s" % (n, M2[n]["theme"]), "Focus: " + s["focus"], ""]
                for a, b in s["rows"]:
                    lines.append("%s: %s" % (a, strip_tags(b)))
                if s.get("notes"):
                    lines += ["", "Notes: " + strip_tags(s["notes"])]
                lines += ["", "Printout: " + os.path.join(week_folder(s["activity"], n), "Week %02d %s.pdf" % (n, s["activity"]))]
                title = ("%s: %s" % (s["activity"], s["title"])) if not s.get("optional") else s["title"]
                out.append(dict(summary=title, startTime=start.strftime("%Y-%m-%dT%H:%M:00") + TZ, endTime=end.strftime("%Y-%m-%dT%H:%M:00") + TZ,
                                description="\n".join(lines), colorId=COLOR_IDS[s["activity"]] if not s.get("optional") else "8",
                                reminderMinutes=reminder))
    return out

if __name__ == "__main__":
    overview_pdf()
    made = 1
    for n in WEEKS:
        swim_note_pdf(n); made += 1
        for act, key in zip(["Bike", "Run", "Strength"], ["bike", "run", "strength"]):
            activity_week_pdf(act, n, M2[n][key]); made += 1
    ev = events()
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(ev, f, indent=1)
    print("PDFs:", made, "Events:", len(ev))
