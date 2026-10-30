from alembic import context
from sqlalchemy import create_engine

from yadi.config import Settings


def _url() -> str:
    # Tests pass an explicit URL; normal runs read validated settings.
    return context.config.attributes.get("url") or Settings().database_url.get_secret_value()  # type: ignore[call-arg]


engine = create_engine(_url())
with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=None)
    with context.begin_transaction():
        context.run_migrations()
