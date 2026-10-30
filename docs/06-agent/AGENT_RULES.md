# Agent Rules (persistent)

These rules apply to any coding agent working on Yadi. Source: the Master Product Vision, section 1.

1. Do not implement the whole application at once. Work one milestone at a time.
2. Document before building. Each milestone folder (`docs/milestones/Mxx-*`) needs README, REQUIREMENTS, PLAN, TASKS, TEST_PLAN, DEMO_SCRIPT, COMPLETION_REPORT before code starts.
3. Research important technical decisions; do not guess. Record them in `DECISION_LOG.md` (and an ADR in `docs/03-architecture/ADR/` for architectural ones).
4. Never claim a feature is complete without verifying it (run the tests, run the app). Report failures and technical debt honestly in `KNOWN_ISSUES.md`.
5. Do not advance to the next milestone until acceptance criteria are met, unless a documented exception is approved by the product owner.
6. Keep the stack minimal. No new dependency or abstraction without a stated reason (need, maintenance, security, size, license).
7. AI interprets; deterministic services decide and execute. The LLM never gets raw DB access, never validates schedules, and its output is schema-validated before it touches state.
8. Keep secrets server-side; use synthetic data only; never commit secrets.
9. Explain work in simple English for the product owner.
10. Ask the product owner only when a decision is genuinely theirs; otherwise recommend a reversible default and document it.

## Session protocol

- **Start:** read `AGENT_PROGRESS.md`, then `MILESTONE_STATUS.md`, then `KNOWN_ISSUES.md`.
- **End:** update `AGENT_PROGRESS.md` (verified state and exact resume point) and append to `SESSION_LOG.md`.
- Mark each item in progress docs as **verified** (evidence given) or **unverified**.
