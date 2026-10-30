# Environment Setup

Verified on the dev machine (Windows 11) during M01.

## Prerequisites
- Docker Desktop (engine running). Node.js ≥ 22 (dev: 24.12.0) and npm. Git.
- Python 3.13 via **uv**: `pip install --user uv`, invoked as `python -m uv` (the `uv` command is not on PATH). uv downloads Python 3.13 itself; the machine's own Python is 3.14.2.

## Steps
See the Quick start in the root `README.md`. Summary: copy `.env.example` → `.env`; `docker compose up -d db`; in `services/api` run `uv sync`, `alembic upgrade head`, the seed, and uvicorn; in `apps/web` run `npm install` and `npm run dev`.

## Notes and gotchas
- Database host port is **5433** (avoids clashing with any local Postgres); always use `127.0.0.1`, not `localhost` (IPv6 attempt stalls ~200 s on this machine).
- API config is validated at startup (`pydantic-settings`); invalid/missing `DATABASE_URL` or `ENVIRONMENT` stops the process.
- The dev identity is seeded only when `ENVIRONMENT=development`; `DEV_IDENTITY_ENABLED=true` is rejected in production.
- Regenerate frontend API types after changing the API: `node scripts/api-types.mjs` (the `check` gate fails if stale).
- Environments: development, test, production. Production secrets never live in the repo.
