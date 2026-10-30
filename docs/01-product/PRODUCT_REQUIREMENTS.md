# Product Requirements (summary)

Status: **Draft — proposed until the SRS is approved.** Formal requirements with IDs go in `docs/02-requirements/SRS.md`.

## MVP scope (proposed)
1. Identity: local dev identity first; real auth by M05 (Q3).
2. Dashboard: today's schedule, upcoming tasks, next action, prominent "tell Yadi" input.
3. Text natural-language task capture with AI extraction to structured data.
4. Editable title, deadline, duration, priority (Critical/High/Medium/Low), reminders.
5. Task list and daily schedule views.
6. Basic deterministic scheduler (fixed vs flexible, deadlines, working hours, conflicts reported).
7. Conversational updates and rescheduling via validated services.
8. Complete / cancel tasks; task history.
9. Persistent storage (PostgreSQL).
10. Server-side durable reminders.
11. Loading, empty, error, success states.
12. Settings: timezone, working hours, reminders, notification permission.
13. Automated tests on critical flows; docs and demo.

## Task lifecycle (proposed)
Inbox → Planned → Scheduled → In progress → Completed / Cancelled. "Deferred" is represented by rescheduling with history, not a separate status, to keep the model understandable. To be confirmed in the SRS.

## Not in MVP
Long-term memory, autonomous actions, calendar integration, voice (optional early only if cheap), multi-agent orchestration, wearables.

## Clarification rule
AI must never silently invent missing details. If ambiguity affects scheduling, ask or propose an editable assumption.
