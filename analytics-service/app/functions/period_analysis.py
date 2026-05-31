"""PeriodAnalysis function."""
from __future__ import annotations

from app.builders.function_result_builder import FunctionResultBuilder
from app.functions.base import BaseAnalyticsFunction
from app.helpers import filters, grouping, money
from app.helpers.safe_math import safe_divide
from app.runner.function_context import FunctionContext


class PeriodAnalysis(BaseAnalyticsFunction):
    name = "period_analysis"

    def __init__(self) -> None:
        self._builder = FunctionResultBuilder()

    def run(self, ctx: FunctionContext):
        transactions = ctx.package.data.transactions
        if not transactions:
            return self._builder.empty(self.name, warnings=["No transactions in period."])

        income_tx = filters.income_transactions(transactions)
        expense_tx = filters.expense_transactions(transactions)
        total_income = money.sum_income(income_tx)
        total_expenses = money.sum_expenses(expense_tx)
        net_cashflow = total_income - total_expenses
        ratio = safe_divide(total_expenses, total_income, default=0.0) if total_income > 0 else None

        category_totals = grouping.group_by_category(expense_tx)
        merchant_totals = grouping.group_by_merchant(expense_tx)

        return self._builder.success(
            self.name,
            {
                "total_income": round(total_income, 2),
                "total_expenses": round(total_expenses, 2),
                "net_cashflow": round(net_cashflow, 2),
                "expenses_to_income_ratio": round(ratio, 4) if ratio is not None else None,
                "top_categories": grouping.top_n_items(category_totals),
                "top_merchants": grouping.top_n_items(merchant_totals),
                "largest_transactions": grouping.largest_transaction_summaries(transactions),
                "cashback_total": round(money.sum_cashback(transactions), 2),
                "rounding_to_savings_total": round(
                    money.sum_rounding_to_savings(transactions), 2
                ),
            },
            input_used={"transactions_count": len(transactions)},
        )
