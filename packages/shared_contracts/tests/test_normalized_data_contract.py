"""Normalized data contract tests."""
import pytest
from pydantic import ValidationError

from shared_contracts.normalized_data import (
    CategoryProfile,
    TransactionNormalized,
    UserFinancialContextNormalized,
)
from conftest import minimal_transaction


def test_transaction_normalized_can_be_created() -> None:
    tx = minimal_transaction()
    assert tx.transaction_id == "tx_1"
    assert tx.direction == "expense"


def test_user_financial_context_normalized_defaults() -> None:
    ctx = UserFinancialContextNormalized()
    assert ctx.current_savings is None
    assert ctx.has_debt is None


def test_category_profile_can_be_created() -> None:
    profile = CategoryProfile(category="Фастфуд", category_group="food_outside")
    assert profile.can_optimize is True


def test_transaction_normalized_requires_operation_datetime() -> None:
    with pytest.raises(ValidationError):
        TransactionNormalized(
            operation_amount=100,
            operation_currency="RUB",
            direction="expense",
        )
