# -*- coding: utf-8 -*-
"""Month 2 (November 2026, Weeks 5-9): keto-adaptation block. Builds PDFs and the calendar event JSON.
Run from this folder: python build_month2.py"""
import os, json, datetime as dt
from build_plan import (ROOT, MONTHS, ACTIVITIES, COLORS, H2, BODY, inch, Paragraph, Spacer, KeepTogether,
                        table, build_pdf, header_block, bullets, week_folder, week_monday, week_dates, DAY_NAMES,
                        bike, run, strength, strip_tags, COLOR_IDS, drill_cards, DRILLS)

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
    ("Warm-up (5 min)", "Monster walk 2 x 10 steps each way, clamshell 1 x 15 each, 10 slow bodyweight step-downs each leg", "The band work is the warm-up now, not the session"),
    ("Machine glute thrust", "3 x {a} starting at 150 lb (Week 7 target 180-200 lb)", "Your Sep 20 top was 250 lb. 2 s squeeze at the top, ribs down, leave 3 reps in reserve"),
    ("Bulgarian split squat, rear foot on a bench, dumbbells", "3 x {a} each leg at 2 x 25 lb (Week 7 target 2 x 35 lb)", "Front shin near vertical, knee over the second toe, torso tall. This is the squat pattern running actually uses"),
    ("Single-leg dumbbell deadlift", "3 x {a} each leg at 35-40 lb", "Hinge, free-side hip stays level, a hand on the rack for balance is fine. Hamstring and glute medius together"),
    ("Weighted step-down from a 6-8 inch step", "3 x {s} each leg holding a 20-25 lb dumbbell goblet-style", "Slow 3 s lower, free heel taps the floor, knee never dives inward. Patellar tracking under load"),
    ("Leg press calf raise, straight knee", "3 x 15 at 180 lb (Week 7 target 200 lb)", "Full range, 3 s down, 30 s rest as you already do. Achilles capacity"),
    ("Copenhagen plank, short lever (knee on the bench)", "3 x {e} s each side", "Top knee and shin on the bench, bottom leg bent, hips in line. Adductors protect the knee; build time, not lever length"),
    ("Cable Pallof press", "3 x {a} each side at 25-30 lb", "Cable at chest height, arms long, resist the twist. Add 5 lb when 12 feel easy"),
    ("Suitcase carry", "3 x 40 m each hand with a 50-70 lb dumbbell", "Walk tall, shoulders level, no lean. Lateral core under real load; the finisher you will enjoy"),
]
LEVELS = {5: dict(a=10, b=10, c=8, d=30, s=12, e=20), 6: dict(a=12, b=12, c=10, d=40, s=15, e=25), 7: dict(a=12, b=12, c=10, d=45, s=15, e=30),
          8: dict(a=12, b=14, c=10, d=45, s=15, e=30), 9: dict(a=8, b=8, c=6, d=30, s=10, e=20)}

def str_rows(exs, n):
    return [(name, s.format(**LEVELS[n]) + ". " + cue) for name, s, cue in exs]

def strength_pair(n, note_a, note_b):
    return [
        strength(0, "Strength A - Full-body foundation", "Movement quality, tendon loading, core", str_rows(STR_A, n), 45,
                 "Warm up 5 min easy, then 10 bodyweight squats, 10 hinges, 10 arm circles. Rest 60-90 s. Fasted is fine at this length. " + note_a),
        strength(4, "Strength B - Single-leg strength", "Run durability: glute medius, patellar tracking, Achilles, adductors, lateral core. The same muscles as the band version, loaded.", str_rows(STR_B, n), 45,
                 "Rebuilt 29 Oct 2026 from your end-of-October comments: the band version felt like accessory work. Every stride lands about 2.5 x bodyweight on one leg; this session is what makes that safe. "
                 "Rest 60-90 s, nothing to failure, own day with no run before it. " + note_b),
    ]

def trainer(n, title, focus, rows, dur, notes=""):
    return bike(1, title, focus, rows, dur, notes + " Fan on, bottle with electrolytes. ERG mode at the stated watts (provisional FTP %d W)." % FTP)

