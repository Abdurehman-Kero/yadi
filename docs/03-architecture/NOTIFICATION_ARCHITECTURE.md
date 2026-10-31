# Notification Architecture

## Separation
**Scheduling** (create reminder rows) is separate from **delivery** (channel transport). The `reminders` table is the durable queue.

## State machine
```
scheduled ──claim──► processing ──ok──► delivered
    │                    │ ──error, attempts<max──► scheduled (next_attempt_at = backoff)
    │                    └─error, attempts=max──► failed
    └──task cancelled/completed/changed──► cancelled
processing with expired lease ──recovery──► scheduled
```
`delivered` means the channel accepted it (server-side). Device presentation is not guaranteed and is recorded as unknown unless the channel confirms.

## Worker
Loop every ~5 s: `SELECT … WHERE state='scheduled' AND next_attempt_at<=now() ORDER BY next_attempt_at FOR UPDATE SKIP LOCKED LIMIT n`; set `processing`, `locked_until=now()+60s`; deliver; write `reminder_attempts`; update state. A separate sweep returns expired-lease rows to `scheduled`. Safe with multiple workers and after restarts.

## Idempotency
`idempotency_key = hash(task_id, kind, anchor kind, anchor time, lead time)` unique → recomputation never creates duplicates. Delivery includes the reminder id as the notification tag so a retry replaces rather than duplicates.

## Retries
Exponential backoff 30 s, 2 m, 10 m; 4 attempts in total. A reminder delivered after its anchor time is still sent once, with wording that says it is late (M05 decision: nothing is dropped silently). Only in-app delivery is retried; push is best-effort and recorded.

## Timezone/DST
`remind_at` is an absolute UTC instant derived from the task time in the user's zone at creation; if the task time changes, reminders are recomputed. Recurring tasks expand per local wall-clock time.

## Permission denial
Web Push permission denied/unsupported → fall back to in-app notification center (shown on next load) and show a settings hint. Sound is best-effort only; never promised.

## Snooze/reschedule
Snooze creates a new reminder (new key) and cancels the old one atomically.

## Monitoring
Metrics: queue depth, oldest due age, processing delay p95, failure rate, duplicate count (must be 0). Structured logs per attempt.
