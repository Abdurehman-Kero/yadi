# M06 Completion Report

**Status: BUILT, NOT COMPLETE.** Everything behind the AI is verified, but no message of this kind has been sent to the real model, so M06-R12 and real-world understanding are unproven. (2026-10-31 UTC). Not committed: the owner makes commits.

## Delivered
- `POST /assistant/message` and `POST /assistant/apply`; intent schema and prompt; resolver; action layer; move planner.
- One Tell Yadi box on Today: conversation, task options, confirmation, and the existing review for new tasks.
- 24-case intent evaluation, scorer, and `--intents` on the evaluation script.

## Verified (fake model only)
- `node scripts/run.mjs all`: 10/10 PASS. pytest 210, vitest 27, Playwright 23.
- Each action changes stored data; history records actor `ai`; reminders follow moves.
- Several matches ask; none says so; invented task numbers are ignored.
- Cancel, fixed-event moves, blocking time and moves past a deadline change nothing until confirmed, and apply checks everything again.
- Moves that do not fit, or use bad dates, change nothing and explain why.
- Another user's task returns 404 on every action, and never reaches the prompt.
- The prompt holds only active tasks, without notes, at most 40; a title cannot add lines to it.
- Browser test: only the model's reading was mocked; confirmation, options and data changes ran through the real API.

## Not verified / limitations
- **Real-model understanding.** Both evaluations are unrun. The model could misread a message and act on the wrong task: complete, start, priority and flexible moves apply directly when one task matches. They are reversible, and the reply says what changed, but this is why the evaluation matters before relying on it.
- A new-task message makes two model calls. Latency and cost are unmeasured. The free-tier quota may run out sooner.
- `create_tasks` is decided per message, so "finished the report and add a dentist visit" handles only one part. Several actions in one message are out of scope.
- Conversation is lost on reload by design.
- Moving a split task puts all its remaining time in one block, which must fit in a row.
- Replies are English only.
- The demo script has not been run by hand.

## Deviations
History is not sent from the server: it is held in the browser and limited on the server, rather than stored (see PLAN.md).

## Remaining
TASKS.md. M01 to M06 cover the MVP's features; the MVP also still needs M03 and M06's evaluations, and real sign-in before hosting.
