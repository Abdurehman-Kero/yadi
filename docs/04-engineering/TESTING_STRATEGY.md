# Testing Strategy

| Layer | Tool | Scope |
|---|---|---|
| Backend unit | pytest, Hypothesis | Validation, date resolver, scheduling engine (property tests), priority rules, state machines |
| Backend integration | pytest + real PostgreSQL (Docker, per-run database) + FastAPI `TestClient` | Repositories, API routes, authorization/isolation, reminder worker claim/retry/recovery, AI adapter with fake and recorded responses |
| Frontend unit/component | Vitest + Testing Library | Components, hooks, forms |
| E2E | Playwright | Create task, extract from text, generate schedule, reschedule, complete, trigger reminder, AI failure fallback |
| Contract | OpenAPI → TS types regenerated in CI; diff must be empty | Client/server drift |
| Security | pytest cross-user tests, `pip-audit`, `npm audit`, secret scan | Isolation, input fuzz, no secrets in bundle/logs |
| Accessibility | axe via Playwright + manual keyboard/screen-reader pass | Per screen |
| Performance | k6 + timing tests | Budgets in PERFORMANCE_BUDGETS |
| AI evaluation | Fixture-based eval harness (pytest) | Extraction accuracy, unnecessary clarifications, invalid actions |

## Quality gates (every milestone)
1. `mypy --strict` and `tsc --noEmit` 2. `ruff check` and ESLint 3. `ruff format --check` and Prettier check 4. unit tests 5. integration tests 6. E2E (where applicable) 7. Alembic migrations verified up (and down where feasible) on a fresh DB 8. no unresolved critical security issue 9. docs match implementation 10. DEMO_SCRIPT executed end to end.
Any gate not run is disclosed in COMPLETION_REPORT.

## Rules
Tests for a bug are written before the fix. LLM calls are never made in CI. Reminder tests use an injectable clock. Synthetic data only.
