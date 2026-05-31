"""AnalysisResult builder from function_results."""
from __future__ import annotations

from shared_contracts.common import FunctionResultStatus, RiskLevel
from shared_contracts.financial_analysis_result import AnalysisResult, FunctionResult


class AnalysisResultBuilder:
    def build(self, function_results: dict[str, FunctionResult]) -> AnalysisResult:
        budget = function_results.get("budget_recommendation")
        if budget and budget.status == FunctionResultStatus.SUCCESS and budget.result:
            return AnalysisResult(
                risk_score=float(budget.result.get("risk_score", 0.0)),
                risk_level=budget.result.get("risk_level") or RiskLevel.LOW,
                main_problem=budget.result.get("main_problem"),
                problem_tags=list(budget.result.get("problem_tags", [])),
                recommendation_type=budget.result.get("recommendation_type"),
                category_to_optimize=list(budget.result.get("category_to_optimize", [])),
                expected_savings=float(budget.result.get("expected_savings", 0.0)),
                priority=budget.result.get("priority"),
            )

        period = function_results.get("period_analysis")
        if period and period.status == FunctionResultStatus.SUCCESS and period.result:
            return AnalysisResult(
                main_problem="period_summary",
                expected_savings=0.0,
            )

        return AnalysisResult()
