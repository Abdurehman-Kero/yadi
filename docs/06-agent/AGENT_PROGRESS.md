# Agent Progress

_Last updated: 2026-10-31_

## Project identity
Yadi · M00 to M05 complete · **M06 and a UI/UX pass built, awaiting owner review** · Next, by the owner's agreed order: real sign-in and deployment preparation, then M07.

## Current position
- Evidence: `docs/milestones/M06-conversational-management/COMPLETION_REPORT.md`.
- Last commit is the owner's. **Recent work is uncommitted; check `git status`. The owner makes commits. Do not commit.**
- AI provider is Gemini (D-012). `.env` holds keys: never read or print them. Use made-up data only (KI-012).
- Tartiiba is out of scope (D-010).
- Three processes: API, website, worker (root README).

## Blocked on the owner
1. For sign-in: a Google OAuth client ID and secret, in `.env`.
2. Review of the new UI, and one manual browser-alert try (KI-015).

## Last verified checks
`node scripts/run.mjs all`: 10/10 PASS (pytest 210, vitest 27, Playwright 26). Real-model evaluations: 20/20 and 24/24 after tuning, on the same messages. Dev database at migration 0005.

## Relevant files
- `apps/web/src/features/schedule/` (`DayTimeline`, `BlockDetails`), `features/tasks/` (`TaskRow`, `TaskForm`, `AssistantCapture`), `features/today/`, `app/globals.css`.
- `services/api/src/yadi/modules/assistant/`, `modules/scheduling/move.py`, `core/deps.py` (development identity, replaced by sign-in).
- `services/api/scripts/run_ai_eval.py` (`--intents`, `--only=`); paced for the free tier.

## Known problems
`KNOWN_ISSUES.md`: KI-003, 005, 007, 009, 010, 012 to 018.

## Tooling note for agents
Very long multi-file Bash heredocs failed to parse here. Use the Write tool, or a patch script in the scratchpad.

## Resume instructions
1. Run `git status`; do not commit. `docker compose up -d db`, then `node scripts/run.mjs all`.
2. Apply the owner's UI feedback first, if any.
3. Write docs for the sign-in step before code. Read ADR-005 and SECURITY_AND_PRIVACY. Check current Google OIDC docs and library (Authlib or similar). Remove `X-Dev-User` outside development; add sessions, CSRF protection and logout, and prove isolation still holds.
4. Then deployment preparation (hosting choice is the owner's: OPEN_QUESTIONS Q5), then M07.
