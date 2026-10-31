# M06 Plan

1. Allow an actor on task changes.
2. Intent schema, prompt, deterministic resolver and action layer, test-first with a fake model.
3. Move planner in the scheduling module.
4. `POST /assistant/message` and `POST /assistant/apply`.
5. One message box with conversation, options and confirmation.
6. Intent evaluation set. Gates, report.

## Decisions
- **One box.** The model first decides what the message is. New tasks then go through the existing extraction and review, which costs a second model call; measure this if the accuracy run happens.
- **Conversation is held in the browser** and sent with each message (6 turns at most). It is not stored, which means less personal data held and nothing to delete. It is lost on reload.
- **The proposal is re-checked on apply.** A confirmed action is treated like any request: ownership and rules are checked again, so tampering gains nothing.
- **Moved blocks are locked**, like a manual move, and one message moves the whole remaining task into one block.
- **Direct:** move, complete, start, priority, replan, since each is easy to reverse. **Confirm:** cancel, fixed-event move, blocking time, moving past a deadline.
- **Replies are written by code**, not the model, so they cannot claim something that did not happen.
