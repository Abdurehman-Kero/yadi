# M06 Demo Script

## A. What we built
You can change your plan by asking. Yadi moves, completes, starts, cancels or re-prioritises tasks, blocks out time, replans, and answers questions on your plan.

## B. Why it matters
Changing a plan should take a sentence, not a trip through forms, and it must change the real data.

## C. How it works
Gemini only reads your message and picks from a fixed list of actions. Yadi's own code then finds the task, checks the rules, makes the change through the same services as the buttons, and writes the reply from what actually happened.

## D. Before the demo
Run all three processes from the root README, after `python -m uv run alembic upgrade head`. Your Gemini key must be in `.env`. Use made-up tasks: on the free tier Google may use this text. Each message uses quota. Add these tasks with estimates, and click Plan my week: "Weekly report" (60 min), "Project report" (60 min), "Read chapter 3" (30 min).

## E. Steps (on Today, in Tell Yadi)
1. "What should I do next?"
2. "Move chapter 3 to tomorrow afternoon"
3. "The report is done"
4. Choose one of the two options.
5. "Forget chapter 3", then No, keep it. Send it again, then Yes, do it.
6. "I am unavailable tomorrow from 1 PM to 3 PM", then Yes, do it.
7. "I have 45 minutes free. What can I do?"
8. "Send an email to my boss"
9. "I have a dentist visit on Monday at 9"

## F. Expected results
The real model passed a matching evaluation, but these exact steps have not been run by hand.
- 1, 7: answers from your own plan. 2: "Moved ..."; the plan updates.
- 3: asks which report. 4: that one is completed; the other is untouched.
- 5: No changes nothing; Yes cancels. 6: an Unavailable block appears and work moves around it.
- 8: says it cannot do that. 9: the review form opens.

## G. How to verify
- Open a task's History on Tasks: changes appear there.
- `docker compose exec db psql -U yadi -d yadi -c "select type, actor, at from task_events where actor='ai' order by id desc limit 5"`
- `docker compose exec db psql -U yadi -d yadi -c "select operation, ok, latency_ms, cost_estimate_usd from ai_usage order by id desc limit 5"`
- `node scripts/run.mjs all`: ten PASS lines.
- Accuracy, using your quota, from `services/api` in Git Bash: `PYTHONPATH="src;." python -m uv run python scripts/run_ai_eval.py --yes --intents`

## H. Known limitations
See COMPLETION_REPORT.md: one action per message, conversation lost on reload, free-tier rate limits, and accuracy measured only on made-up messages.

## I. Presentation script
"You just tell Yadi what changed. The AI only works out what you mean. Tested rules decide what is allowed, it asks when unsure, and it checks with you before anything hard to undo. The reply tells you what actually happened, because it is written after the change is made."
