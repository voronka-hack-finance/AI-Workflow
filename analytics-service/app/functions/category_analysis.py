"""CategoryAnalysis function."""
from __future__ import annotations

from app.builders.function_result_builder import FunctionResultBuilder
from app.functions.base import BaseAnalyticsFunction
from app.helpers import filters, grouping, money
from app.runner.function_context import FunctionContext


class CategoryAnalysis(BaseAnalyticsFunction):
    name = "category_analysis"

    def __init__(self) -> None:
        self._builder = FunctionResultBuilder()

    def run(self, ctx: FunctionContext):
        expense_tx = filters.expense_transactions(ctx.package.data.transactions)
        profiles = grouping.category_profile_map(ctx.package.data.category_profiles)
        warnings: list[str] = []

        if not expense_tx:
            return self._builder.empty(self.name, warnings=["No expense transactions."])

        category_totals = grouping.group_by_category(expense_tx)
        total = money.sum_expenses(expense_tx)
        categories: list[dict] = []

        for cat, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            profile = profiles.get(cat)
            categories.append(
                {
                    "category": cat,
                    "amount": round(amount, 2),
                    "share": round(amount / total, 4) if total > 0 else 0.0,
                    "category_group": profile.category_group if profile else "unknown",
                    "can_optimize": profile.can_optimize if profile else True,
                    "protected_by_default": profile.protected_by_default if profile else False,
                }
            )

        optimizable = [c for c in categories if c.get("can_optimize") and not c.get("protected_by_default")]

        return self._builder.success(
            self.name,
            {
                "categories": categories,
                "optimizable_categories": optimizable[:5],
                "total_expenses": round(total, 2),
            },
            warnings=warnings or None,
        )
