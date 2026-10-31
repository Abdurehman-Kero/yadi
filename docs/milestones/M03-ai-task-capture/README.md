# M03 — AI-Powered Task Capture

**Purpose:** type a sentence, see the tasks Yadi understood, correct them, and save them. Nothing is saved until the user confirms.

**Status:** Complete, with a caveat: see COMPLETION_REPORT.md.

## In scope
- `POST /api/v1/assistant/extract`: text in, validated task drafts and questions out. Saves no tasks.
- Provider adapter behind an internal interface (ADR-003), usage and cost records, per-user daily limit.
- "Tell Yadi" box on the Tasks screen: review, edit, save or discard each draft.
- Fallback: if the AI fails, the manual form opens with the user's text kept.
- Evaluation set and scorer.

## Out of scope
Voice (M09), changing existing tasks by chat (M06), fixed-time events and scheduling (M04), recurrence. "Meeting tomorrow at 10" is captured as a task due at 10:00 until M04 adds fixed events.

## Requirements covered
FR-TASK-001, FR-AI-001, FR-AI-002, FR-AI-003, FR-AI-004.
