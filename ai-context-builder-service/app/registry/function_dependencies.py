"""Analytics function dependency graph."""
from __future__ import annotations

from shared_contracts.common import MVP_ANALYTICS_FUNCTIONS

FUNCTION_DEPENDENCIES: dict[str, list[str]] = {
    "period_analysis": [],
    "expense_breakdown": [],
    "income_analysis": [],
    "transfer_analysis": [],
    "category_analysis": [],
    "cashflow_analysis": ["income_analysis", "expense_breakdown"],
    "spending_leak_detection": ["expense_breakdown"],
    "emergency_fund_analysis": ["expense_breakdown", "cashflow_analysis"],
    "debt_analysis": ["income_analysis", "cashflow_analysis"],
    "budget_recommendation": [
        "income_analysis",
        "expense_breakdown",
        "cashflow_analysis",
        "transfer_analysis",
        "spending_leak_detection",
        "emergency_fund_analysis",
        "debt_analysis",
    ],
    "goal_analysis": ["income_analysis", "cashflow_analysis"],
    "budget_plan": ["income_analysis", "cashflow_analysis"],
    "action_plan": [
        "income_analysis",
        "expense_breakdown",
        "cashflow_analysis",
        "budget_recommendation",
    ],
}

REGISTRY_VERSION = "v1.0"


def get_dependencies(function_name: str) -> list[str]:
    if function_name not in MVP_ANALYTICS_FUNCTIONS:
        raise ValueError(f"Unknown MVP analytics function: {function_name}")
    return list(FUNCTION_DEPENDENCIES.get(function_name, []))
