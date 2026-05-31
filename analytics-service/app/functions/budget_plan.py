"""BudgetPlan function."""
from __future__ import annotations

from app.builders.function_result_builder import FunctionResultBuilder
from app.functions.base import BaseAnalyticsFunction
from app.runner.function_context import FunctionContext


class BudgetPlan(BaseAnalyticsFunction):
    name = "budget_plan"

    def __init__(self) -> None:
        self._builder = FunctionResultBuilder()

    def run(self, ctx: FunctionContext):
        cashflow = ctx.prior_result_data("cashflow_analysis")
        budget = ctx.prior_result_data("budget_recommendation")
        expense = ctx.prior_result_data("expense_breakdown")

        income_base = float(cashflow.get("income_base", 0))
        total_expenses = float(
            expense.get("total_expenses") or cashflow.get("total_expenses", 0)
        )
        expected_savings = float(budget.get("expected_savings", 0))

        if income_base <= 0:
            return self._builder.needs_clarification(
                self.name,
                warnings=["income_base required for budget plan."],
            )

        recommended_limit = max(income_base - expected_savings, total_expenses * 0.9)

        return self._builder.success(
            self.name,
            {
                "horizon": "next_month",
                "income_base": round(income_base, 2),
                "current_expenses": round(total_expenses, 2),
                "recommended_spending_limit": round(recommended_limit, 2),
                "target_savings": round(expected_savings, 2),
                "categories_to_watch": list(budget.get("category_to_optimize", [])),
            },
        )
