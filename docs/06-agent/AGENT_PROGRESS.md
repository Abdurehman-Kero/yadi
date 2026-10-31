# Agent Progress

_Last updated: 2026-10-31 (UTC)_

## Project identity
Yadi · Phase: MVP build · M00, M01, M02 done · M03 open (accuracy test owed, exception D-013) · **M04 built and verified, awaiting owner review** · Next: M05 reliable reminders.

## Current position
- M04 evidence: `docs/milestones/M04-priority-and-scheduling/COMPLETION_REPORT.md`.
- Last commit is the owner's `035c673` (through M01). **M02, M03 and M04 are uncommitted. The owner makes commits. Do not commit.**
- AI provider is Google Gemini (D-012). The key is in `.env`; never read or print it. Use made-up data only: free-tier content is used by Google (KI-012).
- Tartiiba is out of scope (D-010).

## Last verified checks
`node scripts/run.mjs all`: 10/10 PASS (pytest 143, vitest 20, Playwright 16). Dev database at migration 0004. One live Gemini call succeeded.

## Relevant files
- `services/api/src/yadi/modules/scheduling/`: `engine.py` (pure), `service.py`, `router.py`, `models.py`, `schemas.py`.
- `apps/web/src/features/today/`, `features/schedule/`, `components/NavLinks.tsx`, `app/globals.css` (design tokens).
- `services/api/evals/`, `scripts/run_ai_eval.py`: M03 evaluation, not yet run.

## Known problems
`KNOWN_ISSUES.md`: KI-003, 005, 007, 009, 010, 011, 012, 013, 014.

## Tooling note for agents
Very long multi-file Bash heredocs failed to parse here. Use the Write tool, or a small patch script in the scratchpad.

## Resume instructions
1. Run `git status`; do not commit. `docker compose up -d db`, then `node scripts/run.mjs all`.
2. Once the owner approves M04: mark it complete, then write the M05 docs (FR-NOT-001 to FR-NOT-005, FR-SET-001, NFR-PERF-002, NFR-REL-001) before code. Read `NOTIFICATION_ARCHITECTURE.md`, ADR-002 and ADR-005 first. ADR-005 requires real sign-in by M05: confirm the plan with the owner, because reminders to real users depend on it.
3. Reminder the owner that M03's accuracy test is still owed, and that real personal data needs Gemini paid billing.
