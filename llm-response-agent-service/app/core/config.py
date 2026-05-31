"""Application configuration."""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    service_name: str = Field(default="llm-response-agent-service", alias="RESPONSE_AGENT_SERVICE_NAME")
    service_port: int = Field(default=8014, alias="RESPONSE_AGENT_PORT")

    response_agent_llm_provider: str = Field(default="mock", alias="RESPONSE_AGENT_LLM_PROVIDER")
    response_agent_llm_model: str = Field(default="qwen2.5-7b-instruct", alias="RESPONSE_AGENT_LLM_MODEL")
    openai_compatible_base_url: str = Field(
        default="http://127.0.0.1:1234/v1",
        alias="OPENAI_COMPATIBLE_BASE_URL",
    )
    openai_compatible_api_key: str = Field(default="local", alias="OPENAI_COMPATIBLE_API_KEY")
    response_agent_llm_temperature: float = Field(default=0.2, alias="RESPONSE_AGENT_LLM_TEMPERATURE")
    response_agent_max_output_tokens: int = Field(default=3000, alias="RESPONSE_AGENT_MAX_OUTPUT_TOKENS")
    response_agent_llm_timeout_seconds: int = Field(default=120, alias="RESPONSE_AGENT_LLM_TIMEOUT_SECONDS")
    response_agent_max_selected_agents: int = Field(default=3, alias="RESPONSE_AGENT_MAX_SELECTED_AGENTS")


@lru_cache
def get_settings() -> Settings:
    return Settings()
