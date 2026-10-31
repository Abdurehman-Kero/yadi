# M03 Plan

## Provider facts (from Google's Gemini API docs, 2026-10-30; SDK `google-genai` 2.34.0)
- Default model `gemini-3.5-flash-lite`, which Google recommends for fast, low-cost, high-volume work. Free tier available; paid $0.30 / $2.50 per million input / output tokens.
- `gemini-3.8-flash` is the stronger option: free tier available; paid $0.75 / $3.75, doubling on 2027-01-01. Selected with `AI_MODEL`.
- Validated JSON through a response schema; Yadi validates again with Pydantic.
- **Free-tier content is used to improve Google's products; paid-tier content is not.**

## Decisions
- **Provider:** Gemini, chosen by the owner (D-012).
- **Dates (changes AI_DESIGN):** the model receives the current local date and timezone and returns local wall-clock time plus the phrase it came from. Application code validates and converts it. A hand-written resolver for phrases like "next Friday evening" would duplicate work and still fail on unusual wording; the user reviews every draft, with the original phrase shown.
- **Timeouts:** 25 s per attempt, two attempts; the Next.js proxy timeout is raised to match.
- **No key is not a crash:** the app runs normally without a key, and capture falls back to the manual form.

## Steps
1. Add SDK; migration 0003 `ai_usage`; config.
2. Interface, fake client, provider adapter (tested through a fake HTTP transport).
3. Extraction service, endpoint, tests.
4. UI capture flow, component and browser tests.
5. Evaluation set, scorer, manual live runner.
6. Gates, docs, report.
