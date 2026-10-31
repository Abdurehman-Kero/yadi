from typing import Any

from fastapi.testclient import TestClient

from tests.conftest import USER_B, as_user

BASE = "/api/v1/tasks"
DUE = "2030-01-15T10:00:00+03:00"


def make(api: TestClient, **fields: Any) -> dict[str, Any]:
    r = api.post(BASE, json={"title": "Write report", **fields})
    assert r.status_code == 201, r.text
    body: dict[str, Any] = r.json()
    return body


def test_create_minimal_defaults(api: TestClient) -> None:
    t = make(api)
    assert t["title"] == "Write report"
    assert t["status"] == "inbox" and t["priority"] == "medium"
    assert t["dueAt"] is None and t["estimatedMinutes"] is None


def test_create_full_is_planned_and_stored_as_same_instant(api: TestClient) -> None:
    t = make(api, description="Q4", dueAt=DUE, estimatedMinutes=90, priority="critical")
    assert t["status"] == "planned" and t["priority"] == "critical"
    assert t["dueAt"] == "2030-01-15T07:00:00Z"
    assert api.get(f"{BASE}/{t['id']}").json() == t


def test_create_validation(api: TestClient) -> None:
    bad: list[dict[str, Any]] = [
        {},
        {"title": "   "},
        {"title": "x" * 201},
        {"title": "ok", "priority": "urgent"},
        {"title": "ok", "estimatedMinutes": 0},
        {"title": "ok", "estimatedMinutes": 1441},
        {"title": "ok", "dueAt": "2030-01-15T10:00:00"},  # no timezone: ambiguous, so rejected
        {"title": "ok", "status": "completed"},
        {"title": "ok", "userId": "00000000-0000-0000-0000-000000000000"},
    ]
    for body in bad:
        r = api.post(BASE, json=body)
        assert r.status_code == 400, body
        assert r.json()["error"]["code"] == "VALIDATION_FAILED"
        assert r.json()["error"]["details"]


def test_title_is_trimmed(api: TestClient) -> None:
    assert make(api, title="  Call advisor ")["title"] == "Call advisor"


def test_edit_and_clear_fields_updates_status(api: TestClient) -> None:
    t = make(api, dueAt=DUE, estimatedMinutes=30)
    r = api.patch(f"{BASE}/{t['id']}", json={"title": "New", "dueAt": None})
    assert r.status_code == 200
    assert r.json()["title"] == "New" and r.json()["dueAt"] is None
    assert r.json()["status"] == "inbox"
    assert r.json()["estimatedMinutes"] == 30


def test_edit_cannot_set_status_or_null_title(api: TestClient) -> None:
    t = make(api)
    for body in ({"status": "completed"}, {"title": None}, {"priority": None}):
        assert api.patch(f"{BASE}/{t['id']}", json=body).status_code == 400


def test_editing_in_progress_task_keeps_its_status(api: TestClient) -> None:
    t = make(api)
    api.post(f"{BASE}/{t['id']}/start")
    r = api.patch(f"{BASE}/{t['id']}", json={"dueAt": DUE, "estimatedMinutes": 5})
    assert r.json()["status"] == "in_progress"


def test_start_complete_reopen(api: TestClient) -> None:
    t = make(api, dueAt=DUE, estimatedMinutes=30)
    url = f"{BASE}/{t['id']}"
    assert api.post(f"{url}/start").json()["status"] == "in_progress"
    done = api.post(f"{url}/complete").json()
    assert done["status"] == "completed" and done["completedAt"]
    reopened = api.post(f"{url}/reopen").json()
    assert reopened["status"] == "planned" and reopened["completedAt"] is None


