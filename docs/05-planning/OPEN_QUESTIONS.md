# Open Questions

| # | Question | Status | Outcome |
|---|---|---|---|
| Q1 | Spec truncated | Resolved | Full spec read from writing-block.md |
| Q2 | Frontend/backend/database | Resolved (owner) | Next.js + FastAPI + PostgreSQL (ADR-001) |
| Q3 | Authentication | Resolved | Dev identity until M05, then Google sign-in (ADR-005) |
| Q4 | AI provider | Resolved (default) | Claude behind adapter; model chosen in M03 |
| Q5 | Hosting target | **Deferred** | Decide before M11; container-based meanwhile |
| Q6 | Single/multi-user | Resolved | Multi-user model, single user in practice |
| Q7 | Notification channels | Resolved | In-app + Web Push; email later |
| Q8 | Keep docx generator in repo? | Open (low) | Recommend yes, `scripts/docs/`, in M01 |
| Q9 | Python version | Resolved | Pin 3.13 via uv; core libs also list 3.14 support (verified 2026-10-27) |
