"""Development-only seed: one fixed user so the app can run before real auth exists (ADR-005)."""

from sqlalchemy import Engine, text

from yadi.config import Settings

DEV_EMAIL = "dev@yadi.local"


def seed_dev_user(engine: Engine, settings: Settings) -> bool:
    """Create the dev user and preferences; returns False (no-op) outside development."""
    if settings.environment != "development":
        return False
    with engine.begin() as conn:
        user_id = conn.execute(
            text(
                "INSERT INTO users (email) VALUES (:e) ON CONFLICT (email) DO NOTHING RETURNING id"
            ),
            {"e": DEV_EMAIL},
        ).scalar()
        if user_id is not None:
            conn.execute(text("INSERT INTO user_preferences (user_id) VALUES (:u)"), {"u": user_id})
    return True


if __name__ == "__main__":
    from yadi.db.session import create_db_engine

    cfg = Settings()
    print(
        "seeded dev user"
        if seed_dev_user(create_db_engine(cfg), cfg)
        else "skipped (not development)"
    )
