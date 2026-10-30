"""Database engine creation. Sessions are opened per unit of work by services, not routers."""

from sqlalchemy import Engine, create_engine

from yadi.config import Settings


def create_db_engine(settings: Settings) -> Engine:
    return create_engine(
        settings.database_url.get_secret_value(),
        pool_pre_ping=True,
        # Fail fast instead of hanging; also avoids long waits on unreachable hosts.
        connect_args={"connect_timeout": 5},
    )
