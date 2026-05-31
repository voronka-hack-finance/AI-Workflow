"""Map backend transaction DTO to TransactionNormalized."""
from __future__ import annotations

from shared_contracts.common import TransactionDirection
from shared_contracts.normalized_data import TransactionNormalized

from app.data_adapters.warnings import NormalizationWarnings
from app.schemas.backend_dto import BackendTransaction

KNOWN_CATEGORY_GROUPS: dict[str, str] = {
    "Фастфуд": "food_outside",
    "Рестораны": "food_outside",
    "Продукты": "essential_variable",
    "ЖКХ": "essential_fixed",
    "Зарплата": "financial_special",
}


class TransactionMapper:
    def map_many(
        self,
        items: list[BackendTransaction],
        warnings: NormalizationWarnings | None = None,
    ) -> list[TransactionNormalized]:
        collector = warnings or NormalizationWarnings()
        return [self.map_one(item, collector) for item in items]

    def map_one(
        self,
        item: BackendTransaction,
        warnings: NormalizationWarnings | None = None,
    ) -> TransactionNormalized:
        collector = warnings or NormalizationWarnings()
        direction = self._resolve_direction(item.type, item.sum)

        if item.ambiguous:
            collector.add_ambiguous_transaction(item.id)
            collector.add_warning(f"Ambiguous transaction: {item.id}")

        category = item.bankCategory
        if category and category not in KNOWN_CATEGORY_GROUPS:
            collector.add_unmapped_category(category)

        merchant = item.merchantName
        return TransactionNormalized(
            transaction_id=item.id,
            operation_datetime=item.date,
            payment_date=None,
            card_id=None,
            account_id=None,
            status=None,
            operation_amount=item.sum,
            operation_currency=item.currency,
            payment_amount=item.sum,
            payment_currency=item.currency,
            cashback=None,
            category=category,
            mcc=item.mccCode,
            description=merchant,
            merchant=merchant,
            counterparty=None,
            bonuses=None,
            rounding_to_savings=None,
            rounded_operation_amount=None,
            direction=direction,
        )

    def _resolve_direction(self, tx_type: str, amount: float) -> str:
        normalized = tx_type.strip().lower()
        if normalized in {"in", "income"}:
            return TransactionDirection.INCOME
        if normalized in {"out", "expense"}:
            return TransactionDirection.EXPENSE
        return TransactionDirection.INCOME if amount >= 0 else TransactionDirection.EXPENSE
