# M03 Completion Report

**Status: COMPLETE, with a caveat.** Evaluated on the real model on 2026-10-31: 20/20 after prompt tuning, median 1.6 s. The prompts were tuned on the same made-up messages, so this does not predict real-world accuracy. See the M06 report.

## Provider change
The owner chose Gemini instead of Anthropic (D-012). Only the adapter, settings, prices and the provider notice changed; the service, endpoint and screens did not.

## Delivered
Extraction endpoint, Gemini adapter behind an interface, usage and cost records (migration 0003), daily limit, Tell Yadi review screen, manual fallback, 20-case evaluation set, scorer and live-run script.

## Verified (2026-10-30, no real AI calls)
- `node scripts/run.mjs all`: 10 of 10 PASS. pytest 111, vitest 18, Playwright 10.
- The real Google SDK was exercised against a fake HTTP transport: request shape, parsing, blocked, cut-off and invalid answers, API errors, invalid key, timeouts.
- Nothing is saved by extraction; message text is absent from usage rows and logs (tests).
- The no-key fallback was run in a real browser against the real API.
- The review screen was tested in a real browser with a mocked AI answer, and viewed in a screenshot before the provider change.
- `npm audit --omit=dev` and `pip-audit`: no known vulnerabilities.

## Not verified
- Accuracy on real people's messages, and cost and speed at real use.
- Free-tier request limits: Google shows them only in AI Studio.
- The API-error shapes in the tests are built from Google's documented format, not captured from live traffic.

## Privacy finding
Google's pricing page says free-tier content is used to improve its products; paid-tier content is not. Real users' messages must not go through the free tier. Development and demos use synthetic data only, and paid billing is required before real users (KI-012).

## Deviations
- Dates: the model returns local time and the application converts it (see PLAN.md).
- No repair retry: a bad answer goes straight to the manual form.
- The code calls `generate_content`. Google's structured-output page now leads with its newer Interactions API; `generate_content` is in the installed SDK and was chosen because its request and usage fields could be inspected. Revisit if the live run shows a problem.
- `gemini-3.8-flash` prices double on 2027-01-01; the price table will need updating if that model is chosen.
- Also improved: browser tests build in `.next-e2e`, so they can run while `npm run dev` is open.

## Remaining
Paid billing and a review of Google's data terms before real users (KI-012).
