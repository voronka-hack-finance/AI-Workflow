"""Money aggregation helpers."""
from __future__ import annotations

from shared_contracts.normalized_data import TransactionNormalized


def sum_amounts(transactions: list[TransactionNormalized]) -> float:
    return sum(tx.operation_amount for tx in transactions)


def sum_income(transactions: list[TransactionNormalized]) -> float:
    return sum_amounts(transactions)


def sum_expenses(transactions: list[TransactionNormalized]) -> float:
    return sum(abs(tx.operation_amount) for tx in transactions)


def sum_cashback(transactions: list[TransactionNormalized]) -> float:
    return sum(tx.cashback or 0.0 for tx in transactions)


def sum_rounding_to_savings(transactions: list[TransactionNormalized]) -> float:
    return sum(tx.rounding_to_savings or 0.0 for tx in transactions)
