"""Few-shot examples for intent parsing prompts."""
from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

HUMAN_INPUT_INSTRUCTION = "Parse this input into nested intent_result JSON only.\n\nInput:\n"

_BASE_INTENT: dict[str, Any] = {
    "primary_intent": "unknown",
    "intents": [],
    "intent_confidence": 0.9,
    "requested_functions": [],
    "period": {"type": "current_month", "start_date": None, "end_date": None},
    "comparison": {"enabled": False, "type": None, "start_date": None, "end_date": None},
    "focus": {
        "category": None,
        "categories": [],
        "merchant": None,
        "mcc": None,
        "card_id": None,
        "direction": "all",
    },
    "recommendation_horizon": None,
    "goal": {"name": None, "amount": None, "deadline_months": None},
    "budget_plan": {"horizon": None, "available_money": None, "mandatory_expenses": None},
    "debt": {"requested": False},
    "emergency_fund": {"requested": False},
    "style": {"agent_style": "balanced", "difficulty": "medium", "output_format": "chat_text"},
    "constraints": {"protected_categories": [], "allowed_to_cut": [], "max_cut_level": None},
    "clarification": {
        "required": False,
        "reason": None,
        "missing_fields": [],
        "question": None,
    },
}


def format_human_input(payload: dict[str, Any]) -> str:
    return HUMAN_INPUT_INSTRUCTION + json.dumps(payload, ensure_ascii=False, indent=2)


def _example_input(
    raw_message: str,
    *,
    current_date: str = "2026-05-29",
    timezone: str = "Europe/Moscow",
    chat_summary: str | None = None,
    last_6_messages: list[dict[str, Any]] | None = None,
    active_workflow: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "current_date": current_date,
        "timezone": timezone,
        "chat_summary": chat_summary,
        "last_6_messages": last_6_messages or [],
        "active_workflow": active_workflow,
        "raw_message": raw_message,
    }


def _example_output(**overrides: Any) -> str:
    payload = json.loads(json.dumps(_BASE_INTENT))
    payload.update(overrides)
    return json.dumps(payload, ensure_ascii=False)


def _pair(
    human_payload: dict[str, Any],
    *,
    output_overrides: dict[str, Any],
) -> list[HumanMessage | AIMessage]:
    return [
        HumanMessage(content=format_human_input(human_payload)),
        AIMessage(content=_example_output(**output_overrides)),
    ]


FEW_SHOT_EXAMPLES: list[HumanMessage | AIMessage] = []
FEW_SHOT_EXAMPLES += _pair(
    _example_input("Куда уходят деньги?"),
    output_overrides={
        "primary_intent": "expense_breakdown",
        "intents": ["expense_breakdown"],
        "intent_confidence": 0.93,
        "requested_functions": ["expense_breakdown"],
    },
)
FEW_SHOT_EXAMPLES += _pair(
    _example_input("Дай рекомендацию по бюджету на месяц."),
    output_overrides={
        "primary_intent": "budget_recommendation",
        "intents": ["budget_recommendation"],
        "intent_confidence": 0.94,
        "requested_functions": ["budget_recommendation"],
        "recommendation_horizon": "next_month",
    },
)
FEW_SHOT_EXAMPLES += _pair(
    _example_input("Смогу ли накопить на ноутбук?"),
    output_overrides={
        "primary_intent": "goal_analysis",
        "intents": ["goal_analysis"],
        "intent_confidence": 0.88,
        "requested_functions": ["goal_analysis"],
        "goal": {"name": "ноутбук", "amount": None, "deadline_months": None},
    },
)
FEW_SHOT_EXAMPLES += _pair(
    _example_input("Смогу ли накопить 120 тысяч на ноутбук за 6 месяцев?"),
    output_overrides={
        "primary_intent": "goal_analysis",
        "intents": ["goal_analysis"],
        "intent_confidence": 0.95,
        "requested_functions": ["goal_analysis"],
        "goal": {"name": "ноутбук", "amount": 120000, "deadline_months": 6},
    },
)
FEW_SHOT_EXAMPLES += _pair(
    _example_input("Что с фастфудом?"),
    output_overrides={
        "primary_intent": "category_analysis",
        "intents": ["category_analysis"],
        "intent_confidence": 0.91,
        "requested_functions": ["category_analysis"],
        "focus": {
            "category": "Фастфуд",
            "categories": ["Фастфуд"],
            "merchant": None,
            "mcc": None,
            "card_id": None,
            "direction": "expense",
        },
    },
)
FEW_SHOT_EXAMPLES += _pair(
    _example_input("Я стал тратить больше?"),
    output_overrides={
        "primary_intent": "expense_breakdown",
        "intents": ["expense_breakdown"],
        "intent_confidence": 0.9,
        "requested_functions": ["expense_breakdown"],
        "comparison": {
            "enabled": True,
            "type": "previous_period",
            "start_date": None,
            "end_date": None,
        },
    },
)
FEW_SHOT_EXAMPLES += _pair(
    _example_input(
        "А за неделю?",
        last_6_messages=[
            {"role": "user", "content": "Куда уходят деньги?"},
            {"role": "assistant", "content": "За текущий месяц..."},
        ],
    ),
    output_overrides={
        "primary_intent": "expense_breakdown",
        "intents": ["expense_breakdown"],
        "intent_confidence": 0.89,
        "requested_functions": ["expense_breakdown"],
        "period": {"type": "last_7_days", "start_date": None, "end_date": None},
    },
)
FEW_SHOT_EXAMPLES += _pair(
    _example_input(
        "120 тысяч за 6 месяцев",
        active_workflow={
            "workflow_run_id": "run_123",
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
        },
    ),
    output_overrides={
        "primary_intent": "goal_analysis",
        "intents": ["goal_analysis"],
        "intent_confidence": 0.93,
        "requested_functions": ["goal_analysis"],
        "goal": {"name": "ноутбук", "amount": 120000, "deadline_months": 6},
    },
)
FEW_SHOT_EXAMPLES += _pair(
    _example_input("Сколько я потратил за прошлую неделю?"),
    output_overrides={
        "primary_intent": "expense_breakdown",
        "intents": ["expense_breakdown"],
        "intent_confidence": 0.92,
        "requested_functions": ["expense_breakdown"],
        "period": {"type": "last_7_days", "start_date": None, "end_date": None},
        "focus": {
            "category": None,
            "merchant": None,
            "mcc": None,
            "card_id": None,
            "direction": "expense",
        },
    },
)


def select_few_shot_examples(limit: int | None) -> list[HumanMessage | AIMessage]:
    """Return up to `limit` human/assistant pairs. None = all, 0 = none."""
    if limit is None:
        return FEW_SHOT_EXAMPLES
    if limit <= 0:
        return []
    return FEW_SHOT_EXAMPLES[: limit * 2]
