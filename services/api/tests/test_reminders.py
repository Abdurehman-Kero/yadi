import base64
import os
import subprocess
import sys
import threading
import time
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
import pywebpush  # type: ignore[import-untyped]
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session

from tests.conftest import USER_A, USER_B, as_user, make_settings
from yadi.modules.reminders.delivery import (
    ExpiredSubscriptionError,
    Message,
    WebPushChannel,
    build_push_channel,
)
from yadi.worker import MAX_ATTEMPTS, deliver_one, process_due, recover_expired_leases

TASKS = "/api/v1/tasks"


def later(**delta: float) -> datetime:
    return datetime.now(UTC) + timedelta(**delta)


def make(api: TestClient, **fields: Any) -> dict[str, Any]:
    r = api.post(TASKS, json={"title": "Work", **fields})
    assert r.status_code == 201, r.text
    body: dict[str, Any] = r.json()
    return body


def engine_of(api: TestClient) -> Engine:
    engine: Engine = api.app.state.engine  # type: ignore[attr-defined]
    return engine


def reminders(api: TestClient, task: dict[str, Any], state: str | None = None) -> list[Any]:
    with engine_of(api).connect() as c:
        rows = c.execute(
            text("SELECT * FROM reminders WHERE task_id = :t ORDER BY created_at"),
            {"t": task["id"]},
        ).mappings()
        return [dict(r) for r in rows if state is None or r["state"] == state]


def notifications(api: TestClient) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = api.get("/api/v1/notifications").json()["items"]
    return items


def make_due(api: TestClient, task: dict[str, Any]) -> None:
    """Moves a task's pending reminder into the past, as if its time had come."""
    with engine_of(api).begin() as c:
        c.execute(
            text(
                "UPDATE reminders SET remind_at = now() - interval '1 second', "
                "next_attempt_at = now() - interval '1 second' "
                "WHERE task_id = :t AND state = 'scheduled'"
            ),
            {"t": task["id"]},
        )


# --- Following the task


def test_reminder_uses_the_default_lead_time_and_the_deadline(api: TestClient) -> None:
    due = later(days=2)
    task = make(api, dueAt=due.isoformat())
    rows = reminders(api, task, "scheduled")
    assert len(rows) == 1
    assert rows[0]["anchor_kind"] == "due"
    assert rows[0]["remind_at"] == pytest.approx(
        due - timedelta(minutes=15), abs=timedelta(seconds=1)
    )


def test_fixed_start_beats_the_deadline_and_own_lead_time_beats_default(api: TestClient) -> None:
    start = later(days=1)
    task = make(
        api,
        fixedStartAt=start.isoformat(),
        fixedEndAt=(start + timedelta(hours=1)).isoformat(),
        dueAt=later(days=3).isoformat(),
        reminderMinutesBefore=60,
    )
    row = reminders(api, task, "scheduled")[0]
    assert row["anchor_kind"] == "start"
    assert row["remind_at"] == pytest.approx(start - timedelta(hours=1), abs=timedelta(seconds=1))


def test_no_time_or_reminders_off_means_no_reminder(api: TestClient) -> None:
    assert reminders(api, make(api)) == []
    assert reminders(api, make(api, dueAt=later(days=1).isoformat(), reminderEnabled=False)) == []
    assert reminders(api, make(api, dueAt=later(days=-1).isoformat())) == []


def test_lead_time_longer_than_the_time_left_fires_straight_away(api: TestClient) -> None:
    task = make(api, dueAt=later(minutes=5).isoformat())
    row = reminders(api, task, "scheduled")[0]
    assert row["remind_at"] <= later(seconds=5)


