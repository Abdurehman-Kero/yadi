from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.conftest import make_settings
from yadi.main import create_app


def _app_with_boom() -> FastAPI:
    app = create_app(make_settings())

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("secret internals")

    @app.get("/typed/{n}")
    def typed(n: int) -> dict[str, int]:
        return {"n": n}

    return app


def test_unknown_route_is_standard_404(client: TestClient) -> None:
    r = client.get("/api/v1/nope")
    assert r.status_code == 404
    e = r.json()["error"]
    assert e["code"] == "NOT_FOUND" and e["requestId"]


def test_validation_error_is_400_with_details() -> None:
    c = TestClient(_app_with_boom(), raise_server_exceptions=False)
    r = c.get("/typed/abc")
    assert r.status_code == 400
    e = r.json()["error"]
    assert e["code"] == "VALIDATION_FAILED"
    assert e["details"][0]["field"]


def test_unhandled_exception_is_500_without_internals() -> None:
    c = TestClient(_app_with_boom(), raise_server_exceptions=False)
    r = c.get("/boom")
    assert r.status_code == 500
    assert r.json()["error"]["code"] == "INTERNAL"
    assert "secret internals" not in r.text and "Traceback" not in r.text


def test_request_id_header_roundtrip(client: TestClient) -> None:
    r = client.get("/api/v1/health", headers={"X-Request-ID": "abc-123"})
    assert r.headers["X-Request-ID"] == "abc-123"
    assert client.get("/api/v1/health").headers["X-Request-ID"]
