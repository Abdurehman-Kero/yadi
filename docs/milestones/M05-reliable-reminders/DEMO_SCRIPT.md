# M05 Demo Script

## A. What we built
Reminders that do not depend on Yadi being open. A background worker sends them, they survive restarts, they never arrive twice, and every attempt is recorded. Forms now open in modal dialogs.

## B. Why it matters
A reminder that only works while a tab is open is not a reminder you can trust.

## C. How it works
When a task gets a time, Yadi stores a reminder in the database, in the same save as the task. The worker checks for due reminders every few seconds, claims each one so no other worker can take it, writes the notification, and records the result. If the worker dies, its claim expires and the reminder is retried. If the plan changes, the reminder moves with it.

## D. Before the demo
Three terminals in Git Bash, with Docker running. Use made-up tasks.

Terminal 1, API:
`cd ~/Desktop/yadi/services/api`, then `python -m uv run alembic upgrade head`, then `python -m uv run uvicorn --app-dir src --factory yadi.main:create_app --port 8000`

Terminal 2, website:
`cd ~/Desktop/yadi/apps/web`, then `npm run dev`

Terminal 3, worker:
`cd ~/Desktop/yadi/services/api`, then `PYTHONPATH=src python -m uv run python -m yadi.worker`

## E. Steps
1. Open http://localhost:3000/settings. Set your timezone and save.
2. Click New task on Tasks. Title "Call advisor". Tick the fixed-time box, and set it to start 10 minutes from now and end 30 minutes from now. Add it.
3. Open Notifications and wait a few seconds, refreshing if needed.
4. Click Snooze 10 min.
5. Stop the worker with Ctrl+C. Add another task the same way. Open Notifications.
6. Start the worker again and refresh after a few seconds.
7. Optional, real browser alerts: in Settings, click Turn on browser alerts and allow them. Add another task as in step 2, close the Yadi tab, and wait.
8. Press Escape in any open form, and check focus returns to the button that opened it.

## F. Expected results
- 3: "Call advisor" appears with "Starts at ...", marked New, and the navigation shows a count.
- 4: the notification is read, and it returns 10 minutes later as "Snoozed: Call advisor".
- 5: a warning says the service is not running; nothing new arrives.
- 6: the waiting reminder arrives once, and the warning clears.
- 7: a system notification should appear. **This step has not been tried on a real browser yet.** Your browser, Windows notification settings or Focus mode can hide it.

## G. How to verify
- `docker compose exec db psql -U yadi -d yadi -c "select state, attempts, remind_at from reminders order by created_at desc limit 5"`
- `docker compose exec db psql -U yadi -d yadi -c "select channel, outcome, at from reminder_attempts order by id desc limit 5"`
- `node scripts/run.mjs all` from the repo root: ten PASS lines.

## H. Known limitations
See COMPLETION_REPORT.md. The worker must be running, there is no real sign-in yet, and sound is never promised.

## I. Presentation script
"Close the app and Yadi still does its job. Reminders live in the database and a separate worker sends them. We killed that worker in testing: nothing was lost and nothing arrived twice. When plans change, reminders follow them, and if something goes wrong Yadi records it rather than hiding it."
