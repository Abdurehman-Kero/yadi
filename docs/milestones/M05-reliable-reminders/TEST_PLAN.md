# M05 Test Plan

| Area | Test | Layer |
|---|---|---|
| Sync | Anchor choice, lead time, none, recalculation, cancel on finish, reactivation, no duplicates | pytest + Postgres |
| Worker | Delivery, retry schedule, final failure, expired lease recovery, finished task, late wording | pytest, injected clock |
| Concurrency | Two workers on the same due reminders: exactly one notification each | pytest, threads |
| Real process | Stop the worker, create work, restart, delivered once; timeliness measured | pytest, subprocess |
| API | Snooze, cancel, read, read all, subscriptions, status, isolation | pytest |
| Push | Payload, expired subscription removal, failure does not undo delivery (fake sender) | pytest |
| UI | Modal open, close, focus; forms in modals | Vitest, Playwright |
| Journey | Task with a due reminder appears as a notification from the real worker; snooze; permission states | Playwright |
| Accessibility | axe with modals open and on the notifications page, light and dark | Playwright |
