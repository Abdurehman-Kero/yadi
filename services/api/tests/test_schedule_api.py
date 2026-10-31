import statistics
import time
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import text

from tests.conftest import USER_A, USER_B, as_user

TASKS = "/api/v1/tasks"
SCHEDULE = "/api/v1/schedule"
GENERATE = "/api/v1/schedule/generate"
PREFS = "/api/v1/preferences"


def tomorrow(hour: int, minute: int = 0) -> datetime:
    day = datetime.now(UTC) + timedelta(days=1)
    return day.replace(hour=hour, minute=minute, second=0, microsecond=0)


def iso(moment: datetime) -> str:
    return moment.isoformat()


def make(api: TestClient, title: str = "Work", **fields: Any) -> dict[str, Any]:
    r = api.post(TASKS, json={"title": title, **fields})
    assert r.status_code == 201, r.text
    body: dict[str, Any] = r.json()
    return body


def generate(api: TestClient, **body: Any) -> dict[str, Any]:
    r = api.post(GENERATE, json=body)
    assert r.status_code == 200, r.text
    result: dict[str, Any] = r.json()
    return result


def blocks_of(schedule: dict[str, Any], task: dict[str, Any]) -> list[dict[str, Any]]:
    return [b for b in schedule["blocks"] if b["taskId"] == task["id"]]


def test_generates_around_a_fixed_event_and_sets_statuses(api: TestClient) -> None:
    meeting = make(api, "Meeting", fixedStartAt=iso(tomorrow(9)), fixedEndAt=iso(tomorrow(10)))
    work = make(api, "Report", estimatedMinutes=60, dueAt=iso(tomorrow(16)))
    schedule = generate(api)

    fixed = blocks_of(schedule, meeting)[0]
    assert fixed["isFixed"] is True and fixed["locked"] is True
    assert fixed["startAt"] == tomorrow(9).isoformat().replace("+00:00", "Z")
    placed = blocks_of(schedule, work)[0]
    assert placed["isFixed"] is False and placed["reason"]
    assert placed["endAt"] <= fixed["startAt"] or placed["startAt"] >= fixed["endAt"]
    assert api.get(f"{TASKS}/{work['id']}").json()["status"] == "scheduled"
    assert schedule["unscheduled"] == [] and schedule["stale"] is False
    events = api.get(f"{TASKS}/{work['id']}/events").json()
    assert events[-1]["type"] == "scheduled" and events[-1]["actor"] == "system"


def test_what_does_not_fit_is_reported_and_keeps_its_details(api: TestClient) -> None:
    big = make(api, "Too big", estimatedMinutes=1000, dueAt=iso(tomorrow(11)), priority="critical")
    none = make(api, "No estimate")
    schedule = generate(api)
    assert blocks_of(schedule, big) == []
    by_id = {item["taskId"]: item for item in schedule["unscheduled"]}
    assert by_id[big["id"]]["reason"] == "NO_CAPACITY_BEFORE_DEADLINE"
    assert by_id[big["id"]]["alternatives"]
    assert by_id[none["id"]]["reason"] == "NO_ESTIMATE"
    stored = api.get(f"{TASKS}/{big['id']}").json()
    assert stored["status"] == "planned" and stored["priority"] == "critical"


def test_overlapping_fixed_events_are_reported(api: TestClient) -> None:
    make(api, "A", fixedStartAt=iso(tomorrow(9)), fixedEndAt=iso(tomorrow(11)))
    make(api, "B", fixedStartAt=iso(tomorrow(10)), fixedEndAt=iso(tomorrow(12)))
    conflict = generate(api)["conflicts"][0]
    assert {conflict["firstTitle"], conflict["secondTitle"]} == {"A", "B"}


def test_fixed_time_must_be_a_valid_range(api: TestClient) -> None:
    for body in (
        {"fixedStartAt": iso(tomorrow(9))},
        {"fixedEndAt": iso(tomorrow(9))},
        {"fixedStartAt": iso(tomorrow(10)), "fixedEndAt": iso(tomorrow(9))},
    ):
        assert api.post(TASKS, json={"title": "x", **body}).status_code == 400
    task = make(api, "ok", fixedStartAt=iso(tomorrow(9)), fixedEndAt=iso(tomorrow(10)))
    r = api.patch(f"{TASKS}/{task['id']}", json={"fixedEndAt": iso(tomorrow(8))})
    assert r.status_code == 400
    assert api.get(f"{TASKS}/{task['id']}").json()["status"] == "planned"


def test_regeneration_replaces_plans_but_keeps_locked_and_fixed(api: TestClient) -> None:
    task = make(api, "Report", estimatedMinutes=60)
    first = blocks_of(generate(api), task)[0]
    move = {"startAt": iso(tomorrow(15)), "endAt": iso(tomorrow(16))}
    r = api.patch(f"{SCHEDULE}/blocks/{first['id']}", json=move)
    assert r.status_code == 200 and r.json()["locked"] is True

    other = make(api, "Other", estimatedMinutes=60)
    schedule = generate(api)
    kept = blocks_of(schedule, task)
    assert len(kept) == 1 and kept[0]["id"] == first["id"]
    assert kept[0]["startAt"] == tomorrow(15).isoformat().replace("+00:00", "Z")
    assert len(blocks_of(schedule, other)) == 1
    assert len(schedule["blocks"]) == 2


