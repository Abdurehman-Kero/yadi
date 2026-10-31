# Decision Log

| ID | Date | Decision | Status | Rationale |
|---|---|---|---|---|
| D-001 | 2026-10-27 | Documentation-first, one milestone at a time, M00 before any code. | Accepted (owner spec) | Required by master specification. |
| D-002 | 2026-10-27 | Deterministic scheduling engine and reminder system; LLM only interprets and explains. | Accepted (owner spec) | Schedules must be verifiably valid. |
| D-003 | 2026-10-27 | Modular monolith, REST. | Accepted | Spec baseline. |
| D-005 | 2026-10-27 | **Owner chose** Next.js (frontend), FastAPI (backend), PostgreSQL (database). Supersedes React+Vite/Fastify proposal. | Accepted by owner | See ADR-001. |
| D-006 | 2026-10-27 | Delegated choices: Pydantic v2, SQLAlchemy 2 (sync) + psycopg 3, Alembic, uv, Ruff, mypy strict, pytest + Hypothesis, Vitest, Playwright, OpenAPI→TS generated types, Next.js rewrite proxy. | Accepted; versions verified in M01 | See ADR-001. |
| D-004 | 2026-10-27 | Reminders via durable DB-backed job queue (no in-memory timers). | Accepted (ADR-002) | Meets restart-recovery needs without adding Redis. |
| D-007 | 2026-10-27 | Auth: dev identity until M05, then Google sign-in (OIDC) with server-side sessions. | Accepted (ADR-005) | No password storage; fits Calendar later. |
| D-008 | 2026-10-27 | Multi-user data model, single user in practice; notifications in-app + Web Push; hosting deferred to before M11. | Accepted | Owner delegated to agent recommendation. |
| D-009 | 2026-10-30 | M01 implementation choices: Python 3.13 via uv; TS 5 + ESLint 9 kept from official scaffold; @types/node 24; DB on 127.0.0.1:5433; Next.js experimental flags removed; contract types via OpenAPI + drift check. | Accepted | See M01 COMPLETION_REPORT deviations. |
| D-010 | 2026-10-30 | Tartiiba (owner's separate app) features are **not** added to Yadi; it was only partly read and nothing from it is in the plan. | Accepted by owner | Owner: leave it completely and start M02. |
| D-011 | 2026-10-30 | M03: AI via adapter; model returns local time and the app converts it; no key means manual fallback. | Accepted | See M03 PLAN. |
| D-012 | 2026-10-30 | **Owner chose Google Gemini instead of Anthropic.** Default `gemini-3.5-flash-lite`. Free tier for development with synthetic data only; paid billing before real users, because free-tier content is used to improve Google's products. | Accepted by owner; model choice pending evaluation | Google pricing page, 2026-10-30. |
| D-013 | 2026-10-30 | **Documented exception:** owner chose to start M04 before M03's live accuracy test, and asked for a UI redesign within M04. The test is still owed before the MVP is called complete. | Accepted by owner | Rule 14 of the brief requires an explicit exception. |
| D-014 | 2026-10-30 | Generating a schedule applies it, with no separate accept step; the design uses neutral surfaces with one green accent. | Accepted (reversible) | Fewer steps for routine use; UX_PRINCIPLES. |
| D-015 | 2026-10-31 | Real sign-in moved out of M05 to its own step before any hosting. Reminders use the development identity until then. | Accepted by owner | Yadi runs only on the owner's computer for now. |
| D-016 | 2026-10-31 | Forms open in native `dialog` modals; generated browser-alert keys live only in `.env`. | Accepted | Owner asked for modals; no new dependency. |
| D-017 | 2026-10-31 | M06: one message box; replies written by code; conversation held in the browser only; flexible moves, complete, start and priority apply directly, while cancel, fixed moves, blocking time and past-deadline moves need confirmation. | Accepted (reversible) | See M06 PLAN. |
| D-018 | 2026-10-31 | Owner approved the real-model evaluations and the order: sign-in and deployment preparation next, then M07. Owner asked for better UI/UX; patterns recorded in UX_PRINCIPLES. | Accepted by owner | Owner: "go ahead". |

Architectural decisions get a full ADR in `docs/03-architecture/ADR/`.
