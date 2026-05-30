"""Application configuration."""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    ai_workflow_service_name: str = Field(
        default="ai-workflow-service",
        validation_alias="AI_WORKFLOW_SERVICE_NAME",
    )
    ai_workflow_port: int = Field(default=8010, validation_alias="AI_WORKFLOW_PORT")
    service_port: int = Field(default=8010, validation_alias="AI_WORKFLOW_SERVICE_PORT")

    rabbitmq_url: str = Field(
        default="amqp://finance_ai:finance_ai@localhost:5672/",
        validation_alias="RABBITMQ_URL",
    )
    rabbitmq_workflow_queue: str = Field(
        default="ai.workflow.tasks",
        validation_alias="RABBITMQ_WORKFLOW_QUEUE",
    )
    rabbitmq_prefetch_count: int = Field(default=3, validation_alias="RABBITMQ_PREFETCH_COUNT")

    ai_workflow_max_concurrent_runs: int = Field(
        default=3,
        validation_alias="AI_WORKFLOW_MAX_CONCURRENT_RUNS",
    )
    ai_workflow_http_timeout_seconds: float = Field(
        default=30.0,
        validation_alias="AI_WORKFLOW_HTTP_TIMEOUT_SECONDS",
    )
    ai_workflow_http_max_retries: int = Field(
        default=2,
        validation_alias="AI_WORKFLOW_HTTP_MAX_RETRIES",
    )
    intent_parser_http_timeout_seconds: float = Field(
        default=150.0,
        validation_alias="INTENT_PARSER_HTTP_TIMEOUT_SECONDS",
    )

    intent_parser_service_url: str = Field(
        default="http://localhost:8011",
        validation_alias="INTENT_PARSER_SERVICE_URL",
    )
    context_builder_service_url: str = Field(
        default="http://localhost:8012",
        validation_alias="CONTEXT_BUILDER_SERVICE_URL",
    )
    analytics_service_url: str = Field(
        default="http://localhost:8013",
        validation_alias="ANALYTICS_SERVICE_URL",
    )
    response_agent_service_url: str = Field(
        default="http://localhost:8014",
        validation_alias="RESPONSE_AGENT_SERVICE_URL",
    )
    ai_workflow_enable_rabbitmq_consumer: bool = Field(
        default=True,
        validation_alias="AI_WORKFLOW_ENABLE_RABBITMQ_CONSUMER",
    )
    ai_workflow_enable_http_trigger: bool = Field(
        default=True,
        validation_alias="AI_WORKFLOW_ENABLE_HTTP_TRIGGER",
    )

    @property
    def port(self) -> int:
        return self.ai_workflow_port or self.service_port


@lru_cache
def get_settings() -> Settings:
    return Settings()
