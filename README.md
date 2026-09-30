# Triathlon Training - 12-Month Ironman Plan

Week 1 starts Monday 5 October 2026. Week 52 ends Sunday 3 October 2027 (assumed race day).

## Folder layout

```
00 - Plan Overview/            Roadmap, swim drill glossary, prehab guide (print once)
Month 01 - October 2026/       Month Overview PDF
  Swim/Week 01 .. Week 04/     One printable PDF per week with every swim of that week + drill cue cards
  Bike/Week 01 .. Week 04/
  Run/Week 01 .. Week 04/
  Strength/Week 01 .. Week 04/
Month 02 - November 2026/      Weeks 05-09 (folders ready, workouts written at end of Month 1)
...
Month 12 - September 2027/     Weeks 49-52
```

Months follow calendar months; weeks start on Monday. Four months (Nov, Mar, May, Aug) hold 5 weeks so the 52 weeks fit exactly.

## Calendar

Every session is a Google Calendar event on the primary calendar, colour-coded
(swim blue, bike green, run orange, strength purple). The event description holds the
full workout and the path to the matching PDF.

## Regenerating

`00 - Plan Overview/_generator/build_plan.py` builds the folders, PDFs and the
calendar event list. Each new month's sessions are added to that script.
