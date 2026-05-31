"""DebtAnalysis function."""
from __future__ import annotations

from app.builders.function_result_builder import FunctionResultBuilder
from app.functions.base import BaseAnalyticsFunction
from app.helpers.safe_math import safe_divide
from app.runner.function_context import FunctionContext


class DebtAnalysis(BaseAnalyticsFunction):
    name = "debt_analysis"

    def __init__(self) -> None:
        self._builder = FunctionResultBuilder()

    def run(self, ctx: FunctionContext):
        user_ctx = ctx.package.data.user_context
        cashflow_prior = ctx.prior_result_data("cashflow_analysis")
        income_prior = ctx.prior_result_data("income_analysis")

        has_debt = bool(user_ctx.has_debt)
        debt_amount = user_ctx.debt_amount or 0.0
        monthly_payment = user_ctx.monthly_debt_payment or 0.0
        income_base = float(
            cashflow_prior.get("income_base")
            or income_prior.get("stable_income_estimate")
            or 0
        )

        payment_ratio = (
            safe_divide(monthly_payment, income_base) if income_base > 0 else None
        )

        if not has_debt and debt_amount <= 0 and monthly_payment <= 0:
            return self._builder.success(
                self.name,
                {
                    "has_debt": False,
                    "debt_amount": 0.0,
                    "monthly_debt_payment": 0.0,
                    "debt_to_income_ratio": 0.0,
                    "debt_pressure": "none",
                },
            )

        pressure = "low"
        if payment_ratio is not None:
            if payment_ratio >= 0.4:
                pressure = "high"
            elif payment_ratio >= 0.2:
                pressure = "medium"

        return self._builder.success(
            self.name,
            {
                "has_debt": has_debt or debt_amount > 0,
                "debt_amount": round(debt_amount, 2),
                "monthly_debt_payment": round(monthly_payment, 2),
                "debt_to_income_ratio": round(payment_ratio, 4) if payment_ratio else None,
                "debt_pressure": pressure,
            },
        )
