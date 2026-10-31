from fastapi.testclient import TestClient

from tests.conftest import BAD_DB_URL, make_settings
from yadi.main import create_app


def test_dev_identity_disabled_means_401(migrated_db_url: str) -> None:
    app = create_app(make_settings(database_url=migrated_db_url, dev_identity_enabled=False))
    r = TestClient(app).get("/api/v1/tasks", headers={"X-Dev-User": "a@example.test"})
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "UNAUTHENTICATED"


def test_unknown_dev_user_is_401(api: TestClient) -> None:
    r = api.get("/api/v1/tasks", headers={"X-Dev-User": "nobody@example.test"})
    assert r.status_code == 401


def test_database_outage_is_503_not_500() -> None:
    app = create_app(make_settings(database_url=BAD_DB_URL, dev_identity_enabled=True))
    r = TestClient(app, raise_server_exceptions=False).get("/api/v1/tasks")
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "SERVICE_UNAVAILABLE"
    assert "wrong" not in r.text
