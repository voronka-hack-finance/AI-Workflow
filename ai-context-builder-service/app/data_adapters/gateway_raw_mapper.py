"""Map raw gateway / worker JSON into internal backend DTOs."""
from __future__ import annotations

from typing import Any

from app.schemas.backend_dto import (
    BackendCategoryProfile,
    BackendTransaction,
    BackendUserContext,
)


def _parse_amount(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", ".")
    if not text:
        return 0.0
    return float(text)


def _parse_optional_amount(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return _parse_amount(value)


def map_gateway_transaction(item: dict[str, Any]) -> BackendTransaction:
    if "operation_amount" in item:
        amount = _parse_amount(item.get("operation_amount"))
        tx_type = str(item.get("type", "expense")).lower()
        operation_at = item.get("operation_at") or item.get("payment_at") or ""
        date_value = str(operation_at)[:10] if operation_at else ""
        return BackendTransaction(
            id=str(item["id"]),
            sum=abs(amount),
            currency=str(item.get("operation_currency") or item.get("payment_currency") or "RUB"),
            type=tx_type,
            merchantName=item.get("description"),
            bankCategory=item.get("category_name"),
            mccCode=item.get("mcc"),
            date=date_value,
            ambiguous=False,
        )

    return BackendTransaction(
        id=str(item["id"]),
        sum=_parse_amount(item.get("sum")),
        currency=str(item.get("currency", "RUB")),
        type=str(item.get("type", "expense")),
        merchantName=item.get("merchantName"),
        bankCategory=item.get("bankCategory"),
        mccCode=item.get("mccCode"),
        date=str(item.get("date", "")),
        ambiguous=bool(item.get("ambiguous", False)),
    )


def map_transactions_page(payload: dict[str, Any] | None) -> list[BackendTransaction]:
    if not payload:
        return []
    items = payload.get("items") or []
    return [map_gateway_transaction(item) for item in items]


def map_user_context(payload: dict[str, Any] | None) -> BackendUserContext | None:
    if not payload:
        return None

    def pick(*keys: str) -> Any:
        for key in keys:
            if key in payload and payload[key] is not None:
                return payload[key]
        return None

    return BackendUserContext(
        currentSavings=_parse_optional_amount(pick("currentSavings", "current_savings")),
        stableMonthlyIncome=_parse_optional_amount(
            pick("stableMonthlyIncome", "stable_monthly_income")
        ),
        hasDebt=pick("hasDebt", "has_debt"),
        monthlyDebtPayment=_parse_optional_amount(
            pick("monthlyDebtPayment", "monthly_debt_payment")
        ),
        debtAmount=_parse_optional_amount(pick("debtAmount", "debt_amount")),
        financialGoal=pick("financialGoal", "financial_goal"),
        goalAmount=_parse_optional_amount(pick("goalAmount", "goal_amount")),
        goalDeadlineMonths=pick("goalDeadlineMonths", "goal_deadline_months"),
        salaryDay=pick("salaryDay", "salary_day"),
        currentBalance=_parse_optional_amount(pick("currentBalance", "current_balance")),
    )


def map_category_profiles(items: list[dict[str, Any]] | None) -> list[BackendCategoryProfile]:
    if not items:
        return []
    profiles: list[BackendCategoryProfile] = []
    for item in items:
        profiles.append(
            BackendCategoryProfile(
                category=str(item.get("category", "")),
                categoryGroup=item.get("categoryGroup") or item.get("category_group"),
                canOptimize=bool(item.get("canOptimize", item.get("can_optimize", True))),
                protectedByDefault=bool(
                    item.get("protectedByDefault", item.get("protected_by_default", False))
                ),
                isRequiredExpense=bool(
                    item.get("isRequiredExpense", item.get("is_required_expense", False))
                ),
            )
        )
    return profiles
