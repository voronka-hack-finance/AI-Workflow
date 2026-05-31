"""Data quality builder tests."""
from shared_contracts.common import CalculationMode
from shared_contracts.context_package import ContextPackageData, DataRequirements
from shared_contracts.normalized_data import TransactionNormalized, UserFinancialContextNormalized

from app.builder.data_quality_builder import DataQualityBuilder
from app.data_adapters.warnings import NormalizationWarnings
from tests.conftest import goal_intent_full, goal_intent_missing_amount


def test_full_mode_when_requirements_met() -> None:
    builder = DataQualityBuilder()
    data = ContextPackageData()
    requirements = DataRequirements()
    quality = builder.build(
        data=data,
        requirements=requirements,
        intent_result=goal_intent_full(),
        normalization=NormalizationWarnings(),
    )
    assert quality.can_run_analytics is True
    assert quality.calculation_mode == CalculationMode.FULL


def test_partial_mode_for_missing_hard_fields() -> None:
    builder = DataQualityBuilder()
    data = ContextPackageData()
    requirements = DataRequirements(
        hard_required_fields=["goal.amount", "goal.deadline_months"],
    )
    quality = builder.build(
        data=data,
        requirements=requirements,
        intent_result=goal_intent_missing_amount(),
        normalization=NormalizationWarnings(),
    )
    assert quality.can_run_analytics is True
    assert quality.calculation_mode == CalculationMode.PARTIAL
    assert "goal.amount" in quality.missing_hard_required_fields


def test_partial_mode_for_missing_soft_fields() -> None:
    builder = DataQualityBuilder()
    data = ContextPackageData(
        transactions=[
            TransactionNormalized(
                operation_datetime="2026-05-10T18:25:00",
                operation_amount=-100,
                operation_currency="RUB",
                direction="expense",
            )
        ],
        user_context=UserFinancialContextNormalized(stable_monthly_income=85000),
    )
    requirements = DataRequirements(
        hard_required_data=["transactions"],
        soft_required_fields=["current_savings"],
    )
    quality = builder.build(
        data=data,
        requirements=requirements,
        intent_result=goal_intent_full(),
        normalization=NormalizationWarnings(),
    )
    assert quality.can_run_analytics is True
    assert quality.calculation_mode == CalculationMode.PARTIAL
    assert "current_savings" in quality.missing_soft_required_fields
