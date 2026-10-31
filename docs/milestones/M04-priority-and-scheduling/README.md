# M04 — Priority and Intelligent Scheduling

**Purpose:** Yadi builds a realistic plan around fixed commitments, working hours and deadlines, explains it, and says honestly what does not fit. This milestone also delivers the Today dashboard and a redesign of the whole interface, at the owner's request.

**Status:** Complete. See COMPLETION_REPORT.md.

**Exception (D-013):** the owner chose to start M04 before M03's live accuracy test. M03 remains open; its test is still owed before the MVP is called complete.

## In scope
- Fixed-time tasks, preferred time of day, task dependencies (engine and API).
- Pure deterministic scheduling engine with property tests.
- Generate, read and manually edit a schedule; locked blocks survive regeneration.
- Conflict reporting with reasons and alternatives; plain-language reasons from the engine (no AI).
- Today dashboard, Schedule screen, redesigned Tasks and Settings.

## Out of scope
AI priority suggestions, AI-worded explanations, reminders (M05), chat changes (M06), recurrence, unavailable ranges (M06), weekday-specific working hours (M07), a dependency picker in the UI.

## Requirements covered
FR-PRI-001, FR-PRI-002, FR-SCH-001 to FR-SCH-006, FR-UI-001.
