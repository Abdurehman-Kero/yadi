# M02 Requirements

| ID | Requirement | Acceptance criterion |
|---|---|---|
| M02-R1 | Create a task with title (required), description, due date/time, estimated minutes, priority. | Invalid input returns 400 with field details; the form shows the message and keeps what was typed. |
| M02-R2 | View tasks, newest first, filtered Active / Completed / Cancelled, paginated. | Cursor pagination returns every task exactly once. |
| M02-R3 | Edit task fields, including clearing due date and estimate. | Edits survive a page refresh. Status cannot be changed through edit. |
| M02-R4 | Lifecycle: inbox, planned, in_progress, completed, cancelled (`scheduled` is reserved for M04). Illegal changes return 409 `CONFLICT`. | State-machine tests cover every pair. |
| M02-R5 | A task with both a due date and an estimate is automatically `planned`; otherwise `inbox` (until started). | Tested on create, edit and reopen. |
| M02-R6 | Completed tasks can be reopened; cancelled tasks are final; finished tasks cannot be edited. | Tested; cancelling asks for confirmation in the UI. |
| M02-R7 | Every change writes a history event with actor, in the same transaction. History is viewable per task. | Tested. |
| M02-R8 | A user can never read or change another user's tasks: other users' tasks return 404. | Isolation test on every task route. |
| M02-R9 | Settings: timezone (validated IANA name), working hours (end after start), default reminder minutes, buffer minutes. | Invalid values rejected; dates display and are entered in the saved timezone, including across DST. |
| M02-R10 | Dev identity only works when `DEV_IDENTITY_ENABLED=true`; otherwise 401. Rejected in production at startup. | Tested. |
| M02-R11 | Every screen has loading, empty, error and success states and works by keyboard. | Component and E2E tests; no serious axe violations. |
| M02-R12 | Database outage returns 503 in the standard format, not 500. | Tested. |
| M02-R13 | Task list API p95 <= 150 ms for 50 items with 2,000 tasks (NFR-PERF-001). | Measured by test, on this dev machine. |
