# M01 Test Plan

| Area | Test | Layer |
|---|---|---|
| Config | Missing/invalid env stops startup with clear error; secrets not logged | pytest unit |
| Health | `/health` ok with DB down; `/health/ready` 200 with DB, 503 standard error without | pytest integration (real Postgres) |
| Errors | Validation error → 400 format; unknown route → 404; raised exception → 500 `INTERNAL`, no traceback in body | pytest |
| Logging | One JSON log line per request with request id, status, duration; no body | pytest (capture) |
| Migrations | Fresh DB: upgrade head, tables/constraints exist, downgrade base | pytest integration |
| Dev identity | Seeded in development; startup fails if enabled with `ENVIRONMENT=production` | pytest unit |
| Web | Health widget shows loading, ok, and error states | Vitest + Testing Library |
| Contract | Regenerating TS types yields no diff | script |
| Static | mypy strict, ruff check/format, eslint, prettier, tsc | `check` script |
| Manual | Follow DEMO_SCRIPT from a clean shell | owner-visible |

Gates (TESTING_STRATEGY): all must pass or be disclosed. Playwright E2E and security/perf suites start in later milestones; their absence in M01 is expected and will be stated.
