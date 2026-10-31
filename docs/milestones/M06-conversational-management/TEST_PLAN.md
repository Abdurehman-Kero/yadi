# M06 Test Plan

| Area | Test | Layer |
|---|---|---|
| Actions | Each action changes stored data; history actor; reminders follow | pytest + Postgres |
| Resolution | One, several, none, invalid numbers, recent-task context | pytest |
| Confirmation | Nothing changes before confirm; apply re-checks | pytest |
| Move | Date, period, time, working hours, overlap, buffer, deadline, fixed, past dates, no estimate | pytest |
| Hostile input | Bad model output, foreign ids, injection text in prompts | pytest |
| Prompt | Minimal fields, limits, delimiters | pytest |
| Questions | Next, free time, today, empty states | pytest |
| UI | Thread, options, confirm, create route, fallback | Vitest, Playwright |
| Evaluation | Scorer on fixed answers; live run is manual | pytest |
