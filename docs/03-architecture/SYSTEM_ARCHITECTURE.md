# System Architecture

Status: Proposed (M00). Decisions backed by ADR-001 to ADR-005.

## Shape
A **modular monolith**: one Next.js web app, one FastAPI API process, one worker process (same Python package as the API), one PostgreSQL database. No microservices, no Redis in the MVP.

```
Browser (Next.js / React UI)
   │ HTTPS; /api/* proxied by Next.js rewrite → same-origin cookies
   ▼
API (FastAPI, Python, Pydantic)
   ├─ modules: users · tasks · scheduling · reminders · assistant · preferences
   ├─ AI adapter  ──► LLM provider (server-side key only)
   └─ PostgreSQL (tasks, events, schedule, reminders = job queue, audit)
        ▲
Worker process (reminder dispatcher; polls DB with SKIP LOCKED)
   └─ delivery channels: in-app, Web Push (later email)
```

## Responsibilities
| Component | Owns | Must not |
|---|---|---|
| Web client | UI, forms, client state | Hold secrets, query DB, contain scheduling rules |
| API/transport | Routing, auth, validation, error mapping | Contain business rules |
| Task service | Task CRUD, lifecycle, history | Call LLM directly |
| Scheduling engine | Pure functions: tasks+events+prefs → plan/conflicts | Do I/O, call LLM |
| Assistant module | Turns messages into validated *intents*, calls services | Write to DB itself, bypass validation |
| AI adapter | Prompts, SDK, retries, timeouts, usage tracking | Leak provider types outside its folder |
| Reminders | Reminder records, scheduling, state machine | Send notifications (delivery is separate) |
| Delivery | Channel transport, attempt records | Decide *when* to send |
| Persistence | Queries, migrations, transactions | Hold business decisions |

## Key flows
1. **Capture:** message → assistant → AI adapter → Pydantic-validated `TaskDraft[]` → user reviews/edits → task service saves → scheduling re-run → reminders created.
2. **Conversational change:** message → AI returns `Intent` → resolver finds target task(s) (ask if >1) → scheduling validates → service applies in a transaction → response states actual result.
3. **Reminder:** worker claims due row (`FOR UPDATE SKIP LOCKED`) → delivery → attempt recorded → state updated; crash leaves row reclaimable after lease expiry.

## Time
All instants stored as UTC `timestamptz`; the user's IANA timezone is stored in preferences; local-time conversions happen only at the edges using the user's zone.

## Single-user now, multi-user ready
Every user-owned table has `user_id`; every query is scoped by it (see SECURITY_AND_PRIVACY).
