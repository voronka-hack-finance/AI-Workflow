"""Shared test fixtures."""
from __future__ import annotations

import os

os.environ.setdefault("CONTEXT_BUILDER_DATA_PROVIDER", "mock")

import pytest

from shared_contracts.common import PeriodType
from shared_contracts.context_package import SourceMessage
from shared_contracts.intent_result import (
    ComparisonInput,
    FocusInput,
    GoalInput,
    IntentResult,
    PeriodInput,
)

from app.schemas.context_builder_request import ContextBuilderRequest


@pytest.fixture(autouse=True)
def _force_mock_provider() -> None:
    os.environ["CONTEXT_BUILDER_DATA_PROVIDER"] = "mock"
    from app.builder.deps import get_context_builder_service
    from app.core.config import get_settings

    get_settings.cache_clear()
    get_context_builder_service.cache_clear()


def sample_source_message() -> SourceMessage:
    return SourceMessage(
        raw_message="Дай рекомендацию по бюджету на месяц.",
        current_date="2026-05-29",
        timezone="Europe/Moscow",
    )


def budget_intent() -> IntentResult:
    return IntentResult(
        primary_intent="budget_recommendation",
        intents=["budget_recommendation"],
        intent_confidence=0.92,
        requested_functions=["budget_recommendation"],
        period=PeriodInput(type=PeriodType.CURRENT_MONTH),
    )


def goal_intent_full() -> IntentResult:
    return IntentResult(
        primary_intent="goal_analysis",
        intents=["goal_analysis"],
        intent_confidence=0.9,
        requested_functions=["goal_analysis"],
        goal=GoalInput(name="ноутбук", amount=120000, deadline_months=6),
    )


def goal_intent_missing_amount() -> IntentResult:
    return IntentResult(
        primary_intent="goal_analysis",
        intents=["goal_analysis"],
        intent_confidence=0.8,
        requested_functions=["goal_analysis"],
        goal=GoalInput(name="ноутбук", amount=None, deadline_months=None),
    )


def comparison_intent() -> IntentResult:
    return IntentResult(
        primary_intent="expense_breakdown",
        intents=["expense_breakdown"],
        requested_functions=["expense_breakdown"],
        period=PeriodInput(type=PeriodType.CURRENT_MONTH),
        comparison=ComparisonInput(enabled=True),
    )


def category_intent_missing_focus() -> IntentResult:
    return IntentResult(
        primary_intent="category_analysis",
        intents=["category_analysis"],
        requested_functions=["category_analysis"],
        focus=FocusInput(category=None),
    )


def build_request(
    intent_result: IntentResult,
    *,
    user_id: str = "user_123",
) -> ContextBuilderRequest:
    return ContextBuilderRequest(
        request_id="req_001",
        workflow_run_id="run_001",
        user_id=user_id,
        chat_id="chat_001",
        source_message=sample_source_message(),
        intent_result=intent_result,
    )
