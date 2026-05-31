"""Application configuration."""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    service_name: str = Field(default="analytics-service", alias="ANALYTICS_SERVICE_NAME")
    service_port: int = Field(default=8013, alias="ANALYTICS_SERVICE_PORT")
    rules_version: str = Field(default="v1.0", alias="ANALYTICS_RULES_VERSION")
    default_currency: str = Field(default="RUB", alias="ANALYTICS_DEFAULT_CURRENCY")


@lru_cache
def get_settings() -> Settings:
    return Settings()