def test_changing_the_time_replaces_the_reminder_without_duplicates(api: TestClient) -> None:
    task = make(api, dueAt=later(days=1).isoformat())
    original = reminders(api, task, "scheduled")[0]
    new_due = later(days=2).isoformat()
    api.patch(f"{TASKS}/{task['id']}", json={"dueAt": new_due})
    api.patch(f"{TASKS}/{task['id']}", json={"dueAt": new_due, "title": "Same time"})
    pending = reminders(api, task, "scheduled")
    assert len(pending) == 1 and pending[0]["id"] != original["id"]
    assert len(reminders(api, task, "cancelled")) == 1


def test_moving_back_revives_the_cancelled_reminder(api: TestClient) -> None:
    due = later(days=1).isoformat()
    task = make(api, dueAt=due)
    api.patch(f"{TASKS}/{task['id']}", json={"dueAt": later(days=2).isoformat()})
    api.patch(f"{TASKS}/{task['id']}", json={"dueAt": due})
    assert len(reminders(api, task, "scheduled")) == 1
    assert len(reminders(api, task)) == 2


def test_turning_reminders_off_cancels(api: TestClient) -> None:
    task = make(api, dueAt=later(days=1).isoformat())
    api.patch(f"{TASKS}/{task['id']}", json={"reminderEnabled": False})
    assert reminders(api, task, "scheduled") == []


def test_finishing_a_task_cancels_everything_including_snoozes(api: TestClient) -> None:
    for action in ("complete", "cancel"):
        task = make(api, dueAt=later(days=1).isoformat())
        rid = reminders(api, task, "scheduled")[0]["id"]
        api.post(f"/api/v1/reminders/{rid}/snooze", json={"minutes": 10})
        if action == "complete":
            api.post(f"{TASKS}/{task['id']}/complete")
        else:
            api.delete(f"{TASKS}/{task['id']}")
        assert reminders(api, task, "scheduled") == []


def test_reminder_follows_the_generated_plan_and_a_moved_block(api: TestClient) -> None:
    task = make(api, estimatedMinutes=60, dueAt=later(days=5).isoformat())
    schedule = api.post("/api/v1/schedule/generate", json={}).json()
    block = schedule["blocks"][0]
    row = reminders(api, task, "scheduled")[0]
    assert row["anchor_kind"] == "start"
    assert row["anchor_at"] == datetime.fromisoformat(block["startAt"])

    day = later(days=2).replace(hour=14, minute=0, second=0, microsecond=0)
    move = {"startAt": day.isoformat(), "endAt": (day + timedelta(hours=1)).isoformat()}
    assert api.patch(f"/api/v1/schedule/blocks/{block['id']}", json=move).status_code == 200
    assert reminders(api, task, "scheduled")[0]["anchor_at"] == day


def test_regenerating_twice_does_not_duplicate(api: TestClient) -> None:
    task = make(api, estimatedMinutes=60, dueAt=later(days=5).isoformat())
    api.post("/api/v1/schedule/generate", json={})
    api.post("/api/v1/schedule/generate", json={})
    assert len(reminders(api, task, "scheduled")) == 1


# --- The worker


def test_due_reminder_becomes_one_notification(api: TestClient) -> None:
    task = make(api, title="Call advisor", dueAt=later(hours=3).isoformat())
    make_due(api, task)
    assert process_due(engine_of(api), datetime.now(UTC)) == 1
    assert process_due(engine_of(api), datetime.now(UTC)) == 0

    items = notifications(api)
    assert len(items) == 1 and items[0]["title"] == "Call advisor"
    assert items[0]["body"].startswith("Due at")
    assert reminders(api, task)[0]["state"] == "delivered"
    with engine_of(api).connect() as c:
        attempts = c.execute(text("SELECT channel, outcome FROM reminder_attempts")).all()
    assert [tuple(a) for a in attempts] == [("in_app", "ok")]


def test_not_yet_due_is_left_alone(api: TestClient) -> None:
    make(api, dueAt=later(days=2).isoformat())
    assert process_due(engine_of(api), datetime.now(UTC)) == 0
    assert notifications(api) == []


