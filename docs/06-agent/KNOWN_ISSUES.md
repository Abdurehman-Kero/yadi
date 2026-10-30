# Known Issues

| ID | Issue | Impact | Workaround / follow-up |
|---|---|---|---|
| KI-002 | `psql` not installed locally. | Postgres must run via Docker (available). | Use Docker Compose in M01. |
| KI-003 | No docx renderer (LibreOffice/pandoc/Poppler) here; skill's render helper fails on Windows. | SRS.docx / report layout and TOC not visually verified. | Owner opens in Word and updates TOC field; or install LibreOffice. |
| KI-004 | ~~Library versions unverified~~ — checked against PyPI/npm 2026-10-27 (registry metadata only). Install-compatibility and release-note review still pending at scaffold time. | Next 16, TS 7, Vitest 5 are new majors. | Fall back one major if blocked; log it. |
| KI-006 | ~~Docker/uv missing~~ | Resolved 2026-10-30 | — |
| KI-005 | Docx generator scripts live in the session scratchpad, not the repo. | Regenerating SRS.docx requires rewriting the script. | Decide whether to keep a `scripts/docs/` generator (M01). |
| KI-007 | `localhost` resolves to IPv6 first and stalls ~200 s on this machine. | Slow DB connections if used. | Use `127.0.0.1` (documented). |
| KI-008 | No browser-level check of the page yet. | UI appearance unverified. | Playwright E2E from M02. |

Resolved: KI-001 (spec truncation) — full text found in `writing-block.md`.
