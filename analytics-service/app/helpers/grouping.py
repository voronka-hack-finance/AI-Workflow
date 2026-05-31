"""Grouping helpers for transactions."""
from __future__ import annotations

from collections import defaultdict

from shared_contracts.normalized_data import CategoryProfile, TransactionNormalized

from app.helpers.money import sum_expenses


def group_sum_by_key(
    transactions: list[TransactionNormalized],
    key_fn,
) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for tx in transactions:
        key = key_fn(tx) or "unknown"
        totals[key] += abs(tx.operation_amount)
    return dict(totals)


def group_by_category(transactions: list[TransactionNormalized]) -> dict[str, float]:
    return group_sum_by_key(transactions, lambda tx: tx.category or "unknown")


def group_by_merchant(transactions: list[TransactionNormalized]) -> dict[str, float]:
    return group_sum_by_key(transactions, lambda tx: tx.merchant or "unknown")


def group_by_mcc(transactions: list[TransactionNormalized]) -> dict[str, float]:
    return group_sum_by_key(transactions, lambda tx: tx.mcc or "unknown")


def top_n_items(totals: dict[str, float], n: int = 5) -> list[dict[str, float | str]]:
    sorted_items = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    return [{"name": name, "amount": amount} for name, amount in sorted_items[:n]]


def spending_concentration(category_totals: dict[str, float]) -> float:
    total = sum(category_totals.values())
    if total <= 0:
        return 0.0
    if not category_totals:
        return 0.0
    top_share = max(category_totals.values()) / total
    return round(top_share, 4)


def category_profile_map(
    profiles: list[CategoryProfile],
) -> dict[str, CategoryProfile]:
    return {p.category: p for p in profiles}


def largest_transaction_summaries(
    transactions: list[TransactionNormalized],
    n: int = 3,
) -> list[dict[str, str | float | None]]:
    sorted_tx = sorted(transactions, key=lambda tx: abs(tx.operation_amount), reverse=True)
    summaries: list[dict[str, str | float | None]] = []
    for tx in sorted_tx[:n]:
        summaries.append(
            {
                "transaction_id": tx.transaction_id,
                "operation_datetime": tx.operation_datetime,
                "amount": abs(tx.operation_amount),
                "category": tx.category,
                "merchant": tx.merchant,
                "direction": str(tx.direction),
            }
        )
    return summaries


def expense_total(transactions: list[TransactionNormalized]) -> float:
    return sum_expenses(transactions)
