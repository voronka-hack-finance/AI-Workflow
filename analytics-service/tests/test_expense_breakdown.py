"""Expense breakdown tests."""
from app.functions.expense_breakdown import ExpenseBreakdown
from app.runner.function_context import FunctionContext


def test_expense_breakdown_categories(context_package_with_transactions):
    result = ExpenseBreakdown().run(FunctionContext(package=context_package_with_transactions))
    assert result.status == "success"
    breakdown = result.result["category_breakdown"]
    assert len(breakdown) == 2
    total = sum(item["amount"] for item in breakdown)
    assert total == 4794.0
