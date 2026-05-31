"""Intent parser service smoke/regression tests."""
import pytest

from app.parser.service import IntentParserService
from app.schemas.intent_request import IntentParseRequest
from shared_contracts.intent_result import IntentResult


def _request(message: str, **overrides: object) -> IntentParseRequest:
    payload = {
        "request_id": "req_001",
        "user_id": "user_123",
        "chat_id": "chat_001",
        "raw_message": message,
        "current_date": "2026-05-29",
        "timezone": "Europe/Moscow",
    }
    payload.update(overrides)
    return IntentParseRequest.model_validate(payload)


def _goal_clarification_workflow() -> dict[str, object]:
    prior_intent = IntentResult(
        primary_intent="goal_analysis",
        intents=["goal_analysis"],
        requested_functions=["goal_analysis"],
        goal={"name": "ноутбук", "amount": None, "deadline_months": None},
        clarification={
            "required": True,
            "reason": "missing_required_data",
            "missing_fields": ["goal.amount", "goal.deadline_months"],
            "question": "На какую сумму и за какой срок ты хочешь накопить?",
        },
    )
    return {
        "workflow_run_id": "run_123",
        "status": "awaiting_user_input",
        "missing_fields": ["goal.amount", "goal.deadline_months"],
        "intent_result": prior_intent.model_dump(),
    }


@pytest.mark.asyncio
async def test_expense_question(service: IntentParserService) -> None:
    response = await service.parse(_request("Куда уходят деньги?"))
    assert response.intent_result.requested_functions == ["expense_breakdown"]


@pytest.mark.asyncio
async def test_budget_recommendation(service: IntentParserService) -> None:
    response = await service.parse(_request("Дай рекомендацию по бюджету на месяц"))
    assert response.intent_result.requested_functions == ["budget_recommendation"]
    assert response.intent_result.period.type == "current_month"


@pytest.mark.asyncio
async def test_goal_with_full_data(service: IntentParserService) -> None:
    response = await service.parse(
        _request("Смогу ли накопить 120 тысяч на ноутбук за 6 месяцев?")
    )
    assert "goal_analysis" in response.intent_result.requested_functions
    assert response.intent_result.clarification.required is False
    assert response.intent_result.goal.amount == 120000
    assert response.intent_result.goal.deadline_months == 6


@pytest.mark.asyncio
async def test_saving_question_does_not_require_clarification(service: IntentParserService) -> None:
    response = await service.parse(_request("как сэкономить мне?"))
    assert "action_plan" in response.intent_result.requested_functions
    assert response.intent_result.clarification.required is False


@pytest.mark.asyncio
async def test_goal_with_missing_data(service: IntentParserService) -> None:
    response = await service.parse(_request("Смогу ли накопить на ноутбук?"))
    assert "goal_analysis" in response.intent_result.requested_functions
    assert response.intent_result.clarification.required is False


@pytest.mark.asyncio
async def test_active_workflow_goal_merge(service: IntentParserService) -> None:
    response = await service.parse(
        _request(
            "120 тысяч за 6 месяцев",
            chat_context={"active_workflow": _goal_clarification_workflow()},
        )
    )
    assert response.intent_result.goal.amount == 120000
    assert response.intent_result.goal.deadline_months == 6
    assert response.intent_result.clarification.required is False


@pytest.mark.asyncio
async def test_follow_up_period(service: IntentParserService) -> None:
    response = await service.parse(
        _request(
            "а за неделю?",
            chat_context={
                "last_6_messages": [
                    {"role": "user", "content": "Куда уходят деньги?"},
                    {"role": "assistant", "content": "За текущий месяц..."},
                ]
            },
        )
    )
    assert response.intent_result.period.type == "last_7_days"


@pytest.mark.asyncio
async def test_category_focus(service: IntentParserService) -> None:
    response = await service.parse(_request("Что с фастфудом?"))
    assert response.intent_result.requested_functions == ["category_analysis"]
    assert response.intent_result.focus.category == "Фастфуд"
    assert response.intent_result.focus.direction == "expense"


@pytest.mark.asyncio
async def test_comparison_scenario(service: IntentParserService) -> None:
    response = await service.parse(_request("Я стал тратить больше?"))
    assert response.intent_result.requested_functions == ["expense_breakdown"]
    assert response.intent_result.comparison.enabled is True
