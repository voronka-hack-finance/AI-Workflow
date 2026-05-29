"""Application configuration."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    service_port: int = 8010

    # Service URLs (workflow orchestrator)
    intent_parser_service_url: str = "http://localhost:8011"
    context_builder_service_url: str = "http://localhost:8012"
    analytics_service_url: str = "http://localhost:8013"
    response_agent_service_url: str = "http://localhost:8014"
    rabbitmq_url: str = "amqp://finance_ai:finance_ai@localhost:5672/"
    ai_workflow_max_concurrency: int = 3
    ai_workflow_timeout_seconds: int = 120


@lru_cache
def get_settings() -> Settings:
    # TODO: validate required secrets in production
    return Settings()