def weekend(n, title, focus, rows, dur, notes=""):
    return bike(5, title, focus, rows, dur, notes + " Outdoors if 5 C or warmer and dry; otherwise the trainer version in the second row.", start="08:00")

def elliptical(n, dur):
    return cross(3, "Optional - Elliptical Zone 2", "Low-impact aerobic time, zero tendon cost. Skip it freely", [
        ("Main", "%d min at a conversational effort (heart rate under about 140). No intervals today." % dur),
    ], dur, "Only if the week feels good and the shoulder and legs are quiet. This is the first session to drop when life is busy.")


def swim2(day, title, focus, rows, drills, total, dur, notes="", start="06:00"):
    for d in drills:
        assert d in DRILLS, d
    return dict(activity="Swim", day=day, start=start, dur=dur, title=title, focus=focus, rows=rows, drills=drills, total=total, notes=notes)

# Swimming returns in Month 2 (first swim back 30 Oct 2026: 850 m, shoulder 1/10, 1:50 per 100 m at a low heart rate,
# 13 strokes per 25 m). Roberto's stated priority: learn the feeling of being fast in the water after ten years of plodding
# endurance swimming. So: short fast 25s and 50s with full rest, stroke count as the honesty check, fins as a tool.
# Endurance volume waits until the fast stroke is the default. Monday swim sits after Strength A; Thursday swim replaces
# the optional elliptical (which stays as the no-pool fallback).
SWIM_WU = ("Warm-up", "100 kick with fins (board, or on your back), then 100 easy FS. Fins are fine for every kick this month; bare-foot kick is not a speed set for anyone.")
SWIM_CD = ("Cool-down", "100 easy, any stroke, finish with the shoulder loose, not worked.")
SWIM_FAST = ("Fast means the quickest stroke you can hold at 12-13 strokes per 25 m (your count on 30 Oct). If the count climbs to 15-16 you are muscling it: "
             "take the full rest and swim the next one smoother, not harder. Rest is part of the set, never shorten it.")
SWIM_GATE = ("Shoulder gate: the fast set happens only if the morning after the last swim was 0-1/10 (0 = no pain). At 2-3, swim the same distance easy instead. "
             "Sharp pain above 3 during a swim: kick and drills only, stop pulling. Fins yes, paddles no.")
THU_NOTE = "No pool today? 30-40 min elliptical at a conversational effort is the fallback, not a replacement to prefer."

def swim_pair(n, a_rows, a_drills, a_total, a_dur, a_title, b_rows, b_drills, b_total, b_dur, b_title, a_focus, b_focus, extra_a="", extra_b=""):
    return [
        swim2(0, a_title, a_focus, [SWIM_WU] + a_rows + [SWIM_CD], a_drills, a_total, a_dur,
              SWIM_FAST + " " + SWIM_GATE + (" " + extra_a if extra_a else ""), start="06:50"),
        swim2(3, b_title, b_focus, [SWIM_WU] + b_rows + [SWIM_CD], b_drills, b_total, b_dur,
              SWIM_FAST + " " + SWIM_GATE + " " + THU_NOTE + (" " + extra_b if extra_b else "")),
    ]

SWIMS = {}
SWIMS[5] = swim_pair(5,
    [("Drills", "4 x 50 (25 Fingertip drag / 25 FS) r20"),
     ("Main", "8 x 25 Build 50-style (easy to fast over the length) r30. Reps 1-4 with fins, 5-8 without. Count strokes on every one and write the counts on the sheet."),
     ("Easy", "4 x 50 FS r20 at 1:50-2:00, long and relaxed")],
    ["Fingertip drag", "Build 50", "Stroke count"], 900, 30, "Swim 1 - Fast feel, build 25s",
    [("Drills", "4 x 50 (25 Zipper / 25 FS) r20"),
     ("Main", "6 x 50 as 25 fast / 25 easy r30. Fins on reps 2, 4 and 6. The fast 25 is quick and smooth, the easy 25 is where you notice what changed.")],
    ["Zipper", "Stroke count"], 800, 25, "Swim 2 - Fast feel, 25 fast / 25 easy",
    "Speed exposure with fins first, then without. Shoulder still settling, so builds rather than flat-out.",
    "Same idea from a push: fast length, easy length.",
    extra_a="First swim of the block: if anything feels off, the Easy set is the session and the Main set waits a week.")

