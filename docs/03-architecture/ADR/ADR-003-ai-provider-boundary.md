# ADR-003: AI provider abstraction

Status: **Accepted 2026-10-27**. Provider changed by the owner to Google Gemini on 2026-10-30. Default model `gemini-3.5-flash-lite`; final choice follows the M03 evaluation. Free-tier content is used by Google to improve its products, so real users require paid billing.

## Decision
All LLM access goes through `LlmClient.generate_structured(schema, system, prompt)` inside `yadi/modules/assistant/ai/` (Python, `Protocol` interface). Provider: Google Gemini (`gemini_client.py`). Config selects provider/model. Calls are server-side, with timeout, one retry, rate limits, and usage logging. Outputs validated with Pydantic models; invalid output goes straight to the manual fallback.

## Alternatives rejected
Calling an SDK directly from feature code (lock-in); agent frameworks (unnecessary complexity); tool-calling that writes DB directly (violates the safety rule).

## Consequences
Easy to swap models; a fake `LlmClient` makes tests deterministic.
