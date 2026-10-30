# Data Model (initial, MVP)

Status: Proposed. Refined in M01/M02 migrations.

## Entities
| Table | Key columns | Notes |
|---|---|---|
| users | id, email, created_at | Dev identity first (OQ-Q3) |
| user_preferences | user_id PK, timezone, locale, work_start, work_end, default_reminder_minutes, buffer_minutes | Working hours as local time + weekdays |
| tasks | id, user_id, title, description, status, priority, priority_source, due_at, estimated_minutes, is_fixed_time, fixed_start_at, fixed_end_at, preferred_period, recurrence_rule, created_at, updated_at, completed_at | `priority_source` = user \| ai \| default |
| task_dependencies | task_id, depends_on_task_id | Later; prevent cycles |
| schedule_blocks | id, user_id, task_id, start_at, end_at, locked, generated_run_id | One task may have several blocks |
| schedule_runs | id, user_id, created_at, inputs_hash, unscheduled jsonb | Stores conflicts/explanations |
| task_events | id, task_id, user_id, type, payload jsonb, at, actor (user\|ai\|system) | Append-only history/audit |
| reminders | id, user_id, task_id, remind_at, state, attempts, next_attempt_at, locked_until, idempotency_key UNIQUE | Doubles as the job queue |
| reminder_attempts | id, reminder_id, started_at, channel, outcome, error | Server processing ≠ device delivery |
| ai_usage | id, user_id, operation, model, input_tokens, output_tokens, cost_estimate, latency_ms, ok, at | No message content |

## Enums
- `task.status`: `inbox, planned, scheduled, in_progress, completed, cancelled`
- `task.priority`: `critical, high, medium, low`
- `reminder.state`: `scheduled, processing, delivered, failed, cancelled`

## Lifecycle rules
- inbox → planned (details complete) → scheduled (has blocks) → in_progress → completed.
- Any non-terminal → cancelled. completed/cancelled are terminal (reopen = new event, allowed from completed only).
- Rescheduling is an event, not a status.
- Cancelling or completing a task cancels its `scheduled` reminders in the same transaction.
- Changing `due_at` or fixed time recomputes reminders.

## Constraints
FKs with `ON DELETE CASCADE` from user; `CHECK (estimated_minutes > 0)`; `CHECK (end_at > start_at)`; unique `reminders.idempotency_key`; indexes: `tasks(user_id,status,due_at)`, `schedule_blocks(user_id,start_at)`, `reminders(state,next_attempt_at)` partial where state in (scheduled).

## Deletion
User deletion cascades all rows. Backups age out per retention policy (see SECURITY_AND_PRIVACY).
