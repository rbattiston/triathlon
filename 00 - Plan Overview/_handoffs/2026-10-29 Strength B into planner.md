# Handoff: enter the rebuilt Strength B into BAI Daily Manager (planner.battiston.ai)

You are working on the server that hosts BAI Daily Manager, Roberto Battiston's own training app
(planner.battiston.ai). Your job is to add the rebuilt **Strength B - Single-leg strength** workout to the
app's Workouts > Programs data directly in the database, so Roberto can start it from the Log tab on the day.
Do not touch any logged session history.

## Source of truth

Repository: github.com/rbattiston/triathlon (public), branch `main`, commit `addaed6` or later.

- `00 - Plan Overview/_generator/build_month2.py`: the `STR_B` list is the exercise definition
  (name, sets-and-reps template, cue). The `LEVELS` dict gives the per-week values that fill the
  `{a}`, `{s}` and `{e}` placeholders. Weeks 5 to 9 are Fridays 6, 13, 20, 27 Nov and 4 Dec 2026.
- `00 - Plan Overview/_generator/month2_events.json`: the same sessions fully expanded as plain text,
  one entry per Friday, `summary` starts with "Strength: Strength B".
- The table below is the expanded version so you do not have to parse either file.

## Before you write anything

1. Inspect how the existing program for **Strength A - Full-body foundation** is stored (tables, columns,
   how exercises link to programs, order, sets/reps/weight defaults, per-side flags, timed holds,
   muscle-group tags, notes/cues, RIR). Mirror that structure exactly. Strength A is the template.
2. List the existing exercise records and reuse them wherever the movement is the same. Known existing
   names in the planner (as shown in its Stats tab on 29 Oct 2026):
   - `Monster Walk (band)`, `Clamshell (band)`, `Step-down (low step)`: reuse for the warm-up.
   - `Glute Thrusts` (machine, top 250 lb on 20 Sep 2026): reuse for the machine glute thrust.
   - `Leg Press Calf Raises 30s Rest` (top 180 lb on 20 Oct 2026): reuse for the leg press calf raise.
   - `Pallof Press (band)`: do NOT reuse for the cable version; create a separate cable exercise so the
     load history stays clean.
   Reusing an existing exercise record keeps the Stats tab's progression tracking intact. Only create a
   new exercise when nothing matches.
3. Take a database backup, or run the change inside a transaction you can roll back.

## The workout

Program name: `Strength B - Single-leg strength`
Short description / focus: `Run durability: glute medius, patellar tracking, Achilles, adductors, lateral core. The same muscles as the band version, loaded.`
Program note (shown once): `Every stride lands about 2.5 x bodyweight on one leg; this session is what makes that safe. Rest 60-90 s, nothing to failure, own day with no run before it.`
Scheduled days: Fridays 6, 13, 20, 27 Nov and 4 Dec 2026, plus one first run on a day Roberto picks in the
window 30 Oct to 1 Nov 2026 (use Week 5 values for that one).

Exercises, in this order. Weights are pounds. "each" means per leg or per side (unilateral, log L/R if
the schema supports it). "s" means a timed hold in seconds, not reps.

