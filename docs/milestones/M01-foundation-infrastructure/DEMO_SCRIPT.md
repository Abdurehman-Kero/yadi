# M01 Demo Script

## A. What we built
The healthy skeleton of Yadi: a web page, an API and a database that talk to each other, plus automatic quality checks.

## B. Why it matters
Every later feature sits on this. Clear errors, versioned database changes and automatic checks prevent slow, hard-to-find problems later.

## C. How it works
Browser → Next.js page → `/api/*` is forwarded to FastAPI → FastAPI asks PostgreSQL a trivial question → the page shows the result. Every error has one standard shape and each request writes one log line with a request id (never the request body).

## D. Before the demo
Docker Desktop running; Node and uv installed; `.env` copied from `.env.example` (see README Quick start).

## E. Steps
1. `docker compose up -d db`
2. `cd services/api && python -m uv sync && python -m uv run alembic upgrade head`
3. `PYTHONPATH=src python -m uv run python -m yadi.db.seed`
4. `python -m uv run uvicorn --app-dir src --factory yadi.main:create_app --port 8000`
5. New terminal: `cd apps/web && npm install && npm run dev`; open http://localhost:3000
6. In another terminal: `curl http://127.0.0.1:3000/api/v1/health/ready`
7. `docker compose stop db`; run the curl again; refresh the page.
8. `docker compose start db`; refresh again.
9. From the repo root: `node scripts/run.mjs all`

## F. Expected results
3: "seeded dev user". 5: page shows "API: ok · Database: ok". 6: `{"status":"ok","database":"ok"}`. 7: HTTP 503 with `{"error":{"code":"SERVICE_UNAVAILABLE",...,"requestId":...}}` and the page shows a "Problem: Database is not available." message. 8: back to ok. 9: nine PASS lines.

## G. How to verify
Test output (pytest 15, vitest 4); the API terminal shows one JSON log line per request; `docker compose exec db psql -U yadi -d yadi -c "\dt"` lists `users`, `user_preferences`, `alembic_version`.

## H. Known limitations
No features, no login, no deployment, no end-to-end browser tests (start in M02). The page's visual appearance was checked via HTML/proxy responses and component tests, not a screenshot.

## I. Presentation script
"This is the foundation of Yadi. The screen, the server and the database are connected, failures are reported clearly, and every change must pass nine automatic quality checks. Next we build real task management on top of it."
