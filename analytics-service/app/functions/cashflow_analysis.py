"""CashflowAnalysis function."""
from __future__ import annotations

from app.builders.function_result_builder import FunctionResultBuilder
from app.functions.base import BaseAnalyticsFunction
from app.helpers import filters, money
from app.helpers.safe_math import safe_divide
from app.runner.function_context import FunctionContext


class CashflowAnalysis(BaseAnalyticsFunction):
    name = "cashflow_analysis"

    def __init__(self) -> None:
        self._builder = FunctionResultBuilder()

    def run(self, ctx: FunctionContext):
        transactions = ctx.package.data.transactions
        user_ctx = ctx.package.data.user_context
        income_prior = ctx.prior_result_data("income_analysis")
        expense_prior = ctx.prior_result_data("expense_breakdown")
        period_prior = ctx.prior_result_data("period_analysis")

        total_inflow = income_prior.get("total_inflow")
        if total_inflow is None:
            total_inflow = money.sum_income(filters.income_transactions(transactions))
        total_expenses = expense_prior.get("total_expenses")
        if total_expenses is None:
            total_expenses = money.sum_expenses(filters.expense_transactions(transactions))
        if total_expenses is None and period_prior:
            total_expenses = period_prior.get("total_expenses", 0.0)

        net_cashflow = float(total_inflow or 0) - float(total_expenses or 0)

        if user_ctx.stable_monthly_income and user_ctx.stable_monthly_income > 0:
            income_base = user_ctx.stable_monthly_income
            income_base_type = "user_context"
        elif income_prior.get("stable_income_estimate"):
            income_base = float(income_prior["stable_income_estimate"])
            income_base_type = income_prior.get("income_base_type", "income_analysis")
        else:
            income_base = float(total_inflow or 0)
            income_base_type = "conservative_estimate"

        ratio = (
            safe_divide(float(total_expenses or 0), income_base)
            if income_base > 0
            else None
        )
        margin = safe_divide(net_cashflow, income_base) if income_base > 0 else None

        if income_base <= 0:
            cashflow_status = "unknown"
        elif net_cashflow < 0:
            cashflow_status = "deficit"
        elif margin is not None and margin < 0.1:
            cashflow_status = "tight"
        else:
            cashflow_status = "positive"

        warnings: list[str] | None = None
        if income_base <= 0:
            warnings = ["income_base unavailable; cashflow metrics are limited."]

        return self._builder.success(
            self.name,
            {
                "income_base": round(income_base, 2),
                "income_base_type": income_base_type,
                "total_inflow": round(float(total_inflow or 0), 2),
                "total_expenses": round(float(total_expenses or 0), 2),
                "net_cashflow": round(net_cashflow, 2),
                "expenses_to_income_ratio": round(ratio, 4) if ratio is not None else None,
                "cashflow_margin": round(margin, 4) if margin is not None else None,
                "cashflow_status": cashflow_status,
                "comparison": {},
            },
            warnings=warnings,
        )
