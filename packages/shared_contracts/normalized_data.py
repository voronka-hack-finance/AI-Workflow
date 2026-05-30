"""Normalized data contract models."""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel

from shared_contracts.common import TransactionDirection


class CategoryGroup(StrEnum):
    ESSENTIAL_FIXED = "essential_fixed"
    ESSENTIAL_VARIABLE = "essential_variable"
    HEALTH = "health"
    TRANSPORT = "transport"
    FOOD_OUTSIDE = "food_outside"
    SHOPPING_LIFESTYLE = "shopping_lifestyle"
    ENTERTAINMENT = "entertainment"
    EDUCATION_DEVELOPMENT = "education_development"
    TRAVEL = "travel"
    FINANCIAL_SPECIAL = "financial_special"
    UNCLEAR_SPECIAL = "unclear_special"
    PENALTY = "penalty"
    UNKNOWN = "unknown"


class TransactionNormalized(BaseModel):
    transaction_id: str | None = None
    operation_datetime: str
    payment_date: str | None = None
    card_id: str | None = None
    account_id: str | None = None
    status: str | None = None
    operation_amount: float
    operation_currency: str
    payment_amount: float | None = None
    payment_currency: str | None = None
    cashback: float | None = None
    category: str | None = None
    mcc: str | None = None
    description: str | None = None
    merchant: str | None = None
    counterparty: str | None = None
    bonuses: float | None = None
    rounding_to_savings: float | None = None
    rounded_operation_amount: float | None = None
    direction: TransactionDirection | str


class UserFinancialContextNormalized(BaseModel):
    current_savings: float | None = None
    stable_monthly_income: float | None = None
    has_debt: bool | None = None
    monthly_debt_payment: float | None = None
    debt_amount: float | None = None
    financial_goal: str | None = None
    goal_amount: float | None = None
    goal_deadline_months: int | None = None
    salary_day: int | None = None
    current_balance: float | None = None


class CategoryProfile(BaseModel):
    category: str
    category_group: CategoryGroup | str
    can_optimize: bool = True
    protected_by_default: bool = False
    is_required_expense: bool = False
