# M06 Requirements

| ID | Requirement | Acceptance criterion |
|---|---|---|
| M06-R1 | Move, complete, start, cancel, re-prioritise, block time and replan by message. | Stored data changes, tested through the API. |
| M06-R2 | Replies state what actually happened, written by application code after the change. | Test: a failed change never reports success. |
| M06-R3 | Several matches: ask which, with options. No match: say so. Never guess. | Tests. |
| M06-R4 | Cancelling, moving a fixed event, blocking time, and moving past a deadline need confirmation; nothing changes until confirmed. | Tests. |
| M06-R5 | A move is checked against working hours, other blocks and the buffer; if it does not fit, nothing changes and Yadi says why. | Tests. |
| M06-R6 | The model cannot touch data: unknown task numbers, bad dates and other users' ids are rejected by application code. | Tests with hostile model output and requests. |
| M06-R7 | Task and message text is treated as data; an instruction inside it cannot widen what is possible. | Allowed actions are a closed list; test. |
| M06-R8 | Only active tasks, with minimal fields, and at most 6 recent turns reach the model. | Test inspects the prompt. |
| M06-R9 | Questions are answered from stored data, without inventing anything. | Tests. |
| M06-R10 | Assistant changes are recorded in history with actor `ai`. | Test. |
| M06-R11 | If the AI is unavailable, the user is told and can still act by hand. | Browser test. |
| M06-R12 | Evaluation set for references and actions, with a scorer. | Scorer tested. A live run needs the owner's approval. |
