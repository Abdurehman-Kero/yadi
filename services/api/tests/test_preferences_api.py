from typing import Any

from fastapi.testclient import TestClient

from tests.conftest import USER_B, as_user

URL = "/api/v1/preferences"
VALID: dict[str, Any] = {
    "timezone": "Africa/Addis_Ababa",
    "workStart": "08:30:00",
    "workEnd": "18:00:00",
    "defaultReminderMinutes": 10,
    "bufferMinutes": 0,
}


def test_defaults(api: TestClient) -> None:
    p = api.get(URL).json()
    assert p["timezone"] == "UTC" and p["workStart"] == "09:00:00"


def test_update_persists_for_this_user_only(api: TestClient) -> None:
    r = api.put(URL, json=VALID)
    assert r.status_code == 200 and r.json() == VALID
    assert api.get(URL).json() == VALID
    assert api.get(URL, headers=as_user(USER_B)).json()["timezone"] == "UTC"


def test_invalid_values_rejected(api: TestClient) -> None:
    for change in (
        {"timezone": "Mars/Olympus"},
        {"timezone": "../../etc/passwd"},
        {"workStart": "18:00:00", "workEnd": "08:00:00"},
        {"workStart": "09:00:00", "workEnd": "09:00:00"},
        {"defaultReminderMinutes": -1},
        {"bufferMinutes": 241},
    ):
        r = api.put(URL, json={**VALID, **change})
        assert r.status_code == 400, change
        assert r.json()["error"]["code"] == "VALIDATION_FAILED"
    assert api.get(URL).json()["timezone"] == "UTC"
