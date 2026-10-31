# M03 Demo Script

## A. What we built
A "Tell Yadi" box. You write what you need to do in normal language, Yadi shows the tasks it understood with any questions, and you correct and save each one.

## B. Why it matters
Filling in a form for every task is the tedious part of planning. Yadi removes that without letting the AI change your data on its own.

## C. How it works
Your message goes to FastAPI, which sends it to Google Gemini with today's date and your timezone. Gemini must answer in a fixed format. Yadi checks the answer, converts times itself, and returns drafts. Nothing is stored until you click Save, which uses the same checked task API as the manual form. Yadi also records the tokens used and the estimated cost, never your text.

## D. Before the demo
- Everything from the M02 demo. Restart the API and website, because both changed.
- For live AI: a key from https://aistudio.google.com/apikey in `.env` as `GEMINI_API_KEY=...`. Never commit `.env`. On the free tier Google may use your text to improve its products, so demo with made-up tasks only.
- Run the database update once. In Git Bash: `cd ~/Desktop/yadi/services/api`, then `python -m uv run alembic upgrade head`.

## E. Steps, without a key (free)
1. Open http://localhost:3000/tasks.
2. Type "Call my advisor tomorrow" in Tell Yadi and click Understand.

## F. Expected, without a key
A message says the AI is not available. A form opens with your words as the title. Save task adds it.

## E2. Steps, with a key
1. Set your timezone in Settings.
2. Type: "I have a university assignment due Friday at 5 PM, a meeting tomorrow at 10 AM, and I need to work on my project for two hours. I also want to exercise in the evening."
3. Click Understand. Change one title and click Save task. Click Discard on another.
4. Type "What is the capital of Ethiopia?" and click Understand.

## F2. Expected, with a key
Separate drafts appear, with the phrase you used beside the time Yadi read. "In the evening" should get a question rather than an invented time. Only the saved draft appears in the list. The question gets a short explanation and no draft. These are expectations: **no live run has happened yet**.

## G. How to verify
- `docker compose exec db psql -U yadi -d yadi -c "select model, input_tokens, output_tokens, cost_estimate_usd, latency_ms, ok, error_kind from ai_usage order by id desc limit 5"`
- `node scripts/run.mjs all` from the repo root: ten PASS lines.
- Accuracy, which uses your quota, from `services/api` in Git Bash: `PYTHONPATH="src;." python -m uv run python scripts/run_ai_eval.py --yes`

## H. Known limitations
- Live extraction quality, speed and real cost are unmeasured.
- "Meeting at 10" is a task due at 10, not a fixed event, until M04.
- A saved task's reminder and schedule do not exist until M04 and M05.
- Message text goes to Google. Real users require paid billing, because free-tier content is used to improve Google's products.

## I. Presentation script
"You tell Yadi what's on your plate in your own words. It shows what it understood, asks when something is unclear, and saves nothing until you agree. If the AI is down, you simply carry on by hand and lose nothing. We also track what every AI call costs, without storing what you wrote."
