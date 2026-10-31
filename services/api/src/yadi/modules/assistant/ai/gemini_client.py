"""Gemini adapter. The only module allowed to import the Google GenAI SDK (ADR-003)."""

from typing import Any, TypeVar

import httpx
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ValidationError

from yadi.modules.assistant.ai.client import AiError, LlmResult

T = TypeVar("T", bound=BaseModel)

MAX_OUTPUT_TOKENS = 4096
TIMEOUT_MS = 25_000
ATTEMPTS = 2
REFUSED = {
    types.FinishReason.SAFETY,
    types.FinishReason.PROHIBITED_CONTENT,
    types.FinishReason.BLOCKLIST,
    types.FinishReason.SPII,
    types.FinishReason.RECITATION,
}


def _map_api_error(exc: errors.APIError) -> AiError:
    # An invalid key comes back as a 400, not a 401.
    if exc.code in (401, 403) or (exc.code == 400 and "API_KEY" in str(exc)):
        return AiError("auth")
    if exc.code == 429:
        return AiError("rate_limited")
    return AiError("provider")


class GeminiLlmClient:
    def __init__(self, *, api_key: str, model: str, http_client: Any = None) -> None:
        self.model = model
        self._client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=TIMEOUT_MS,
                retry_options=types.HttpRetryOptions(attempts=ATTEMPTS),
                httpx_client=http_client,
            ),
        )

    def generate_structured(self, *, schema: type[T], system: str, prompt: str) -> LlmResult[T]:
        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                    response_mime_type="application/json",
                    response_json_schema=schema.model_json_schema(),
                ),
            )
        except httpx.TimeoutException as exc:
            raise AiError("timeout") from exc
        except httpx.TransportError as exc:
            raise AiError("connection") from exc
        except errors.APIError as exc:
            raise _map_api_error(exc) from exc

        if response.prompt_feedback and response.prompt_feedback.block_reason:
            raise AiError("refused")
        finish = response.candidates[0].finish_reason if response.candidates else None
        if finish in REFUSED:
            raise AiError("refused")
        if finish == types.FinishReason.MAX_TOKENS:
            raise AiError("truncated")
        try:
            output = schema.model_validate_json(response.text or "")
        except ValidationError as exc:
            raise AiError("invalid_output") from exc

        usage = response.usage_metadata
        input_tokens = (usage.prompt_token_count or 0) if usage else 0
        # Thinking tokens are billed as output.
        output_tokens = (
            (usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0) if usage else 0
        )
        return LlmResult(
            output=output,
            model=self.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
