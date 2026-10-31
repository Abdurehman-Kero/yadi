# M05 Plan

1. Migration 0005: reminder fields on tasks; `reminders`, `reminder_attempts`, `notifications`, `push_subscriptions`, `worker_heartbeat`.
2. Reminder sync (from task to reminder), with tests.
3. Worker: claim, deliver, retry, recover, heartbeat; concurrency and real-process tests.
4. APIs: reminders, snooze, notifications, push subscriptions, service status.
5. Web: native `dialog` modal; notification page and unread badge; Settings section; service worker.
6. Browser and accessibility tests; live worker measurement; report.

## Decisions
- **What a reminder points at:** fixed start, else the first future planned block, else the deadline. A task in progress is reminded only of its deadline.
- **Duplicate prevention:** the unique key is built from task, anchor time and lead time, not from the current clock, so recalculating cannot create a second reminder. The in-app row is unique per reminder and is committed in the same transaction as `delivered`.
- **Push is best-effort:** it runs after that commit. A crash in between means no push but still an in-app notification, never a duplicate. Push failures are recorded and not retried; expired subscriptions are removed.
- **Late reminders are never dropped silently** after an outage: they are delivered once with wording that says so. This is simpler and more honest than the earlier idea of cancelling them.
- **Delivered means the server processed it.** Whether a device displayed a push is unknown, and the UI does not claim otherwise.
- **Sign-in moved** out of M05 to its own step before any hosting (D-015). Everything stays scoped by user.
- **Modals** use the browser's `dialog` element: focus trapping and Escape come built in, with no new dependency.
