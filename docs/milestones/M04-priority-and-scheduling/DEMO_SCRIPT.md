# M04 Demo Script

## A. What we built
Yadi now plans your week. It works around fixed commitments and your working hours, puts the tightest deadlines first, explains each decision, and tells you what does not fit. The whole interface was also redesigned.

## B. Why it matters
A to-do list ignores how much time you have. Yadi's plan is checked by tested rules, so it never pretends impossible work will fit.

## C. How it works
Your tasks and settings go to a scheduling engine: plain code with no AI, which always gives the same answer for the same input. It finds your free time, places work, and writes a reason for each block. Your own changes are locked and kept when replanning.

## D. Before the demo
Docker running; restart the API and website because both changed. Run the database update once, in Git Bash: `cd ~/Desktop/yadi/services/api`, then `python -m uv run alembic upgrade head`. Set your timezone in Settings. Use made-up tasks.

## E. Steps
1. Go to Tasks, click New task. Add "Team meeting", tick the fixed-time box, and set tomorrow 10:00 to 11:00.
2. Add "Finish assignment": 120 minutes, due tomorrow at 16:00, Critical.
3. Add "Work on project": 120 minutes, High.
4. Add "Impossible task": 1440 minutes, due tomorrow at 12:00.
5. Add "Call advisor" with no estimate.
6. Go to Schedule and click Plan my week.
7. On "Work on project", click Move, set a time inside your working hours that is free, and save.
8. Click Replan.
9. Go to Today. Click Complete on the Next up task.

## F. Expected results
- 6: the meeting shows Fixed with no Move button. Other blocks flow around it and each gives a reason. "Not in the plan" lists the impossible task with options, and "Call advisor" asking for an estimate.
- 7: the block shows "Kept in place". A time outside working hours or on another block shows a clear message instead.
- 8: the moved block stays where you put it.
- 9: the task leaves the plan, and Next up moves on. The page may suggest replanning.

## G. How to verify
- `node scripts/run.mjs all` from the repo root: ten PASS lines.
- `docker compose exec db psql -U yadi -d yadi -c "select start_at, end_at, is_fixed, locked from schedule_blocks order by start_at"`

## H. Known limitations
See COMPLETION_REPORT.md. The main ones: weekends count as working days, Tell Yadi cannot create fixed events yet, and reminders do not exist until M05.

## I. Presentation script
"Tell Yadi what you need to do and it builds a realistic plan around your commitments. The plan comes from tested rules rather than AI guesses, so every block can be explained, and if something does not fit, Yadi says so and offers options. Anything you move yourself stays where you put it."