def test_body_uses_the_users_timezone(api: TestClient) -> None:
    api.put(
        "/api/v1/preferences",
        json={
            "timezone": "Africa/Addis_Ababa",
            "workStart": "09:00:00",
            "workEnd": "17:00:00",
            "defaultReminderMinutes": 15,
            "bufferMinutes": 5,
        },
    )
    due = later(days=2).replace(hour=7, minute=0, second=0, microsecond=0)
    task = make(api, dueAt=due.isoformat())
    make_due(api, task)
    process_due(engine_of(api), datetime.now(UTC))
    assert "10:00" in notifications(api)[0]["body"]


def test_late_reminder_is_delivered_once_and_says_so(api: TestClient) -> None:
    task = make(api, dueAt=later(hours=1).isoformat())
    make_due(api, task)
    process_due(engine_of(api), datetime.now(UTC) + timedelta(hours=5))
    body = notifications(api)[0]["body"]
    assert "late" in body and body.startswith("Was due")


def failing_writer(*_: Any) -> None:
    raise RuntimeError("secret detail")


def test_failures_retry_on_schedule_then_stop(api: TestClient) -> None:
    task = make(api, dueAt=later(days=2).isoformat())
    make_due(api, task)
    now = datetime.now(UTC)
    expected = [timedelta(seconds=30), timedelta(minutes=2), timedelta(minutes=10)]
    for delay in expected:
        assert process_due(engine_of(api), now, write=failing_writer) == 1
        row = reminders(api, task)[0]
        assert row["state"] == "scheduled"
        assert row["next_attempt_at"] == now + delay
        assert (
            process_due(engine_of(api), now + delay - timedelta(seconds=1), write=failing_writer)
            == 0
        )
        now += delay
    assert process_due(engine_of(api), now, write=failing_writer) == 1
    row = reminders(api, task)[0]
    assert row["state"] == "failed" and row["attempts"] == MAX_ATTEMPTS
    assert process_due(engine_of(api), now + timedelta(days=1), write=failing_writer) == 0
    with engine_of(api).connect() as c:
        rows = c.execute(text("SELECT outcome, error_kind FROM reminder_attempts")).all()
    assert [tuple(r) for r in rows] == [("failed", "RuntimeError")] * MAX_ATTEMPTS
    assert notifications(api) == []


def test_recovers_after_a_failure(api: TestClient) -> None:
    task = make(api, dueAt=later(days=2).isoformat())
    make_due(api, task)
    now = datetime.now(UTC)
    process_due(engine_of(api), now, write=failing_writer)
    process_due(engine_of(api), now + timedelta(seconds=31))
    assert len(notifications(api)) == 1
    assert reminders(api, task)[0]["state"] == "delivered"


def test_a_crashed_workers_lease_expires_and_delivery_happens_once(api: TestClient) -> None:
    task = make(api, dueAt=later(days=2).isoformat())
    make_due(api, task)
    now = datetime.now(UTC)
    with engine_of(api).begin() as c:  # As if a worker claimed this, then died.
        c.execute(
            text(
                "UPDATE reminders SET state='processing', attempts=1, locked_until=:l "
                "WHERE task_id=:t"
            ),
            {"l": now + timedelta(seconds=60), "t": task["id"]},
        )
    assert process_due(engine_of(api), now) == 0  # Lease still held.
    assert notifications(api) == []
    assert process_due(engine_of(api), now + timedelta(seconds=61)) == 1
    assert len(notifications(api)) == 1


def test_spent_lease_becomes_failed(api: TestClient) -> None:
    task = make(api, dueAt=later(days=2).isoformat())
    now = datetime.now(UTC)
    with engine_of(api).begin() as c:
        c.execute(
            text(
                "UPDATE reminders SET state='processing', attempts=:a, locked_until=:l "
                "WHERE task_id=:t"
            ),
            {"a": MAX_ATTEMPTS, "l": now - timedelta(seconds=1), "t": task["id"]},
        )
    with Session(engine_of(api)) as session:
        assert recover_expired_leases(session, now) == 1
    assert reminders(api, task)[0]["state"] == "failed"