| # | Exercise (planner name to use) | Type / tags | Week 5 | Week 6 | Week 7 | Week 8 | Week 9 | Cue (store as the exercise note) |
|---|---|---|---|---|---|---|---|---|
| 1 | Monster Walk (band) [existing] | warm-up, Glutes | 2 x 10 steps each way | same | same | same | same | Warm-up. Stay low, knees out |
| 2 | Clamshell (band) [existing] | warm-up, Glutes | 1 x 15 each | same | same | same | same | Warm-up. Pelvis does not roll back |
| 3 | Step-down (low step) [existing] | warm-up, Legs | 1 x 10 each, bodyweight, slow | same | same | same | same | Warm-up. Knee over the second toe |
| 4 | Glute Thrusts [existing] | Glutes; secondary Legs | 3 x 10 at 150 | 3 x 12 at 160-170 | 3 x 12 at 180-200 | 3 x 12 at 180-200 | 3 x 8 at 130-150 | 2 s squeeze at the top, ribs down, leave 3 reps in reserve |
| 5 | Bulgarian Split Squat (dumbbells) [new] | Legs; secondary Glutes; unilateral | 3 x 10 each at 2 x 25 | 3 x 12 each at 2 x 25-30 | 3 x 12 each at 2 x 35 | 3 x 12 each at 2 x 35 | 3 x 8 each at 2 x 25 | Rear foot on a bench. Front shin near vertical, knee over the second toe, torso tall |
| 6 | Single-leg Dumbbell Deadlift [new] | Legs, Glutes; secondary Back; unilateral | 3 x 10 each at 35 | 3 x 12 each at 35-40 | 3 x 12 each at 40 | 3 x 12 each at 40 | 3 x 8 each at 30 | Hinge, free-side hip stays level, a hand on the rack for balance is fine |
| 7 | Step-down (weighted, 6-8 inch step) [new] | Legs; secondary Glutes; unilateral | 3 x 12 each at 20 | 3 x 15 each at 20-25 | 3 x 15 each at 25 | 3 x 15 each at 25 | 3 x 10 each at 20 | Dumbbell held goblet-style. Slow 3 s lower, free heel taps the floor, knee never dives inward |
| 8 | Leg Press Calf Raises 30s Rest [existing] | Calves | 3 x 15 at 180 | 3 x 15 at 180-190 | 3 x 15 at 200 | 3 x 15 at 200 | 3 x 15 at 180 | Straight knee, full range, 3 s down, 30 s rest |
| 9 | Copenhagen Plank (short lever) [new] | Abs, Legs (adductors); unilateral; timed | 3 x 20 s each | 3 x 25 s each | 3 x 30 s each | 3 x 30 s each | 3 x 20 s each | Top knee and shin on the bench, bottom leg bent, hips in line. Build time, not lever length |
| 10 | Pallof Press (cable) [new] | Abs; unilateral | 3 x 10 each at 25 | 3 x 12 each at 25-30 | 3 x 12 each at 30 | 3 x 12 each at 30 | 3 x 8 each at 25 | Cable at chest height, arms long, resist the twist. Add 5 lb when 12 feel easy |
| 11 | Suitcase Carry [new] | Abs; secondary Back; unilateral | 3 x 40 m each hand at 50-60 | 3 x 40 m each hand at 60 | 3 x 40 m each hand at 60-70 | 3 x 40 m each hand at 60-70 | 3 x 40 m each hand at 50 | Walk tall, shoulders level, no lean |

Weekly notes (store on the program or the dated instance, whichever the schema supports):

- Week 5 (6 Nov, and the first run on 30 Oct to 1 Nov): "Find the loads. Glute thrust 150 lb, split squat 2 x 25 lb, single-leg deadlift 35 lb, 3 reps in reserve everywhere."
- Week 6 (13 Nov): "+10-20 lb on the glute thrust, +5 lb per dumbbell where Week 5 was clean."
- Week 7 (20 Nov): "Heaviest week. Glute thrust 180-200 lb, split squat 2 x 35 lb, calf raise 200 lb."
- Week 8 (27 Nov): "Hold Week 7 loads. Copenhagen plank to 30 s, add a rep where it is clean."
- Week 9 (4 Dec): "Light. Weights down 20-30%, keep the calf raises at full volume."

## Decisions you can make without asking

- If the schema stores one program with default sets/reps/weight (no per-week variation), store the
  **Week 5** values and put the weekly progression in the program note. Roberto progresses loads in the log.
- If the schema stores dated program instances (one per scheduled day), create five, one per Friday, with
  that week's values, plus the first-run instance if a date is obvious; otherwise leave the first run as
  Week 5 values with no date.
- Group exercises 1 to 3 as a warm-up superset if the schema has supersets; otherwise keep them as the
  first three exercises with "Warm-up." at the start of each note.
- Distance for the suitcase carry: if there is no distance field, store it as reps = 1 with "40 m each
  hand" in the note.
- Muscle-group tags follow the existing taxonomy (Legs, Glutes, Calves, Abs, Back, Chest, Shoulders,
  Biceps, Triceps). Primary first, secondary as marked.

## Do not

- Do not modify or delete any existing exercise record, any logged session, or the Strength A program.
- Do not rename `Glute Thrusts`, `Leg Press Calf Raises 30s Rest` or the band exercises.
- Do not create a second copy of an exercise that already exists.

## When finished, report

1. Program ID(s) created and the dates attached.
2. For each of the 11 exercises: reused (with existing ID) or created (with new ID).
3. Anything in the schema that did not fit the table above and how you handled it.
4. Confirm the program renders in the Workouts > Programs tab and can be started from the Log tab.
