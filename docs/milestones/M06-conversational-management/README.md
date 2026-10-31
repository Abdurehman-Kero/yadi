# M06 — Conversational Task and Schedule Management

**Purpose:** change the plan by asking: "move my project to the afternoon", "I finished the report", "what should I do next?". The AI only interprets. Application code finds the task, checks the rules, makes the change and reports what actually happened.

**Status:** Built; not complete. The real AI has not been tested on these messages. See COMPLETION_REPORT.md.

## In scope
- One message box on Today for capturing tasks, changing them and asking about the plan.
- Actions: move, complete, start, cancel, change priority, block out unavailable time, replan.
- Questions answered from stored data: what is next, what fits in N minutes, what is on today.
- Asking which task when several match; confirmation for consequential changes.
- Short conversation context held in the browser only.
- Every AI-requested change recorded in history as made through the assistant.

## Out of scope
Several actions in one message, voice (M09), memory across sessions (M07), AI-written explanations, undo beyond the existing reopen and move.

## Requirements covered
FR-CONV-001, FR-CONV-002, FR-CONV-003.
