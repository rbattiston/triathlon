# -*- coding: utf-8 -*-
"""One-page pool sheet for the first swim back after the shoulder flare (Friday 30 Oct 2026, Week 4).
Run from this folder: python build_swim_return.py"""
import os
from build_plan import ROOT, COLORS, H2, BODY, inch, Paragraph, Spacer, table, build_pdf, header_block, bullets, week_folder

def main():
    story = header_block("Swim", "Return to the pool - Friday 30 October 2026",
                         "Week 4 &nbsp;|&nbsp; first swim since the shoulder flare &nbsp;|&nbsp; about 850 m, 25 minutes &nbsp;|&nbsp; fins allowed, no paddles")
    story.append(Paragraph("The order matters: legs first, drills second, easy pulling third, speed from the legs only. "
        "Sprinting freestyle is the biggest load the catch phase can take, so it waits for session three. "
        "Pace guide: easy freestyle today is 2:10-2:20 per 100 m, slower than your usual 2:00.", BODY))
    story.append(Spacer(1, 4))
    rows = [["Section", "Set", "How it should feel / cues"],
        ["1. Kick warm-up<br/>200 m", "4 x 50 kick, 15 s rest.<br/>Board, or on your back with arms at your sides.",
         "Legs do all the work; the shoulder just gets warm. If a streamline overhead pinches, push off the wall with arms at your sides."],
        ["2. Drills<br/>200 m", "4 x 50, 20 s rest:<br/>25 Fingertip drag / 25 easy freestyle<br/>25 Zipper / 25 easy freestyle<br/>(repeat)",
         "<b>Fingertip drag:</b> fingertips trail the surface on recovery, elbow high and pointing at the ceiling. "
         "<b>Zipper:</b> thumb runs from hip to armpit before reaching forward. Both keep the recovery high-elbow and the pull short. Breathe every 2, alternate sides each 50."],
        ["3. Easy swim<br/>200 m", "4 x 50 freestyle, 20 s rest.<br/>Long, relaxed, 2:10-2:20 pace.",
         "First real pulling of the day. Hand enters in front of the shoulder, never across the centre line. Fingertips down early, elbow high, press the water back toward your feet, not down."],
        ["4. Fast legs<br/>100 m", "4 x 25 fast kick with board, 30 s rest.",
         "This is today's speed set, legs only. Hips at the surface, kick from the hip, small fast feet. Enjoy it."],
        ["5. Cool-down<br/>150 m", "150 m easy: 50 kick on your back, 100 easy freestyle.",
         "Finish with the shoulder feeling warm and loose, not worked."],
    ]
    story.append(table(rows, [1.15*inch, 2.25*inch, 3.7*inch], color=COLORS["Swim"]))
    story.append(Paragraph("Stop rule", H2))
    bullets(story, [
        "Any sharp shoulder pain above 3/10 (0 = no pain, 10 = worst): drop sections 3 and 5, finish with kick only, and that still counts as a successful first swim.",
        "A dull ache or fatigue under 3/10 is fine. Note where in the stroke you feel it (reach, catch, pull-through, recovery).",
    ])
    story.append(Paragraph("What comes next", H2))
    story.append(table([["If the shoulder is...", "Next session (early next week)", "Session three"],
        ["0-1/10 the next morning", "Same sheet, plus 4 x 50 build to fast (easy to quick over the 50), 30 s rest, in place of section 4.", "Your speed set: 6 x 50 fast freestyle, 30 s rest, then kick."],
        ["2-3/10 the next morning", "Repeat this sheet exactly.", "Decide on the day."],
        ["Above 3/10, or sharp during", "Kick and drills only for a week, then try again.", "-"],
    ], [1.6*inch, 3.2*inch, 2.3*inch], color=COLORS["Swim"]))
    story.append(Paragraph("Shoulder log", H2))
    story.append(table([["During (0-10)", "Where in the stroke", "Next morning (0-10)", "Total distance", "Notes"], ["", "", "", "", ""]],
                       [1.1*inch, 1.6*inch, 1.3*inch, 1.1*inch, 2.0*inch], color=COLORS["Swim"]))
    path = os.path.join(week_folder("Swim", 4), "Week 04 Swim - Return to the pool (30 Oct).pdf")
    build_pdf(path, story, "Week 04 Swim - Return to the pool")
    print(path)

if __name__ == "__main__":
    main()
