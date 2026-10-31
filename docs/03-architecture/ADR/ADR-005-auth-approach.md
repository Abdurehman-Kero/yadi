# ADR-005: Authentication approach

Status: **Accepted 2026-10-27** (owner delegated the choice to the agent's recommendation).

## Options
1. Dev identity only (fast; unsafe for hosting).
2. Email + password (argon2id, server sessions) — we would own password storage, reset and breach risk.
3. OAuth/OIDC with Google — no passwords stored; the same Google relationship is needed later for Calendar (M08).

## Decision
- Until then: local development identity (a fixed seeded user, only when `ENVIRONMENT=development`), with `user_id` on all data and all queries.
- Before any real user or deployment, as its own step (changed from "by M05", D-015): **Google sign-in (OIDC)** handled by FastAPI, server-side sessions in an HttpOnly, SameSite cookie, CSRF protection for state-changing requests.
- Email + password is not planned; revisit only if Google-only sign-in proves unacceptable.

## Consequences
Dev identity must be impossible to enable in production (startup check + test). Users need a Google account. Library choice (e.g. Authlib) verified when that step is planned.
