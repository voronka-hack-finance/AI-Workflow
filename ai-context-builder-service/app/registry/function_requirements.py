"""Per-function data and field requirements."""
from __future__ import annotations

from shared_contracts.context_package import DataRequirements

_BASE_TRANSACTIONS = DataRequirements(hard_required_data=["transactions"])

FUNCTION_REQUIREMENTS: dict[str, DataRequirements] = {
    "period_analysis": _BASE_TRANSACTIONS,
    "expense_breakdown": _BASE_TRANSACTIONS,
    "income_analysis": _BASE_TRANSACTIONS,
    "transfer_analysis": _BASE_TRANSACTIONS,
    "cashflow_analysis": _BASE_TRANSACTIONS,
    "spending_leak_detection": DataRequirements(
        hard_required_data=["transactions"],
        soft_required_data=["category_profiles"],
    ),
    "emergency_fund_analysis": DataRequirements(
        hard_required_data=["transactions"],
        soft_required_data=["user_context"],
        soft_required_fields=["current_savings"],
    ),
    "debt_analysis": DataRequirements(
        hard_required_data=["transactions"],
        soft_required_data=["user_context"],
        soft_required_fields=["stable_monthly_income"],
        optional_enrichment_fields=["has_debt", "monthly_debt_payment", "debt_amount"],
    ),
    "category_analysis": DataRequirements(
        hard_required_data=["transactions"],
        hard_required_fields=["focus.category"],
    ),
    "budget_recommendation": DataRequirements(
        hard_required_data=["transactions"],
        soft_required_data=["user_context", "category_profiles"],
        soft_required_fields=["current_savings", "stable_monthly_income"],
        optional_enrichment_fields=["has_debt", "monthly_debt_payment", "debt_amount"],
    ),
    "goal_analysis": DataRequirements(
        hard_required_data=["transactions"],
        hard_required_fields=["goal.amount", "goal.deadline_months"],
        soft_required_fields=["current_savings", "stable_monthly_income"],
        optional_enrichment_fields=["has_debt", "monthly_debt_payment", "debt_amount"],
    ),
    "budget_plan": DataRequirements(
        hard_required_data=["transactions"],
        soft_required_data=["user_context", "category_profiles"],
        soft_required_fields=["stable_monthly_income"],
    ),
    "action_plan": DataRequirements(
        hard_required_data=["transactions"],
        soft_required_data=["user_context", "category_profiles"],
    ),
}

COMPARISON_DATA_REQUIREMENT = DataRequirements(
    hard_required_data=["previous_period_transactions"],
)

OPTIONAL_ENRICHMENT_DEFAULT = DataRequirements(
    optional_data=["existing_financial_analysis_result"],
)


def get_requirements(function_name: str) -> DataRequirements:
    return FUNCTION_REQUIREMENTS.get(function_name, _BASE_TRANSACTIONS)


def merge_requirements(requirements: list[DataRequirements]) -> DataRequirements:
    hard_data: set[str] = set()
    soft_data: set[str] = set()
    optional_data: set[str] = set()
    hard_fields: set[str] = set()
    soft_fields: set[str] = set()
    optional_fields: set[str] = set()

    for req in requirements:
        hard_data.update(req.hard_required_data)
        soft_data.update(req.soft_required_data)
        optional_data.update(req.optional_data)
        hard_fields.update(req.hard_required_fields)
        soft_fields.update(req.soft_required_fields)
        optional_fields.update(req.optional_enrichment_fields)

    return DataRequirements(
        hard_required_data=sorted(hard_data),
        soft_required_data=sorted(soft_data),
        optional_data=sorted(optional_data),
        hard_required_fields=sorted(hard_fields),
        soft_required_fields=sorted(soft_fields),
        optional_enrichment_fields=sorted(optional_fields),
    )