def test_illegal_transitions_conflict(api: TestClient) -> None:
    t = make(api)
    url = f"{BASE}/{t['id']}"
    assert api.post(f"{url}/reopen").status_code == 409  # not completed
    api.post(f"{url}/complete")
    assert api.post(f"{url}/start").status_code == 409
    assert api.post(f"{url}/complete").status_code == 409
    assert api.delete(url).status_code == 409  # finished tasks: reopen first
    r = api.patch(url, json={"title": "x"})
    assert r.status_code == 409 and r.json()["error"]["code"] == "CONFLICT"


def test_cancel_is_final_and_keeps_the_record(api: TestClient) -> None:
    t = make(api)
    url = f"{BASE}/{t['id']}"
    r = api.delete(url)
    assert r.status_code == 200 and r.json()["status"] == "cancelled"
    assert api.get(url).json()["status"] == "cancelled"
    for call in (api.post(f"{url}/reopen"), api.post(f"{url}/start"), api.delete(url)):
        assert call.status_code == 409


def test_list_filter_and_pagination(api: TestClient) -> None:
    ids = [make(api, title=f"T{i}")["id"] for i in range(5)]
    api.post(f"{BASE}/{ids[0]}/complete")
    api.delete(f"{BASE}/{ids[1]}")

    seen: list[str] = []
    cursor = None
    while True:
        params: dict[str, Any] = {"limit": 2}
        if cursor:
            params["cursor"] = cursor
        page = api.get(BASE, params=params).json()
        seen += [t["id"] for t in page["items"]]
        cursor = page["nextCursor"]
        if not cursor:
            break
    assert seen == list(reversed(ids))  # newest first, each exactly once

    done = api.get(BASE, params={"status": "completed"}).json()["items"]
    assert [t["id"] for t in done] == [ids[0]]
    active = api.get(BASE, params={"status": ["inbox", "planned", "in_progress"]}).json()["items"]
    assert {t["id"] for t in active} == set(ids[2:])


def test_list_rejects_bad_input(api: TestClient) -> None:
    assert api.get(BASE, params={"cursor": "garbage"}).status_code == 400
    assert api.get(BASE, params={"limit": 0}).status_code == 400
    assert api.get(BASE, params={"limit": 101}).status_code == 400
    assert api.get(BASE, params={"status": "nope"}).status_code == 400


def test_history_records_each_change_in_order(api: TestClient) -> None:
    t = make(api)
    url = f"{BASE}/{t['id']}"
    api.patch(url, json={"title": "Changed"})
    api.patch(url, json={"title": "Changed"})  # no real change: no event
    api.post(f"{url}/start")
    api.post(f"{url}/complete")
    api.post(f"{url}/reopen")
    events = api.get(f"{url}/events").json()
    assert [e["type"] for e in events] == ["created", "updated", "started", "completed", "reopened"]
    assert all(e["actor"] == "user" for e in events)
    assert events[1]["payload"]["changed"] == ["title"]
    assert events[2]["payload"] == {"from": "inbox", "to": "in_progress"}


def test_other_users_tasks_are_invisible_on_every_route(api: TestClient) -> None:
    t = make(api)
    url = f"{BASE}/{t['id']}"
    b = as_user(USER_B)
    calls = [
        api.get(url, headers=b),
        api.get(f"{url}/events", headers=b),
        api.patch(url, json={"title": "stolen"}, headers=b),
        api.post(f"{url}/start", headers=b),
        api.post(f"{url}/complete", headers=b),
        api.post(f"{url}/reopen", headers=b),
        api.delete(url, headers=b),
    ]
    for r in calls:
        assert r.status_code == 404, r.request.url
        assert "Write report" not in r.text
    assert api.get(BASE, headers=b).json()["items"] == []
    assert api.get(url).json()["title"] == "Write report"
    assert api.get(url).json()["status"] == "inbox"


def test_unknown_or_malformed_id_is_handled(api: TestClient) -> None:
    assert api.get(f"{BASE}/00000000-0000-0000-0000-000000000000").status_code == 404
    assert api.get(f"{BASE}/not-a-uuid").status_code == 400
