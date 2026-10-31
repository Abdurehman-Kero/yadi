# Yadi

AI-powered personal assistant for organizing daily life through natural conversation: task capture, realistic scheduling, reliable reminders, and (later) permissioned memory and calendar integration.

**Status:** Working app: tasks, Tell Yadi (Gemini), and a scheduling engine with a Today dashboard. Latest: change-by-chat evaluated on real Gemini, and a UI/UX redesign. Real sign-in is needed before hosting.

## Where to start

| If you want to... | Read |
|---|---|
| Resume work after an interruption | [docs/06-agent/AGENT_PROGRESS.md](docs/06-agent/AGENT_PROGRESS.md) |
| Understand the product | [docs/01-product/PRODUCT_VISION.md](docs/01-product/PRODUCT_VISION.md) |
| See what the MVP includes | [docs/01-product/PRODUCT_REQUIREMENTS.md](docs/01-product/PRODUCT_REQUIREMENTS.md) |
| See the plan | [docs/05-planning/ROADMAP.md](docs/05-planning/ROADMAP.md) |
| See milestone status | [docs/05-planning/MILESTONE_STATUS.md](docs/05-planning/MILESTONE_STATUS.md) |
| Read the plan summary (Word) | [docs/05-planning/PLAN_REVIEW_REPORT.docx](docs/05-planning/PLAN_REVIEW_REPORT.docx) |
| Read the requirements (Word) | [docs/02-requirements/SRS.docx](docs/02-requirements/SRS.docx) |
| Check unresolved decisions | [docs/05-planning/OPEN_QUESTIONS.md](docs/05-planning/OPEN_QUESTIONS.md) |
| Follow the rules agents must obey | [docs/06-agent/AGENT_RULES.md](docs/06-agent/AGENT_RULES.md) |

## Approach

Documentation-first, one milestone at a time, deterministic core (scheduling, reminders) with AI limited to interpretation and explanation. Nothing is marked complete until verified.

## Quick start (Windows, from the repo root)

Prerequisites: Docker Desktop running, Node 22+/npm, Python 3.13 via uv (`pip install --user uv`, run as `python -m uv`).

```bash
cp .env.example .env                       # once
docker compose up -d db                    # PostgreSQL on 127.0.0.1:5433
cd services/api
python -m uv sync                          # install API dependencies
python -m uv run alembic upgrade head      # create tables
PYTHONPATH=src python -m uv run python -m yadi.db.seed   # dev user (development only)
python -m uv run uvicorn --app-dir src --factory yadi.main:create_app --port 8000
# second terminal
cd apps/web && npm install && npm run dev  # http://localhost:3000
# third terminal: sends reminders
cd services/api && PYTHONPATH=src python -m uv run python -m yadi.worker
```

Quality gates, from the repo root: `node scripts/run.mjs check`, `node scripts/run.mjs test`, or `node scripts/run.mjs all`.

Use `127.0.0.1`, not `localhost`, for the database: on this Windows setup `localhost` tries IPv6 first and hangs for minutes.
