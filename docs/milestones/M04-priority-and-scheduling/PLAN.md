# M04 Plan

1. Migration 0004: fixed time and preferred period on tasks; `task_dependencies`, `schedule_blocks`, `schedule_runs`.
2. Pure engine, property tests first (Hypothesis), plus a brute-force comparison to measure how often the greedy order misses a feasible plan (ADR-004).
3. Schedule service and API; task lifecycle links.
4. Redesign: design tokens, app shell with sidebar and phone tab bar, components.
5. Today dashboard, Schedule screen, Tasks and Settings on the new design.
6. Browser and accessibility tests, including dark mode.
7. All gates, screenshots, report.

## Decisions
- Generating a schedule applies it. There is no separate "accept" step: the user reviews it and edits or regenerates, which keeps the routine path short. Task data is never changed beyond its scheduling status.
- A fixed event is a task with a fixed start and end, so it can be completed or cancelled like any task.
- Past blocks stay for display, but unfinished work is planned again in full, because Yadi cannot know how much was done. Partial progress tracking is deferred.
- Time-of-day windows: morning 05:00-12:00, afternoon 12:00-17:00, evening 17:00-22:00, always intersected with working hours.
- Reasons are written by the engine from facts it used, not by the AI.
