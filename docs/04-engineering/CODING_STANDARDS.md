# Coding Standards

## Python (services/api)
- Python type hints everywhere; `mypy --strict` must pass; no `Any` without a comment explaining why.
- Validate at boundaries (HTTP input, env config, LLM output, JSON columns) with Pydantic models. Config via `pydantic-settings`, validated once at start; refuse to start on invalid config.
- Format and lint with Ruff. No wildcard imports.
- Layering: routers → services → repositories. Scheduling module is pure (no DB, no clock, no network). No circular imports.
- No SQL or session use in routers. No business rules in routers.
- Errors: raise typed `AppError(code, http_status, message)`; one exception handler maps to the API error format; never swallow; never leak internals; log with request id.
- Time: stdlib `datetime` with `zoneinfo`; aware datetimes only (naive datetimes rejected); UTC in storage; no manual DST math.
- Naming: `snake_case` functions/modules, `PascalCase` classes, verbs for functions (`create_task`, `generate_daily_schedule`), no cryptic abbreviations.

## TypeScript (apps/web)
- `strict: true`; no `any` without a comment. Prefer `unknown` + validation.
- API types come from the generated OpenAPI client; never hand-copy server types.
- No data fetching logic or business rules inside presentational components; feature folders under `src/features/`.
- Next.js server code is limited to rendering and the API rewrite; domain rules live in FastAPI.
- Accessible by default: labels, focus, contrast, not colour alone; reusable components in `components/ui`.

## Both
- Functions ≈10–40 lines; split by meaning, not mechanically.
- Comments explain *why*; each complex module has a README with its public interface.
- Each dependency needs a stated reason (need, maintenance, security, size, license); lockfiles committed.
- Technical debt is logged in `KNOWN_ISSUES.md` with impact and follow-up.
