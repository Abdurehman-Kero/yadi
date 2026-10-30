# M01 — Application Foundation and Development Infrastructure

**Purpose:** a minimal but solid skeleton: Next.js app and FastAPI API running locally, PostgreSQL connected, migrations, health checks, strict quality tooling, tests, structured logging and consistent API errors. **No product features.**

**Status:** Planned (docs written 2026-10-27, no code yet).

## In scope
- Repo skeleton (`apps/web`, `services/api`, root scripts, docker compose for Postgres).
- API: app factory, config validation, `/api/v1/health` and `/health/ready`, error handler + error format, request-id middleware, structured JSON logging.
- Database: SQLAlchemy engine/session, Alembic set up, first migration creating `users` and `user_preferences` (minimal), seeded dev user.
- Web: Next.js app with a placeholder home page that calls the API health endpoint and shows status; `/api/*` rewrite to FastAPI.
- OpenAPI → TypeScript type generation with a CI/script drift check.
- Tooling: Ruff, mypy strict, pytest; ESLint, Prettier, `tsc`, Vitest; one-command `check` and `test` scripts.
- Env: `.env.example`, `.gitignore`, `.editorconfig`, `CONTRIBUTING.md`, README setup steps.
- Git init (with owner OK) and first commit.

## Out of scope
Tasks, AI, scheduling, reminders, real authentication, deployment.

## Requirements covered
NFR-MNT-001, NFR-SEC-001 (secrets handling pattern), NFR-SEC-003 (consistent errors), NFR-PRV-001 (log hygiene). See REQUIREMENTS.md.

## Prerequisites the owner must provide
1. Docker Desktop **running** (currently the engine is not running).
2. Install **uv** (agent can do this with owner OK: `pip install uv` or official installer).
