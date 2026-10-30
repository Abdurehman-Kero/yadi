# YADI — Master Product Vision, System Specification, and AI Development Agent Instructions

**Project name:** Yadi  
**Product category:** AI-powered personal assistant and intelligent daily-life management system  
**Project approach:** Documentation-first, milestone-based, modular, test-driven, and production-oriented  
**Long-term vision:** Build a reliable personal AI assistant that understands natural language, remembers relevant personal context with permission, organizes daily life, manages tasks and schedules, sends timely reminders, and gradually becomes capable of taking useful actions on the user's behalf.

---

# 1. Instructions to the AI Development Agent

You are the lead software architect, product planner, UX designer, technical researcher, developer, QA engineer, documentation owner, and project progress manager for Yadi.

You are receiving this project for the first time. Do not assume that you already understand its purpose, requirements, architecture, or implementation.

Your responsibility is to help me build Yadi from the initial idea into a well-documented, reliable, secure, scalable, and production-ready product.

You must approach this project as a long-term software product rather than a small demo application.

I am the product owner. You are responsible for helping me make technically sound decisions, explaining those decisions in understandable language, and implementing the project in a disciplined way.

## Non-negotiable rules

1. Do not begin by implementing the entire application.
2. Understand and document the product before building it.
3. Research important technical decisions when necessary instead of guessing.
4. Create a complete project roadmap before implementation.
5. Divide development into clearly defined milestones.
6. Give every milestone its own requirements, implementation plan, testing plan, completion report, and demonstration script.
7. Maintain a persistent agent progress file so work can resume after a computer restart, context loss, or interrupted session.
8. Keep the codebase modular, readable, testable, and easy for a new developer to understand.
9. Prioritize usability, accessibility, security, reliability, performance, and maintainability.
10. Never claim a feature is complete without verifying it.
11. Never hide errors, incomplete requirements, technical debt, or failed tests.
12. Explain what has been built in simple English so I can understand and demonstrate the system.
13. Do not introduce unnecessary technologies, dependencies, abstractions, or complicated infrastructure.
14. Do not move to the next milestone until the current milestone satisfies its acceptance criteria, unless an explicitly documented exception is approved.
15. Make important decisions explicit and record them in project documentation.

If an important decision is missing, identify it, explain the available options, recommend one, and ask me only when my decision is genuinely necessary. For reversible technical decisions, you may recommend and document a sensible default rather than blocking progress.

---

# 2. Product Vision

## 2.1 What is Yadi?

Yadi is an AI-powered personal assistant designed to help people organize their lives through natural conversation.

Instead of requiring users to manually create every task, assign dates, calculate priorities, and manage calendar conflicts, Yadi should allow them to communicate naturally.

For example, a user might say:

"I have a university assignment due Friday, a meeting tomorrow at 10 AM, and I need to work on my project for two hours. I also want to exercise in the evening."

Yadi should understand the user's intentions, identify the individual activities, recognize deadlines and fixed commitments, ask for clarification when necessary, and help create a realistic schedule.

The user should be able to correct Yadi conversationally.

For example:

"Move my project work to the afternoon."

"Make the assignment my highest priority."

"Remind me 15 minutes before my meeting."

"I couldn't finish my assignment today. Help me rearrange tomorrow."

Yadi should understand these requests in context and update the appropriate information without forcing the user to start over.

The long-term goal is to make Yadi feel like a personal assistant that understands context, remembers relevant information with permission, helps users plan ahead, and follows through on agreed actions.

## 2.2 What Yadi is not

Yadi should not be merely:

- A conventional to-do list.
- A basic calendar application.
- A chatbot that only gives advice.
- An AI wrapper that generates schedules without checking whether they are feasible.
- A notification application with an AI interface.
- An autonomous agent that makes consequential decisions without user permission.

Yadi should combine conversational AI, structured personal information, scheduling logic, reliable background processing, and a clear user experience.

## 2.3 Product principles

All product and technical decisions should support these principles:

- **Simple interaction:** Users should be able to express intentions in ordinary language.
- **User control:** Users can review, correct, approve, reschedule, and cancel actions.
- **Realistic planning:** Schedules respect time, deadlines, availability, and constraints.
- **Reliable follow-through:** Reminders and scheduled actions should not depend on the application remaining open.
- **Useful memory:** Yadi remembers relevant context only according to explicit, understandable privacy controls.
- **Explainable decisions:** Users can understand why tasks were prioritized or scheduled at particular times.
- **Graceful recovery:** Errors and missed tasks should be handled without losing important information.
- **Progressive intelligence:** Begin with dependable functionality and add more advanced AI capabilities as the product matures.

---

# 3. Product Scope and Long-Term Capabilities

Plan Yadi as a system that can grow over time. Do not attempt to implement every capability in the first release.

## 3.1 Natural-language task capture

Users should be able to enter text or speak naturally.

Examples:

- "Remind me to call my advisor tomorrow morning."
- "I need three hours to finish my project before Sunday."
- "Every weekday, help me reserve time for studying."
- "I have a meeting at 2 PM and need 30 minutes to prepare."

Yadi should extract structured information such as:

- Task title and description.
- Due date and time.
- Estimated duration.
- Priority.
- Preferred time.
- Recurrence.
- Dependencies.
- Whether the activity has a fixed time.
- Reminder preferences.
- Relevant context.
- Confidence and unresolved ambiguities.

The AI must not silently invent missing details.

When an ambiguity materially affects scheduling, Yadi should ask a concise clarification question or propose an editable assumption.

For example, if the user says "tomorrow morning," Yadi should interpret it using the user's configured timezone and preferences. If the exact time matters, it should ask or propose a time for confirmation.

## 3.2 Intelligent task prioritization

Yadi should help users determine what deserves attention first.

Consider factors such as:

- Deadline urgency.
- Task importance.
- Consequences of missing the deadline.
- Estimated duration.
- Dependencies.
- User-defined priority.
- Available time.
- Current commitments.
- User preferences.

Start with a transparent, deterministic priority system.

A proposed initial priority scale is:

- Critical.
- High.
- Medium.
- Low.

The AI may recommend a priority, but users must be able to override it.

A task's priority must not be confused with its scheduling position. A high-priority task may still need to be scheduled after a fixed appointment or before another task that it depends on.

Explain important recommendations in plain language.

## 3.3 Intelligent scheduling

Yadi should generate and maintain realistic daily and weekly plans.

The scheduling engine must consider:

- Fixed appointments.
- Task duration.
- Deadlines.
- Priority.
- Dependencies.
- Available time.
- Preferred working hours.
- Sleep and rest periods when configured.
- Breaks and transition buffers.
- Recurring activities.
- Timezone.
- Existing calendar commitments.
- User-defined scheduling restrictions.

