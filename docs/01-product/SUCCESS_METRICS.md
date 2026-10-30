# Success Metrics

| Metric | Definition | Data needed |
|---|---|---|
| Extraction accuracy | % of fields in eval set matching gold labels | Eval fixtures |
| Unnecessary clarification rate | Clarifications asked where gold has no ambiguity ÷ eval cases | Eval fixtures |
| Hard-constraint satisfaction | % of generated schedules with zero violations (must be 100%) | Property tests, schedule_runs |
| Reminder timeliness | % processed within 30 s of due time | reminder_attempts timestamps |
| Duplicate reminder rate | duplicates ÷ reminders (target 0) | idempotency key collisions |
| AI correction rate | % of AI-proposed fields edited by user before save | task_events |
| Priority acceptance | % AI-recommended priorities left unchanged | task_events |
| Time to create a task | median seconds from open input to saved | client timing (no content) |
| API latency / error rate | p95, 5xx % | logs/metrics |
| AI cost per interaction | cost_estimate mean | ai_usage |
| User satisfaction | optional short survey | opt-in only |

Collect only counts and timings, never message content. No productivity-improvement claims without evidence.
