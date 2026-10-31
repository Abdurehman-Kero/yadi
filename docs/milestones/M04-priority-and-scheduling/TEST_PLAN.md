# M04 Test Plan

| Area | Test | Layer |
|---|---|---|
| Invariants | No overlap, working hours, fixed intact, buffer, dependency order, full minutes, deadlines, determinism | Hypothesis |
| Time | Daylight-saving days in New York, non-UTC zones | pytest |
| Conflicts | Over capacity, past deadline, cycles, missing estimate, overlapping fixed events | pytest |
| Greedy quality | Miss rate against brute force on small random cases | pytest (measured) |
| API | Generate, read, edit, lock, regenerate, stale flag, statuses, isolation, 409s | pytest + Postgres |
| Performance | Generation with 100 tasks | timed pytest |
| UI | Time helpers, form fixed-time fields | Vitest |
| Journey | Fixed event plus tasks, generate, see order and conflict, edit block, complete task | Playwright |
| Accessibility | axe on every screen, light and dark; keyboard | Playwright |
