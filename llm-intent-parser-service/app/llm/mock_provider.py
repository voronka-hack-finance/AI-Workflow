"""Deterministic mock LLM provider for tests and CI."""
from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import BaseMessage, HumanMessage

from app.parser.message_hints import _parse_amount, _parse_deadline_months, build_message_intent_hints
from app.schemas.chat_context import ActiveWorkflow
from app.schemas.intent_request import IntentParseRequest
from shared_contracts.common import MVP_ANALYTICS_FUNCTIONS


def _default_intent_result() -> dict[str, Any]:
    return {
        "primary_intent": "unknown",
        "intents": [],
        "intent_confidence": 0.5,
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
        "style": {
            "agent_style": "balanced",
            "difficulty": "medium",
            "output_format": "chat_text",
        },
        "constraints": {
            "protected_categories": [],
            "allowed_to_cut": [],
            "max_cut_level": None,
        },
        "clarification": {
            "required": False,
            "reason": None,
            "missing_fields": [],
            "question": None,
        },
    }


def _with_functions(primary: str, functions: list[str], **overrides: Any) -> dict[str, Any]:
    result = _default_intent_result()
    result["primary_intent"] = primary
    result["intents"] = functions
    result["intent_confidence"] = 0.92
    result["requested_functions"] = functions
    result.update(overrides)
    return result


def build_mock_intent_result(request: IntentParseRequest) -> dict[str, Any]:
    message = request.raw_message.strip()
    workflow = request.active_workflow_state()

    if workflow and workflow.status == "awaiting_user_input":
        prior = workflow.intent_result
        prior_dict: dict[str, Any]
        if prior is None:
            prior_dict = _default_intent_result()
        elif hasattr(prior, "model_dump"):
            prior_dict = prior.model_dump()
        else:
            prior_dict = dict(prior)

        goal = dict(prior_dict.get("goal") or {})
        amount = _parse_amount(message)
        deadline = _parse_deadline_months(message)
        if amount is not None:
            goal["amount"] = amount
        if deadline is not None:
            goal["deadline_months"] = deadline

        return _with_functions(
            prior_dict.get("primary_intent", "goal_analysis"),
            prior_dict.get("requested_functions") or ["goal_analysis"],
            goal=goal,
        )

    hints = build_message_intent_hints(message)
    if hints is not None:
        result = _default_intent_result()
        result.update(hints)
        return result

    return _default_intent_result()


class MockProvider:
    def __init__(self, request: IntentParseRequest | None = None) -> None:
        self._request = request

    def bind_request(self, request: IntentParseRequest) -> MockProvider:
        self._request = request
        return self

    async def generate(self, messages: list[BaseMessage]) -> str:
        request = self._request
        if request is None:
            for message in reversed(messages):
                if isinstance(message, HumanMessage):
                    request = IntentParseRequest(
                        request_id="mock-req",
                        user_id="mock-user",
                        chat_id="mock-chat",
                        raw_message=str(message.content),
                        current_date="2026-05-29",
                    )
                    break
        if request is None:
            payload = _default_intent_result()
        else:
            payload = build_mock_intent_result(request)
        for fn in payload.get("requested_functions", []):
            if fn not in MVP_ANALYTICS_FUNCTIONS:
                raise ValueError(f"Unknown MVP analytics function: {fn}")
        return json.dumps(payload, ensure_ascii=False)

    @staticmethod
    def extract_request_context(messages: list[BaseMessage]) -> tuple[str | None, ActiveWorkflow | None]:
        del messages
        return None, None
