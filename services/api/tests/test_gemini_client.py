"""Exercises the real SDK against a fake HTTP transport: no network, no cost."""

import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest

from yadi.modules.assistant.ai.client import AiError
from yadi.modules.assistant.ai.gemini_client import GeminiLlmClient
from yadi.modules.assistant.schemas import Extraction

MODEL = "gemini-3.5-flash-lite"
GOOD = {"tasks": [], "note": "ok"}


def answer(payload: Any, *, finish: str = "STOP") -> dict[str, Any]:
    text = payload if isinstance(payload, str) else json.dumps(payload)
    return {
        "candidates": [
            {"content": {"role": "model", "parts": [{"text": text}]}, "finishReason": finish}
        ],
        "usageMetadata": {
            "promptTokenCount": 12,
            "candidatesTokenCount": 30,
            "thoughtsTokenCount": 4,
            "totalTokenCount": 46,
        },
    }


def api_error(code: int, status: str, reason: str = "") -> httpx.Response:
    body = {"error": {"code": code, "message": f"failed {reason}", "status": status}}
    return httpx.Response(code, json=body)


def client_with(handler: Callable[[httpx.Request], httpx.Response]) -> GeminiLlmClient:
    http = httpx.Client(transport=httpx.MockTransport(handler))
    return GeminiLlmClient(api_key="test-key", model=MODEL, http_client=http)


def call(client: GeminiLlmClient) -> Any:
    return client.generate_structured(schema=Extraction, system="sys", prompt="hello")


def test_sends_the_expected_request_and_parses_the_answer() -> None:
    seen: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["key"] = request.headers.get("x-goog-api-key")
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json=answer(GOOD))

    result = call(client_with(handler))
    assert result.output == Extraction(tasks=[], note="ok")
    assert (result.input_tokens, result.output_tokens) == (12, 34)  # thinking counts as output
    assert f"models/{MODEL}:generateContent" in seen["url"]
    assert seen["key"] == "test-key"
    body = seen["body"]
    assert body["contents"][0]["parts"][0]["text"] == "hello"
    assert body["systemInstruction"]["parts"][0]["text"] == "sys"
    config = body["generationConfig"]
    assert config["responseMimeType"] == "application/json"
    assert "tasks" in config["responseJsonSchema"]["properties"]


@pytest.mark.parametrize(
    "response,kind",
    [
        (httpx.Response(200, json=answer("", finish="SAFETY")), "refused"),
        (httpx.Response(200, json={"promptFeedback": {"blockReason": "SAFETY"}}), "refused"),
        (httpx.Response(200, json=answer('{"tasks":', finish="MAX_TOKENS")), "truncated"),
        (httpx.Response(200, json=answer("not json")), "invalid_output"),
        (httpx.Response(200, json=answer({"tasks": "nope", "note": None})), "invalid_output"),
        (api_error(400, "INVALID_ARGUMENT", "API_KEY_INVALID"), "auth"),
        (api_error(403, "PERMISSION_DENIED"), "auth"),
        (api_error(429, "RESOURCE_EXHAUSTED"), "rate_limited"),
        (api_error(400, "INVALID_ARGUMENT", "bad schema"), "provider"),
        (api_error(500, "INTERNAL"), "provider"),
    ],
)
def test_failures_map_to_ai_errors(response: httpx.Response, kind: str) -> None:
    with pytest.raises(AiError) as caught:
        call(client_with(lambda _: response))
    assert caught.value.kind == kind


def test_connection_failure_and_timeout() -> None:
    def refuse(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down", request=request)

    def slow(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow", request=request)

    with pytest.raises(AiError) as caught:
        call(client_with(refuse))
    assert caught.value.kind == "connection"
    with pytest.raises(AiError) as caught:
        call(client_with(slow))
    assert caught.value.kind == "timeout"
