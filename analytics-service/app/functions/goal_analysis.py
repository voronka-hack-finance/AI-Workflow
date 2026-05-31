"""GoalAnalysis function."""
from __future__ import annotations

from app.builders.function_result_builder import FunctionResultBuilder
from app.functions.base import BaseAnalyticsFunction
from app.helpers.safe_math import safe_divide
from app.runner.function_context import FunctionContext


class GoalAnalysis(BaseAnalyticsFunction):
    name = "goal_analysis"

    def __init__(self) -> None:
        self._builder = FunctionResultBuilder()

    def run(self, ctx: FunctionContext):
        user_ctx = ctx.package.data.user_context
        cashflow = ctx.prior_result_data("cashflow_analysis")
        budget = ctx.prior_result_data("budget_recommendation")

        goal_amount = user_ctx.goal_amount
        deadline_months = user_ctx.goal_deadline_months

        if goal_amount is None or goal_amount <= 0 or not deadline_months:
            return self._builder.needs_clarification(
                self.name,
                result={"missing_fields": ["goal_amount", "goal_deadline_months"]},
                warnings=["goal.amount and goal.deadline_months are required."],
            )

        current_savings = user_ctx.current_savings or 0.0
        remaining = max(goal_amount - current_savings, 0.0)
        required_monthly = safe_divide(remaining, deadline_months)
        net_cashflow = float(cashflow.get("net_cashflow", 0))
        expected_savings = float(budget.get("expected_savings", 0))
        potential_free = net_cashflow + expected_savings
        goal_gap = max(required_monthly - potential_free, 0.0)
        progress = safe_divide(current_savings, goal_amount) * 100 if goal_amount > 0 else 0.0

        if potential_free >= required_monthly:
            feasibility = "feasible"
        elif potential_free >= required_monthly * 0.5:
            feasibility = "challenging"
        else:
            feasibility = "unlikely"

        return self._builder.success(
            self.name,
            {
                "goal_amount": round(goal_amount, 2),
                "current_savings": round(current_savings, 2),
                "remaining_amount": round(remaining, 2),
                "required_monthly_saving": round(required_monthly, 2),
                "current_free_cashflow": round(net_cashflow, 2),
                "expected_savings_after_optimization": round(expected_savings, 2),
                "potential_free_cashflow": round(potential_free, 2),
                "goal_gap": round(goal_gap, 2),
                "goal_progress_percent": round(progress, 2),
                "goal_feasibility_status": feasibility,
                "missing_monthly_amount": round(goal_gap, 2),
            },
        )
