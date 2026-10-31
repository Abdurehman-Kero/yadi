# M02 Demo Script

## A. What we built
A working task manager, with no AI yet. You can add, edit, start, complete, reopen and cancel tasks, see each task's history, and set your timezone and working hours.

## B. Why it matters
Later features (AI capture, scheduling, reminders) all act on these tasks. The rules for what may happen to a task now live in one tested place.

## C. How it works
The browser sends each action to FastAPI through Next.js. FastAPI checks who you are and that the action is allowed, saves the change and its history entry together in PostgreSQL, and returns the result. Dates are stored in UTC and shown in the timezone from your settings.

## D. Before the demo
Docker Desktop running; the setup in the root README done once. `.env` must contain `DEV_IDENTITY_ENABLED=true` (copy it from `.env.example` if missing). There is no sign-in yet: everyone is the built-in dev user.

## E. Steps
1. `docker compose up -d db`
2. `cd services/api`, then `python -m uv run alembic upgrade head`
3. `python -m uv run uvicorn --app-dir src --factory yadi.main:create_app --port 8000`
4. New terminal: `cd apps/web`, then `npm install` and `npm run dev`. Open http://localhost:3000/tasks
5. Add a task with only a title.
6. Refresh the page.
7. Click Edit, add a due date and an estimate, and save.
8. Click Start, then Complete. Open the Completed filter and click History.
9. Click Reopen, then go back to the Active filter.
10. Click Cancel task, then Keep task. Click Cancel task again, then Yes, cancel task. Open the Cancelled filter.
11. Add a task with a due date. Go to Settings, change the timezone, save, and return to Tasks.
12. In the first terminal, stop the API with Ctrl+C. Try to add a task. Restart the API and submit again.
13. Stop `npm run dev`. From the repo root: `node scripts/run.mjs all`

## F. Expected results
- 5: the task appears, marked Inbox. 6: it is still there.
- 7: it becomes Planned, showing the due date and minutes. A past due date also shows Overdue.
- 8: In progress, then it moves to Completed. History lists each step with its time.
- 9: back in Active, Planned.
- 10: Keep task changes nothing; after confirming, it appears only under Cancelled, with no Reopen button.
- 11: the time shown shifts to the new timezone; the moment itself is unchanged.
- 12: a "Could not reach Yadi" message appears and your typing stays in the form. After the restart, the task saves.
- 13: ten PASS lines.

## G. How to verify
- `docker compose exec db psql -U yadi -d yadi -c "select title, status from tasks"`
- `docker compose exec db psql -U yadi -d yadi -c "select type, actor, at from task_events order by id"`
- The API terminal shows one JSON log line per request, without task text.

## H. Known limitations
- No real sign-in, so this must not be hosted yet. Real sign-in comes by M05.
- Reminders and scheduling are not built; those two settings are saved but not used yet. Cancelled and completed tasks have no reminders to cancel until M05.
- Two people editing the same task at once: the last save wins.
- Performance figure (about 19 ms) is from this dev machine with a test client, not a load test.

## I. Presentation script
"This is Yadi's core: a dependable task manager. Every change is checked against clear rules, saved with its history, and one user can never reach another's tasks. Times follow your own timezone, including daylight-saving changes. If the server fails, you see a clear message and keep what you typed. The AI and scheduling come next, and they will use these same tested rules."