Use a deterministic, testable scheduling engine for core constraints. An LLM may interpret user intent and help explain recommendations, but it must not be the sole authority deciding whether a schedule is valid.

The system should distinguish:

- Fixed events that must not be moved without permission.
- Flexible tasks that can be rearranged.
- Tasks with deadlines.
- Tasks with preferred times.
- Tasks that have no specific deadline.
- Tasks that cannot fit into the current schedule.

If all work cannot fit, Yadi should explain the conflict and offer alternatives instead of pretending everything can be completed.

Users should be able to inspect, edit, accept, and regenerate their schedule.

## 3.4 Reminders and notifications

Yadi should provide dependable reminders before and at the appropriate time.

Potential capabilities include:

- Custom reminder times.
- Multiple reminders for selected tasks.
- In-app notifications.
- Browser or mobile push notifications where supported.
- Sound alerts where permitted.
- Daily schedule briefings.
- Upcoming-deadline warnings.
- Missed-task follow-ups.
- Snooze and reschedule actions.

Reminder delivery must use durable backend scheduling and background workers rather than depending exclusively on a running browser tab.

Define behavior for timezones, daylight-saving transitions where relevant, retries, duplicate prevention, and notification permission denial.

Do not promise that every reminder will produce a sound. Browsers and operating systems may restrict background audio or notifications.

## 3.5 Conversational schedule management

Users should be able to change their plans through natural language.

Examples:

- "Move my reading task to tomorrow."
- "I finished that task."
- "Give this assignment a higher priority."
- "I am unavailable between 1 PM and 3 PM."
- "What should I focus on next?"
- "I have 45 minutes free. What can I complete?"

Yadi should identify the intended task or ask for clarification if several tasks match.

Changes must update the underlying structured data, not merely generate a conversational response claiming that something changed.

After a successful change, the assistant should summarize what was updated.

For consequential operations, show the proposed action and obtain confirmation when appropriate.

## 3.6 Task lifecycle management

Every task should have a clear lifecycle.

At minimum, consider:

- Inbox or unprocessed.
- Planned.
- Scheduled.
- In progress.
- Completed.
- Cancelled.
- Deferred or rescheduled.

Choose the final model during requirements analysis. Avoid introducing unnecessary statuses that users cannot understand.

Record relevant task history so users can see important changes, such as rescheduling or completion.

## 3.7 Personal preferences and routines

Yadi should gradually support configurable preferences such as:

- Preferred working hours.
- Usual wake-up and sleep times.
- Study or work routines.
- Break preferences.
- Preferred reminder intervals.
- Typical task durations.
- Preferred days for recurring activities.
- Notification preferences.
- Timezone and locale.

Users must be able to edit these preferences.

Do not infer sensitive personal information unnecessarily. Do not treat a temporary preference as a permanent rule without sufficient evidence or user confirmation.

## 3.8 Conversational memory

In later milestones, Yadi should maintain useful context across conversations.

Examples:

- The user prefers studying in the morning.
- A project has a deadline next month.
- The user usually wants a short break after focused work.
- A recurring activity should remain in the weekly plan.

Distinguish between:

1. Current conversation context.
2. Structured application data, such as tasks and appointments.
3. Explicitly saved personal preferences.
4. Optional inferred preferences.
5. Historical conversation records.

Do not rely on vector search or chat history as the sole source of truth for deadlines, task status, or calendar events.

Users must be able to inspect, correct, and delete saved memories. Sensitive information should not be saved by default.

## 3.9 Calendar integration

In later phases, investigate integrations with external calendars, such as Google Calendar.

Plan for:

- Authentication and authorization.
- Reading existing events.
- Creating or updating events.
- Synchronization conflicts.
- Revoked permissions.
- Duplicate prevention.
- Timezone handling.
- Token security.
- User confirmation for external changes.

Do not assume that a task has been added to an external calendar unless the integration confirms success.

## 3.10 Proactive assistance

In the long term, Yadi should help users before they explicitly ask.

Examples:

- Identifying a deadline that may be missed.
- Suggesting a better time for an overloaded day.
- Noticing an unresolved task that needs attention.
- Preparing a morning briefing.
- Recommending the next useful action.
- Suggesting a schedule adjustment after a missed commitment.

Proactive behavior must be relevant, explainable, configurable, and non-intrusive.

Do not generate excessive notifications or repeatedly interrupt focused work.

## 3.11 Future voice and wearable capabilities

Design the architecture so that future versions could support:

- A mobile application.
- Voice-first interaction.
- Hands-free task capture.
- Optional wearable hardware.
- More advanced speech recognition.
- Voice responses.
- Context-aware reminders.

Do not build custom wearable hardware in the initial MVP. Keep the core assistant independent of any particular device.

---

# 4. Define the MVP Clearly

Before implementation, create an explicit MVP scope document.

The first useful version should prioritize the following:

1. Account or local development identity, with a clearly defined authentication approach.
2. A clean dashboard showing today's schedule and upcoming tasks.
3. Text-based natural-language task capture.
4. AI extraction of task information into structured data.
5. Editable task titles, deadlines, duration, priority, and reminders.
6. A task list and daily schedule view.
7. A basic deterministic scheduling engine.
8. Conversational task updates and rescheduling.
9. Task completion and cancellation.
10. Persistent data storage.
11. Reliable server-side reminder scheduling.
12. Clear error handling and loading states.
13. A settings page for basic preferences and notification controls.
14. Automated tests for the critical workflows.
15. Documentation and a working demonstration.

Voice input can be added early if it is practical, but do not let speech technology delay the core scheduling and reminder functionality.

Do not include advanced long-term memory, broad autonomous actions, custom hardware, complex multi-agent orchestration, or extensive integrations in the MVP unless a documented product decision justifies them.

---

# 5. Documentation-First Development

Before building product features, create the documentation system.

Documentation is a core project deliverable, not an optional activity performed at the end.

Create a clear source of truth for requirements, architecture, decisions, implementation plans, testing, and progress.

## 5.1 Required initial documents

Create these documents before feature implementation.

### Product and requirements

- `README.md` — project overview, setup, current status, and links to important documents.
- `docs/01-product/PRODUCT_VISION.md` — purpose, target users, problems, goals, non-goals, and long-term direction.
- `docs/01-product/PRODUCT_REQUIREMENTS.md` — product capabilities, user journeys, MVP scope, and future features.
- `docs/01-product/USER_PERSONAS.md` — primary user types and their needs.
- `docs/01-product/USER_FLOWS.md` — workflows from task capture to completion.
- `docs/01-product/UX_PRINCIPLES.md` — design principles and usability standards.
- `docs/02-requirements/SRS.md` — formal Software Requirements Specification.
- `docs/02-requirements/USE_CASES.md` — actors, preconditions, actions, exceptions, and outcomes.
- `docs/02-requirements/ACCEPTANCE_CRITERIA.md` — measurable completion criteria.
- `docs/02-requirements/REQUIREMENTS_TRACEABILITY.md` — mapping requirements to implementation and tests.

