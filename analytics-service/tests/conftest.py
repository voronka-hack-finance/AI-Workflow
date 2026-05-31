"""Analytics service test fixtures."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from shared_contracts.common import CalculationMode, TransactionDirection
from shared_contracts.context_package import (
    AnalyticsRequest,
    AppliedFilters,
    ContextBuilderMetadata,
    ContextPackage,
    ContextPackageData,
    ContextPackageMetadata,
    DataQuality,
    ExecutionPlanItem,
    ResolvedComparison,
    ResolvedPeriod,
    SourceMessage,
)
from shared_contracts.intent_result import IntentResult
from shared_contracts.normalized_data import (
    CategoryProfile,
    TransactionNormalized,
    UserFinancialContextNormalized,
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _resolved_period() -> ResolvedPeriod:
    return ResolvedPeriod(
        type="current_month",
        start_date="2026-05-01",
        end_date="2026-05-31",
    )


def _execution_plan(functions: list[str]) -> list[ExecutionPlanItem]:
    return [
        ExecutionPlanItem(step=idx, function_name=name, depends_on=[])
        for idx, name in enumerate(functions, start=1)
    ]


@pytest.fixture
def sample_transactions() -> list[TransactionNormalized]:
    return [
        TransactionNormalized(
            transaction_id="tx_1",
            operation_datetime="2026-05-10T18:25:00",
            operation_amount=-1294.0,
            operation_currency="RUB",
            category="Фастфуд",
            merchant="Вкусно — и точка",
            mcc="5814",
            direction=TransactionDirection.EXPENSE,
        ),
        TransactionNormalized(
            transaction_id="tx_2",
            operation_datetime="2026-05-05T10:00:00",
            operation_amount=85000.0,
            operation_currency="RUB",
            category="Зарплата",
            merchant="Зарплата",
            direction=TransactionDirection.INCOME,
        ),
        TransactionNormalized(
            transaction_id="tx_3",
            operation_datetime="2026-05-12T14:30:00",
            operation_amount=-3500.0,
            operation_currency="RUB",
            category="Продукты",
            merchant="Пятёрочка",
            mcc="5411",
            direction=TransactionDirection.EXPENSE,
        ),
    ]


@pytest.fixture
def context_package_with_transactions(
    sample_transactions: list[TransactionNormalized],
) -> ContextPackage:
    functions = [
        "income_analysis",
        "expense_breakdown",
        "period_analysis",
        "cashflow_analysis",
        "budget_recommendation",
    ]
    return ContextPackage(
        request_id="req_test_001",
        workflow_run_id="run_test_001",
        user_id="user_123",
        chat_id="chat_001",
        source_message=SourceMessage(
            raw_message="Дай рекомендацию по бюджету.",
            current_date="2026-05-29",
            timezone="Europe/Moscow",
        ),
        intent_result=IntentResult(
            primary_intent="budget_recommendation",
            intents=["budget_recommendation"],
            intent_confidence=0.92,
            requested_functions=["budget_recommendation"],
        ),
        context_builder=ContextBuilderMetadata(
            requested_functions=["budget_recommendation"],
            expanded_functions=functions,
            execution_plan=_execution_plan(functions),
            resolved_period=_resolved_period(),
            resolved_comparison=ResolvedComparison(enabled=False),
            applied_filters=AppliedFilters(
                period={"start_date": "2026-05-01", "end_date": "2026-05-31"},
                direction="all",
            ),
        ),
        data=ContextPackageData(
            transactions=sample_transactions,
            user_context=UserFinancialContextNormalized(
                current_savings=45000.0,
                stable_monthly_income=85000.0,
                has_debt=False,
            ),
            category_profiles=[
                CategoryProfile(
                    category="Фастфуд",
                    category_group="food_outside",
                    can_optimize=True,
                ),
                CategoryProfile(
                    category="Продукты",
                    category_group="essential_variable",
                    can_optimize=True,
                    is_required_expense=True,
                ),
            ],
        ),
        data_quality=DataQuality(can_run_analytics=True),
        analytics_request=AnalyticsRequest(functions_to_execute=functions),
        metadata=ContextPackageMetadata(created_at="2026-05-29T12:00:00Z"),
    )


@pytest.fixture
def blocked_context_package() -> ContextPackage:
    return ContextPackage(
        request_id="req_blocked",
        workflow_run_id="run_blocked",
        user_id="user_123",
        chat_id="chat_001",
        source_message=SourceMessage(
            raw_message="test",
            current_date="2026-05-29",
            timezone="Europe/Moscow",
        ),
        intent_result=IntentResult(
            primary_intent="budget_recommendation",
            intents=["budget_recommendation"],
            intent_confidence=0.9,
            requested_functions=["budget_recommendation"],
        ),
        context_builder=ContextBuilderMetadata(
            requested_functions=["budget_recommendation"],
            expanded_functions=["budget_recommendation"],
            execution_plan=_execution_plan(["budget_recommendation"]),
            resolved_period=_resolved_period(),
            resolved_comparison=ResolvedComparison(enabled=False),
            applied_filters=AppliedFilters(
                period={"start_date": "2026-05-01", "end_date": "2026-05-31"},
            ),
        ),
        data_quality=DataQuality(
            can_run_analytics=False,
            calculation_mode=CalculationMode.CLARIFICATION_REQUIRED,
            missing_hard_required_data=["transactions"],
        ),
        analytics_request=AnalyticsRequest(
            functions_to_execute=["budget_recommendation"]
        ),
        metadata=ContextPackageMetadata(created_at="2026-05-29T12:00:00Z"),
    )
