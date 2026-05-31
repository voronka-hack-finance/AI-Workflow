"""IncomeAnalysis function."""
from __future__ import annotations

from app.builders.function_result_builder import FunctionResultBuilder
from app.functions.base import BaseAnalyticsFunction
from app.helpers import filters, money
from app.helpers.safe_math import safe_divide
from app.runner.function_context import FunctionContext

_TRANSFER_KEYWORDS = ("перевод", "transfer", "p2p", "сбп", "между счетами")


class IncomeAnalysis(BaseAnalyticsFunction):
    name = "income_analysis"

    def __init__(self) -> None:
        self._builder = FunctionResultBuilder()

    def run(self, ctx: FunctionContext):
        income_tx = filters.income_transactions(ctx.package.data.transactions)
        user_ctx = ctx.package.data.user_context
        warnings: list[str] = []

        if not income_tx and user_ctx.stable_monthly_income is None:
            return self._builder.empty(self.name, warnings=["No income transactions in period."])

        total_inflow = money.sum_income(income_tx) if income_tx else 0.0
        stable_from_context = user_ctx.stable_monthly_income
        transfer_unclear = 0.0
        salary_income = 0.0
        bonus_income = 0.0
        interest_income = 0.0

        for tx in income_tx:
            label = (tx.category or tx.merchant or tx.description or "").lower()
            amount = tx.operation_amount
            if any(kw in label for kw in _TRANSFER_KEYWORDS):
                transfer_unclear += amount
            elif "зарплат" in label or "salary" in label:
                salary_income += amount
            elif "процент" in label or "interest" in label:
                interest_income += amount
            elif "прем" in label or "bonus" in label:
                bonus_income += amount

        if stable_from_context is not None and stable_from_context > 0:
            stable_estimate = stable_from_context
            income_base_type = "user_context"
        elif salary_income > 0:
            stable_estimate = salary_income
            income_base_type = "salary_transactions"
        else:
            stable_estimate = max(total_inflow - transfer_unclear, 0.0)
            income_base_type = "conservative_estimate"

        stable_share = safe_divide(stable_estimate, total_inflow) if total_inflow > 0 else 0.0
        unclear_share = safe_divide(transfer_unclear, total_inflow) if total_inflow > 0 else 0.0

        if unclear_share > 0.3:
            warnings.append("High share of unclear transfer income; stable income may be overstated.")
        if total_inflow <= 0:
            income_stability = "unknown"
        elif unclear_share > 0.5:
            income_stability = "unstable"
        elif stable_share >= 0.7:
            income_stability = "stable"
        else:
            income_stability = "moderate"

        return self._builder.success(
            self.name,
            {
                "total_inflow": round(total_inflow, 2),
                "stable_income_estimate": round(stable_estimate, 2),
                "stable_income_share": round(stable_share, 4),
                "income_base_type": income_base_type,
                "income_stability": income_stability,
                "interest_income": round(interest_income, 2),
                "bonus_income": round(bonus_income, 2),
                "confirmed_extra_income": round(bonus_income + interest_income, 2),
                "transfer_income_unclear": round(transfer_unclear, 2),
                "needs_user_clarification": unclear_share > 0.5,
                "income_sources": grouping_top_sources(income_tx),
            },
            input_used={"income_transactions_count": len(income_tx)},
            warnings=warnings or None,
        )


def grouping_top_sources(income_tx) -> list[dict[str, str | float]]:
    totals: dict[str, float] = {}
    for tx in income_tx:
        key = tx.category or tx.merchant or "unknown"
        totals[key] = totals.get(key, 0.0) + tx.operation_amount
    return [
        {"source": k, "amount": round(v, 2)}
        for k, v in sorted(totals.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
