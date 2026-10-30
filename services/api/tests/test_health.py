from fastapi.testclient import TestClient


def test_health_ok_without_db(client_db_down: TestClient) -> None:
    r = client_db_down.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ready_ok_with_db(client: TestClient) -> None:
    r = client.get("/api/v1/health/ready")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "database": "ok"}


def test_ready_503_when_db_down(client_db_down: TestClient) -> None:
    r = client_db_down.get("/api/v1/health/ready")
    assert r.status_code == 503
    body = r.json()
    assert body["error"]["code"] == "SERVICE_UNAVAILABLE"
    assert body["error"]["requestId"]
    assert "wrong" not in r.text  # no credentials leaked
