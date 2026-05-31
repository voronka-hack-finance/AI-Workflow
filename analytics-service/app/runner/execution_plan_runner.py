"""Executes analytics functions in plan order."""
from __future__ import annotations

from shared_contracts.context_package import ExecutionPlanItem
from shared_contracts.financial_analysis_result import FunctionResult

from app.builders.function_result_builder import FunctionResultBuilder
from app.runner.function_context import FunctionContext
from app.runner.function_registry import FunctionRegistry


class ExecutionPlanRunner:
    def __init__(
        self,
        registry: FunctionRegistry | None = None,
        result_builder: FunctionResultBuilder | None = None,
    ) -> None:
        self._registry = registry or FunctionRegistry()
        self._result_builder = result_builder or FunctionResultBuilder()

    def execute(
        self,
        ctx: FunctionContext,
        plan_steps: list[ExecutionPlanItem],
    ) -> dict[str, FunctionResult]:
        results: dict[str, FunctionResult] = {}
        for step in plan_steps:
            name = step.function_name
            fn = self._registry.get(name)
            if fn is None:
                results[name] = self._result_builder.error(
                    name,
                    warnings=[f"Unknown analytics function: {name}"],
                )
                continue
            step_ctx = FunctionContext(
                package=ctx.package,
                prior_results=dict(ctx.prior_results),
            )
            step_ctx.prior_results.update(results)
            try:
                results[name] = fn.run(step_ctx)
            except Exception as exc:  # noqa: BLE001
                results[name] = self._result_builder.error(
                    name,
                    warnings=[f"Function execution failed: {exc}"],
                )
        return results