SWIMS[6] = swim_pair(6,
    [("Drills", "4 x 50 (25 Catch-up / 25 FS) r20"),
     ("Main", "10 x 25 fast r30, alternating fins / no fins. On the no-fin ones hold 12-13 strokes; that is the whole game."),
     ("Easy", "4 x 50 FS r20")],
    ["Catch-up", "Stroke count"], 950, 30, "Swim 1 - Fast 25s, fins on and off",
    [("Drills", "4 x 50 6-3-6 r20"),
     ("Main", "8 x 50 as 25 fast / 25 easy r30. Fins on the even reps. Try to make the fast 25 without fins feel like the one with fins: hips high, quick turnover, not more kick.")],
    ["6-3-6", "Stroke count"], 900, 30, "Swim 2 - 25 fast / 25 easy, longer",
    "Ten fast lengths, half with fins. The fins show you the position; the bare-foot ones are where you keep it.",
    "Two more 50s than last week, same rule.")

SWIMS[7] = swim_pair(7,
    [("Drills", "4 x 50 (25 Fist drill / 25 FS) r20"),
     ("Main", "6 x 50 fast r40. Fins on 1, 3 and 5. Hold the stroke count across both lengths; the second 25 is where it usually climbs."),
     ("Easy", "4 x 50 FS r20")],
    ["Fist drill", "Stroke count"], 1000, 32, "Swim 1 - Fast 50s",
    [("Drills", "4 x 50 (25 Fingertip drag / 25 FS) r20"),
     ("Main", "3 rounds of (4 x 25 fast r20, then 50 easy). Rounds 1-2 without fins, round 3 with fins so the last fast lengths of the day are the quickest.")],
    ["Fingertip drag", "Stroke count"], 950, 30, "Swim 2 - Fast 25s in rounds",
    "First fast 50s. Twice the distance per rep, so the stroke count tells you more.",
    "Short rest inside the round, a long easy 50 between rounds.")

SWIMS[8] = swim_pair(8,
    [("Drills", "4 x 50 (25 Catch-up / 25 FS) r20"),
     ("Main", "8 x 50 fast r40, no fins. Note the time of each 50 off the watch and the stroke count. Aim: every 50 faster than 1:40 per 100 pace at 12-13 strokes per 25."),
     ("Easy", "4 x 50 FS r20")],
    ["Catch-up", "Stroke count"], 1100, 35, "Swim 1 - Fast 50s, no fins",
    [("Drills", "4 x 50 (25 Zipper / 25 FS) r20"),
     ("Main", "12 x 25 fast r30. Fins on 1-4, then 8 without. Same count, same feel, no fins."),
     ("Easy", "4 x 50 FS r20")],
    ["Zipper", "Stroke count"], 1000, 32, "Swim 2 - Twelve fast 25s",
    "The biggest fast set of the block, all bare-foot. This is the week you find out if the fins taught you anything.",
    "Volume of fast lengths up, fins down.")

SWIMS[9] = swim_pair(9,
    [("Drills", "4 x 50 (25 Fingertip drag / 25 FS) r20"),
     ("Main", "4 x Build 50 r30 with fins. Easy, and enjoy the speed at the end of each.")],
    ["Fingertip drag", "Build 50"], 700, 22, "Swim 1 - Recovery week, builds only",
    [("Drills", "4 x 50 (25 Catch-up / 25 FS) r20"),
     ("Checkpoint", "200 m time trial from a push, no fins, even pace. Record the time and the stroke count per 25 on the sheet. Reference from 30 Oct: 1:50 per 100 average, best 50 at 1:34 pace, 13 strokes per 25. "
                    "Only if the shoulder has been 0-1/10 for the last two weeks; otherwise swim 4 x 50 easy instead and test in Week 10."),
     ("Easy", "4 x 50 FS r20")],
    ["Catch-up", "Stroke count"], 900, 28, "Swim 2 - Checkpoint 200 m",
    "Light week. No fast set, just the feeling.",
    "The number for the Month 2 reflection. Pace per 100 and strokes per 25 together, not pace alone.")

