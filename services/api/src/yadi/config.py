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

    @model_validator(mode="after")
    def _no_dev_identity_in_production(self) -> Self:
        if self.environment == "production" and self.dev_identity_enabled:
            raise ValueError("dev identity must not be enabled in production")
        return self
