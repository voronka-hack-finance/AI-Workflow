"""LLM provider factory."""
from __future__ import annotations

from app.core.config import Settings, get_settings
from app.llm.base import LLMProvider
from app.llm.mock_provider import MockProvider
from app.llm.openai_compatible_provider import OpenAICompatibleProvider
from app.llm.retry_policy import LLMRetryPolicy


def create_llm_provider(settings: Settings | None = None) -> LLMProvider:
    config = settings or get_settings()
    provider_name = config.response_agent_llm_provider.strip().lower()
    retry_policy = LLMRetryPolicy()

    if provider_name == "mock":
        return MockProvider()
    if provider_name == "openai_compatible":
        return OpenAICompatibleProvider(config, retry_policy=retry_policy)

    raise ValueError(
        f"Unsupported RESPONSE_AGENT_LLM_PROVIDER: {provider_name}. "
        "Allowed values: mock, openai_compatible"
    )
