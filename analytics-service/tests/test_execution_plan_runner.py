"""Execution plan runner tests."""
from app.runner.analytics_runner import AnalyticsRunner
from app.runner.execution_plan_runner import ExecutionPlanRunner
from app.runner.function_context import FunctionContext
from shared_contracts.context_package import ExecutionPlanItem


def test_execution_plan_preserves_order(context_package_with_transactions):
    runner = ExecutionPlanRunner()
    plan = [
        ExecutionPlanItem(step=1, function_name="income_analysis", depends_on=[]),
        ExecutionPlanItem(step=2, function_name="expense_breakdown", depends_on=[]),
        ExecutionPlanItem(step=3, function_name="period_analysis", depends_on=[]),
    ]
    ctx = FunctionContext(package=context_package_with_transactions)
    results = runner.execute(ctx, plan)
    assert list(results.keys()) == ["income_analysis", "expense_breakdown", "period_analysis"]
    assert results["period_analysis"].status == "success"


def test_analytics_runner_uses_functions_to_execute(context_package_with_transactions):
    result = AnalyticsRunner().run(context_package_with_transactions)
    assert result.request_id == "req_test_001"
    assert "period_analysis" in result.executed_functions
    assert len(result.function_results) >= 3
