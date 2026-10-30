import uuid
from collections.abc import Iterator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError

from tests.conftest import DB_URL, make_settings
from yadi.db.seed import DEV_EMAIL, seed_dev_user


@pytest.fixture
def temp_db_url() -> Iterator[str]:
    """A throwaway database so migrations are tested from empty, never against dev data."""
    name = f"yadi_test_{uuid.uuid4().hex[:8]}"
    admin = create_engine(DB_URL, isolation_level="AUTOCOMMIT")
    with admin.connect() as c:
        c.execute(text(f'CREATE DATABASE "{name}"'))
    try:
        yield make_url(DB_URL).set(database=name).render_as_string(hide_password=False)
    finally:
        with admin.connect() as c:
            c.execute(text(f'DROP DATABASE "{name}" WITH (FORCE)'))
        admin.dispose()


def _cfg(url: str) -> Config:
    cfg = Config("alembic.ini")
    cfg.attributes["url"] = url
    return cfg


def test_upgrade_and_downgrade(temp_db_url: str) -> None:
    command.upgrade(_cfg(temp_db_url), "head")
    engine = create_engine(temp_db_url)
    assert {"users", "user_preferences"} <= set(inspect(engine).get_table_names())
    command.downgrade(_cfg(temp_db_url), "base")
    assert "users" not in inspect(engine).get_table_names()
    engine.dispose()


def test_constraints_enforced(temp_db_url: str) -> None:
    command.upgrade(_cfg(temp_db_url), "head")
    engine = create_engine(temp_db_url)
    with pytest.raises(IntegrityError), engine.begin() as c:
        c.execute(text("INSERT INTO user_preferences (user_id) VALUES (gen_random_uuid())"))
    with pytest.raises(IntegrityError), engine.begin() as c:
        c.execute(text("INSERT INTO users (email) VALUES ('a@b'), ('a@b')"))
    engine.dispose()


def test_seed_runs_only_in_development(temp_db_url: str) -> None:
    command.upgrade(_cfg(temp_db_url), "head")
    engine = create_engine(temp_db_url)
    assert seed_dev_user(engine, make_settings(environment="test")) is False
    assert seed_dev_user(engine, make_settings(environment="development")) is True
    assert seed_dev_user(engine, make_settings(environment="development")) is True  # idempotent
    with engine.connect() as c:
        assert (
            c.execute(text("SELECT count(*) FROM users WHERE email=:e"), {"e": DEV_EMAIL}).scalar()
            == 1
        )
        assert c.execute(text("SELECT count(*) FROM user_preferences")).scalar() == 1
    engine.dispose()
