# AI Design

## Principle
AI interprets; services decide and execute. The model never touches the database, never judges schedule validity, and its output is never trusted until validated.

## Operations (each has a Pydantic model)
| Operation | Output | Milestone |
|---|---|---|
| `extractTasks(message, context)` | `TaskDraft[]` each with per-field `confidence` and `ambiguities[]` | M03 |
| `parseIntent(message, contextTasks)` | `Intent` (reschedule, complete, reprioritize, set_unavailable, query, …) with a task reference description | M06 |
| `recommendPriority(task)` | priority + reason (user may override; deterministic rules are the default) | M04 |
| `explain(planDiff)` | plain-language text from engine-produced facts | M04 |
| `suggestMemory(...)` | proposed memory, saved only after user confirm | M07 |

## Boundary
`services/api/src/yadi/modules/assistant/ai/` is the only place that imports a provider SDK. Interface: `LlmClient.generate_structured(schema, system, prompt)`, which returns a result or raises `AiError`. Provider/model chosen by config.

## Validation & fallback
1. Parse JSON → validate with Pydantic → semantic checks (dates valid, in user zone, duration > 0).
2. Invalid output: return `AI_UNAVAILABLE` and show the manual task form with the user's text preserved. Structured outputs replace the planned repair retry.
3. Never fabricate: missing material fields go in `ambiguities`; the UI asks or shows an editable assumption.
4. Relative dates: the model receives `now` and the user timezone, and returns local wall-clock time plus the original phrase. Application code validates and converts it to UTC, and the user reviews every draft with the phrase shown (M03 decision). Vague times such as "tomorrow morning" stay empty with a question.

## Safety
Prompt-injection stance: user text and task content are data. Model has no tools that write directly; it proposes intents only. Send minimal context (only candidate tasks, not full history). No secrets in prompts. Log operation, model, tokens, latency, cost — not message content.

## Limits
Timeout 25 s per attempt, 1 retry, per-user limit of 200 calls a day (`AI_DAILY_CALL_LIMIT`). Values are provisional until measured.

## Evaluation
`services/api/evals/` holds labeled sets for extraction and for intents (clear, ambiguous dates, multi-task, conflicting, transcription errors, multi-match references, over-capacity, unsupported actions). Metrics: field accuracy, unnecessary-clarification rate, invalid-action rate. CI tests the scorer only; live-model runs are manual and paid (`scripts/run_ai_eval.py`).
