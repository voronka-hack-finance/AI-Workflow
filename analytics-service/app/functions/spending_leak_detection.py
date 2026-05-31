"""SpendingLeakDetection function."""
from __future__ import annotations

from app.builders.function_result_builder import FunctionResultBuilder
from app.functions.base import BaseAnalyticsFunction
from app.runner.function_context import FunctionContext


class SpendingLeakDetection(BaseAnalyticsFunction):
    name = "spending_leak_detection"

    def __init__(self) -> None:
        self._builder = FunctionResultBuilder()

    def run(self, ctx: FunctionContext):
        expense_prior = ctx.prior_result_data("expense_breakdown")
        category_prior = ctx.prior_result_data("category_analysis")
        profiles = {
            p["category"]: p
            for p in category_prior.get("optimizable_categories", [])
            if isinstance(p, dict) and p.get("category")
        }

        breakdown = expense_prior.get("category_breakdown", [])
        if not breakdown:
            return self._builder.empty(
                self.name,
                warnings=["expense_breakdown result required for leak detection."],
            )

        leaks: list[dict] = []
        for item in breakdown:
            if not isinstance(item, dict):
                continue
            cat = item.get("category")
            share = float(item.get("share", 0))
            amount = float(item.get("amount", 0))
            if share >= 0.15 and cat and profiles.get(cat, {}).get("can_optimize", True):
                leaks.append(
                    {
                        "category": cat,
                        "amount": amount,
                        "share": share,
                        "leak_type": "high_concentration",
                    }
                )
            elif share >= 0.08 and amount >= 3000:
                leaks.append(
                    {
                        "category": cat,
                        "amount": amount,
                        "share": share,
                        "leak_type": "large_discretionary",
                    }
                )

        leaks = sorted(leaks, key=lambda x: x["amount"], reverse=True)[:5]

        return self._builder.success(
            self.name,
            {
                "leaks_detected": len(leaks),
                "leaks": leaks,
            },
        )
