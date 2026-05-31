"""Transaction filter helpers."""
from __future__ import annotations

from shared_contracts.common import TransactionDirection
from shared_contracts.normalized_data import TransactionNormalized


def filter_by_direction(
    transactions: list[TransactionNormalized],
    direction: TransactionDirection | str,
) -> list[TransactionNormalized]:
    return [tx for tx in transactions if tx.direction == direction]


def income_transactions(transactions: list[TransactionNormalized]) -> list[TransactionNormalized]:
    return filter_by_direction(transactions, TransactionDirection.INCOME)


def expense_transactions(transactions: list[TransactionNormalized]) -> list[TransactionNormalized]:
    return filter_by_direction(transactions, TransactionDirection.EXPENSE)
