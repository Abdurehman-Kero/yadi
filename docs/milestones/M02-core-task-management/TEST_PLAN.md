# M02 Test Plan

| Area | Test | Layer |
|---|---|---|
| Lifecycle | Every status pair allowed/rejected; planned/inbox rule | pytest unit |
| Tasks API | Create, validation, edit, clear fields, list filters, pagination, start/complete/reopen/cancel, 409s | pytest + real Postgres |
| History | Event per change, with actor and changed fields; no event on no-op edit | pytest |
| Isolation | User B gets 404 on every route for user A's task; lists never mix | pytest |
| Identity | 401 when disabled; unknown user 401 | pytest |
| Preferences | Read, update, bad timezone, end before start | pytest |
| Outage | Task route with DB down returns 503 | pytest |
| Performance | p95 of list with 2,000 tasks | pytest (timed) |
| Timezone | Wall time to UTC and back, DST days in New York, no-DST zones | Vitest |
| UI | Form errors keep input; list states; cancel confirmation | Vitest + Testing Library |
| Journey | Create, refresh, edit, start, complete, reopen, cancel, filter; server failure message; settings change alters displayed time | Playwright |
| Accessibility | axe on /tasks and /settings; keyboard-only task creation | Playwright |