M2 = {}

M2[5] = dict(swim=SWIMS[5], theme="Keto adaptation 1: settle in", bike=[
    trainer(5, "Trainer - Zone 2 with spin-ups", "Aerobic base, fast legs without metabolic cost", [
        ("Warm-up", "10 min building from %s to %s, cadence 85-90" % (Z["z1"], Z["z2"])),
        ("Main", "25 min at 115-130 W. Every 4 min: 30 s spin-up to 110+ rpm at the same watts (6 total). Sit tall, no bouncing."),
        ("Cool-down", "10 min easy, %s" % Z["z1"]),
    ], 45, "First week of the block. Heart rate will run high for the watts; that is adaptation, not a problem."),
    weekend(5, "Weekend ride - Zone 2", "60 minutes aerobic", [
        ("Outdoors", "60 min easy on the Tay loop or similar. Keep the effort to full-sentence conversation, avoid chasing the hills."),
        ("Trainer version", "10 min warm-up, 40 min at 115-135 W with 3 x 5 min at 95 rpm, 10 min cool-down."),
    ], 60)],
    run=[walkrun(2, 6, 1.5, 2.0, "5 and 6", 45), walkrun(6, 6, 1.5, 2.0, "5 and 6", 40, start="08:00")],
    strength=strength_pair(5, "Week 5: hold the Oct 8 loads. Push-ups only if the shoulder is at 0-1/10.", "Week 5: find the loads. Glute thrust 150 lb, split squat 2 x 25 lb, single-leg deadlift 35 lb, 3 reps in reserve everywhere."))

M2[6] = dict(swim=SWIMS[6], theme="Keto adaptation 2: one more rep", bike=[
    trainer(6, "Trainer - Zone 2, spin-ups and single-leg", "Pedalling skill while the engine adapts", [
        ("Warm-up", "10 min building to %s" % Z["z2"]),
        ("Main", "30 min at 115-135 W. Every 4 min: 30 s spin-up to 110+ rpm (8 total). Then 4 x (30 s left / 30 s right / 1 min both) single-leg in an easy gear."),
        ("Cool-down", "8 min easy"),
    ], 50),
    weekend(6, "Weekend ride - Zone 2", "75 minutes aerobic", [
        ("Outdoors", "75 min easy. Add 4 x 1 min at 100 rpm on the flats to keep it interesting."),
        ("Trainer version", "10 min warm-up, 55 min at 115-135 W with 2 x 10 min at 95 rpm, 10 min cool-down."),
    ], 75, "Carry water with sodium even if you eat nothing.")],
    run=[walkrun(2, 7, 1.5, 2.0, "6 and 7", 50), walkrun(6, 7, 1.5, 2.0, "6 and 7", 45, start="08:00")],
    strength=strength_pair(6, "Week 6: add 1-2 reps per set, same weights.", "Week 6: +10-20 lb on the glute thrust, +5 lb per dumbbell where Week 5 was clean."))

