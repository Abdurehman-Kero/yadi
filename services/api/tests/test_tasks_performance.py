import statistics
import time

from fastapi.testclient import TestClient
from sqlalchemy import text

from tests.conftest import USER_A


def test_list_p95_with_2000_tasks(api: TestClient) -> None:
    """NFR-PERF-001: p95 <= 150 ms for a 50-item page with 2,000 tasks (dev machine)."""
    engine = api.app.state.engine  # type: ignore[attr-defined]
    with engine.begin() as c:
        c.execute(
            text(
                "INSERT INTO tasks (user_id, title, created_at) "
                "SELECT u.id, 'Task ' || g, now() - g * interval '1 minute' "
                "FROM users u, generate_series(1, 2000) g WHERE u.email = :e"
            ),
            {"e": USER_A},
        )
    timings = []
    for _ in range(40):
        start = time.perf_counter()
        r = api.get("/api/v1/tasks", params={"limit": 50})
        timings.append((time.perf_counter() - start) * 1000)
        assert len(r.json()["items"]) == 50
    p95 = statistics.quantiles(timings, n=20)[18]
    print(f"list p95: {p95:.1f} ms")
    assert p95 <= 150
