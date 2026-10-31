# M01 Completion Report

**Status: COMPLETE.** Verified 2026-10-30; owner committed it (035c673) and started M02.

## Delivered
- Docker Compose PostgreSQL 17; `.env.example`, `.gitignore`, `.editorconfig`, `CONTRIBUTING.md`.
- FastAPI app factory with validated settings, `/api/v1/health` (no DB) and `/api/v1/health/ready` (DB check, 503 in the standard error format), request-id middleware, one JSON access-log line per request (no bodies), centralized error handlers.
- SQLAlchemy engine (5 s connect timeout), Alembic migration 0001 (`users`, `user_preferences` with check constraints), development-only seed of one dev user.
- Next.js 16 app with a health widget (loading / ok / error states) and `/api/*` rewrite to FastAPI.
- OpenAPI → TypeScript type generation with a stale-types check.
- `node scripts/run.mjs check|test|all` running nine gates.

## Verified (evidence, 2026-10-30)
- `node scripts/run.mjs all`: 9 of 9 PASS (ruff format, ruff lint, mypy strict, prettier, eslint, tsc, API-types freshness, pytest 15 passed, vitest 4 passed).
- Migration up/down and constraints tested on throwaway databases; seed idempotent and refuses outside development.
- Live run: migrated and seeded the dev DB (verified with psql); API and Next.js ran together; `/api/v1/health/ready` returned ok directly and through the Next.js proxy; with the DB stopped it returned HTTP 503 `SERVICE_UNAVAILABLE` with a request id and no credentials, liveness stayed ok, and it recovered after restart.
- `npm audit --omit=dev`: 0 vulnerabilities. `.env` is git-ignored.

## Not verified / limitations
- The page was not viewed in a browser or screenshot; its states are covered by component tests and HTML/proxy responses.
- No Playwright E2E, accessibility (axe), security or performance suites yet (planned from M02 on). `pip-audit` not run.
- Docs generator scripts for the Word files are still not in the repo (KI-005).

## Deviations from the plan (all logged)
- Scaffold selected TypeScript 5 and ESLint 9 (not 7 / 10); `@types/node` raised to 24 for Vitest 5; kept as is.
- Removed the scaffold's `cacheComponents` / `partialPrefetching` flags (unneeded).
- DB host port 5433 and `127.0.0.1` instead of `localhost` (IPv6 stall of ~200 s on this machine).
- uv installed as 0.11.16 (pip's resolution), not the 0.13.6 the index listed.
- `httpx` is used by Starlette's test client with a deprecation warning recommending `httpx2`; harmless, revisit later.

## Remaining
Owner approval; the owner makes the first git commit. Then M02 planning.
