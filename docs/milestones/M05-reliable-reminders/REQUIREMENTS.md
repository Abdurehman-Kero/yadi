# M05 Requirements

| ID | Requirement | Acceptance criterion |
|---|---|---|
| M05-R1 | Reminders are processed by a worker with no browser open. | A real worker process delivers with no client connected. |
| M05-R2 | Pending work survives a worker stop or crash. | Real process stopped and restarted; expired leases recovered. |
| M05-R3 | One reminder produces one notification, even with retries or several workers. | Concurrency test: two workers, each reminder delivered once. |
| M05-R4 | A reminder follows the task: moved plan or deadline recalculates it; completed or cancelled tasks cancel it. | API tests. |
| M05-R5 | A task can use the default lead time, its own, or no reminder. | API and form tests. |
| M05-R6 | Failures retry after 30 s, 2 min and 10 min at most; then the state is `failed`. Each attempt is recorded, without message content. | Tests with a failing channel and an injected clock. |
| M05-R7 | Snooze creates one new reminder and cancels any pending one, in one transaction. | API test. |
| M05-R8 | If push is unsupported, denied or not configured, the notification still appears in-app. | Tests; browser test. |
| M05-R9 | A late reminder (after an outage) is still delivered once and says it is late. | Test. |
| M05-R10 | 95% of reminders are processed within 30 s of due time. | Measured with a real worker on this machine. |
| M05-R11 | Other users' reminders, notifications and subscriptions are invisible. | API tests. |
| M05-R12 | Settings shows whether the reminder service is running. | API and browser tests. |
| M05-R13 | Modal dialogs trap focus, close with Escape and return focus; no serious axe issue. | Browser tests. |
