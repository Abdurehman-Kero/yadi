# Known Issues

| ID | Issue | Impact | Workaround / follow-up |
|---|---|---|---|
| KI-002 | `psql` not installed locally. | Postgres must run via Docker (available). | Use Docker Compose in M01. |
| KI-003 | No docx renderer (LibreOffice/pandoc/Poppler) here; skill's render helper fails on Windows. | SRS.docx / report layout and TOC not visually verified. | Owner opens in Word and updates TOC field; or install LibreOffice. |
| KI-004 | ~~Library versions unverified~~ — checked against PyPI/npm 2026-10-27 (registry metadata only). Install-compatibility and release-note review still pending at scaffold time. | Next 16, TS 7, Vitest 5 are new majors. | Fall back one major if blocked; log it. |
| KI-006 | ~~Docker/uv missing~~ | Resolved 2026-10-30 | — |
| KI-005 | Docx generator scripts live in the session scratchpad, not the repo. | Regenerating SRS.docx requires rewriting the script. | Decide whether to keep a `scripts/docs/` generator (M01). |
| KI-007 | `localhost` resolves to IPv6 first and stalls ~200 s on this machine. | Slow DB connections if used. | Use `127.0.0.1` (documented). |
| KI-009 | Concurrent edits to one task: last save wins (no version check). | Low with one user. | Revisit when real multi-user arrives. |
| KI-010 | No screen-reader pass; dark mode not viewed or axe-tested. | Possible accessibility gaps. | Do both before the MVP is called done (M10 at latest). |
| KI-011 | No real AI call has been made. Request acceptance, accuracy, speed and cost are unknown. | Tell Yadi may fail in live use; it would fall back to the manual form. | Evaluation run once the owner provides a key. |
| KI-012 | On Gemini's free tier, content is used to improve Google's products. | Not acceptable for real users' personal data. | Synthetic data only until paid billing is on; required before deployment. |
| KI-013 | Every day counts as a working day. | Plans can land on weekends. | Weekday hours in M07. |
| KI-014 | Tell Yadi cannot create fixed events or dependencies; dependencies have no UI. | User ticks the fixed box on the draft; dependencies are API-only. | Add in M06, once the evaluation exists. |
| KI-015 | No real browser alert has been received; headless browsers cannot test it. | Browser alerts may need fixes. In-app notifications are unaffected. | Owner tries DEMO_SCRIPT step 7. |
| KI-016 | The worker is a separate process with nothing to restart it. | No reminders are sent while it is stopped; they wait and arrive late. Settings shows this. | Hosting must keep it running. |

Resolved: KI-001 (spec truncation) — full text found in `writing-block.md`.
