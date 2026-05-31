"""Execution context passed to analytics functions."""
from __future__ import annotations

from dataclasses import dataclass, field

from shared_contracts.context_package import ContextPackage
from shared_contracts.financial_analysis_result import FunctionResult


@dataclass
class FunctionContext:
    package: ContextPackage
    prior_results: dict[str, FunctionResult] = field(default_factory=dict)

    def get_prior(self, function_name: str) -> FunctionResult | None:
        return self.prior_results.get(function_name)

    def prior_result_data(self, function_name: str) -> dict:
        prior = self.get_prior(function_name)
        if prior is None:
            return {}
        return prior.result if isinstance(prior.result, dict) else {}