M2[7] = dict(swim=SWIMS[7], theme="Adaptation easing: a little more time at the top of Zone 2", bike=[
    trainer(7, "Trainer - upper Zone 2 blocks", "Sustained aerobic work at a brisk cadence", [
        ("Warm-up", "10 min building to %s, with 3 x 30 s spin-ups" % Z["z2"]),
        ("Main", "3 x 8 min at %s at 95 rpm / 4 min easy at %s between" % (Z["z2hi"], Z["z1"])),
        ("Cool-down", "10 min easy"),
    ], 60, "If breathing turns ragged in the blocks, drop 10 W rather than quitting the block."),
    weekend(7, "Weekend ride - Zone 2 with two lifts", "90 minutes, the longest of the block", [
        ("Outdoors", "90 min easy with 2 x 10 min at a brisk-but-conversational effort (upper Zone 2), 10 min easy between."),
        ("Trainer version", "10 min warm-up, 70 min at 115-135 W with 2 x 10 min at %s, 10 min cool-down." % Z["z2hi"]),
    ], 90, "Electrolytes in the bottle. Note how the last 20 min feel compared with Week 5.")],
    run=[walkrun(2, 6, 2.0, 2.0, "5 and 6", 50), walkrun(6, 6, 2.0, 2.0, "5 and 6", 45, start="08:00")],
    strength=strength_pair(7, "Week 7: heaviest week of the block. Goblet squat 75 lb, RDL 60 lb if the last two weeks were clean.", "Week 7: heaviest week. Glute thrust 180-200 lb, split squat 2 x 35 lb, calf raise 200 lb."))

M2[8] = dict(swim=SWIMS[8], theme="Consolidate", bike=[
    trainer(8, "Trainer - upper Zone 2 blocks, lower cadence", "Same work, more torque", [
        ("Warm-up", "10 min building to %s, with 3 x 30 s spin-ups" % Z["z2"]),
        ("Main", "4 x 6 min at %s at 85-90 rpm / 3 min easy between" % Z["z2hi"]),
        ("Cool-down", "10 min easy"),
    ], 60),
    weekend(8, "Weekend ride - steady Zone 2", "90 minutes, no surges", [
        ("Outdoors", "90 min steady, full-sentence effort throughout. The goal is a flat heart rate line."),
        ("Trainer version", "10 min warm-up, 70 min at 120-135 W at 90 rpm, 10 min cool-down."),
    ], 90, "Compare average heart rate with Week 7. Lower at the same watts means adaptation is landing.")],
    run=[walkrun(2, 7, 2.0, 2.0, "6 and 7", 55), walkrun(6, 7, 2.0, 2.0, "6 and 7", 50, start="08:00")],
    strength=strength_pair(8, "Week 8: hold Week 7 loads, add a rep where it is clean.", "Week 8: hold Week 7 loads. Copenhagen plank to 30 s, add a rep where it is clean."))

M2[9] = dict(swim=SWIMS[9], theme="Recovery week and checkpoint", bike=[
    trainer(9, "Trainer - easy spin", "Recovery", [
        ("Warm-up", "10 min easy"),
        ("Main", "20 min at 105-120 W at 90-95 rpm, 4 x 30 s spin-ups"),
        ("Cool-down", "10 min easy"),
    ], 40),
    bike(5, "Checkpoint ride - FTP test if adapted, otherwise easy", "Decide on the day", [
        ("If the 70% feeling has lifted", "20-minute FTP test on the trainer: 20 min warm-up (3 x 1 min at 100 rpm, 5 min hard-but-steady, 5 min easy), 20 min at the highest even power you can hold, 10 min cool-down. FTP = 20-min average x 0.95 = ________ W. Replace the provisional 190 W everywhere."),
        ("If not yet", "60 min easy Zone 2, outdoors or trainer. Test in Week 10 or 11 instead. Nothing is lost by waiting."),
    ], 60, "Either way, weigh in this week and write the number in the Month 2 reflection.", start="08:00")],
    run=[walkrun(2, 5, 1.5, 2.0, "4 and 5", 40), walkrun(6, 5, 1.5, 2.0, "4 and 5", 35, start="08:00")],
    strength=strength_pair(9, "Week 9: light. Weights down 20-30%, reps as listed.", "Week 9: light. Weights down 20-30%, keep the calf raises at full volume."))

