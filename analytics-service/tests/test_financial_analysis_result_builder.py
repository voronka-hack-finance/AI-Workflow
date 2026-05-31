"""Financial analysis result builder tests."""
from shared_contracts.common import FunctionResultStatus
from shared_contracts.financial_analysis_result import FunctionResult, FunctionResultMetadata

from app.builders.financial_analysis_result_builder import FinancialAnalysisResultBuilder
from app.runner.analytics_runner import AnalyticsRunner


def test_analysis_result_from_budget_recommendation(context_package_with_transactions):
    result = AnalyticsRunner().run(context_package_with_transactions)
    budget = result.function_results.get("budget_recommendation")
    assert budget is not None
    if budget.status == FunctionResultStatus.SUCCESS:
        assert result.analysis_result.risk_score == budget.result.get("risk_score", 0)


def test_builder_blocked(blocked_context_package):
    built = FinancialAnalysisResultBuilder().build_blocked(blocked_context_package)
    assert built.executed_functions == []
    assert built.function_results == {}


def test_function_result_metadata():
    fr = FunctionResult(
        function_name="test",
        status="success",
        metadata=FunctionResultMetadata(calculated_at="2026-05-29T12:00:00Z"),
    )
    assert fr.metadata.rules_version == "v1.0"
