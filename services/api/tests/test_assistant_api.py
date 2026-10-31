from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from tests.conftest import make_settings
from yadi.main import create_app
from yadi.modules.assistant.ai.client import AiError, LlmResult
from yadi.modules.assistant.schemas import ExtractedTask, Extraction

URL = "/api/v1/assistant/extract"
ZONE_PREFS = {
    "timezone": "Africa/Addis_Ababa",
    "workStart": "09:00:00",
    "workEnd": "17:00:00",
    "defaultReminderMinutes": 15,
    "bufferMinutes": 5,
}
SECRET_TEXT = "my private assignment"


def task(**overrides: Any) -> ExtractedTask:
    values: dict[str, Any] = {
        "title": "Finish assignment",
        "description": None,
        "due_local": None,
        "due_phrase": None,
        "estimated_minutes": None,
        "priority": None,
        "confidence": "high",
        "questions": [],
    }
    return ExtractedTask(**{**values, **overrides})


@dataclass
class FakeLlm:
    tasks: list[ExtractedTask] = field(default_factory=lambda: [task()])
    note: str | None = None
    error: str | None = None
    model: str = "gemini-3.5-flash-lite"
    prompts: list[str] = field(default_factory=list)

    def generate_structured(self, *, schema: Any, system: str, prompt: str) -> LlmResult[Any]:
        self.prompts.append(prompt)
        if self.error:
            raise AiError(self.error)
        output = Extraction(tasks=self.tasks, note=self.note)
        return LlmResult(output=output, model=self.model, input_tokens=1000, output_tokens=500)


def use(api: TestClient, fake: FakeLlm | None) -> None:
    api.app.state.llm_client = fake  # type: ignore[attr-defined]


def usage_rows(api: TestClient) -> list[Any]:
    with api.app.state.engine.connect() as c:  # type: ignore[attr-defined]
        return list(c.execute(text("SELECT * FROM ai_usage ORDER BY id")).mappings())


def test_returns_drafts_and_saves_nothing(api: TestClient) -> None:
    use(api, FakeLlm(tasks=[task(title="A"), task(title="B", priority="high")]))
    r = api.post(URL, json={"text": "do A and B"})
    assert r.status_code == 200
    assert [d["title"] for d in r.json()["drafts"]] == ["A", "B"]
    assert [d["priority"] for d in r.json()["drafts"]] == ["medium", "high"]
    assert api.get("/api/v1/tasks").json()["items"] == []


def test_due_time_is_converted_in_the_users_timezone(api: TestClient) -> None:
    api.put("/api/v1/preferences", json=ZONE_PREFS)
    fake = FakeLlm(tasks=[task(due_local="2099-01-15T10:00", due_phrase="Jan 15 at 10")])
    use(api, fake)
    draft = api.post(URL, json={"text": "x"}).json()["drafts"][0]
    assert draft["dueAt"] == "2099-01-15T07:00:00Z"
    assert draft["duePhrase"] == "Jan 15 at 10"
    assert draft["questions"] == []
    assert "Timezone: Africa/Addis_Ababa" in fake.prompts[0]


def test_bad_values_become_questions_not_data(api: TestClient) -> None:
    use(
        api,
        FakeLlm(
            tasks=[
                task(due_local="next friday", estimated_minutes=99999),
                task(title="Past", due_local="2001-01-01T10:00"),
                task(title="   "),
            ]
        ),
    )
    drafts = api.post(URL, json={"text": "x"}).json()["drafts"]
    assert len(drafts) == 2
    assert drafts[0]["dueAt"] is None and drafts[0]["estimatedMinutes"] is None
    assert {q["field"] for q in drafts[0]["questions"]} == {"due", "estimate"}
    assert "passed" in drafts[1]["questions"][0]["question"]


def test_model_questions_and_note_reach_the_user(api: TestClient) -> None:
    q = {"field": "due", "question": "What time?"}
    use(api, FakeLlm(tasks=[task(questions=[q], confidence="low")], note="Only tasks."))
    body = api.post(URL, json={"text": "x"}).json()
    assert body["note"] == "Only tasks."
    assert body["drafts"][0]["questions"] == [q]
    assert body["drafts"][0]["confidence"] == "low"


@pytest.mark.parametrize("body", [{}, {"text": "   "}, {"text": "x" * 2001}])
def test_invalid_input_is_rejected_without_calling_the_model(
    api: TestClient, body: dict[str, str]
) -> None:
    fake = FakeLlm()
    use(api, fake)
    assert api.post(URL, json=body).status_code == 400
    assert fake.prompts == []


@pytest.mark.parametrize(
    "kind", ["timeout", "connection", "rate_limited", "auth", "provider", "refused", "truncated"]
)
def test_provider_failures_are_503_and_recorded(api: TestClient, kind: str) -> None:
    use(api, FakeLlm(error=kind))
    r = api.post(URL, json={"text": SECRET_TEXT})
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "AI_UNAVAILABLE"
    assert kind not in r.json()["error"]["message"]
    row = usage_rows(api)[0]
    assert row["ok"] is False and row["error_kind"] == kind


def test_no_key_configured_is_503(api: TestClient) -> None:
    use(api, None)
    assert api.post(URL, json={"text": "x"}).status_code == 503
    assert usage_rows(api) == []


def test_usage_is_recorded_without_any_message_text(
    api: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    use(api, FakeLlm())
    api.post(URL, json={"text": SECRET_TEXT})
    row = usage_rows(api)[0]
    assert row["ok"] is True and row["operation"] == "extract_tasks"
    assert row["input_tokens"] == 1000 and row["output_tokens"] == 500
    assert float(row["cost_estimate_usd"]) == pytest.approx(0.00155)  # $0.30/M in, $2.50/M out
    assert SECRET_TEXT not in str(dict(row))
    assert SECRET_TEXT not in caplog.text


def test_daily_limit_stops_calls_and_old_usage_does_not_count(api: TestClient) -> None:
    fake = FakeLlm()
    use(api, fake)
    api.app.state.settings.ai_daily_call_limit = 1  # type: ignore[attr-defined]
    assert api.post(URL, json={"text": "x"}).status_code == 200
    r = api.post(URL, json={"text": "x"})
    assert r.status_code == 429 and r.json()["error"]["code"] == "RATE_LIMITED"
    assert len(fake.prompts) == 1

    with api.app.state.engine.begin() as c:  # type: ignore[attr-defined]
        c.execute(
            text("UPDATE ai_usage SET at = :t"),
            {"t": datetime.now(UTC) - timedelta(days=2)},
        )
    assert api.post(URL, json={"text": "x"}).status_code == 200


def test_requires_identity(migrated_db_url: str) -> None:
    app = create_app(make_settings(database_url=migrated_db_url, dev_identity_enabled=False))
    assert TestClient(app).post(URL, json={"text": "x"}).status_code == 401


def test_only_the_adapter_imports_the_provider_sdk() -> None:
    src = Path(__file__).parents[1] / "src"
    importers = [
        p.relative_to(src).as_posix()
        for p in src.rglob("*.py")
        if "from google import genai" in p.read_text(encoding="utf-8")
    ]
    assert importers == ["yadi/modules/assistant/ai/gemini_client.py"]