### Architecture and engineering

- `docs/03-architecture/SYSTEM_ARCHITECTURE.md` — components, responsibilities, and communication.
- `docs/03-architecture/DATA_MODEL.md` — entities, relationships, constraints, and lifecycle rules.
- `docs/03-architecture/API_SPECIFICATION.md` — endpoints, schemas, errors, authentication, and authorization.
- `docs/03-architecture/AI_DESIGN.md` — AI responsibilities, structured output, validation, fallback behavior, and model-provider boundaries.
- `docs/03-architecture/SCHEDULING_ENGINE.md` — scheduling constraints, algorithms, conflict handling, and priorities.
- `docs/03-architecture/NOTIFICATION_ARCHITECTURE.md` — background jobs, delivery, retries, idempotency, and monitoring.
- `docs/03-architecture/SECURITY_AND_PRIVACY.md` — threat model, privacy controls, permissions, retention, and security requirements.
- `docs/03-architecture/ADR/` — Architecture Decision Records.
- `docs/04-engineering/CODING_STANDARDS.md` — naming, modularity, error handling, and code-quality standards.
- `docs/04-engineering/TESTING_STRATEGY.md` — unit, integration, end-to-end, security, and performance testing.
- `docs/04-engineering/DEVELOPMENT_WORKFLOW.md` — branching, commits, code review, migrations, and release practices.
- `docs/04-engineering/ENVIRONMENT_SETUP.md` — prerequisites and reproducible local setup.
- `docs/04-engineering/DEPLOYMENT_AND_OPERATIONS.md` — deployment, configuration, logging, backup, recovery, and rollback.
- `docs/04-engineering/PERFORMANCE_BUDGETS.md` — measurable performance targets and resource constraints.

### Project planning and agent continuity

- `docs/05-planning/ROADMAP.md` — all phases and milestones.
- `docs/05-planning/MILESTONE_STATUS.md` — milestone completion status and blockers.
- `docs/05-planning/RISKS_AND_ASSUMPTIONS.md` — technical, product, security, and operational risks.
- `docs/05-planning/OPEN_QUESTIONS.md` — unresolved decisions.
- `docs/06-agent/AGENT_RULES.md` — persistent instructions for coding agents.
- `docs/06-agent/AGENT_PROGRESS.md` — latest verified progress and exact resume point.
- `docs/06-agent/DECISION_LOG.md` — significant decisions and their rationale.
- `docs/06-agent/KNOWN_ISSUES.md` — unresolved defects, limitations, and workarounds.
- `docs/06-agent/SESSION_LOG.md` — concise record of work performed in each session.

### Milestone-specific documentation

Create a separate directory for each milestone.

For example:

`docs/milestones/M00-foundation/`

`docs/milestones/M01-core-task-management/`

Each milestone directory must contain:

- `README.md` — purpose and scope.
- `REQUIREMENTS.md` — requirements covered by the milestone.
- `PLAN.md` — ordered implementation steps.
- `TASKS.md` — actionable development checklist.
- `TEST_PLAN.md` — verification strategy.
- `DEMO_SCRIPT.md` — explanation and demonstration instructions.
- `COMPLETION_REPORT.md` — verified outcomes, test results, known limitations, and remaining work.

Create these documents before implementing the relevant milestone. Update them when requirements or implementation decisions change.

Do not create every future milestone's detailed implementation documents prematurely if important decisions are still unknown. Establish the overall roadmap first, then create or refine detailed plans just before each milestone.

---

# 6. Software Requirements Specification

The SRS must define the system in sufficient detail that another developer could understand what must be built without reading our entire conversation.

Use unique identifiers for requirements.

For example:

- `FR-TASK-001` — natural-language task capture.
- `FR-TASK-002` — editing task information.
- `FR-AI-001` — structured extraction of task data.
- `FR-SCH-001` — schedule generation.
- `FR-SCH-002` — fixed-event conflict prevention.
- `FR-NOT-001` — durable reminder scheduling.
- `FR-MEM-001` — user-controlled saved preferences.
- `NFR-SEC-001` — secrets must not be exposed to clients.
- `NFR-PERF-001` — task-list responses must meet the defined performance target.

Each requirement must contain:

- ID.
- Name.
- Description.
- Business justification.
- Priority.
- Preconditions.
- Expected behavior.
- Acceptance criteria.
- Dependencies.
- Verification method.
- Current implementation status.

Use MoSCoW prioritization:

- Must have.
- Should have.
- Could have.
- Won't have in the current release.

The SRS must also cover:

- System boundaries.
- Actors and permissions.
- Functional requirements.
- Non-functional requirements.
- External interfaces.
- Data requirements.
- Business rules.
- Error conditions.
- Security and privacy.
- Accessibility.
- Performance and reliability.
- Assumptions and constraints.
- Out-of-scope capabilities.
- Acceptance criteria.

Do not confuse a future idea with an approved requirement. Label proposed features clearly until they are accepted.

---

# 7. Milestone-Based Development Strategy

Plan the entire development journey before implementing the MVP.

The milestones below are a proposed baseline. Adjust them when research shows a better sequence, but record the reasoning.

## M00 — Discovery, product definition, and repository foundation

Objectives:

- Establish the product vision.
- Define the MVP and long-term scope.
- Research technical options.
- Produce the SRS.
- Create the initial architecture and data model.
- Establish the roadmap and acceptance criteria.
- Create the repository and documentation structure.
- Define coding-agent continuity rules.

Expected deliverables:

- Approved foundational documentation.
- Architecture proposal.
- Initial directory structure.
- Technology decision records.
- Risk register.
- Milestone roadmap.
- A list of unresolved product decisions.

No full product feature implementation should begin before the foundational scope is sufficiently defined.

Demo script:

Explain what Yadi is, who it serves, what the MVP will do, what it will not do yet, and how development will proceed.

## M01 — Application foundation and development infrastructure

Objectives:

- Set up the frontend and backend.
- Configure the database.
- Establish environment configuration.
- Implement basic health checks.
- Configure code formatting, linting, and type checking.
- Establish automated test execution.
- Configure database migrations.
- Establish structured logging and consistent API errors.

Expected outcome:

A minimal application that runs locally, can connect to its database, and provides a reliable foundation for future development.

Demo script:

Start the application, verify the health endpoint, confirm database connectivity, run checks and tests, and explain the repository structure.

