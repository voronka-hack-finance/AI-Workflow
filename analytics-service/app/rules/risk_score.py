"""Risk score calculation."""
from __future__ import annotations


def calculate_risk_score(
    *,
    expenses_to_income_ratio: float | None,
    emergency_months: float | None,
    has_debt: bool,
    spending_leak_count: int,
) -> float:
    score = 0.0
    if expenses_to_income_ratio is not None:
        if expenses_to_income_ratio >= 1.0:
            score += 40
        elif expenses_to_income_ratio >= 0.85:
            score += 25
        elif expenses_to_income_ratio >= 0.7:
            score += 15
    if emergency_months is not None:
        if emergency_months < 1:
            score += 25
        elif emergency_months < 3:
            score += 15
    if has_debt:
        score += 20
    score += min(spending_leak_count * 5, 15)
    return min(score, 100.0)
