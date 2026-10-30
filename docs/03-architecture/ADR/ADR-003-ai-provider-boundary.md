# ADR-003: AI provider abstraction

Status: **Accepted 2026-10-27**. Provider/model selection and pricing review deferred to M03 (must use official docs then).

## Decision
All LLM access goes through `LlmClient.generateStructured(schema, prompt, opts)` inside `yadi/modules/assistant/ai/` (Python, `Protocol` interface). Default provider: Anthropic Claude. Config selects provider/model. Calls are server-side, with timeout, one retry, rate limits, and usage logging. Outputs validated with Pydantic models; invalid output triggers one repair attempt then manual fallback.

## Alternatives rejected
Calling an SDK directly from feature code (lock-in); agent frameworks (unnecessary complexity); tool-calling that writes DB directly (violates the safety rule).

## Consequences
Easy to swap models; a fake `LlmClient` makes tests deterministic.
