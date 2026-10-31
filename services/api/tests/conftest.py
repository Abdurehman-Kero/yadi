import os
import uuid
from collections.abc import Iterator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from yadi.config import Settings
from yadi.main import create_app

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://yadi:yadi_dev_password@127.0.0.1:5433/yadi",
)
BAD_DB_URL = "postgresql+psycopg://yadi:wrong@127.0.0.1:1/none?connect_timeout=1"

USER_A = "a@example.test"
USER_B = "b@example.test"


def make_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {"environment": "test", "database_url": DB_URL}
    values.update(overrides)
    return Settings(_env_file=None, **values)  # type: ignore[arg-type]


def as_user(email: str) -> dict[str, str]:
    return {"X-Dev-User": email}


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app(make_settings()), raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def client_db_down() -> Iterator[TestClient]:
    app = create_app(make_settings(database_url=BAD_DB_URL))
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture(scope="session")
def migrated_db_url() -> Iterator[str]:
    """One throwaway migrated database per test run; dev data is never touched."""
    name = f"yadi_test_{uuid.uuid4().hex[:8]}"
    admin = create_engine(DB_URL, isolation_level="AUTOCOMMIT")
    with admin.connect() as c:
        c.execute(text(f'CREATE DATABASE "{name}"'))
    url = make_url(DB_URL).set(database=name).render_as_string(hide_password=False)
    cfg = Config("alembic.ini")
    cfg.attributes["url"] = url
    command.upgrade(cfg, "head")
    try:
        yield url
    finally:
        with admin.connect() as c:
            c.execute(text(f'DROP DATABASE "{name}" WITH (FORCE)'))
        admin.dispose()


@pytest.fixture
def api(migrated_db_url: str) -> Iterator[TestClient]:
    """Client acting as user A on a clean database. Pass headers=as_user(USER_B) to switch."""
    app = create_app(make_settings(database_url=migrated_db_url, dev_identity_enabled=True))
    with app.state.engine.begin() as c:
        c.execute(text("TRUNCATE users CASCADE"))
        for email in (USER_A, USER_B):
            uid = c.execute(
                text("INSERT INTO users (email) VALUES (:e) RETURNING id"), {"e": email}
            ).scalar()
            c.execute(text("INSERT INTO user_preferences (user_id) VALUES (:u)"), {"u": uid})
    with TestClient(app, raise_server_exceptions=False, headers=as_user(USER_A)) as c:
        yield c
    app.state.engine.dispose()
