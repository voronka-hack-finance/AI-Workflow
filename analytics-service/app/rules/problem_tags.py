"""Problem tag derivation."""
from __future__ import annotations


def derive_problem_tags(
    *,
    expenses_to_income_ratio: float | None,
    emergency_months: float | None,
    has_debt: bool,
    spending_leak_count: int,
) -> list[str]:
    tags: list[str] = []
    if expenses_to_income_ratio is not None and expenses_to_income_ratio >= 0.85:
        tags.append("high_expense_ratio")
    if emergency_months is not None and emergency_months < 3:
        tags.append("low_emergency_fund")
    if has_debt:
        tags.append("debt_pressure")
    if spending_leak_count > 0:
        tags.append("spending_leaks")
    return tags
