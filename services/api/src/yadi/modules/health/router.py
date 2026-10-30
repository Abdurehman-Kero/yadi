from fastapi import APIRouter, Request
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from yadi.core.errors import AppError

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness: the process is up. Never touches the database."""
    return {"status": "ok"}


@router.get("/health/ready")
def ready(request: Request) -> dict[str, str]:
    """Readiness: the database answers a trivial query."""
    engine: Engine = request.app.state.engine
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise AppError("SERVICE_UNAVAILABLE", 503, "Database is not available.") from exc
    return {"status": "ok", "database": "ok"}
