import pytest
from pydantic import ValidationError

from yadi.config import Settings


def test_missing_database_url_fails() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, environment="test")


def test_invalid_environment_fails() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, environment="staging-ish", database_url="x")


def test_dev_identity_rejected_in_production() -> None:
    with pytest.raises(ValidationError, match="dev identity"):
        Settings(
            _env_file=None,
            environment="production",
            database_url="postgresql+psycopg://u:p@h/db",
            dev_identity_enabled=True,
        )


def test_secrets_hidden_in_repr() -> None:
    s = Settings(
        _env_file=None, environment="test", database_url="postgresql+psycopg://u:secret@h/db"
    )
    assert "secret" not in repr(s)
