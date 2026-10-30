# ADR-001: Language, backend, frontend, repo structure

Status: **Accepted 2026-10-27.** Next.js, FastAPI and PostgreSQL were chosen by the owner; the supporting choices are agent recommendations the owner delegated and approved. Exact versions are verified against official docs at M01 start. Supersedes the earlier React+Vite/Fastify proposal.

## Owner decisions
- Frontend: **Next.js** (React, TypeScript)
- Backend: **FastAPI** (Python)
- Database: **PostgreSQL**

## Delegated choices (recommended)
| Area | Choice | Reason |
|---|---|---|
| API models/validation | Pydantic v2 (comes with FastAPI) | Same models validate requests, LLM output and config |
| DB access | SQLAlchemy 2.x (sync) + psycopg 3 | Mature, typed, supports `FOR UPDATE SKIP LOCKED` needed by reminders; sync keeps code and tests simple, FastAPI runs sync routes in a thread pool |
| Migrations | Alembic | Standard companion to SQLAlchemy |
| Dependency/runtime management | uv + `pyproject.toml` + lockfile | Fast, reproducible; can install a pinned Python version |
| Python version | 3.12 or 3.13 (pin at M01). Dev machine has only 3.14.2; verify library support before using it | Avoid unproven binary wheels |
| Python quality tools | Ruff (lint+format), mypy `--strict` | One fast linter/formatter, strict typing |
| Python tests | pytest, Hypothesis (scheduler property tests) | Matches testing strategy |
| Dates/time | stdlib `datetime` + `zoneinfo` | No extra dependency; UTC storage |
| Worker | Separate Python process from same package (`python -m yadi.worker`) | See ADR-002 |
| Frontend tests/quality | Vitest, Testing Library, ESLint, Prettier, `tsc --noEmit`; Playwright for E2E | Standard for Next.js |
| API contract | FastAPI generates OpenAPI; TypeScript types generated with `openapi-typescript`; CI fails on drift | Replaces shared TS/Zod package, keeps both sides in sync |
| Repo | Monorepo: `apps/web` (Next.js), `services/api` (Python package + worker), `database/` only if needed beyond Alembic | Simple, no JS/Python package mixing |

## How Next.js is used
Mainly as the UI framework and dev/build tooling for a logged-in, interactive app. **Business logic stays in FastAPI**; Next.js route handlers/server actions are not used for domain rules. Browser calls go to the API through a Next.js rewrite (`/api/*` → FastAPI) so session cookies are same-origin (simpler CSRF and no CORS).

## Consequences
- Two languages and two toolchains (npm and uv). Cost accepted by owner; mitigated by OpenAPI-generated types and a single `make`/script entry point.
- Python is a good fit for the AI and scheduling work.
- Next.js adds a Node runtime to deploy (web container). Acceptable; documented in deployment plan.
- No shared validation code between client and server; client validates for UX only, server is authoritative.
