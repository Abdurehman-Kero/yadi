# Requirements Traceability

This table is the live implementation status (SRS.docx shows the baseline). Implementation and test columns are filled in as milestones complete.

| Requirement | Name | Priority | Milestone | Verification | Implementation | Tests | Status |
|---|---|---|---|---|---|---|---|
| FR-TASK-001 | Natural-language task capture | Must | M03 | Test + Eval | modules/assistant, AssistantCapture | test_assistant_api, test_gemini_client | Built; live AI unverified |
| FR-TASK-002 | Task create/read/update | Must | M02 | Test | modules/tasks, features/tasks | test_tasks_api, tasks.spec | Done (M02) |
| FR-TASK-003 | Task lifecycle | Must | M02 | Test | modules/tasks, features/tasks | test_tasks_api, tasks.spec | Done (M02) |
| FR-TASK-004 | Task history | Should | M02 | Test | modules/tasks, features/tasks | test_tasks_api, tasks.spec | Done (M02) |
| FR-TASK-005 | Cancel and complete | Must | M02/M05 | Test | modules/tasks | test_tasks_api | Done (M05) |
| FR-AI-001 | Structured extraction | Must | M03 | Test + Eval | modules/assistant, AssistantCapture | test_assistant_api, test_gemini_client | Built; live AI unverified |
| FR-AI-002 | Ambiguity handling | Must | M03 | Eval | modules/assistant, AssistantCapture | test_assistant_api, test_gemini_client | Built; live AI unverified |
| FR-AI-003 | AI failure fallback | Must | M03 | E2E | AssistantCapture | test_assistant_api, tasks.spec | Done (M03) |
| FR-AI-004 | Usage tracking | Should | M03 | Test | ai_usage | test_assistant_api | Done offline; cut-off answers under-counted |
| FR-PRI-001 | Priority model | Must | M04 | Test | modules/scheduling, features/schedule, features/today | test_scheduling_engine, test_schedule_api, tasks.spec | Done (M04): no AI suggestions yet |
| FR-PRI-002 | Explained recommendations | Should | M04 | Review | modules/scheduling, features/schedule, features/today | test_scheduling_engine, test_schedule_api, tasks.spec | Done (M04): ordering reasons |
| FR-SCH-001 | Schedule generation | Must | M04 | Test | modules/scheduling, features/schedule, features/today | test_scheduling_engine, test_schedule_api, tasks.spec | Done (M04) |
| FR-SCH-002 | Fixed-event protection | Must | M04 | Property test | modules/scheduling, features/schedule, features/today | test_scheduling_engine, test_schedule_api, tasks.spec | Done (M04) |
| FR-SCH-003 | Constraint compliance | Must | M04 | Property test | modules/scheduling, features/schedule, features/today | test_scheduling_engine, test_schedule_api, tasks.spec | Done; dependencies have no UI |
| FR-SCH-004 | Conflict reporting | Must | M04 | Test | modules/scheduling, features/schedule, features/today | test_scheduling_engine, test_schedule_api, tasks.spec | Done (M04) |
| FR-SCH-005 | Schedule editing | Should | M04 | E2E | modules/scheduling, features/schedule, features/today | test_scheduling_engine, test_schedule_api, tasks.spec | Done (M04) |
| FR-SCH-006 | Timezone correctness | Must | M04 | Test | modules/scheduling, features/schedule, features/today | test_scheduling_engine, test_schedule_api, tasks.spec | Done (M04) |
| FR-NOT-001 | Durable reminders | Must | M05 | Integration | modules/reminders, worker.py, features/notifications | test_reminders, tasks.spec | Done (M05) |
| FR-NOT-002 | Retries and idempotency | Must | M05 | Integration | modules/reminders, worker.py, features/notifications | test_reminders, tasks.spec | Done (M05) |
| FR-NOT-003 | Snooze and reschedule | Should | M05 | E2E | modules/reminders, worker.py, features/notifications | test_reminders, tasks.spec | Done (M05) |
| FR-NOT-004 | Permission denial fallback | Must | M05 | E2E | modules/reminders, worker.py, features/notifications | test_reminders, tasks.spec | Done (M05) |
| FR-NOT-005 | Delivery records | Should | M05 | Test | modules/reminders, worker.py, features/notifications | test_reminders, tasks.spec | Done (M05) |
| FR-CONV-001 | Conversational updates | Must | M06 | E2E | modules/assistant, scheduling/move.py, AssistantCapture | test_assistant_conversation, tasks.spec | Built; real AI untested |
| FR-CONV-002 | Reference resolution | Must | M06 | Eval + Test | modules/assistant, scheduling/move.py, AssistantCapture | test_assistant_conversation, tasks.spec | Built; real AI untested |
| FR-CONV-003 | Confirmation of consequential changes | Must | M06 | E2E | modules/assistant, scheduling/move.py, AssistantCapture | test_assistant_conversation, tasks.spec | Built; real AI untested |
| FR-MEM-001 | User-controlled preferences | Should | M07 | E2E | — | — | Not started |
| FR-MEM-002 | Controlled memory | Should | M07 | E2E | — | — | Not started |
| FR-CAL-001 | Calendar integration | Could | M08 | Integration | — | — | Not started |
| FR-VOI-001 | Voice input | Could | M09 | E2E | — | — | Not started |
| FR-PRO-001 | Proactive assistance | Could | M10 | E2E | — | — | Not started |
| FR-SET-001 | Settings | Must | M02/M05 | E2E | modules/preferences, features/settings | test_preferences_api, tasks.spec | Done (M05); real alerts unconfirmed |
| FR-UI-001 | Dashboard | Must | M04 | E2E | modules/scheduling, features/schedule, features/today | test_scheduling_engine, test_schedule_api, tasks.spec | Done (M04) |
| NFR-SEC-001 | Secret protection | Must | M01+ | Test + Scan | — | — | Not started |
| NFR-SEC-002 | User data isolation | Must | M02+ | Integration | service user_id scoping | test_tasks_api | Done for M02 routes; continues |
| NFR-SEC-003 | Input validation and safe errors | Must | M01+ | Test | core/errors, schemas | test_errors, test_tasks_api | Done for current routes; continues |
| NFR-PRV-001 | Privacy minimisation | Must | M01+ | Review | — | — | Not started |
| NFR-PERF-001 | Task list performance | Should | M02 | Perf test | ix_tasks_user_created | test_tasks_performance | Done (dev-machine measurement) |
| NFR-PERF-002 | Reminder timeliness | Must | M05 | Integration | modules/reminders, worker.py, features/notifications | test_reminders, tasks.spec | Done (dev-machine measurement) |
| NFR-REL-001 | Recovery | Must | M05 | Integration | modules/reminders, worker.py, features/notifications | test_reminders, tasks.spec | Done for worker and API; AI fallback in M03 |
| NFR-ACC-001 | Accessibility | Must | M02+ | axe + manual | web screens | tasks.spec (axe, keyboard) | Partial: no screen-reader pass |
| NFR-MNT-001 | Maintainability | Must | M01 | CI | scripts/run.mjs | 10 gates | Done locally; no CI yet |
