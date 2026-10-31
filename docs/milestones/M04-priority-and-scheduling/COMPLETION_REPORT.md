# M04 Completion Report

**Status: COMPLETE.** Owner approved 2026-10-31; committed in ace8bb6.

## Delivered
- Migration 0004: fixed times and preferred period on tasks; `task_dependencies`, `schedule_blocks`, `schedule_runs`.
- Pure deterministic engine; schedule, block-edit and dependency APIs; completing or cancelling a task removes its future blocks.
- Full interface redesign: sidebar and phone tab bar, Today dashboard, Schedule screen, Tasks, Settings, light and dark themes.

## Verified
- All gates: see the final line of this section for counts. pytest includes 150 random schedules checked against every hard constraint: no overlap, working hours, fixed events, buffers, dependency order, full minutes, deadlines, determinism.
- Greedy quality: on 300 small random cases, 237 had a feasible plan and the engine missed 3 (1.3%). This is a synthetic measure, not real user data.
- Generation p95: about 170 ms against a 500 ms target, 100 tasks, single client on this machine. Not a load test.
- Daylight-saving days tested in New York. Browser tests cover the fixed-event journey, conflict report, moving a block, and keeping it through replanning.
- axe finds no serious issues on any of the four screens in light or dark mode, on the data present during the test run. Screens viewed by the agent as screenshots on desktop and phone.
- Counts: pytest 143, vitest 20, Playwright 16; 10/10 gates.

## Not verified / limitations
- No screen-reader pass; no real-user usability testing of the new design.
- `FR-SCH-003` is partial for dependencies: they work in the engine and API, but there is no picker in the UI, and Tell Yadi cannot set them.
- Tell Yadi cannot create fixed events yet: "meeting at 10" arrives as a task due at 10, and the user ticks the fixed-time box in the draft.
- All seven days count as working days. Weekday-specific hours are planned for M07.
- Unfinished past work is replanned in full, because partial progress is not tracked.
- There is no separate "accept" step: generating applies the plan (see PLAN.md).
- Changing Settings does not flag a schedule as out of date.
- Two tabs editing at once: last save wins on task fields (KI-009).

## Exception
M03's live accuracy test was skipped at the owner's request (D-013) and is still owed.
