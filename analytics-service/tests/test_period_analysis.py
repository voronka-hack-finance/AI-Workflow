"""Period analysis formula tests."""
from app.functions.period_analysis import PeriodAnalysis
from app.runner.function_context import FunctionContext


def test_period_analysis_formulas(context_package_with_transactions):
    result = PeriodAnalysis().run(FunctionContext(package=context_package_with_transactions))
    assert result.status == "success"
    data = result.result
    assert data["total_income"] == 85000.0
    assert data["total_expenses"] == 4794.0
    assert data["net_cashflow"] == 80206.0
    assert data["expenses_to_income_ratio"] is not None


def test_period_analysis_empty_transactions(blocked_context_package):
    blocked_context_package.data.transactions = []
    blocked_context_package.data_quality.can_run_analytics = True
    result = PeriodAnalysis().run(FunctionContext(package=blocked_context_package))
    assert result.status == "empty_result"
