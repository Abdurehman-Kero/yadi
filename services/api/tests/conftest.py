import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from yadi.config import Settings
from yadi.main import create_app

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://yadi:yadi_dev_password@127.0.0.1:5433/yadi",
)
BAD_DB_URL = "postgresql+psycopg://yadi:wrong@127.0.0.1:1/none?connect_timeout=1"


def make_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {"environment": "test", "database_url": DB_URL}
    values.update(overrides)
    return Settings(_env_file=None, **values)  # type: ignore[arg-type]


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app(make_settings()), raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def client_db_down() -> Iterator[TestClient]:
    app = create_app(make_settings(database_url=BAD_DB_URL))
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
