"""Application settings, read once from the environment and validated at startup."""

from typing import Literal, Self

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../../.env", extra="ignore")

    environment: Literal["development", "test", "production"] = "development"
    database_url: SecretStr
    log_level: str = "INFO"
    dev_identity_enabled: bool = False
    gemini_api_key: SecretStr | None = None
    ai_model: str = "gemini-3.5-flash-lite"
    ai_daily_call_limit: int = 200
    worker_poll_seconds: float = 5
    vapid_public_key: str | None = None
    vapid_private_key: SecretStr | None = None
    vapid_subject: str = "mailto:admin@yadi.local"

    @model_validator(mode="after")
    def _no_dev_identity_in_production(self) -> Self:
        if self.environment == "production" and self.dev_identity_enabled:
            raise ValueError("dev identity must not be enabled in production")
        return self
