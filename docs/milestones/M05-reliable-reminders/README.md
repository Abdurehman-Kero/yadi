# M05 — Reliable Reminders and Background Jobs

**Purpose:** reminders fire from a background worker whether or not Yadi is open, survive restarts, never arrive twice, and are recorded. This milestone also moves the app's forms into modal dialogs, at the owner's request.

**Status:** Complete, except one manual browser-alert try. See COMPLETION_REPORT.md.

## In scope
- Durable reminders stored in PostgreSQL; a separate worker process (ADR-002).
- Reminders that follow the task: fixed start, first planned block, or deadline. They update when plans change and cancel when a task is finished.
- In-app notification centre (always) and Web Push (when configured and permitted).
- Retries with backoff, duplicate prevention, recovery after crashes, delivery records, snooze.
- Reminder settings per task; notification permission and reminder-service status in Settings.
- Modal dialogs for new task, edit task, move block, cancel confirmation, and reviewing Tell Yadi drafts.

## Out of scope
Real sign-in (moved to its own step before hosting, D-015), email, sound guarantees, daily briefings (M10), recurring reminders.

## Requirements covered
FR-NOT-001 to FR-NOT-005, FR-TASK-005 (reminder half), FR-SET-001 (notification half), NFR-PERF-002, NFR-REL-001.