def test_block_edit_rules(api: TestClient) -> None:
    meeting = make(api, "Meeting", fixedStartAt=iso(tomorrow(9)), fixedEndAt=iso(tomorrow(10)))
    task = make(api, "Report", estimatedMinutes=60)
    schedule = generate(api)
    block = blocks_of(schedule, task)[0]["id"]
    fixed = blocks_of(schedule, meeting)[0]["id"]
    url = f"{SCHEDULE}/blocks/{block}"

    def move(start: datetime, end: datetime) -> Any:
        return api.patch(url, json={"startAt": iso(start), "endAt": iso(end)})

    assert move(tomorrow(20), tomorrow(21)).status_code == 409  # outside working hours
    assert move(tomorrow(9, 30), tomorrow(10, 30)).status_code == 409  # onto the meeting
    assert move(tomorrow(14), tomorrow(13)).status_code == 400
    r = api.patch(
        f"{SCHEDULE}/blocks/{fixed}",
        json={"startAt": iso(tomorrow(11)), "endAt": iso(tomorrow(12))},
    )
    assert r.status_code == 409


def test_finishing_a_task_removes_its_future_blocks(api: TestClient) -> None:
    done = make(api, "Done", estimatedMinutes=60)
    gone = make(api, "Gone", estimatedMinutes=60)
    generate(api)
    api.post(f"{TASKS}/{done['id']}/complete")
    api.delete(f"{TASKS}/{gone['id']}")
    assert api.get(SCHEDULE).json()["blocks"] == []


def test_schedule_is_flagged_stale_after_a_change(api: TestClient) -> None:
    task = make(api, "Report", estimatedMinutes=60)
    assert api.get(SCHEDULE).json()["generatedAt"] is None
    generate(api)
    assert api.get(SCHEDULE).json()["stale"] is False
    api.patch(f"{TASKS}/{task['id']}", json={"estimatedMinutes": 90})
    assert api.get(SCHEDULE).json()["stale"] is True
    assert generate(api)["stale"] is False


def test_working_hours_in_the_users_timezone(api: TestClient) -> None:
    prefs = {
        "timezone": "Africa/Addis_Ababa",
        "workStart": "09:00:00",
        "workEnd": "10:00:00",
        "defaultReminderMinutes": 15,
        "bufferMinutes": 0,
    }
    api.put(PREFS, json=prefs)
    make(api, "Report", estimatedMinutes=60)
    block = generate(api)["blocks"][0]
    start = datetime.fromisoformat(block["startAt"])
    assert (start.hour, start.minute) == (6, 0)  # 09:00 in Addis Ababa


def test_dependencies_order_tasks_and_reject_cycles(api: TestClient) -> None:
    first = make(api, "First", estimatedMinutes=60, dueAt=iso(tomorrow(23) + timedelta(days=4)))
    second = make(api, "Second", estimatedMinutes=60, dueAt=iso(tomorrow(23)))
    url = f"{TASKS}/{second['id']}/dependencies"
    assert api.put(url, json={"dependsOn": [first["id"]]}).json()["dependsOn"] == [first["id"]]
    assert api.get(url).json()["dependsOn"] == [first["id"]]

    schedule = generate(api)
    assert blocks_of(schedule, second)[0]["startAt"] >= blocks_of(schedule, first)[0]["endAt"]

    back = f"{TASKS}/{first['id']}/dependencies"
    assert api.put(back, json={"dependsOn": [second["id"]]}).status_code == 409
    assert api.put(back, json={"dependsOn": [first["id"]]}).status_code == 409


def test_other_users_schedule_is_invisible(api: TestClient) -> None:
    task = make(api, "Secret", estimatedMinutes=60)
    block = blocks_of(generate(api), task)[0]["id"]
    b = as_user(USER_B)
    assert api.get(SCHEDULE, headers=b).json()["blocks"] == []
    move = {"startAt": iso(tomorrow(13)), "endAt": iso(tomorrow(14))}
    assert api.patch(f"{SCHEDULE}/blocks/{block}", json=move, headers=b).status_code == 404
    url = f"{TASKS}/{task['id']}/dependencies"
    assert api.get(url, headers=b).status_code == 404
    assert api.put(url, json={"dependsOn": []}, headers=b).status_code == 404

    mine = make(api, "Mine")
    other_user_task = api.post(TASKS, json={"title": "Theirs"}, headers=b).json()
    r = api.put(f"{TASKS}/{mine['id']}/dependencies", json={"dependsOn": [other_user_task["id"]]})
    assert r.status_code == 404

    generate(api, days=1)
    assert api.post(GENERATE, json={}, headers=b).json()["blocks"] == []
    assert blocks_of(api.get(SCHEDULE).json(), task)


def test_unknown_block_is_404_and_days_are_limited(api: TestClient) -> None:
    move = {"startAt": iso(tomorrow(13)), "endAt": iso(tomorrow(14))}
    assert api.patch(f"{SCHEDULE}/blocks/{uuid.uuid4()}", json=move).status_code == 404
    assert api.post(GENERATE, json={"days": 15}).status_code == 400
    assert api.post(GENERATE, json={"days": 0}).status_code == 400


def test_generation_p95_with_100_tasks(api: TestClient) -> None:
    """M04-R13: p95 <= 500 ms for 100 tasks over 7 days (dev machine)."""
    engine = api.app.state.engine  # type: ignore[attr-defined]
    with engine.begin() as c:
        c.execute(
            text(
                "INSERT INTO tasks (user_id, title, estimated_minutes, status) "
                "SELECT u.id, 'Task ' || g, 15 + (g % 4) * 15, 'inbox' "
                "FROM users u, generate_series(1, 100) g WHERE u.email = :e"
            ),
            {"e": USER_A},
        )
    timings = []
    for _ in range(12):
        start = time.perf_counter()
        assert generate(api)["blocks"]
        timings.append((time.perf_counter() - start) * 1000)
    p95 = statistics.quantiles(timings, n=20)[18]
    print(f"generate p95: {p95:.1f} ms")
    assert p95 <= 500
