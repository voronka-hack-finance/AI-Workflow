"""Tests for keyword intent hint correction."""
from __future__ import annotations

from app.parser.message_hints import apply_message_hints, build_message_intent_hints
from app.schemas.intent_request import IntentParseRequest
from shared_contracts.intent_result import IntentResult


def _request(message: str) -> IntentParseRequest:
    return IntentParseRequest.model_validate(
        {
            "request_id": "req_001",
            "user_id": "user_123",
            "chat_id": "chat_001",
            "raw_message": message,
            "current_date": "2026-05-30",
            "timezone": "Europe/Moscow",
        }
    )


def _expense_breakdown_intent(**overrides: object) -> IntentResult:
    payload = {
        "primary_intent": "expense_breakdown",
        "intents": [],
        "intent_confidence": 0.85,
        "requested_functions": ["expense_breakdown"],
        "period": {"type": "current_month", "start_date": None, "end_date": None},
        "focus": {
            "category": None,
            "merchant": None,
            "mcc": None,
            "card_id": None,
            "direction": "expense",
        },
    }
    payload.update(overrides)
    return IntentResult.model_validate(payload)


def test_build_message_intent_hints_fastfood() -> None:
    hints = build_message_intent_hints("сколько я потратил за вчера на фастфуд")
    assert hints is not None
    assert hints["requested_functions"] == ["category_analysis"]
    assert hints["focus"]["categories"] == ["Фастфуд"]
    assert hints["focus"]["category"] == "Фастфуд"


def test_apply_message_hints_overrides_expense_collapse_for_category() -> None:
    result = apply_message_hints(
        _request("сколько я потратил за вчера на фастфуд"),
        _expense_breakdown_intent(period={"type": "yesterday", "start_date": None, "end_date": None}),
    )
    assert result.requested_functions == ["category_analysis"]
    assert result.primary_intent == "category_analysis"
    assert result.focus.categories == ["Фастфуд"]
    assert result.focus.category == "Фастфуд"
    assert result.period.type == "yesterday"


def test_apply_message_hints_overrides_budget_recommendation() -> None:
    result = apply_message_hints(
        _request("Дай рекомендацию по бюджету на месяц"),
        _expense_breakdown_intent(),
    )
    assert result.requested_functions == ["budget_recommendation"]


def test_apply_message_hints_adds_optimization_functions_for_category_query() -> None:
    intent = IntentResult.model_validate(
        {
            "primary_intent": "category_analysis",
            "intents": ["category_analysis"],
            "requested_functions": ["category_analysis"],
            "focus": {
                "categories": ["Отели", "Кино"],
                "direction": "expense",
            },
            "recommendation_horizon": "next_7_days",
        }
    )
    message = (
        "сколько вчера ушло на Отели и Кино "
        "и что предлагаешь чтобы оптимизировать расходы"
    )
    result = apply_message_hints(_request(message), intent)
    assert result.requested_functions == [
        "category_analysis",
        "budget_recommendation",
        "action_plan",
    ]
    assert result.intents == [
        "category_analysis",
        "budget_recommendation",
        "action_plan",
    ]
    assert result.focus.categories == ["Отели", "Кино"]


def test_apply_message_hints_keeps_non_collapsed_llm_intent() -> None:
    intent = IntentResult.model_validate(
        {
            "primary_intent": "goal_analysis",
            "intents": ["goal_analysis"],
            "intent_confidence": 0.9,
            "requested_functions": ["goal_analysis"],
            "goal": {"name": "ноутбук", "amount": 120000, "deadline_months": 6},
        }
    )
    result = apply_message_hints(_request("Дай рекомендацию по бюджету на месяц"), intent)
    assert result.requested_functions == ["goal_analysis"]
