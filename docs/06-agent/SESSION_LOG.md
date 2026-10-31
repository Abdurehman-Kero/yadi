# Session Log

## 2026-10-27 — Session 1
- Received master specification (truncated at section 16).
- Checked environment; project folder empty.
- Created the continuity, planning, and initial product documents listed in AGENT_PROGRESS.md.
- No application code written (by design for M00).

## 2026-10-27 to 2026-10-30 — Sessions 1–2
- M00 approved. Verified library versions. Wrote M01 docs. Installed uv, git init (owner commits). Built and verified M01 (9/9 gates, live run incl. DB-down case). Found and fixed: IPv6 `localhost` stall, a mypy unused-ignore after last edit (caught by rerunning gates).

## 2026-10-30 (continued)
- Owner committed M01 (035c673) and dropped Tartiiba (D-010). Built and verified M02: 10/10 gates. Browser tests caught two bugs that unit tests could not (UTC not selectable, blocked dev resources). Not committed: the owner commits.

## 2026-10-30 (M03)
- Built M03 with no live AI calls: 10/10 offline gates. The fake-transport test showed the SDK rejects cut-off answers while parsing. Blocked on owner key and spending approval. M02 and M03 uncommitted.
- Owner switched the AI provider to Gemini. Adapter, settings and prices replaced; 10/10 offline gates pass. Still no live call.

## 2026-10-30/31 (M04)
- Owner skipped M03's test (D-013) and asked for a redesign. Built engine, schedule API, Today and Schedule screens, new design. First live Gemini call succeeded. Screenshots exposed a misleading overdue message, fixed. M02 to M04 uncommitted.

## 2026-10-31 (M05)
- Owner approved M04, moved sign-in out of M05, asked for modal forms. Built reminders, worker, notifications, browser alerts and modals. Tests caught a push-key naming bug and a focus-return bug. Real alerts untested. M05 uncommitted.
