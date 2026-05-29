"""Base analytics function."""
from abc import ABC, abstractmethod


class BaseAnalyticsFunction(ABC):
    name: str = "base"

    @abstractmethod
    async def run(self, context: dict) -> dict:
        # TODO: implement
        return {}