def test_task_finished_after_claim_is_not_announced(api: TestClient) -> None:
    task = make(api, dueAt=later(days=2).isoformat())
    rid = reminders(api, task)[0]["id"]
    with engine_of(api).begin() as c:
        c.execute(text("UPDATE reminders SET state='processing' WHERE id=:r"), {"r": rid})
        c.execute(text("UPDATE tasks SET status='completed' WHERE id=:t"), {"t": task["id"]})
    assert deliver_one(engine_of(api), rid, datetime.now(UTC)) == "cancelled"
    assert notifications(api) == []


def test_two_workers_never_deliver_the_same_reminder_twice(api: TestClient) -> None:
    tasks = [make(api, title=f"T{i}", dueAt=later(days=2).isoformat()) for i in range(30)]
    for task in tasks:
        make_due(api, task)
    now = datetime.now(UTC)
    errors: list[BaseException] = []

    def work() -> None:
        try:
            while process_due(engine_of(api), now):
                pass
        except BaseException as exc:  # Surface failures from the thread.
            errors.append(exc)

    threads = [threading.Thread(target=work) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert errors == []
    with engine_of(api).connect() as c:
        total = c.execute(
            text("SELECT count(*), count(DISTINCT reminder_id) FROM notifications")
        ).one()
    assert tuple(total) == (30, 30)


def test_redelivering_the_same_reminder_cannot_add_a_notification(api: TestClient) -> None:
    task = make(api, dueAt=later(days=2).isoformat())
    make_due(api, task)
    process_due(engine_of(api), datetime.now(UTC))
    rid = reminders(api, task)[0]["id"]
    with engine_of(api).begin() as c:  # As if the commit's result was lost and it ran again.
        c.execute(text("UPDATE reminders SET state='processing' WHERE id=:r"), {"r": rid})
    deliver_one(engine_of(api), rid, datetime.now(UTC))
    assert len(notifications(api)) == 1


# --- Push


def _subscribe(api: TestClient, endpoint: str = "https://push.example/abc") -> None:
    body = {"endpoint": endpoint, "keys": {"p256dh": "key", "auth": "secret"}}
    assert api.post("/api/v1/push/subscriptions", json=body).status_code == 204


class RecordingSender:
    def __init__(self, error: Exception | None = None) -> None:
        self.sent: list[str] = []
        self.error = error

    def __call__(self, _: Any, payload: str) -> None:
        if self.error:
            raise self.error
        self.sent.append(payload)


def test_push_is_sent_after_the_in_app_notification(api: TestClient) -> None:
    _subscribe(api)
    sender = RecordingSender()
    task = make(api, title="Call advisor", dueAt=later(days=2).isoformat())
    make_due(api, task)
    process_due(engine_of(api), datetime.now(UTC), push=WebPushChannel(sender))
    assert len(sender.sent) == 1 and "Call advisor" in sender.sent[0]
    with engine_of(api).connect() as c:
        rows = c.execute(text("SELECT channel, outcome FROM reminder_attempts ORDER BY id")).all()
    assert [tuple(r) for r in rows] == [("in_app", "ok"), ("push", "accepted")]


def test_push_failure_never_undoes_or_repeats_delivery(api: TestClient) -> None:
    _subscribe(api)
    task = make(api, dueAt=later(days=2).isoformat())
    make_due(api, task)
    process_due(engine_of(api), datetime.now(UTC), push=WebPushChannel(RecordingSender(OSError())))
    assert len(notifications(api)) == 1
    assert reminders(api, task)[0]["state"] == "delivered"
    with engine_of(api).connect() as c:
        rows = c.execute(text("SELECT channel, outcome FROM reminder_attempts ORDER BY id")).all()
    assert [tuple(r) for r in rows] == [("in_app", "ok"), ("push", "failed")]


def test_no_subscription_still_delivers_in_app(api: TestClient) -> None:
    task = make(api, dueAt=later(days=2).isoformat())
    make_due(api, task)
    process_due(engine_of(api), datetime.now(UTC), push=WebPushChannel(RecordingSender()))
    assert len(notifications(api)) == 1
    with engine_of(api).connect() as c:
        rows = c.execute(text("SELECT outcome FROM reminder_attempts WHERE channel='push'")).all()
    assert [r[0] for r in rows] == ["no_subscription"]


def test_expired_subscription_is_removed(api: TestClient) -> None:
    _subscribe(api)
    channel = WebPushChannel(RecordingSender(ExpiredSubscriptionError()))
    with Session(engine_of(api)) as session:
        reminder_user = session.scalar(text("SELECT id FROM users WHERE email=:e"), {"e": USER_A})
        message = Message(uuid.uuid4(), reminder_user, "t", "b")
        assert channel.send(session, message) == "failed"
    with engine_of(api).connect() as c:
        assert c.execute(text("SELECT count(*) FROM push_subscriptions")).scalar() == 0


def test_real_push_library_encrypts_and_maps_responses(monkeypatch: pytest.MonkeyPatch) -> None:
    """Uses real keys and real encryption. Only the final HTTP call is replaced."""
    server = ec.generate_private_key(ec.SECP256R1())
    private = base64.urlsafe_b64encode(
        server.private_numbers().private_value.to_bytes(32, "big")
    ).rstrip(b"=")
    browser = ec.generate_private_key(ec.SECP256R1()).public_key()
    p256dh = base64.urlsafe_b64encode(
        browser.public_bytes(
            serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint
        )
    ).rstrip(b"=")
    settings = make_settings(vapid_private_key=private.decode(), vapid_public_key="unused")
    channel = build_push_channel(settings)
    assert channel is not None
    sent: list[dict[str, Any]] = []
    responses = [201, 410]

    def fake_post(url: str, **kwargs: Any) -> Any:
        sent.append({"url": url, **kwargs})
        response = requests.Response()
        response.status_code = responses.pop(0)
        return response

    monkeypatch.setattr(pywebpush.requests, "post", fake_post)

    class Row:
        id = uuid.uuid4()
        endpoint = "https://push.example/abc"
        auth = base64.urlsafe_b64encode(b"0123456789abcdef").rstrip(b"=").decode()

    Row.p256dh = p256dh.decode()  # type: ignore[attr-defined]

    class FakeSession:
        def __init__(self) -> None:
            self.executed = 0

        def scalars(self, _: Any) -> Any:
            return type("R", (), {"all": staticmethod(lambda: [Row])})

        def execute(self, _: Any) -> None:
            self.executed += 1

        def commit(self) -> None:
            pass

    session = FakeSession()
    message = Message(uuid.uuid4(), uuid.uuid4(), "Secret title", "b")
    assert channel.send(session, message) == "accepted"  # type: ignore[arg-type]
    assert b"Secret title" not in sent[0]["data"]  # Encrypted for the browser.
    assert "vapid" in sent[0]["headers"]["Authorization"].lower()
    assert channel.send(session, message) == "failed"  # type: ignore[arg-type]
    assert session.executed == 1  # 410 removed the subscription.


# --- The API


def test_snooze_replaces_pending_and_fires_once_later(api: TestClient) -> None:
    task = make(api, title="Call", dueAt=later(days=2).isoformat())
    rid = reminders(api, task, "scheduled")[0]["id"]
    r = api.post(f"/api/v1/reminders/{rid}/snooze", json={"minutes": 10})
    assert r.status_code == 201
    pending = reminders(api, task, "scheduled")
    assert len(pending) == 1 and pending[0]["kind"] == "snooze"
    assert pending[0]["remind_at"] == pytest.approx(later(minutes=10), abs=timedelta(seconds=5))

    assert process_due(engine_of(api), datetime.now(UTC)) == 0
    process_due(engine_of(api), later(minutes=11))
    items = notifications(api)
    assert len(items) == 1 and items[0]["title"] == "Snoozed: Call"
    assert process_due(engine_of(api), later(minutes=12)) == 0


def test_a_delivered_reminder_can_be_snoozed_from_its_notification(api: TestClient) -> None:
    task = make(api, dueAt=later(days=2).isoformat())
    make_due(api, task)
    process_due(engine_of(api), datetime.now(UTC))
    rid = notifications(api)[0]["reminderId"]
    assert api.post(f"/api/v1/reminders/{rid}/snooze", json={"minutes": 5}).status_code == 201
    assert len(reminders(api, task, "scheduled")) == 1


def test_snooze_validation_and_finished_tasks(api: TestClient) -> None:
    task = make(api, dueAt=later(days=2).isoformat())
    rid = reminders(api, task, "scheduled")[0]["id"]
    for minutes in (0, 1441):
        assert (
            api.post(f"/api/v1/reminders/{rid}/snooze", json={"minutes": minutes}).status_code
            == 400
        )
    api.post(f"{TASKS}/{task['id']}/complete")
    assert api.post(f"/api/v1/reminders/{rid}/snooze", json={"minutes": 5}).status_code == 409


def test_reminder_cancel_and_listing(api: TestClient) -> None:
    task = make(api, dueAt=later(days=2).isoformat())
    listed = api.get("/api/v1/reminders").json()
    assert [r["taskId"] for r in listed] == [task["id"]]
    rid = listed[0]["id"]
    assert api.post(f"/api/v1/reminders/{rid}/cancel").json()["state"] == "cancelled"
    assert api.post(f"/api/v1/reminders/{rid}/cancel").status_code == 409
    assert api.get("/api/v1/reminders").json() == []


def test_read_state(api: TestClient) -> None:
    for _ in range(2):
        make_due(api, make(api, dueAt=later(days=2).isoformat()))
    process_due(engine_of(api), datetime.now(UTC))
    body = api.get("/api/v1/notifications").json()
    assert body["unread"] == 2
    read = api.post(f"/api/v1/notifications/{body['items'][0]['id']}/read").json()
    assert read["readAt"]
    assert api.get("/api/v1/notifications").json()["unread"] == 1
    assert api.post("/api/v1/notifications/read-all").status_code == 204
    assert api.get("/api/v1/notifications").json()["unread"] == 0


def test_subscription_validation_and_unsubscribe(api: TestClient) -> None:
    bad = {"endpoint": "http://insecure.example", "keys": {"p256dh": "k", "auth": "a"}}
    assert api.post("/api/v1/push/subscriptions", json=bad).status_code == 400
    schema = api.get("/openapi.json").json()["components"]["schemas"]["SubscriptionKeys"]
    assert set(schema["properties"]) == {"p256dh", "auth"}  # The browser's own names.
    _subscribe(api)
    _subscribe(api)  # The same browser twice stays one subscription.
    with engine_of(api).connect() as c:
        assert c.execute(text("SELECT count(*) FROM push_subscriptions")).scalar() == 1
    r = api.post("/api/v1/push/unsubscribe", json={"endpoint": "https://push.example/abc"})
    assert r.status_code == 204
    with engine_of(api).connect() as c:
        assert c.execute(text("SELECT count(*) FROM push_subscriptions")).scalar() == 0


def test_service_status(api: TestClient) -> None:
    status = api.get("/api/v1/reminders/service-status").json()
    assert status["running"] is False and status["pushAvailable"] is False
    with engine_of(api).begin() as c:
        c.execute(
            text(
                "INSERT INTO worker_heartbeat (name, beat_at) VALUES ('reminders', now()) "
                "ON CONFLICT (name) DO UPDATE SET beat_at = now()"
            )
        )
    assert api.get("/api/v1/reminders/service-status").json()["running"] is True
    with engine_of(api).begin() as c:
        c.execute(text("UPDATE worker_heartbeat SET beat_at = now() - interval '5 minutes'"))
    assert api.get("/api/v1/reminders/service-status").json()["running"] is False


def test_other_users_data_is_invisible(api: TestClient) -> None:
    task = make(api, title="Secret", dueAt=later(days=2).isoformat())
    rid = reminders(api, task, "scheduled")[0]["id"]
    b = as_user(USER_B)
    assert api.get("/api/v1/reminders", headers=b).json() == []
    assert (
        api.post(f"/api/v1/reminders/{rid}/snooze", json={"minutes": 5}, headers=b).status_code
        == 404
    )
    assert api.post(f"/api/v1/reminders/{rid}/cancel", headers=b).status_code == 404
    make_due(api, task)
    process_due(engine_of(api), datetime.now(UTC))
    nid = notifications(api)[0]["id"]
    assert api.get("/api/v1/notifications", headers=b).json() == {"items": [], "unread": 0}
    assert api.post(f"/api/v1/notifications/{nid}/read", headers=b).status_code == 404
    api.post("/api/v1/notifications/read-all", headers=b)
    assert api.get("/api/v1/notifications").json()["unread"] == 1


# --- A real worker process


def test_real_worker_survives_a_stop_and_meets_the_timeliness_target(
    api: TestClient, migrated_db_url: str
) -> None:
    """Nothing here uses a browser. Kills a real process, then measures delivery delay."""
    env = {
        **os.environ,
        "DATABASE_URL": migrated_db_url,
        "PYTHONPATH": "src",
        "WORKER_POLL_SECONDS": "1",
        "ENVIRONMENT": "test",
        "VAPID_PRIVATE_KEY": "",
    }
    root = Path(__file__).parents[1]

    def start() -> subprocess.Popen[bytes]:
        return subprocess.Popen(
            [sys.executable, "-m", "yadi.worker"],
            cwd=root,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def wait_for(count: int, limit: float = 20) -> None:
        deadline = time.monotonic() + limit
        while time.monotonic() < deadline:
            with engine_of(api).connect() as c:
                if c.execute(text("SELECT count(*) FROM notifications")).scalar() == count:
                    return
            time.sleep(0.2)
        raise AssertionError(f"expected {count} notifications")

    worker = start()
    try:
        tasks = [make(api, title=f"T{i}", dueAt=later(hours=3).isoformat()) for i in range(20)]
        for task in tasks:
            make_due(api, task)
        wait_for(20)
    finally:
        worker.kill()
        worker.wait()

    # Work that becomes due while no worker is running is not lost.
    missed = make(api, title="While stopped", dueAt=later(hours=3).isoformat())
    make_due(api, missed)
    time.sleep(1.5)
    with engine_of(api).connect() as c:
        assert c.execute(text("SELECT count(*) FROM notifications")).scalar() == 20

    worker = start()
    try:
        wait_for(21)
        time.sleep(1.5)  # Would reveal a duplicate.
    finally:
        worker.kill()
        worker.wait()

    with engine_of(api).connect() as c:
        assert c.execute(text("SELECT count(*) FROM notifications")).scalar() == 21
        delays = [
            row[0]
            for row in c.execute(
                text(
                    "SELECT extract(epoch FROM n.created_at - r.remind_at) "
                    "FROM notifications n JOIN reminders r ON r.id = n.reminder_id "
                    "WHERE n.title <> 'While stopped' ORDER BY 1"
                )
            )
        ]
    p95 = float(delays[int(len(delays) * 0.95) - 1])
    print(f"reminder delay p95: {p95:.2f} s with a 1 s poll")
    assert p95 <= 30