## M02 — Core task management

Objectives:

- Create, read, update, and cancel tasks.
- Validate task inputs.
- Store tasks persistently.
- Display tasks in a clear interface.
- Support completion and basic status changes.
- Add appropriate loading, empty, success, and error states.

Expected outcome:

A useful task-management application that works without AI.

Demo script:

Create a task, edit it, change its status, refresh the application, and demonstrate that data persists.

## M03 — AI-powered task capture

Objectives:

- Accept natural-language task descriptions.
- Integrate the selected AI provider through a backend service.
- Produce structured task data.
- Validate AI outputs using application schemas.
- Handle uncertain dates and missing information.
- Show users extracted information before saving when necessary.
- Provide a fallback if the AI provider fails.

Expected outcome:

Users can express tasks naturally without manually filling in every field.

Demo script:

Enter a request containing a title, deadline, and duration. Show the extracted fields, correct one field, save the task, and demonstrate invalid or ambiguous input handling.

## M04 — Priority and intelligent scheduling

Objectives:

- Implement the priority model.
- Implement deterministic schedule generation.
- Respect fixed events, availability, duration, and deadlines.
- Handle conflicts and unschedulable tasks.
- Support schedule editing and regeneration.
- Explain important scheduling decisions.

Expected outcome:

Yadi can create a feasible schedule and communicate its limitations.

Demo script:

Create tasks with different priorities and deadlines, add a fixed appointment, generate a schedule, and demonstrate how Yadi handles a conflict.

## M05 — Reliable reminders and background jobs

Objectives:

- Build durable reminder records and job processing.
- Schedule reminders based on user preferences.
- Implement retries and duplicate prevention.
- Support snoozing and rescheduling.
- Handle notification permissions and delivery failures.
- Record delivery outcomes.

Expected outcome:

Reminders can be processed independently of the frontend remaining open.

Demo script:

Create a task with a reminder, verify its scheduled job, trigger a test reminder, and demonstrate retry or failure handling.

## M06 — Conversational task and schedule management

Objectives:

- Identify tasks referenced in conversation.
- Support task updates, completion, prioritization, and rescheduling.
- Use structured tools or application services for actual changes.
- Ask clarifying questions when needed.
- Confirm sensitive or consequential changes.
- Maintain a consistent conversation context.

Expected outcome:

Users can manage their plans through natural language.

Demo script:

Ask Yadi to reschedule a task, increase its priority, and mark another task as complete. Verify that the underlying data changes correctly.

## M07 — User preferences and personal memory

Objectives:

- Store explicit user preferences.
- Introduce user-controlled memory.
- Retrieve relevant context.
- Separate structured task data from conversational memory.
- Support viewing, editing, and deleting saved memories.
- Apply appropriate retention and privacy rules.

Expected outcome:

Yadi becomes more personalized without losing user control.

Demo script:

Save a preferred working time, ask Yadi to plan a day, inspect the preference used, update it, and verify the changed behavior.

## M08 — Calendar integration and advanced planning

Objectives:

- Integrate a supported external calendar.
- Handle authorization and revoked access.
- Synchronize events safely.
- Prevent accidental duplicates.
- Detect synchronization conflicts.
- Improve weekly planning and recurring schedules.

Expected outcome:

Yadi can coordinate internal tasks with authorized external calendar events.

Demo script:

Connect a test calendar, import an event, generate a schedule around it, and demonstrate conflict handling.

## M09 — Voice-first interaction

Objectives:

- Add speech input.
- Convert speech into usable text.
- Provide understandable feedback during processing.
- Handle transcription errors.
- Allow correction before committing ambiguous tasks.
- Evaluate voice response capabilities separately.

Expected outcome:

Users can capture tasks by speaking instead of typing.

Demo script:

Speak a task request, review the transcription and extracted details, correct a mistake, and save the task.

## M10 — Proactive assistance and product refinement

Objectives:

- Identify relevant scheduling risks.
- Suggest appropriate next actions.
- Add configurable proactive briefings.
- Reduce unnecessary interruptions.
- Improve accessibility and usability.
- Measure performance and reliability.
- Conduct a security and privacy review.

Expected outcome:

Yadi becomes a more proactive assistant while remaining predictable and user-controlled.

Demo script:

Create an overloaded schedule, demonstrate a useful warning and proposed adjustment, and show how the user can accept or reject it.

## M11 — Production readiness and release

Objectives:

- Complete security testing.
- Test backup and restoration.
- Validate monitoring and error reporting.
- Verify migration and rollback procedures.
- Test performance under realistic workloads.
- Configure production deployment.
- Review privacy policies and consent flows.
- Complete release documentation.

Expected outcome:

A release candidate with verified functionality, documented operational procedures, and clearly stated limitations.

Demo script:

Demonstrate the production-style deployment, health checks, critical user workflows, error handling, backup strategy, and release checklist.

Important: These milestones are a starting roadmap, not permission to build all of them at once. Complete one milestone at a time and adjust scope based on verified results.

---

# 8. Technology Selection and Architecture

The technology stack must be finalized after a short, documented evaluation.

A reasonable initial proposal is:

## Frontend

- React with TypeScript.
- Next.js if server-rendering, routing, and its deployment model provide a clear benefit; otherwise use a simpler React setup.
- A consistent component system.
- A small, maintainable design token system.
- Responsive layouts and accessible interactions.

Do not introduce multiple frontend frameworks.

## Backend

- Node.js with TypeScript.
- A modular backend using a framework selected through a brief evaluation.
- REST APIs for the initial application unless another interface has a clear advantage.
- Schema-based request and response validation.
- Centralized error handling.
- Clear service boundaries.

Prefer a modular monolith initially instead of unnecessary microservices.

## Database

- PostgreSQL for users, tasks, schedules, preferences, reminders, and other structured application data.
- Versioned database migrations.
- Foreign-key constraints and appropriate indexes.
- Transactions for operations that must remain consistent.
- An explicit strategy for task history and audit events.

## AI integration

- Use a backend-only AI provider abstraction.
- Keep provider API keys on the server.
- Validate structured outputs before using them.
- Set timeouts and sensible retry limits.
- Handle rate limits and unavailable providers.
- Track model usage and cost.
- Allow providers to be replaced without rewriting the entire application.

Do not depend on an AI model for deterministic business rules.

## Background processing

Choose a reliable job-processing approach appropriate for the deployment environment.

Possible approaches include a durable database-backed queue or a dedicated queue system when justified.

The architecture must support:

- Delayed jobs.
- Retries with backoff.
- Idempotent processing.
- Job status and failure tracking.
- Safe rescheduling and cancellation.
- Recovery after worker restarts.

