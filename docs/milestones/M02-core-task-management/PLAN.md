# M02 Plan

1. Migration 0002: `tasks`, `task_events`, index `(user_id, created_at DESC, id DESC)`.
2. Pure lifecycle module (allowed transitions, planned/inbox rule), tested first.
3. Task service and API, test-first, on a throwaway migrated database. Each mutation commits explicitly with its event.
4. Current-user dependency (dev identity). Preferences API.
5. Regenerate OpenAPI types. Web: typed API client, timezone helpers, `/tasks`, `/settings`, navigation, design tokens.
6. Playwright + axe against a dedicated `yadi_e2e` database on ports 8100/3100.
7. Run all gates, dry-run the demo, write the completion report.

## Decisions
- Status changes use action routes (`/start`, `/complete`, `/reopen`, `DELETE` = cancel), not PATCH, so illegal changes are impossible to express by accident.
- `priority_source`, fixed-time fields, recurrence and dependencies from DATA_MODEL.md are added by the milestones that use them, not now.
- Timezone conversion is a small helper over `Intl` rather than a date library (no new dependency).
- Tartiiba features are out of scope (D-010).
