# M06 Completion Report

**Status: BUILT AND EVALUATED, awaiting owner review.** (2026-10-31)

## Real-model evaluation (2026-10-31, `gemini-3.5-flash-lite`, free tier)
- Tasks: 20/20. Changes and questions: 24/24. Median response 1.3 to 1.6 s. Slowest 23 s, probably a rate-limit retry. Estimated cost $0.008 per 20 calls.
- First run, before tuning: of 37 scored messages, 28 passed and 9 failed, and 11 more hit the free tier's per-minute limit. Prompts were then tuned for AM/PM doubts, misheard words, finished work that is not listed, and full dates when blocking time. Two expectations were corrected: the scorer now accepts a space in date-times, as the app does, and "30 hours" is an accurate reading that the app turns into a question.
- **Limit of this result:** the prompts were tuned on these same messages, and the wording is the author's, so 100% does not predict 100% on real use. Expect real messages to do worse. Reliability is also untested: each message ran once.
- Free-tier per-minute limits are real: rapid use gets the manual fallback.

## Delivered
- `POST /assistant/message` and `POST /assistant/apply`; intent schema and prompt; resolver; action layer; move planner.
- One Tell Yadi box on Today: conversation, task options, confirmation, and the existing review for new tasks.
- 24-case intent evaluation, scorer, and `--intents` on the evaluation script.

## Verified with a fake model
- `node scripts/run.mjs all`: 10/10 PASS. pytest 210, vitest 27, Playwright 26.
- Each action changes stored data; history records actor `ai`; reminders follow moves.
- Several matches ask; none says so; invented task numbers are ignored.
- Cancel, fixed-event moves, blocking time and moves past a deadline change nothing until confirmed, and apply checks everything again.
- Moves that do not fit, or use bad dates, change nothing and explain why.
- Another user's task returns 404 on every action, and never reaches the prompt.
- The prompt holds only active tasks, without notes, at most 40; a title cannot add lines to it.
- Browser test: only the model's reading was mocked; confirmation, options and data changes ran through the real API.

## Not verified / limitations
- **Real-world understanding.** The evaluation used made-up messages. The model could still misread one and act on the wrong task: complete, start, priority and flexible moves apply directly when one task matches. They are reversible, and the reply says what changed.
- A new-task message makes two model calls, so it takes about twice as long and uses quota twice as fast.
- `create_tasks` is decided per message, so "finished the report and add a dentist visit" handles only one part. Several actions in one message are out of scope.
- Conversation is lost on reload by design.
- Moving a split task puts all its remaining time in one block, which must fit in a row.
- Replies are English only.
- The demo script has not been run by hand.

## Deviations
History is not sent from the server: it is held in the browser and limited on the server, rather than stored (see PLAN.md).

## Remaining
Owner review. The MVP's features are built; real sign-in is needed before hosting, and Gemini billing before real personal data.
