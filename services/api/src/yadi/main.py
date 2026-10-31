from fastapi import FastAPI

from yadi.config import Settings
from yadi.core.errors import install_error_handlers
from yadi.core.logging import configure_logging, install_request_middleware
from yadi.db.session import create_db_engine
from yadi.modules.assistant.ai.client import LlmClient
from yadi.modules.assistant.ai.gemini_client import GeminiLlmClient
from yadi.modules.assistant.router import router as assistant_router
from yadi.modules.health.router import router as health_router
from yadi.modules.preferences.router import router as preferences_router
from yadi.modules.scheduling.router import router as scheduling_router
from yadi.modules.tasks.router import router as tasks_router


def _build_llm_client(settings: Settings) -> LlmClient | None:
    """No key is a normal state: the app runs and capture falls back to the manual form."""
    key = settings.gemini_api_key.get_secret_value() if settings.gemini_api_key else ""
    return GeminiLlmClient(api_key=key, model=settings.ai_model) if key else None


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    configure_logging(settings.log_level)
    app = FastAPI(title="Yadi API", version="0.1.0")
    app.state.settings = settings
    app.state.engine = create_db_engine(settings)
    app.state.llm_client = _build_llm_client(settings)
    install_request_middleware(app)
    install_error_handlers(app)
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(tasks_router, prefix="/api/v1")
    app.include_router(preferences_router, prefix="/api/v1")
    app.include_router(assistant_router, prefix="/api/v1")
    app.include_router(scheduling_router, prefix="/api/v1")
    return app