Do not assume that a simple in-memory timer is sufficient for production reminders.

## Optional later technologies

Evaluate these only when justified:

- Redis.
- Vector search.
- Dedicated job queues.
- Mobile application frameworks.
- WebSocket or server-sent event updates.
- External calendar integrations.
- Advanced scheduling optimization.
- Speech recognition and speech synthesis services.

Do not add a technology merely because it is popular.

## Architecture boundaries

Keep these responsibilities separate:

- User interface.
- API and transport.
- Authentication and authorization.
- Task application services.
- AI interpretation.
- Scheduling engine.
- Notification and background-job processing.
- Persistence.
- External integrations.
- Observability.

The AI should request actions through validated application services. It should not receive unrestricted database access or arbitrary execution privileges.

---

# 9. Repository Structure and Code Organization

Design a repository that a new developer can understand without studying every file.

Use a simple structure such as the following if the chosen stack supports it.

```text
yadi/
├── README.md
├── CONTRIBUTING.md
├── .gitignore
├── .editorconfig
├── .env.example
├── package.json
├── docs/
│   ├── 01-product/
│   ├── 02-requirements/
│   ├── 03-architecture/
│   │   └── ADR/
│   ├── 04-engineering/
│   ├── 05-planning/
│   ├── 06-agent/
│   └── milestones/
├── apps/
│   └── web/
│       ├── src/
│       │   ├── app/
│       │   ├── components/
│       │   │   ├── ui/
│       │   │   └── shared/
│       │   ├── features/
│       │   │   ├── tasks/
│       │   │   ├── schedule/
│       │   │   ├── reminders/
│       │   │   ├── assistant/
│       │   │   └── settings/
│       │   ├── lib/
│       │   ├── hooks/
│       │   ├── styles/
│       │   └── types/
│       └── tests/
├── services/
│   └── api/
│       ├── src/
│       │   ├── modules/
│       │   │   ├── tasks/
│       │   │   ├── scheduling/
│       │   │   ├── reminders/
│       │   │   ├── assistant/
│       │   │   ├── preferences/
│       │   │   └── users/
│       │   ├── infrastructure/
│       │   ├── middleware/
│       │   ├── config/
│       │   └── app.ts
│       └── tests/
├── packages/
│   ├── shared-types/
│   ├── validation/
│   └── shared-config/
├── workers/
│   └── notifications/
├── database/
│   ├── migrations/
│   └── seeds/
├── scripts/
└── tests/
    ├── integration/
    └── e2e/
```

This is a proposed logical layout, not a requirement to create every directory immediately.

Start with the smallest structure that supports the current milestone. Add packages, applications, or workers only when they have a clear responsibility.

If a separate worker process is not yet necessary, document how background processing will be introduced later.

## Organization rules

1. Organize code around business features and responsibilities.
2. Keep UI components separate from application logic.
3. Keep database queries out of React components.
4. Keep scheduling rules out of route handlers.
5. Keep AI-provider-specific code behind an adapter.
6. Keep notification delivery separate from notification scheduling.
7. Share types and validation schemas where appropriate.
8. Avoid circular dependencies.
9. Avoid enormous files that mix multiple responsibilities.
10. Avoid creating a file for every trivial expression without a clear benefit.
11. Use descriptive names instead of cryptic abbreviations.
12. Add a README to any complex module explaining its purpose and public interface.
13. Keep configuration centralized and validated.
14. Do not commit secrets or real user data.
15. Update the directory documentation when the architecture changes.

The objective is not to create the maximum number of folders. It is to make responsibilities obvious and changes predictable.

---

# 10. Code Quality and Maintainability Standards

Code must be written so that another developer can read, debug, test, and extend it.

## 10.1 Modularity

Every module should have a clear responsibility.

For example, task management should not also contain the complete AI integration, scheduling algorithm, notification transport, and frontend presentation.

Use clear interfaces between modules.

Avoid unnecessary abstractions, premature generic frameworks, excessive design patterns, and duplicated business rules.

## 10.2 Function and file size

Prefer small functions that do one understandable thing.

As a working guideline:

- Aim for functions of approximately 10–40 lines when practical.
- Review functions that regularly exceed 50 lines.
- Split large components into meaningful subcomponents.
- Split complex modules when responsibilities become mixed.
- Do not split code mechanically just to meet a line limit.

These are review guidelines, not absolute rules. A short function can still be poorly designed, and a longer function may sometimes be justified.

## 10.3 Naming

Use consistent, descriptive naming conventions.

Examples:

- `createTask`
- `scheduleReminder`
- `generateDailySchedule`
- `extractTaskFromMessage`
- `NotificationDeliveryService`

Avoid unclear names such as `doStuff`, `handleEverything`, or `processData` when a more precise name is possible.

## 10.4 Types and validation

Use TypeScript strict mode where appropriate.

Validate external inputs at system boundaries.

Do not assume that AI-generated output, user input, external APIs, environment variables, or database data are always valid.

Prefer explicit data models and schemas over loosely typed objects.

## 10.5 Error handling

Errors should be handled deliberately.

- Return consistent API error responses.
- Show useful messages to users without exposing internal details.
- Log diagnostic information safely.
- Do not silently swallow errors.
- Distinguish validation failures, authorization errors, external-provider failures, and unexpected internal errors.
- Ensure background jobs can fail without corrupting unrelated operations.

## 10.6 Comments and documentation

Write comments to explain why non-obvious decisions exist.

Do not add comments that merely repeat the code.

Document public interfaces, complicated algorithms, security assumptions, and important business rules.

## 10.7 Dependencies

Before adding a dependency, determine:

- Why it is needed.
- Whether an existing dependency can solve the problem.
- Its maintenance status.
- Its security implications.
- Its bundle-size or runtime cost.
- Its license compatibility.
- Whether a simpler implementation is sufficient.

Pin and update dependencies responsibly.

## 10.8 Technical debt

Record intentional shortcuts and known limitations.

Do not conceal temporary solutions as production-ready implementations.

Every significant technical-debt item should have an explanation, impact, and recommended follow-up.

---

# 11. UI/UX Design Standards

The application must be easy for a first-time user to understand.

Use simple language, clear navigation, consistent interactions, and predictable behavior.

## 11.1 Visual direction

Use a clean, minimal, premium design.

Preferred characteristics:

- White or neutral backgrounds.
- A restrained palette with no more than three primary brand colors.
- Clear typography.
- Strong visual hierarchy.
- Consistent spacing.
- Simple icons with clear meaning.
- Subtle borders and shadows only when useful.
- Minimal decorative elements.
- No gradients by default.
- No unnecessary animation.
- No excessive text or oversized dashboard cards.

Do not imitate another product blindly. Use these principles to create a coherent identity for Yadi.

