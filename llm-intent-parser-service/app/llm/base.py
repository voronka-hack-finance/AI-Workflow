"""LLM provider protocol."""
from __future__ import annotations

from typing import Protocol

from langchain_core.messages import BaseMessage


class LLMProvider(Protocol):
    async def generate(self, messages: list[BaseMessage]) -> str:
        """Generate raw text response from chat messages."""
