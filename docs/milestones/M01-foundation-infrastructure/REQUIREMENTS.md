# M01 Requirements

| ID | Requirement | Acceptance criterion |
|---|---|---|
| M01-R1 | One command starts db, api, web locally from a clean checkout following README. | Documented steps succeed on this machine. |
| M01-R2 | `GET /api/v1/health` returns 200 `{status:"ok"}` without touching the DB. `GET /api/v1/health/ready` returns 200 only when the DB answers `SELECT 1`, else 503 in the standard error format. | Tests for both states (DB up/down). |
| M01-R3 | Config comes from environment, validated at startup; invalid/missing required values stop the process with a clear message; secrets never logged. | Test with bad env; log inspection test. |
| M01-R4 | All API errors use the format in API_SPECIFICATION.md with a request id; unknown errors return `INTERNAL` with no stack trace. | Tests for validation, not-found, unhandled exception. |
| M01-R5 | Logs are structured JSON with request id, method, path, status, duration; no request bodies. | Test captures a log line and checks fields. |
| M01-R6 | Alembic migration creates `users` and `user_preferences`; upgrade from empty DB works and downgrade works. | Migration test up/down on fresh DB. |
| M01-R7 | Dev identity user is seeded only when `ENVIRONMENT=development`; startup refuses dev identity in production. | Unit test. |
| M01-R8 | Frontend page shows API health fetched through the `/api/*` rewrite, with loading and error states. | Component test + manual demo. |
| M01-R9 | TypeScript API types are generated from OpenAPI; a check command fails if the committed types are stale. | Script test. |
| M01-R10 | `check` runs mypy strict, Ruff lint+format check, ESLint, Prettier check, `tsc`; `test` runs pytest and Vitest; all pass. | Both commands exit 0. |
| M01-R11 | Repo hygiene: `.env` ignored, `.env.example` complete, no secrets committed. | Manual + secret-scan check. |