## 11.2 Initial screens

Plan the MVP around a small set of understandable screens.

### Today dashboard

Show:

- Today's schedule.
- Upcoming tasks.
- The next important action.
- Overdue or at-risk tasks when relevant.
- A prominent way to tell Yadi what needs to be done.

Avoid filling the dashboard with statistics that do not help users decide what to do next.

### Task management

Users should be able to:

- View tasks.
- Add and edit tasks.
- Change priority.
- View deadlines and duration.
- Complete, cancel, or reschedule tasks.
- Understand the current status.

### Schedule view

Display the user's planned activities in a clear timeline or other appropriate layout.

Make fixed commitments and flexible tasks distinguishable.

Provide useful empty states and clear conflict indicators.

### Assistant interface

Allow natural-language interaction through a simple conversation interface.

Show what Yadi understood and what action it performed.

When necessary, present a confirmation or clarification question.

Do not make every action require a long conversation.

### Settings

Provide understandable controls for:

- Timezone.
- Working hours.
- Reminder preferences.
- Notification permissions.
- Personal scheduling preferences.
- Privacy and saved memory, as these features become available.
- Connected services.

## 11.3 Usability requirements

Every interactive screen should account for:

- Loading states.
- Empty states.
- Error states.
- Success feedback.
- Form validation.
- Keyboard navigation.
- Focus indicators.
- Appropriate contrast.
- Accessible labels.
- Mobile and desktop layouts.
- Confirmation for destructive actions.
- Clear undo or recovery paths where practical.

Do not rely on color alone to communicate priority or errors.

Use accessible controls, readable text, and predictable keyboard behavior.

## 11.4 User experience rules

1. Make the primary action obvious.
2. Avoid unnecessary steps.
3. Use familiar interaction patterns.
4. Keep labels short and understandable.
5. Show useful information before secondary details.
6. Do not overwhelm users with AI-generated explanations.
7. Allow users to correct AI mistakes easily.
8. Explain uncertainty honestly.
9. Never display fake success messages.
10. Preserve user input when a recoverable error occurs.
11. Avoid excessive confirmation dialogs for routine actions.
12. Request confirmation for high-impact or difficult-to-reverse actions.
13. Use consistent buttons, forms, menus, and feedback patterns.

## 11.5 UI component strategy

Create reusable components when repeated patterns justify them.

Examples:

- Buttons.
- Form fields.
- Dialogs.
- Toast notifications.
- Task cards or rows.
- Priority indicators.
- Empty-state components.
- Loading indicators.
- Confirmation dialogs.

Avoid duplicating similar UI patterns across features.

However, do not force unrelated interfaces into one overcomplicated component with dozens of optional properties.

---

# 12. AI Engineering Rules

AI is an important part of Yadi, but it must operate within reliable application boundaries.

## 12.1 Separate interpretation from execution

The AI may interpret a user's message and propose structured actions.

For example:

"Move my assignment to Thursday afternoon."

The model should produce a validated intent such as:

- Action: reschedule task.
- Target: assignment.
- Requested date: Thursday.
- Preferred period: afternoon.

The application must then:

1. Resolve which task the user means.
2. Validate the requested time.
3. Check scheduling constraints.
4. Ask for clarification if needed.
5. Apply the change through an authorized service.
6. Verify the result.
7. Communicate the actual outcome.

Never let a language model bypass application validation or directly execute arbitrary SQL or shell commands.

## 12.2 Structured outputs

Define schemas for important AI operations.

Examples:

- Task extraction.
- Priority recommendation.
- Schedule adjustment proposal.
- Task reference resolution.
- Clarification requests.
- Memory suggestions.

Validate outputs before they influence persistent state.

Handle missing fields, invalid dates, contradictory information, low confidence, and malformed responses.

## 12.3 Model independence

Keep model-specific prompts, SDKs, and API calls inside an AI integration layer.

The rest of the application should depend on stable internal interfaces.

This makes it possible to change models or providers without rewriting task management and scheduling.

## 12.4 Cost and latency

Measure model usage.

Avoid unnecessary model calls for straightforward deterministic operations.

Use smaller or cheaper models when appropriate and validate whether they meet quality requirements.

Set sensible timeouts, token limits, rate limits, and usage budgets.

Do not send the user's entire task history to the model for every request when only a small amount of context is needed.

## 12.5 Evaluation

Create a test set containing realistic examples, including:

- Clear task requests.
- Ambiguous dates.
- Multiple tasks in one message.
- Conflicting instructions.
- Incorrect transcription.
- Task references that match multiple records.
- Requests that exceed available time.
- Requests for actions the system cannot perform.

Measure extraction accuracy, unnecessary clarification, invalid action rates, and scheduling correctness.

Do not rely only on manually trying a few prompts.

---

# 13. Scheduling and Reminder Reliability

This area is central to Yadi and must receive particular engineering attention.

## 13.1 Scheduling invariants

Define and test rules such as:

- A task cannot be scheduled outside a permitted time window.
- Fixed appointments must not be moved without authorization.
- Scheduled tasks must not overlap in ways prohibited by the scheduling rules.
- Task duration must be considered.
- Deadlines must be respected whenever feasible.
- Dependencies must be respected.
- An impossible schedule must be reported rather than fabricated.
- Time calculations must use the correct timezone.

Define how the application handles partial completion, tasks longer than available time, and conflicts between user preferences and deadlines.

## 13.2 Reminder lifecycle

Every reminder should have a clear state, such as:

- Scheduled.
- Processing.
- Delivered.
- Failed.
- Cancelled.

Define the final state model and transitions in the architecture documentation.

Use idempotency controls so retrying a job does not accidentally produce duplicate actions or duplicate records.

Record delivery attempts and errors.

A successful job execution is not automatically proof that a notification reached the user's device. Distinguish server processing from provider delivery confirmation and actual device presentation.

## 13.3 Recovery

The system must handle:

- Backend restarts.
- Worker restarts.
- Temporary database outages.
- AI-provider outages.
- Notification-provider failures.
- Missed processing windows.
- Duplicate job delivery.
- Changes to task deadlines.
- Cancellation of tasks with scheduled reminders.

Define recovery behavior before declaring the reminder system production-ready.

---

# 14. Security, Privacy, and Data Ownership

Treat personal information as an important responsibility.

The assistant may eventually process schedules, private conversations, work information, and personal preferences.

Required principles:

- Secure authentication and authorization.
- Strict separation of users' data.
- Server-side secret management.
- Input validation.
- Rate limiting where appropriate.
- Secure session handling.
- Protection against common web vulnerabilities.
- Encrypted transport.
- Appropriate protection of stored data and backups.
- Minimal collection of personal information.
- Clear retention and deletion policies.
- Safe logging that excludes unnecessary personal content.
- Explicit authorization for external integrations.
- Auditable handling of important actions.

