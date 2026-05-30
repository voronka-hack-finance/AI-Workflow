"""Clarification parsing tests."""

from app.parser.clarification import is_clarification_answer, merge_clarification_answer
from app.schemas.intent_request import IntentParseRequest
from shared_contracts.intent_result import IntentResult


def _request(**overrides: object) -> IntentParseRequest:
    payload = {
        "request_id": "req_001",
        "user_id": "user_123",
        "chat_id": "chat_001",
        "raw_message": "120 тысяч за 6 месяцев",
        "current_date": "2026-05-29",
        "timezone": "Europe/Moscow",
        "chat_context": {
            "active_workflow": {
                "status": "awaiting_user_input",
                "missing_fields": ["goal.amount", "goal.deadline_months"],
                "intent_result": {
                    "primary_intent": "goal_analysis",
                    "intents": ["goal_analysis"],
                    "requested_functions": ["goal_analysis"],
                    "goal": {"name": "ноутбук", "amount": None, "deadline_months": None},
                    "clarification": {
                        "required": True,
                        "reason": "missing_required_data",
                        "missing_fields": ["goal.amount", "goal.deadline_months"],
                        "question": "На какую сумму и за какой срок ты хочешь накопить на ноутбук?",
                    },
                },
            }
        },
    }
    payload.update(overrides)
    return IntentParseRequest.model_validate(payload)


def test_is_clarification_answer() -> None:
    assert is_clarification_answer(_request()) is True


def test_merge_clarification_answer_full_answer_clears_clarification() -> None:
    request = _request()
    parsed = IntentResult(
        goal={"name": "ноутбук", "amount": 120000, "deadline_months": 6},
        requested_functions=["goal_analysis"],
    )
    merged = merge_clarification_answer(request, parsed)
    assert merged.clarification.required is False
    assert merged.goal.amount == 120000
    assert merged.goal.deadline_months == 6
    assert merged.clarification.missing_fields == []


def test_merge_clarification_answer_partial_answer_keeps_clarification() -> None:
    request = _request(raw_message="120 тысяч")
    parsed = IntentResult(
        goal={"name": "ноутбук", "amount": 120000, "deadline_months": None},
        requested_functions=["goal_analysis"],
    )
    merged = merge_clarification_answer(request, parsed)
    assert merged.clarification.required is True
    assert merged.goal.amount == 120000
    assert merged.goal.deadline_months is None
    assert merged.clarification.missing_fields == ["goal.deadline_months"]
    assert merged.clarification.question is not None
