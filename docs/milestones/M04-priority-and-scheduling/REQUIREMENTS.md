# M04 Requirements

| ID | Requirement | Acceptance criterion |
|---|---|---|
| M04-R1 | Same input always gives the same schedule. | Property test. |
| M04-R2 | Fixed events are never moved or overlapped by generated work. | Property test. |
| M04-R3 | Generated blocks stay in working hours, never overlap, respect the buffer, and start after dependencies end. | Property tests. |
| M04-R4 | Scheduled minutes equal the task's estimate; chunks are at least 25 minutes unless the whole task is shorter. | Property test. |
| M04-R5 | Deadlines are met or the task is reported unscheduled with a reason and alternatives. Nothing is scheduled past its deadline. | Property and example tests. |
| M04-R6 | Times are correct in the user's timezone, including 23- and 25-hour days. | Example tests. |
| M04-R7 | Priority breaks ties between tasks competing for time; user priority is never changed by scheduling. | Tests. |
| M04-R8 | Regeneration keeps locked and fixed blocks and replaces other future blocks. | API test. |
| M04-R9 | A manual block edit locks the block. Moving outside working hours or onto another block returns 409; fixed blocks cannot be moved. | API tests. |
| M04-R10 | Completing or cancelling a task removes its future blocks. | API test. |
| M04-R11 | Every block has a plain-language reason. The schedule is flagged out of date after a task changes. | API tests. |
| M04-R12 | Another user's schedule and blocks are invisible. | API test. |
| M04-R13 | Generation p95 <= 500 ms for 100 tasks over 7 days. | Timed test on this machine. |
| M04-R14 | Today dashboard shows next action, today's schedule, items needing attention, upcoming tasks and the Tell Yadi box, each with empty states. | Browser test. |
| M04-R15 | Interface follows UX_PRINCIPLES: clear navigation on desktop and phone, no gradients, no colour-only meaning, no serious axe issue in light or dark mode. | Screenshots, axe in both modes. |
