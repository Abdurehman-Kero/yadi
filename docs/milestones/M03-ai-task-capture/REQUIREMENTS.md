# M03 Requirements

| ID | Requirement | Acceptance criterion |
|---|---|---|
| M03-R1 | Extract one or more task drafts from text up to 2,000 characters. | A message with several activities returns several drafts. Empty or overlong text returns 400. |
| M03-R2 | Extraction saves nothing. Saving goes through the normal task API after review. | Test: task count unchanged after extract. |
| M03-R3 | Model output is validated before use; malformed, refused or truncated output never reaches the user as a draft. | Tests for each case return `AI_UNAVAILABLE`. |
| M03-R4 | Missing details stay empty and are never invented. Ambiguity becomes a question on the draft. | Evaluation cases; UI shows questions. |
| M03-R5 | Local times from the model are converted in the user's saved timezone by application code. A time already past gets a question. | Tests including a non-UTC zone. |
| M03-R6 | Provider failure, timeout or missing key returns 503 `AI_UNAVAILABLE`; the UI opens the manual form with the text kept. | API test and browser test. |
| M03-R7 | Every provider call records model, tokens, latency, estimated cost and outcome, and never message text. | Test inspects the row. |
| M03-R8 | Per-user daily call limit returns 429 `RATE_LIMITED` without calling the provider. | Test. |
| M03-R9 | The API key stays on the server and is never logged. | Config repr test; bundle holds no key because the client never receives it. |
| M03-R10 | Provider SDK imports exist only in the adapter module. | Test scans the source tree. |
| M03-R11 | Evaluation set covers clear, ambiguous, multi-task, conflicting, misheard, over-capacity and unsupported requests, with a scorer. | Scorer unit-tested. A live run needs the owner's key. |
