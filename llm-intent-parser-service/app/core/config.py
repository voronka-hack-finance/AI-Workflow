"""Application configuration."""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    service_name: str = Field(default="llm-intent-parser-service", alias="INTENT_PARSER_SERVICE_NAME")
    service_port: int = Field(default=8011, alias="INTENT_PARSER_PORT")

    intent_parser_llm_provider: str = Field(default="openai_compatible", alias="INTENT_PARSER_LLM_PROVIDER")
    intent_parser_llm_model: str = Field(default="qwen3-8b", alias="INTENT_PARSER_LLM_MODEL")
    openai_compatible_base_url: str = Field(
        default="http://127.0.0.1:1234/v1",
        alias="OPENAI_COMPATIBLE_BASE_URL",
    )
    openai_compatible_api_key: str = Field(default="local", alias="OPENAI_COMPATIBLE_API_KEY")
    intent_parser_llm_temperature: float = Field(default=0.1, alias="INTENT_PARSER_LLM_TEMPERATURE")
    intent_parser_max_output_tokens: int = Field(default=1200, alias="INTENT_PARSER_MAX_OUTPUT_TOKENS")
    intent_parser_llm_timeout_seconds: int = Field(default=60, alias="INTENT_PARSER_LLM_TIMEOUT_SECONDS")
    intent_parser_few_shot_limit: int | None = Field(
        default=None,
        alias="INTENT_PARSER_FEW_SHOT_LIMIT",
        description="Max few-shot pairs. None=all, 0=system prompt only (recommended for local 7B).",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
