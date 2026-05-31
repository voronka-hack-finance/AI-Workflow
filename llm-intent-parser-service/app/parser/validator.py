"""Validate and sanitize parsed intent_result payloads."""
from __future__ import annotations

from typing import Any

from pydantic import ValidationError as PydanticValidationError

from app.core.errors import LLMParseError
from app.parser.category_normalizer import normalize_focus_category
from shared_contracts.intent_result import IntentResult, validate_mvp_function_name

_FORBIDDEN_FIELDS = {
    "expanded_functions",
    "execution_plan",
    "data_requirements",
    "function_results",
    "financial_analysis_result",
    "final_answer",
}

_DEFAULT_GOAL: dict[str, Any] = {"name": None, "amount": None, "deadline_months": None}
_DEFAULT_BUDGET_PLAN: dict[str, Any] = {
    "horizon": None,
    "available_money": None,
    "mandatory_expenses": None,
}
_DEFAULT_STYLE: dict[str, Any] = {
    "agent_style": "balanced",
    "difficulty": "medium",
    "output_format": "chat_text",
}
_DEFAULT_CONSTRAINTS: dict[str, Any] = {
    "protected_categories": [],
    "allowed_to_cut": [],
    "max_cut_level": None,
}
_DEFAULT_CLARIFICATION: dict[str, Any] = {
    "required": False,
    "reason": None,
    "missing_fields": [],
    "question": None,
}


def _normalize_null_object(payload: dict[str, Any], field: str, default: dict[str, Any]) -> None:
    if payload.get(field) is None:
        payload[field] = default.copy()


def _normalize_style(payload: dict[str, Any]) -> None:
    style = payload.get("style")
    if isinstance(style, str):
        payload["style"] = {
            **_DEFAULT_STYLE,
            "agent_style": style,
        }
        return
    if isinstance(style, dict):
        payload["style"] = {**_DEFAULT_STYLE, **style}


def _normalize_constraints(payload: dict[str, Any]) -> None:
    constraints = payload.get("constraints")
    if isinstance(constraints, list):
        payload["constraints"] = {
            **_DEFAULT_CONSTRAINTS,
            "protected_categories": [item for item in constraints if isinstance(item, str)],
        }
        return
    if isinstance(constraints, dict):
        payload["constraints"] = {**_DEFAULT_CONSTRAINTS, **constraints}


def _normalize_clarification(payload: dict[str, Any]) -> None:
    payload["clarification"] = _DEFAULT_CLARIFICATION.copy()


def _normalize_intents(payload: dict[str, Any], requested_functions: list[str]) -> None:
    intents = payload.get("intents")
    if not isinstance(intents, list):
        intents = []

    intent_set = {item for item in intents if isinstance(item, str)}
    primary_intent = payload.get("primary_intent", "unknown")
    if isinstance(primary_intent, str) and primary_intent and primary_intent != "unknown":
        intent_set.add(primary_intent)

    if not intent_set:
        intent_set.update(requested_functions)
    else:
        for function_name in requested_functions:
            if function_name in intent_set:
                continue
            if function_name == "budget_recommendation" and "action_plan" in intent_set:
                intent_set.add(function_name)
            elif function_name == "action_plan" and "budget_recommendation" in intent_set:
                intent_set.add(function_name)

    payload["intents"] = sorted(intent_set)


def _normalize_llm_payload(payload: dict[str, Any], requested_functions: list[str]) -> dict[str, Any]:
    """Coerce common local-LLM schema mistakes before contract validation."""
    normalized = dict(payload)
    _normalize_null_object(normalized, "goal", _DEFAULT_GOAL)
    _normalize_null_object(normalized, "budget_plan", _DEFAULT_BUDGET_PLAN)
    _normalize_style(normalized)
    _normalize_constraints(normalized)
    _normalize_clarification(normalized)
    _normalize_intents(normalized, requested_functions)
    normalize_focus_category(normalized)
    return normalized


def _validate_no_dependency_leak(payload: dict[str, Any], requested_functions: list[str]) -> None:
    intents = payload.get("intents", [])
    if not isinstance(intents, list):
        raise LLMParseError("intents must be a list")

    primary_intent = payload.get("primary_intent", "unknown")
    allowed_intents = {intent for intent in intents if isinstance(intent, str)}
    if isinstance(primary_intent, str) and primary_intent and primary_intent != "unknown":
        allowed_intents.add(primary_intent)

    if not allowed_intents:
        return

    extra_functions = sorted(set(requested_functions) - allowed_intents)
    if extra_functions:
        raise LLMParseError(
            "requested_functions contains dependencies not present in intents: "
            + ", ".join(extra_functions)
        )


def validate_intent_payload(payload: dict[str, Any]) -> IntentResult:
    forbidden = sorted(field for field in payload if field in _FORBIDDEN_FIELDS)
    if forbidden:
        raise LLMParseError(f"Forbidden intent_result fields: {', '.join(forbidden)}")

    requested_functions = payload.get("requested_functions", [])
    if not isinstance(requested_functions, list):
        raise LLMParseError("requested_functions must be a list")

    sanitized_functions: list[str] = []
    for function_name in requested_functions:
        if not isinstance(function_name, str):
            raise LLMParseError("requested_functions must contain strings")
        try:
            sanitized_functions.append(validate_mvp_function_name(function_name))
        except ValueError as exc:
            raise LLMParseError(str(exc)) from exc

    normalized = _normalize_llm_payload(payload, sanitized_functions)
    normalized["requested_functions"] = sanitized_functions

    _validate_no_dependency_leak(normalized, sanitized_functions)

    try:
        return IntentResult.model_validate(normalized)
    except PydanticValidationError as exc:
        raise LLMParseError(f"IntentResult validation failed: {exc}") from exc
