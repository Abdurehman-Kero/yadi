# Use Cases

Actor for all: User unless stated. Related requirements in brackets.

## UC-01 Capture tasks from text [FR-TASK-001, FR-AI-001..003]
- **Pre:** signed in (or dev identity); timezone set.
- **Main:** user enters text → system returns drafts with per-field confidence → user edits/confirms → tasks saved → schedule and reminders updated.
- **Exceptions:** ambiguous detail → question or editable assumption; AI unavailable → manual form with text preserved; invalid output → same fallback.
- **Post:** tasks persisted; history event `created` by actor user (or ai-assisted).

## UC-02 Generate and adjust schedule [FR-SCH-001..006]
- **Pre:** ≥1 task or event.
- **Main:** request generation → engine returns blocks → user reviews, edits, locks, accepts.
- **Exceptions:** over capacity → unscheduled list with reasons and options; fixed-event conflict → flagged, nothing moved.
- **Post:** accepted blocks stored; reminders align to blocks.

## UC-03 Change plan by conversation [FR-CONV-001..003]
- **Main:** message → intent → resolve task → validate with engine → (confirm if consequential) → apply → report actual result.
- **Exceptions:** several matches → ask; request not feasible → explain and offer alternatives; unsupported action → say so.

## UC-04 Receive and act on reminder [FR-NOT-001..005]
- **Actor:** System worker, User.
- **Main:** reminder due → worker claims → delivers → records attempt → user snoozes/completes.
- **Exceptions:** permission denied → in-app; delivery failure → retry with backoff then failed state; duplicate job → one notification.

## UC-05 Complete or cancel task [FR-TASK-003, 005]
- Updates status, removes future blocks, cancels pending reminders, writes history.

## UC-06 Configure preferences [FR-SET-001]
- Edit timezone, working hours, reminder defaults, notification permission; affects only future planning unless user regenerates.
