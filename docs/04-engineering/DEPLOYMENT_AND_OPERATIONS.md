# Deployment and Operations (plan)

Hosting target undecided (OQ-Q5). Design is container-based so it stays portable: `web` (Next.js server), `api` (FastAPI), `worker` (same image as api, different command), `db` (managed Postgres preferred).

- **Config:** env vars, validated at start. Staging mirrors production.
- **Migrations:** run as a release step before new code; rollback = redeploy previous image + documented down migration or forward-fix.
- **Health:** `/health` (liveness), `/health/ready` (DB reachable). Worker exposes heartbeat row/metric.
- **Logging:** structured JSON with request id; no message bodies.
- **Monitoring:** error reporting, queue depth/oldest-due age, AI cost, p95 latency; alerts on worker stall.
- **Backup/restore:** daily DB backups, restore tested before release (M11); retention per SECURITY_AND_PRIVACY.
- **Secrets:** platform secret store; rotation procedure documented in M11.
- **Dependencies:** monthly update review, `pip-audit` and `npm audit` in CI.
