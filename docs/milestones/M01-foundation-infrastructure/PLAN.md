# M01 Plan

## Verified versions (checked 2026-10-27 against PyPI and the npm registry)
| Package | Version | Notes |
|---|---|---|
| fastapi | 0.162.0 | Python ≥3.10; lists 3.12–3.14 |
| pydantic / pydantic-settings | 2.14.1 / 2.16.1 | settings needs Python ≥3.11 |
| sqlalchemy | 2.1.6 | Python ≥3.11 |
| alembic | 1.20.1 | |
| psycopg | 3.3.6 | use `psycopg[binary]` |
| uvicorn | 0.54.0 | |
| pytest / hypothesis | 9.1.1 / 6.170.12 | |
| ruff / mypy | 0.17.3 / 2.4.0 | |
| httpx | 0.28.1 | for TestClient/outbound calls |
| uv | 0.13.6 | not installed yet |
| next / react | 16.4.3 / 19.3.1 | Node ≥20.9 |
| typescript | 7.0.2 | |
| vitest | 5.0.5 | Node ^22.12 / ^24 |
| @playwright/test | 1.64.1 | used from M02+ |
| eslint / prettier | 10.13.0 / 3.9.10 | |
| openapi-typescript | 7.13.0 | |

Dev machine Node 24.12.0 satisfies every engine range. Exact versions are pinned by lockfiles at install; this table is what was *current*, not a promise those exact versions install together (confirm with the lockfile). Source: registry metadata only; release notes of Next.js 16, TypeScript 7 and Vitest 5 must be skimmed for breaking changes when scaffolding.

## Decision: Python version
All core libraries list Python 3.14 support, so Python 3.14 is not blocked. Pin **Python 3.13** in `.python-version`/`pyproject` via uv for the widest wheel coverage; revisit 3.14 later. (Resolves Q9.)

## Steps
1. Owner: start Docker Desktop; OK to install uv. Agent: `git init` (with OK).
2. Root: `.gitignore`, `.editorconfig`, `.env.example`, `CONTRIBUTING.md`, `docker-compose.yml` (postgres, named volume, healthcheck, port 5432 on localhost only).
3. `services/api`: `pyproject.toml` (uv, ruff, mypy strict, pytest config), package `yadi/` with `config.py`, `main.py` (app factory), `core/errors.py`, `core/logging.py`, `core/request_id.py`, `db/session.py`, `modules/health/router.py`.
4. Tests first for health, errors, config, logging; then implement.
5. Alembic init, migration 0001 (`users`, `user_preferences`), seed dev user script, migration up/down test using a throwaway database.
6. `apps/web`: scaffold Next.js (TypeScript, ESLint, App Router, no Tailwind unless needed), `next.config` rewrite for `/api/*`, home page health widget, Vitest + Testing Library.
7. OpenAPI export script → `openapi-typescript` → `apps/web/src/api/schema.d.ts`; drift check script.
8. Root scripts `scripts/check` and `scripts/test` (PowerShell and shell variants for this Windows machine).
9. README setup + `ENVIRONMENT_SETUP.md` updated to what actually works.
10. Run all gates; write TEST results and COMPLETION_REPORT; demo script dry-run.

## Risks
Docker engine not running; Next 16 / TS 7 / Vitest 5 are new major versions (possible tooling friction → fall back one major if blocked, recording it in the DECISION_LOG); Windows path/shell differences.
