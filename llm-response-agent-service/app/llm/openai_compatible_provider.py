"""OpenAI-compatible LLM provider via LangChain ChatOpenAI."""
from __future__ import annotations

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

from app.core.config import Settings
from app.llm.retry_policy import LLMRetryPolicy


class OpenAICompatibleProvider:
    def __init__(self, settings: Settings, retry_policy: LLMRetryPolicy | None = None) -> None:
        self._client = ChatOpenAI(
            model=settings.response_agent_llm_model,
            base_url=settings.openai_compatible_base_url,
            api_key=settings.openai_compatible_api_key,
            temperature=settings.response_agent_llm_temperature,
            max_tokens=settings.response_agent_max_output_tokens,
            timeout=settings.response_agent_llm_timeout_seconds,
            max_retries=0,
        )
        self._retry_policy = retry_policy or LLMRetryPolicy()

    async def generate(self, messages: list[BaseMessage]) -> str:
        async def _invoke() -> str:
            response = await self._client.ainvoke(messages)
            content = response.content
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts: list[str] = []
                for item in content:
                    if isinstance(item, str):
                        parts.append(item)
                    elif isinstance(item, dict) and item.get("type") == "text":
                        parts.append(str(item.get("text", "")))
                return "".join(parts)
            return str(content)

        return await self._retry_policy.run(_invoke)
