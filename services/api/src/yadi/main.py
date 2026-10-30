from fastapi import FastAPI

from yadi.config import Settings
from yadi.core.errors import install_error_handlers
from yadi.core.logging import configure_logging, install_request_middleware
from yadi.db.session import create_db_engine
from yadi.modules.health.router import router as health_router


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    configure_logging(settings.log_level)
    app = FastAPI(title="Yadi API", version="0.1.0")
    app.state.settings = settings
    app.state.engine = create_db_engine(settings)
    install_request_middleware(app)
    install_error_handlers(app)
    app.include_router(health_router, prefix="/api/v1")
    return app
