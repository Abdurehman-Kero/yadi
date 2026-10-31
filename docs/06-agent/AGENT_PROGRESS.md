# Agent Progress

_Last updated: 2026-10-31 (UTC)_

## Project identity
Yadi · M00, M01, M02, M04, M05 complete · M03 and M06 built but open (real-AI evaluations owed) · Real sign-in before hosting (D-015) · M07 onward not started.

## Current position
- M06 evidence: `docs/milestones/M06-conversational-management/COMPLETION_REPORT.md`.
- Last commit is the owner's `a7aa3cb` (through M05). **M06 is uncommitted. The owner makes commits. Do not commit.**
- AI provider is Gemini (D-012). `.env` holds keys: never read or print them. Use made-up data only (KI-012).
- Tartiiba is out of scope (D-010).
- Three processes: API, website, worker (root README).

## Blocked on the owner
1. Approval to run evaluations on the real model. The owner has not given it: "continue" was not treated as approval.
2. One manual browser-alert try.

## Last verified checks
`node scripts/run.mjs all`: 10/10 PASS (pytest 210, vitest 27, Playwright 23), fake model only. Dev database at migration 0005.

## Relevant files
- `services/api/src/yadi/modules/assistant/`: `conversation.py` (intent, prompt), `actions.py` (performs, replies), `service.py` (`call_model`, `handle_message`).
- `services/api/src/yadi/modules/scheduling/move.py`.
- `services/api/evals/`, `scripts/run_ai_eval.py` (`--intents`).
- `apps/web/src/features/tasks/AssistantCapture.tsx`.

## Known problems
`KNOWN_ISSUES.md`: KI-003, 005, 007, 009 to 017.

## Tooling note for agents
Very long multi-file Bash heredocs failed to parse here. Use the Write tool, or a patch script in the scratchpad.

## Resume instructions
1. Run `git status`; do not commit. `docker compose up -d db`, then `node scripts/run.mjs all`.
2. With approval, from `services/api` in Git Bash: `PYTHONPATH="src;." python -m uv run python scripts/run_ai_eval.py --yes`, then the same with `--intents`. Fix request errors, then tune prompts. Report accuracy, latency and cost; update M03 and M06 reports.
3. Then ask the owner which comes next: real sign-in and deployment preparation, or M07 preferences and memory. Write that milestone's docs before code.
