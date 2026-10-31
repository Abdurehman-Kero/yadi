# Agent Progress

_Last updated: 2026-10-31 (UTC)_

## Project identity
Yadi · Phase: MVP build · M00, M01, M02, M04 complete · M03 open (accuracy test owed, D-013) · **M05 built and verified except real browser alerts, awaiting owner review** · Next: M06 conversational management. Real sign-in is its own step before hosting (D-015).

## Current position
- M05 evidence: `docs/milestones/M05-reliable-reminders/COMPLETION_REPORT.md`.
- Last commit is the owner's `ace8bb6` (through M04). **M05 is uncommitted. The owner makes commits. Do not commit.**
- AI provider is Gemini (D-012). `.env` holds the Gemini key and browser-alert keys: never read or print them. Use made-up data only (KI-012).
- Tartiiba is out of scope (D-010).
- The app now needs three processes: API, website, worker (root README).

## Last verified checks
`node scripts/run.mjs all`: 10/10 PASS (pytest 178, vitest 23, Playwright 22). Dev database at migration 0005.

## Relevant files
- `services/api/src/yadi/worker.py`; `modules/reminders/` (`sync.py`, `delivery.py`, `router.py`, `models.py`).
- `apps/web/src/components/Modal.tsx`, `features/notifications/`, `features/settings/NotificationSettings.tsx`, `public/sw.js`.
- `services/api/evals/`, `scripts/run_ai_eval.py`: M03 evaluation, not yet run.

## Known problems
`KNOWN_ISSUES.md`: KI-003, 005, 007, 009 to 016.

## Tooling note for agents
Very long multi-file Bash heredocs failed to parse here. Use the Write tool, or a patch script in the scratchpad.

## Resume instructions
1. Run `git status`; do not commit. `docker compose up -d db`, then `node scripts/run.mjs all`.
2. Once the owner approves M05: mark it complete, then write the M06 docs (FR-CONV-001 to FR-CONV-003) before code. Read `AI_DESIGN.md` first. M06 needs live AI quality, so run M03's evaluation with the owner's approval before relying on it.
3. Remind the owner: the accuracy test is owed, real personal data needs Gemini paid billing, and browser alerts need one manual try. The MVP is not finished, despite the commit message "MVP done": M06 is a Must requirement.
