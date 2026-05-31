"""ActionPlan function."""
from __future__ import annotations

from app.builders.function_result_builder import FunctionResultBuilder
from app.functions.base import BaseAnalyticsFunction
from app.runner.function_context import FunctionContext


class ActionPlan(BaseAnalyticsFunction):
    name = "action_plan"

    def __init__(self) -> None:
        self._builder = FunctionResultBuilder()

    def run(self, ctx: FunctionContext):
        budget = ctx.prior_result_data("budget_recommendation")
        leaks = ctx.prior_result_data("spending_leak_detection")
        emergency = ctx.prior_result_data("emergency_fund_analysis")

        if not budget:
            return self._builder.needs_clarification(
                self.name,
                warnings=["budget_recommendation required for action plan."],
            )

        actions: list[dict[str, str]] = []
        rec_type = budget.get("recommendation_type", "balanced_budget")
        categories = budget.get("category_to_optimize", [])

        if categories:
            actions.append(
                {
                    "action": "reduce_spending",
                    "target": ", ".join(categories[:3]),
                    "detail": f"Focus on categories from {rec_type} recommendation.",
                }
            )

        for leak in leaks.get("leaks", [])[:2]:
            if isinstance(leak, dict) and leak.get("category"):
                actions.append(
                    {
                        "action": "review_leak",
                        "target": leak["category"],
                        "detail": f"High spending share: {leak.get('share', 0)}",
                    }
                )

        if emergency.get("emergency_fund_status") in ("low", "critical"):
            actions.append(
                {
                    "action": "build_emergency_fund",
                    "target": "savings",
                    "detail": f"Months covered: {emergency.get('months_covered', 0)}",
                }
            )

        if not actions:
            actions.append(
                {
                    "action": "maintain_budget",
                    "target": "general",
                    "detail": "No critical issues detected.",
                }
            )

        return self._builder.success(
            self.name,
            {
                "actions": actions,
                "priority": str(budget.get("priority", "medium")),
            },
        )