RUN_SUMMARY = {5: "6 x 1:30 / 2:00 (9 min jog)", 6: "7 x 1:30 / 2:00 (10.5 min)", 7: "6 x 2:00 / 2:00 (12 min)", 8: "7 x 2:00 / 2:00 (14 min)", 9: "5 x 1:30 / 2:00 (7.5 min)"}
HOURS = {5: "5.6", 6: "6.3", 7: "6.8", 8: "6.9", 9: "5.1"}

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

def swim_week_pdf(n):
    mon, sun = week_dates(n)
    sub = "Week %d of 52 &nbsp;|&nbsp; %s to %s &nbsp;|&nbsp; Month %d: %s" % (n, mon.strftime("%a %d %b %Y"), sun.strftime("%a %d %b %Y"), MONTH, M2[n]["theme"])
    story = header_block("Swim", "Week %02d Swim" % n, sub)
    story.append(Paragraph("The idea this month: short fast lengths with full rest, stroke count as the honesty check, fins as a teaching tool. "
        "Endurance volume comes back once the fast stroke is the default. 25 m pool. Every swim is 700-1,100 m and 22-35 minutes.", BODY))
    story.append(Spacer(1, 4))
    for s_ in M2[n]["swim"]:
        d = mon + dt.timedelta(days=s_["day"])
        block = [Paragraph("%s, %s &nbsp; %s &nbsp; (%d min)" % (DAY_NAMES[s_["day"]], d.strftime("%d %b"), s_["title"], s_["dur"]), H2),
                 Paragraph("<b>Focus:</b> " + s_["focus"], BODY), Spacer(1, 3)]
        rows = [["Section", "Details"]] + [[a, b] for a, b in s_["rows"]]
        block.append(table(rows, [1.3*inch, 5.8*inch], color=COLORS["Swim"]))
        block.append(Paragraph("<b>Total:</b> about %d m" % s_["total"], BODY))
        block.append(Paragraph("<b>Notes:</b> " + s_["notes"], BODY))
        block.append(Spacer(1, 6))
        story.append(KeepTogether(block))
    names = []
    for s_ in M2[n]["swim"]:
        for dname in s_["drills"]:
            if dname not in names:
                names.append(dname)
    story += drill_cards(names)
    story.append(Paragraph("Shoulder and stroke log (0 = no pain, 10 = worst pain)", H2))
    story.append(table([["Session", "Shoulder during", "Next morning", "Strokes per 25, fast", "Best 25 or 50 time", "Notes"],
                        ["Monday", "", "", "", "", ""], ["Thursday", "", "", "", "", ""]],
                       [0.9*inch, 1.0*inch, 1.0*inch, 1.3*inch, 1.2*inch, 1.7*inch], color=COLORS["Swim"]))
    path = os.path.join(week_folder("Swim", n), "Week %02d Swim.pdf" % n)
    build_pdf(path, story, "Week %02d Swim" % n)
    return path

