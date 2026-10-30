# Roadmap

Baseline from the master specification. One milestone at a time; each ends with a verified COMPLETION_REPORT and demo.

| ID | Name | Outcome |
|---|---|---|
| M00 | Discovery, product definition, repo foundation | Approved docs, architecture proposal, ADRs, roadmap, risks, open questions |
| M01 | Application foundation | Runs locally, DB connected, health check, lint/type/test tooling, migrations, logging, API errors |
| M02 | Core task management | CRUD, statuses, persistence, UI states — works without AI |
| M03 | AI-powered task capture | Natural language → validated structured task, fallback on provider failure |
| M04 | Priority and scheduling | Deterministic scheduler, conflicts reported, editable/regenerable plan |
| M05 | Reliable reminders | Durable jobs, retries, idempotency, snooze, delivery records |
| M06 | Conversational management | Update/complete/reschedule via assistant through validated services |
| M07 | Preferences and memory | Editable preferences, user-controlled memory |
| M08 | Calendar integration | External calendar sync with conflict/duplicate handling |
| M09 | Voice input | Speech to text with review before commit |
| M10 | Proactive assistance and refinement | Risk warnings, briefings, accessibility, security review |
| M11 | Production readiness | Security tests, backup/restore, monitoring, release candidate |

## Proposed adjustment (needs owner approval)
Real authentication is not placed in the baseline until M11-ish, but reminders (M05) and any deployment require it. Proposal: carry a `user_id` on all data from M01, and implement real auth no later than M05. Recorded as OPEN_QUESTIONS Q3.

Detailed milestone docs are written just before each milestone starts.