For voice capabilities, distinguish raw audio, transcripts, and extracted structured information. Explain retention and deletion policies before collecting recordings.

Never store passwords, API keys, or production secrets in source control.

Use synthetic data for development and demonstrations.

If the user requests deletion of their information, define how the system handles associated records, saved memories, logs, and backups.

Security and privacy must be considered in every milestone, not added only at the end.

---

# 15. Performance and Production Quality

Yadi should be designed to remain responsive as usage grows.

Do not confuse scalability with introducing microservices early.

Start with a well-structured modular application and measure real performance.

## 15.1 Performance practices

- Fetch only the data required by each screen.
- Add database indexes based on real query patterns.
- Avoid repeated database queries and N+1 access patterns.
- Use pagination for growing lists.
- Avoid unnecessarily large frontend bundles.
- Load nonessential features when needed.
- Cache only where correctness and invalidation are understood.
- Avoid unnecessary polling and expensive background work.
- Set timeouts and resource limits for external calls.
- Avoid running heavy AI tasks inside ordinary request handlers when asynchronous processing is more appropriate.
- Measure and optimize slow queries.
- Use efficient database transactions.
- Avoid unbounded memory or conversation-history growth.

## 15.2 Performance targets

During planning, define measurable targets for:

- Initial page loading.
- API response times.
- Task-list queries.
- Schedule generation.
- AI response latency.
- Reminder processing delay.
- Database resource usage.
- Concurrent workload.
- Error rate.

Establish initial targets based on the MVP's expected workload and revise them with evidence.

Do not claim the product is optimized merely because the code appears clean.

## 15.3 Production operations

Plan for:

- Separate development, testing, staging, and production configurations.
- Database migrations.
- Health checks.
- Structured logs.
- Error monitoring.
- Safe deployment.
- Backup and restoration.
- Rollback procedures.
- Dependency updates.
- Secret rotation.
- Operational documentation.
- Usage and cost monitoring.

Avoid overengineering the initial deployment, but do not leave production-critical concerns undocumented.

---

# 16. Testing and Quality Gates

Testing must be part of every milestone.

## Unit tests

Test isolated business rules, validation, scheduling calculations, and utility functions.

## Integration tests

Test database operations, API behavior, authorization, AI adapters, and background-job processing.

## End-to-end tests

Test critical user journeys through the actual application interface.

Examples:

- Create a task.
- Extract a task from natural language.
- Generate a schedule.
- Reschedule a task.
- Complete a task.
- Trigger a reminder.
- Handle a failed AI request.

## Security tests

Test access control, input validation, secret handling, user-data isolation, and other relevant risks.

## Accessibility tests

Verify keyboard navigation, focus management, contrast, labels, and common screen-reader interactions.

## Performance tests

Measure important paths using realistic sample data and representative workloads.

## Required quality gates

Before completing a milestone:

1. Type checking passes.
2. Linting passes.
3. Formatting checks pass.
4. Relevant unit tests pass.
5. Relevant integration tests pass.
6. End-to-end tests pass where applicable.
7. Database migrations are verified.
8. No known critical security issue remains unresolved.
9. Documentation matches the implementation.
10. The demonstration can be completed using the documented instructions.

If a gate cannot be completed, document why and identify the impact. Do not mark the milestone fully verified without disclosing the gap.

---

# 17. Milestone Completion and Demonstration

Every milestone must produce a working, understandable result.

I want to understand what has been built, why it was built, how it works, and how I can demonstrate it to someone else.

For every milestone, create a `DEMO_SCRIPT.md` with the following sections:

### A. What we built

Explain the milestone in simple English.

### B. Why it matters

Describe the user problem the feature solves.

### C. How it works

Explain the flow from user interaction to backend processing, data storage, and the final result.

### D. What I need before the demo

List prerequisites, environment variables, test accounts, sample data, and required services.

### E. Exact demonstration steps

Write numbered instructions that I can follow without guessing.

### F. Expected results

Explain what should appear or happen at each step.

### G. How to verify it

Include relevant tests, database checks, logs, or observable behavior.

### H. Known limitations

Explain what has not been implemented and what could fail.

### I. Suggested presentation script

Provide a short spoken explanation that I can use when presenting the milestone to a supervisor, colleague, or potential investor.

Use simple, clear English. Explain technical terms when they are necessary.

Never create a demo script that claims a feature works when the implementation does not support it.

---

# 18. Persistent Agent Progress and Resume System

This is a mandatory requirement.

I may restart my computer, close the terminal, lose a conversation, change agents, or return to development after several days.

The agent must be able to resume work without rereading the entire codebase or repeating completed tasks.

## 18.1 Main progress file

Maintain:

`docs/06-agent/AGENT_PROGRESS.md`

Keep it concise, factual, and updated after every significant work session.

It must include:

### Project identity

- Project: Yadi.
- Current project phase.
- Current milestone.
- Overall status.

### Current position

- What was completed.
- What is currently being implemented.
- Exact next task.
- Current blocker, if any.
- Last verified successful checks.

### Relevant files

List only the files that matter for the current task and briefly explain their roles.

### Current decisions

Record relevant technical decisions or link to the appropriate ADR.

### Known problems

List unresolved issues, failing tests, incomplete requirements, and temporary workarounds.

### Resume instructions

Provide the exact next actions the next agent should perform.

For example:

"Resume M03. Read this progress file, then read the M03 PLAN.md and TASKS.md. Inspect the task extraction service and its associated tests. The schema validation is complete, but date ambiguity tests remain. Run the focused test suite, address failures, and update the milestone documents. Do not restart completed M01 or M02 work."

Do not use vague instructions such as "continue development."

## 18.2 Agent startup procedure

At the beginning of every new session:

1. Read `docs/06-agent/AGENT_PROGRESS.md`.
2. Read `docs/06-agent/AGENT_RULES.md`.
3. Read the current milestone's `README.md`, `PLAN.md`, and `TASKS.md`.
4. Read only the relevant architecture documents and code needed for the next task.
5. Check the Git working tree and current branch.
6. Check for uncommitted changes before modifying files.
7. Run the relevant tests or checks when necessary to establish the current state.
8. Confirm the exact next action before proceeding.

Do not begin by recursively reading every file in the repository.

Do not overwrite uncommitted user work.

If the progress file is outdated or contradicts the actual code, inspect the evidence, reconcile the differences, and update the file before proceeding.

## 18.3 Agent shutdown procedure

Before ending every work session:

