"""TransferAnalysis function."""
from __future__ import annotations

from app.builders.function_result_builder import FunctionResultBuilder
from app.functions.base import BaseAnalyticsFunction
from app.helpers import filters, money
from app.helpers.safe_math import safe_divide
from app.runner.function_context import FunctionContext

_TRANSFER_KEYWORDS = ("перевод", "transfer", "p2p", "сбп", "между счетами")


class TransferAnalysis(BaseAnalyticsFunction):
    name = "transfer_analysis"

    def __init__(self) -> None:
        self._builder = FunctionResultBuilder()

    def run(self, ctx: FunctionContext):
        transactions = ctx.package.data.transactions
        if not transactions:
            return self._builder.empty(self.name, warnings=["No transactions."])

        transfer_tx = []
        for tx in transactions:
            label = (tx.category or tx.merchant or tx.description or "").lower()
            if any(kw in label for kw in _TRANSFER_KEYWORDS):
                transfer_tx.append(tx)

        total_volume = sum(abs(tx.operation_amount) for tx in transfer_tx)
        income_tx = filters.income_transactions(transactions)
        unclear_income = sum(
            tx.operation_amount
            for tx in transfer_tx
            if tx in income_tx or tx.direction == "income"
        )
        total_inflow = money.sum_income(income_tx) if income_tx else 0.0

        return self._builder.success(
            self.name,
            {
                "transfer_count": len(transfer_tx),
                "transfer_volume": round(total_volume, 2),
                "unclear_transfer_income": round(unclear_income, 2),
                "unclear_transfer_share": round(
                    safe_divide(unclear_income, total_inflow), 4
                )
                if total_inflow > 0
                else 0.0,
            },
            input_used={"transactions_count": len(transactions)},
        )
