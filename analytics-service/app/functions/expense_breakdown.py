"""ExpenseBreakdown function."""
from __future__ import annotations

from app.builders.function_result_builder import FunctionResultBuilder
from app.functions.base import BaseAnalyticsFunction
from app.helpers import filters, grouping, money
from app.helpers.safe_math import safe_divide
from app.runner.function_context import FunctionContext


class ExpenseBreakdown(BaseAnalyticsFunction):
    name = "expense_breakdown"

    def __init__(self) -> None:
        self._builder = FunctionResultBuilder()

    def run(self, ctx: FunctionContext):
        expense_tx = filters.expense_transactions(ctx.package.data.transactions)
        warnings: list[str] = []
        if not ctx.package.data.category_profiles:
            warnings.append("category_profiles missing; breakdown uses raw categories only.")

        if not expense_tx:
            return self._builder.empty(
                self.name,
                warnings=["No expense transactions in period."],
            )

        total_expenses = money.sum_expenses(expense_tx)
        category_totals = grouping.group_by_category(expense_tx)
        merchant_totals = grouping.group_by_merchant(expense_tx)
        mcc_totals = grouping.group_by_mcc(expense_tx)

        category_breakdown = [
            {
                "category": cat,
                "amount": round(amt, 2),
                "share": round(safe_divide(amt, total_expenses), 4),
            }
            for cat, amt in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        ]

        return self._builder.success(
            self.name,
            {
                "total_expenses": round(total_expenses, 2),
                "category_breakdown": category_breakdown,
                "merchant_breakdown": grouping.top_n_items(merchant_totals, n=10),
                "mcc_breakdown": grouping.top_n_items(mcc_totals, n=10),
                "top_expense_categories": grouping.top_n_items(category_totals),
                "top_expense_transactions": grouping.largest_transaction_summaries(
                    expense_tx
                ),
                "spending_concentration": grouping.spending_concentration(category_totals),
            },
            input_used={"expense_transactions_count": len(expense_tx)},
            warnings=warnings or None,
        )