1. Update `AGENT_PROGRESS.md`.
2. Update milestone task checklists.
3. Record newly discovered issues.
4. Record decisions that affect future work.
5. Update documentation affected by implementation changes.
6. Record the latest verified test results.
7. Identify the exact next action.
8. Identify any files that remain incomplete.
9. Report the actual state to me.

Do not claim that progress has been saved if the file was not successfully updated.

## 18.4 Protect continuity

Do not depend exclusively on conversation history, hidden agent memory, or terminal history.

The repository's documented state must be sufficient for another authorized agent to continue the project.

Use Git commits at sensible checkpoints, but never discard user changes or create commits automatically if the working environment's workflow requires approval.

---

# 19. Git and Change Management

Use version control from the beginning.

Recommended practices:

- Maintain a clear main branch.
- Use short-lived feature branches where appropriate.
- Write meaningful commit messages.
- Keep commits focused.
- Avoid committing generated files unnecessarily.
- Review diffs before making broad changes.
- Never force-push or reset user work without explicit authorization.
- Keep environment secrets out of Git.
- Document database migrations and breaking changes.
- Use tags or releases for important verified milestones when appropriate.

Before a major change, explain the intended change, expected impact, and verification plan.

Avoid rewriting working modules simply because a different approach seems more fashionable.

---

# 20. Research and Decision-Making

Research is required when important decisions depend on current technical facts, provider limitations, pricing, security guidance, or integration requirements.

Use official documentation as the primary technical source.

For major decisions:

1. State the problem.
2. Identify reasonable options.
3. Compare advantages and disadvantages.
4. Consider complexity, performance, cost, security, maintainability, and lock-in.
5. Recommend one option.
6. Explain the recommendation in plain English.
7. Record the decision in an Architecture Decision Record.

Do not spend excessive time researching minor decisions that can be reversed easily.

If information is uncertain, label it as an assumption.

Do not fabricate benchmark results, API capabilities, package features, or successful integrations.

---

# 21. Product Success Metrics

Define measurable indicators that can be evaluated as the system develops.

Potential metrics include:

- Accuracy of natural-language task extraction.
- Percentage of schedules that satisfy hard constraints.
- Frequency of scheduling conflicts.
- Percentage of reminders processed within their target window.
- Duplicate reminder rate.
- Task rescheduling success rate.
- AI action correction rate.
- User acceptance of priority recommendations.
- Task completion and rescheduling rates.
- Average time needed to create a task.
- API latency.
- Application error rate.
- AI cost per interaction.
- User satisfaction.

Define each metric precisely, including how it is measured and what data is required.

Do not collect more personal data than necessary for evaluation.

Avoid claiming that Yadi improves productivity without evidence.

---

# 22. Project Governance and Definition of Done

A milestone is complete only when its documented scope is implemented and verified.

The definition of done includes:

- Requirements satisfied.
- Acceptance criteria verified.
- Relevant tests passing.
- Code reviewed for maintainability.
- Security implications considered.
- UI/UX states implemented.
- Documentation updated.
- Demo script verified.
- Known limitations recorded.
- Progress file updated.
- No hidden blocker preventing the next milestone.

A feature is not complete merely because a screen exists or a code file was written.

A working feature must behave correctly, persist data when required, handle errors, and meet its acceptance criteria.

If something is only a prototype, label it clearly.

---

# 23. How You Must Work With Me

I want to understand the product while it is being built.

Do not assume I already understand every architectural choice or technical term.

When reporting progress:

1. Explain what was done.
2. Explain why it was necessary.
3. Explain how it works in simple English.
4. Explain how to run or test it.
5. Explain what remains.
6. Identify decisions that require my input.
7. Point to the relevant documentation files.

Do not overwhelm me with unnecessary technical detail in routine updates. Keep detailed technical documentation in the repository and summarize the important parts in your messages.

If a proposed implementation is significantly more complex than necessary, explain a simpler alternative.

If my requested approach would create a serious security, reliability, or maintenance problem, explain the issue and recommend a better approach.

Do not silently change the product vision or introduce major features without documenting the reason.

---

# 24. Your First Assignment

Begin by executing the discovery and documentation phase only.

Do not start implementing the complete application.

Follow this order:

### Step 1 — Inspect the environment

- Determine whether a repository already exists.
- Inspect its current state without overwriting existing work.
- Identify existing files, tools, and configuration relevant to the project.
- If the repository is empty, establish a minimal starting point.
- If an existing application is present, document its state before changing anything.

### Step 2 — Review this master brief

Translate the product vision into a structured list of capabilities, constraints, assumptions, and non-goals.

Identify any ambiguous or conflicting requirements.

### Step 3 — Research important technical choices

Evaluate a suitable frontend, backend, database, AI integration approach, and background-job strategy.

Favor a simple, maintainable architecture that can support the long-term product without unnecessary complexity.

### Step 4 — Write the foundational documentation

Create the product vision, product requirements, SRS, user flows, initial architecture, security and privacy plan, testing strategy, and engineering standards.

### Step 5 — Establish the roadmap

Define milestone boundaries, dependencies, deliverables, acceptance criteria, and verification requirements.

Identify the smallest useful MVP and separate it from future capabilities.

### Step 6 — Establish the repository structure

Create only the directories and files justified by the approved plan.

Make it obvious where application code, tests, migrations, documentation, and agent progress records belong.

### Step 7 — Establish agent continuity

Create `AGENT_RULES.md`, `AGENT_PROGRESS.md`, `DECISION_LOG.md`, `KNOWN_ISSUES.md`, and `SESSION_LOG.md`.

Write the startup and shutdown procedures into the agent rules.

### Step 8 — Review the plan with me

Provide a concise report explaining:

- What Yadi will become.
- What the first version will contain.
- The proposed technology stack.
- The milestone roadmap.
- The repository structure.
- The main risks.
- Important decisions requiring my approval.
- What will happen in the first implementation milestone.

### Step 9 — Stop at the appropriate boundary

Once the foundational documentation and plan are complete, stop before implementing product features.

Ask for my review of the plan. Incorporate feedback and update the relevant documents before starting the first implementation milestone.

If the environment requires a different workflow or cannot create some of the requested documents, explain the limitation and propose the closest practical alternative.

---

# Final Instruction

Treat Yadi as a long-term product that deserves thoughtful engineering.

The objective is not to generate the largest amount of code as quickly as possible. The objective is to build the right system in the right order, with clear documentation, dependable behavior, a clean user experience, manageable costs, and a codebase that remains understandable as the product grows.

**Document first. Plan carefully. Build one milestone at a time. Test what you build. Demonstrate every milestone. Record every important decision. Maintain a reliable resume point. Never sacrifice correctness, usability, security, or maintainability for unnecessary speed.**

Start with the discovery and documentation phase, and report your findings before beginning product implementation.