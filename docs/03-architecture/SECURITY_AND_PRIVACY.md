# Security and Privacy

## Assets
Schedules, tasks, conversation text, preferences, (later) calendar tokens, voice audio/transcripts.

## Threat model (STRIDE-lite)
| Threat | Mitigation |
|---|---|
| Cross-user data access | `user_id` on every table; repository functions require `userId`; integration tests assert isolation |
| Prompt injection via task text/calendar events | LLM proposes intents only; services validate and authorize; no direct tools with side effects |
| Secret leakage (LLM key) | Server-only env; validated config; never in client bundle; `.env` gitignored; secret scanning in CI |
| XSS/CSRF | React escaping, CSP, SameSite cookies, CSRF token for state-changing routes |
| Injection | Parameterized queries only; Pydantic validation at boundaries |
| Brute force/abuse | Rate limits (global, per user, stricter on AI routes) |
| Sensitive data in logs | Log ids and metadata, not message bodies; redact emails/tokens |
| Dependency compromise | Minimal deps, lockfile, `pip-audit` and `npm audit` in CI |
| Replay/duplicate actions | Idempotency keys |

## Authentication
Dev identity until real auth (OQ-Q3). Real auth: decision deferred to an ADR; session cookies server-side, passwords (if used) hashed with argon2id, or OAuth/OIDC.

## Privacy controls
- Data minimization; synthetic data for dev and demos.
- Memory (M07): explicit, inspectable, editable, deletable; sensitive categories not saved by default.
- Voice (M09): raw audio not retained by default; transcripts retention documented before launch.
- External integrations: explicit consent, least-privilege scopes, revocable.
- Third-party LLM: users are told that message text is sent to the provider; provider data-retention terms to be reviewed in the M03 ADR.

## Retention & deletion
Task data kept until user deletes. Deleting an account removes all rows; backups expire within 35 days (to be confirmed). AI usage rows hold no content. Application logs retained 30 days.

## Audit
`task_events` records who (user/ai/system) changed what.
