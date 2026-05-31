"""EmergencyFundAnalysis function."""
from __future__ import annotations

from app.builders.function_result_builder import FunctionResultBuilder
from app.functions.base import BaseAnalyticsFunction
from app.helpers.safe_math import safe_divide
from app.runner.function_context import FunctionContext


class EmergencyFundAnalysis(BaseAnalyticsFunction):
    name = "emergency_fund_analysis"

    def __init__(self) -> None:
        self._builder = FunctionResultBuilder()

    def run(self, ctx: FunctionContext):
        user_ctx = ctx.package.data.user_context
        expense_prior = ctx.prior_result_data("expense_breakdown")
        cashflow_prior = ctx.prior_result_data("cashflow_analysis")

        current_savings = user_ctx.current_savings or user_ctx.current_balance or 0.0
        monthly_expenses = float(
            expense_prior.get("total_expenses")
            or cashflow_prior.get("total_expenses")
            or 0
        )

        if monthly_expenses <= 0:
            return self._builder.empty(
                self.name,
                warnings=["Cannot estimate emergency fund without monthly expenses."],
            )

        months_covered = safe_divide(current_savings, monthly_expenses)
        target_months = 3.0
        gap = max(target_months * monthly_expenses - current_savings, 0.0)

        status = "adequate"
        if months_covered < 1:
            status = "critical"
        elif months_covered < 3:
            status = "low"

        return self._builder.success(
            self.name,
            {
                "current_savings": round(current_savings, 2),
                "monthly_expenses": round(monthly_expenses, 2),
                "months_covered": round(months_covered, 2),
                "target_months": target_months,
                "emergency_fund_gap": round(gap, 2),
                "emergency_fund_status": status,
            },
        )
