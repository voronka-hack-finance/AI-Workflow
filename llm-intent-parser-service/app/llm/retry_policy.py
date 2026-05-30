"""Retry policy for transient LLM errors."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


class LLMRetryPolicy:
    def __init__(self, max_retries: int = 2, delay_seconds: float = 0.5) -> None:
        self.max_retries = max_retries
        self.delay_seconds = delay_seconds

    async def run(self, operation: Callable[[], Awaitable[T]]) -> T:
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                return await operation()
            except Exception as exc:  # noqa: BLE001 - retry on provider failures
                last_error = exc
                if attempt >= self.max_retries:
                    break
                await asyncio.sleep(self.delay_seconds * (attempt + 1))
        assert last_error is not None
        raise last_error