def overview_pdf():
    story = header_block("Plan", "Month 2 Overview - November 2026", "Weeks 5-9 &nbsp;|&nbsp; Phase: Keto-adaptation block &nbsp;|&nbsp; 2 November to 6 December 2026")
    story.append(Paragraph("What changed from Month 1, and why", H2))
    bullets(story, [
        "Built from the 13 Sep to 13 Oct reflection and your comments on it (Reflections folder).",
        "Swimming is back (first swim 30 Oct, shoulder 1/10): two short swims a week, Monday after Strength A and Thursday in place of the elliptical. Built around the feeling of being fast: 25s and 50s with full rest, stroke count as the check, fins as a tool. Volume comes later.",
        "Everything aerobic stays in Zone 1-2 while the body learns to run on ketones (self-rated 70% on 15 Oct). Fast legs come from cadence: 30 s spin-ups on the trainer, 180 steps per minute on marked jog reps.",
        "No FTP test until the adaptation feeling lifts. Provisional FTP 190 W; checkpoint ride in Week 9 decides.",
        "Jog capped at 6.5-7.0 mph. Your 8.6 mph intervals felt fine, and the cap is still there because speed is the Achilles load. It rises in Month 3 if November is pain-free.",
        "Strength B moved to Friday: the Sunday run + strength brick was too hard on keto. Rebuilt 29 Oct as a heavier single-leg day (glute thrust, split squat, single-leg deadlift, weighted step-down, calf raise, Copenhagen plank, Pallof press, suitcase carry): the same protective muscles, loaded like the big lifts you enjoy.",
        "The optional elliptical is gone from the calendar; it stays as the no-pool fallback in the Thursday swim notes.",
    ])
    story.append(Paragraph("Weekly template", H2))
    story.append(table([
        ["Day", "Session", "Time", "Duration"],
        ["Monday", "Strength A - full-body foundation", "12:00 PM", "45 min"],
        ["Monday", "Swim 1 - fast feel (after Strength A, or move to Tuesday)", "12:50 PM", "22-35 min"],
        ["Tuesday", "Bike - trainer, ERG, Zone 2 with spin-ups", "12:00 PM", "40-60 min"],
        ["Wednesday", "Run - treadmill walk/run + prehab", "12:00 PM", "40-55 min"],
        ["Thursday", "Swim 2 - fast feel (elliptical only if no pool)", "12:00 PM", "25-32 min"],
        ["Friday", "Strength B - single-leg strength (run durability)", "12:00 PM", "45 min"],
        ["Saturday", "Bike - weekend ride (outdoor if 5 C+ and dry)", "10:00 AM", "60-90 min"],
        ["Sunday", "Run - treadmill walk/run (no strength after)", "10:00 AM", "35-50 min"],
    ], [1.0*inch, 3.4*inch, 1.0*inch, 1.7*inch]))
    story.append(Paragraph("Calendar slots are placeholders for a mid-day session; drag them to the real time on the day. Every event's single reminder fires at 8:00 AM, nothing earlier.", BODY))
    story.append(Paragraph("Week by week", H2))
    rows = [["Week", "Dates", "Theme", "Trainer", "Weekend ride", "Walk/run (x2)", "Swims (x2)", "Hours"]]
    for n in WEEKS:
        mon, sun = week_dates(n)
        w = M2[n]
        rows.append([str(n), "%s - %s" % (mon.strftime("%d %b"), sun.strftime("%d %b")), w["theme"], "%d min" % w["bike"][0]["dur"], "%d min" % w["bike"][1]["dur"], RUN_SUMMARY[n],
                     "%d + %d m" % (w["swim"][0]["total"], w["swim"][1]["total"]), HOURS[n]])
    story.append(table(rows, [0.45*inch, 0.95*inch, 1.45*inch, 0.65*inch, 0.85*inch, 1.3*inch, 0.85*inch, 0.6*inch]))
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
        ["Shoulder: pain-free pressing for 2 weeks?", "improving", ""], ["200 m swim time trial (time, strokes per 25)", "30 Oct: 1:50/100 avg, 13 strokes", ""], ["Sessions completed", "", "____ of 40"], ["Average Garmin sleep score", "80-91", ""],
    ], [2.6*inch, 2.2*inch, 2.3*inch]))
    build_pdf(os.path.join(ROOT, MONTH_NAME, "Month 02 Overview.pdf"), story, "Month 02 Overview")

# Calendar slots and reminders (agreed 15 Oct 2026): Roberto trains mid-day and wants the ONE notification at 8:00 AM,
# never a 6 AM buzz. Weekdays start 12:00 with a 240-min popup; weekends start 10:00 with a 120-min popup. Both fire at 8:00.
SLOT = {"06:00": ("12:00", 240), "06:50": ("12:50", 290), "08:00": ("10:00", 120), "08:35": ("10:35", 155)}

def events():
    out = []
    for n in WEEKS:
        mon, _ = week_dates(n)
        for key in ["swim", "bike", "run", "strength"]:
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
        swim_week_pdf(n); made += 1
        for act, key in zip(["Bike", "Run", "Strength"], ["bike", "run", "strength"]):
            activity_week_pdf(act, n, M2[n][key]); made += 1
    ev = events()
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(ev, f, indent=1)
    print("PDFs:", made, "Events:", len(ev))
