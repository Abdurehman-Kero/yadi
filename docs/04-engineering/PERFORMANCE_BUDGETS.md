# Performance Budgets (initial — revise with measurements)

Assumed MVP workload: ≤ 100 users, ≤ 2,000 tasks per user, single small instance.

| Area | Target |
|---|---|
| Dashboard initial load (broadband, cached assets) | LCP ≤ 2.5 s; JS ≤ 200 KB gzipped initial |
| Task list API (50 items) | p95 ≤ 150 ms |
| Mutation APIs | p95 ≤ 200 ms |
| Schedule generation (7 days, 100 tasks) | p95 ≤ 500 ms |
| AI extraction | p95 ≤ 8 s; UI shows progress after 300 ms |
| Reminder processing delay | p95 ≤ 30 s after due time; max 60 s |
| Duplicate reminders | 0 |
| Error rate (5xx) | < 0.5% |
| DB | queries on indexed paths; no N+1; pagination on lists |

These are hypotheses, not results. Nothing is claimed as achieved until measured.
