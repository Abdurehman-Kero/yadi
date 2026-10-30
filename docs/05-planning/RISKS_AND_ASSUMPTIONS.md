# Risks and Assumptions

## Risks
| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-01 | LLM misreads dates/intent and silently creates wrong tasks | High | High | Schema validation, show extraction for review, ask on ambiguity, eval set (M03) |
| R-02 | Timezone/DST bugs produce wrong schedules or reminders | Medium | High | Store UTC + user IANA zone, dedicated tests incl. DST |
| R-03 | Reminders lost on restart or sent twice | Medium | High | Durable jobs, idempotency keys, recovery tests (M05) |
| R-04 | Browser blocks notifications or sound | High | Medium | Don't promise sound; in-app fallback; document limits |
| R-05 | Scope creep (voice, memory, calendar) delays core | High | Medium | Strict milestone gating, MVP non-goals |
| R-06 | AI cost/latency grows | Medium | Medium | Small context, cheaper models, usage tracking |
| R-07 | Personal data exposure | Low | High | Per-user isolation, safe logging, synthetic dev data |
| R-08 | Two toolchains (Python + Node) raise setup and CI complexity; client/server types can drift | Medium | Medium | OpenAPI-generated TS types with CI drift check; single wrapper script; documented setup |
| R-09 | Python 3.14 (only version installed) may lack library wheels | Medium | Low | Pin 3.12/3.13 via uv; verify in M01 |

## Assumptions
- A-01 Single developer plus AI agent; modest MVP load.
- A-02 Web app first; mobile/voice/wearable later.
- A-03 Docker is available for local PostgreSQL.
- A-04 Items marked *Proposed* in the DECISION_LOG are not yet binding.
