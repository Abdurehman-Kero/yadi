# M02 — Core Task Management

**Purpose:** a useful task manager that works without AI: create, edit, complete, cancel and reopen tasks, with persistent storage, history, basic settings and clear UI states.

**Status:** Built and verified, awaiting owner approval. See COMPLETION_REPORT.md.

## In scope
- `tasks` and `task_events` tables; REST API; lifecycle rules; per-user isolation.
- Development identity (ADR-005) as the only "login" for now.
- `/tasks` and `/settings` screens; timezone-correct dates.
- Playwright end-to-end tests and axe accessibility checks (first time in the project).

## Out of scope
AI capture (M03), scheduling and the `scheduled` status transitions (M04), reminders (M05), real sign-in (M05), recurrence, dependencies, fixed-time events.

## Requirements covered
FR-TASK-002, FR-TASK-003, FR-TASK-004, FR-TASK-005 (the task half; reminders arrive in M05), FR-SET-001 (timezone and working hours; reminder default stored only), NFR-SEC-002, NFR-SEC-003, NFR-PERF-001, NFR-ACC-001.
