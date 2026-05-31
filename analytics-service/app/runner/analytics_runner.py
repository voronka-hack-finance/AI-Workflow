"""Main analytics orchestrator."""
from __future__ import annotations

from shared_contracts.context_package import ContextPackage, ExecutionPlanItem
from shared_contracts.financial_analysis_result import FinancialAnalysisResult

from app.builders.financial_analysis_result_builder import FinancialAnalysisResultBuilder
from app.runner.execution_plan_runner import ExecutionPlanRunner
from app.runner.function_context import FunctionContext


class AnalyticsRunner:
    def __init__(
        self,
        plan_runner: ExecutionPlanRunner | None = None,
        result_builder: FinancialAnalysisResultBuilder | None = None,
    ) -> None:
        self._plan_runner = plan_runner or ExecutionPlanRunner()
        self._result_builder = result_builder or FinancialAnalysisResultBuilder()

    def run(self, package: ContextPackage) -> FinancialAnalysisResult:
        if not package.data_quality.can_run_analytics:
            return self._result_builder.build_blocked(package)

        functions = self._resolve_functions(package)
        if not functions:
            return self._result_builder.build_blocked(package)

        plan_steps = self._resolve_plan_steps(package, functions)
        ctx = FunctionContext(package=package)
        function_results = self._plan_runner.execute(ctx, plan_steps)
        executed = [step.function_name for step in plan_steps]
        return self._result_builder.build(
            package,
            executed_functions=executed,
            function_results=function_results,
        )

    def _resolve_functions(self, package: ContextPackage) -> list[str]:
        functions = list(package.analytics_request.functions_to_execute)
        if not functions:
            functions = list(package.context_builder.expanded_functions)
        return functions

    def _resolve_plan_steps(
        self,
        package: ContextPackage,
        functions_to_execute: list[str],
    ) -> list[ExecutionPlanItem]:
        allowed = set(functions_to_execute)
        execution_plan = package.context_builder.execution_plan
        if execution_plan:
            steps = [
                step
                for step in sorted(execution_plan, key=lambda s: s.step)
                if step.function_name in allowed
            ]
            planned_names = {step.function_name for step in steps}
            for idx, name in enumerate(functions_to_execute, start=len(steps) + 1):
                if name not in planned_names:
                    steps.append(
                        ExecutionPlanItem(step=idx, function_name=name, depends_on=[])
                    )
            return steps

        return [
            ExecutionPlanItem(step=idx, function_name=name, depends_on=[])
            for idx, name in enumerate(functions_to_execute, start=1)
        ]
