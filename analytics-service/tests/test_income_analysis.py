"""Income analysis tests."""
from app.functions.income_analysis import IncomeAnalysis
from app.runner.function_context import FunctionContext


def test_stable_income_from_user_context(context_package_with_transactions):
    result = IncomeAnalysis().run(FunctionContext(package=context_package_with_transactions))
    assert result.status == "success"
    assert result.result["stable_income_estimate"] == 85000.0
    assert result.result["income_base_type"] == "user_context"
