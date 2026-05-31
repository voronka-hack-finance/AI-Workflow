"""Cashflow analysis tests."""
from app.functions.cashflow_analysis import CashflowAnalysis
from app.functions.expense_breakdown import ExpenseBreakdown
from app.functions.income_analysis import IncomeAnalysis
from app.runner.function_context import FunctionContext
from shared_contracts.financial_analysis_result import FunctionResult, FunctionResultMetadata


def test_income_base_cascade(context_package_with_transactions):
    ctx = FunctionContext(package=context_package_with_transactions)
    income = IncomeAnalysis().run(ctx)
    expense = ExpenseBreakdown().run(ctx)
    ctx.prior_results = {
        "income_analysis": income,
        "expense_breakdown": expense,
    }
    result = CashflowAnalysis().run(ctx)
    assert result.status == "success"
    assert result.result["income_base"] == 85000.0
    assert result.result["cashflow_status"] == "positive"


def test_cashflow_unknown_when_no_income_base(blocked_context_package):
    blocked_context_package.data.transactions = []
    blocked_context_package.data.user_context.stable_monthly_income = None
    blocked_context_package.data_quality.can_run_analytics = True
    ctx = FunctionContext(package=blocked_context_package)
    ctx.prior_results = {
        "income_analysis": FunctionResult(
            function_name="income_analysis",
            status="empty_result",
            metadata=FunctionResultMetadata(calculated_at="2026-01-01T00:00:00Z"),
        ),
    }
    result = CashflowAnalysis().run(ctx)
    assert result.result["cashflow_status"] == "unknown"
