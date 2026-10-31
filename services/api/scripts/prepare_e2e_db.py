"""Recreate the dedicated end-to-end database (`yadi_e2e`), migrated and seeded."""

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from yadi.config import Settings
from yadi.db.seed import seed_dev_user


def main() -> None:
    settings = Settings()
    url = make_url(settings.database_url.get_secret_value())
    if url.database != "yadi_e2e":
        raise SystemExit("Refusing to run: DATABASE_URL must point at yadi_e2e.")

    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text("DROP DATABASE IF EXISTS yadi_e2e WITH (FORCE)"))
        conn.execute(text("CREATE DATABASE yadi_e2e"))
    admin.dispose()

    cfg = Config("alembic.ini")
    cfg.attributes["url"] = url.render_as_string(hide_password=False)
    command.upgrade(cfg, "head")
    engine = create_engine(url)
    seed_dev_user(engine, settings)
    engine.dispose()


if __name__ == "__main__":
    main()
