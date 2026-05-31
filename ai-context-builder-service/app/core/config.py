"""Application configuration."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    service_port: int = 8012
    context_builder_data_provider: str = "mock"
    context_builder_backend_data_timeout_seconds: float = 30.0
    rabbitmq_url: str = "amqp://guest:guest@localhost:5673/"
    rabbitmq_backend_data_request_queue: str = "ai.backend.data.requests"
    rabbitmq_backend_data_response_queue: str = "ai.context_builder.backend_data.responses"


@lru_cache
def get_settings() -> Settings:
    return Settings()
