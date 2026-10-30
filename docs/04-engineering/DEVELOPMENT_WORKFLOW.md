# Development Workflow

- Git from the start; `main` always passes the quality gates. Short-lived branches `mXX/<topic>`.
- Commits: focused, imperative subject (`Add task cancellation service`), body explains why. No commits/pushes without owner approval where required; never force-push or reset user work.
- Review the diff before broad changes; state intended change, impact, and verification plan first.
- Migrations: versioned SQL via the ORM tool; every migration tested up (and down where feasible); destructive changes need a two-step rollout.
- Releases: tag verified milestones (`m02-verified`).
- Session start/end: follow AGENT_RULES.md (read progress → rules → milestone docs → git status; update progress/session log at end).
- Definition of done: requirements met, acceptance verified, tests pass, security considered, UI states done, docs updated, demo script verified, limitations recorded, progress file updated.
