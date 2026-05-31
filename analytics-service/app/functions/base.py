"""Base analytics function."""
from __future__ import annotations

from abc import ABC, abstractmethod

from shared_contracts.financial_analysis_result import FunctionResult

from app.runner.function_context import FunctionContext


class BaseAnalyticsFunction(ABC):
    name: str = "base"

    @abstractmethod
    def run(self, ctx: FunctionContext) -> FunctionResult:
        """Execute analytics function and return FunctionResult."""
