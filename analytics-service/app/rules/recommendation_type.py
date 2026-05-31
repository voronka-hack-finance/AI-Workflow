"""Recommendation type selection."""
from __future__ import annotations


def select_recommendation_type(problem_tags: list[str]) -> str:
    if "debt_pressure" in problem_tags:
        return "debt_focus"
    if "spending_leaks" in problem_tags:
        return "cut_discretionary"
    if "high_expense_ratio" in problem_tags:
        return "reduce_expenses"
    if "low_emergency_fund" in problem_tags:
        return "build_emergency_fund"
    return "balanced_budget"
