# M00 Demo Script

## A. What we built
The plan for Yadi: what it is, what version 1 does, how it will be built, and how we track progress. No app code yet.

## B. Why it matters
Building a scheduling and reminder product without clear rules leads to rework and unreliable behaviour. The documents fix scope and quality bars first.

## C. How it works
Documents form a chain: vision → requirements (SRS, with IDs) → architecture and decisions (ADRs) → milestones with tests and demos. Agent progress files let any session resume.

## D. Before the demo
Word (to open the .docx files) and a Markdown viewer such as VS Code.

## E. Steps
1. Open docs/05-planning/PLAN_REVIEW_REPORT.docx; walk through sections 1–9.
2. Open docs/02-requirements/SRS.docx; show the requirement tables and acceptance criteria.
3. Open docs/05-planning/ROADMAP.md for the milestones.
4. Open docs/03-architecture/ADR/ to show decisions and the open one (ADR-005).
5. Open docs/06-agent/AGENT_PROGRESS.md to show the resume point.

## F. Expected results
Each document opens, is readable, and matches the descriptions above.

## G. Verify
Check that requirement IDs in the SRS match REQUIREMENTS_TRACEABILITY.md.

## H. Limitations
Everything is a draft awaiting owner approval; technology versions are unverified; performance numbers are targets, not measurements; SRS/report layout was not visually rendered by the agent.

## I. Presentation script
"Yadi is a personal assistant you talk to. It turns what you say into tasks, builds a realistic plan, and reminds you reliably. Before writing code we defined exactly what version 1 does, how success is measured, and the safest way to build it. AI understands you, but a tested engine decides the schedule, so the plan can be trusted. We now build in small verified steps, starting with the project foundation."
