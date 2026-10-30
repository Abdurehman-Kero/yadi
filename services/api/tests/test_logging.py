import json
import logging

import pytest
from fastapi.testclient import TestClient


def test_one_json_access_log_per_request(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger="yadi.access"):
        client.post(
            "/api/v1/health", json={"password": "hunter2"}, headers={"X-Request-ID": "rid-1"}
        )
    records = [r for r in caplog.records if r.name == "yadi.access"]
    assert len(records) == 1
    data = json.loads(records[0].getMessage())
    assert data["request_id"] == "rid-1"
    assert data["method"] == "POST" and data["path"] == "/api/v1/health"
    assert isinstance(data["status"], int) and data["duration_ms"] >= 0
    assert "hunter2" not in records[0].getMessage()
