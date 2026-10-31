# M03 Test Plan

| Area | Test | Layer |
|---|---|---|
| Adapter | Request shape, parsing, refusal, truncation, invalid JSON, API errors (fake HTTP transport) | pytest |
| Conversion | Local time to UTC in the user's zone; invalid and past times | pytest |
| Endpoint | Drafts returned, nothing saved, validation, 503, 429, auth required | pytest + Postgres |
| Usage | Row on success and failure, no message text | pytest |
| Boundary | Provider SDK imported only by the adapter | pytest |
| UI | Review, edit, save, discard, questions, fallback keeps text | Vitest, Playwright |
| Evaluation | Scorer logic on fixed answers; live run is manual and costs money | pytest, script |
