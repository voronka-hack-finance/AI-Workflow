"""Build ordered execution plan from expanded functions."""
from __future__ import annotations

from shared_contracts.context_package import ExecutionPlanItem

from app.registry.function_registry import FunctionRegistry


class ExecutionPlanBuilder:
    def __init__(self, registry: FunctionRegistry | None = None) -> None:
        self._registry = registry or FunctionRegistry()

    def build(self, expanded_functions: list[str]) -> list[ExecutionPlanItem]:
        plan: list[ExecutionPlanItem] = []
        for step, function_name in enumerate(expanded_functions, start=1):
            depends_on = self._registry.get_dependencies(function_name)
            plan.append(
                ExecutionPlanItem(
                    step=step,
                    function_name=function_name,
                    depends_on=depends_on,
                )
            )
        return plan
