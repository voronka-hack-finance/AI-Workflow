"""Clarification and active_workflow merge helpers."""
from __future__ import annotations

from typing import Any

from app.schemas.intent_request import IntentParseRequest
from shared_contracts.intent_result import IntentResult


def _as_dict(value: IntentResult | dict[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, IntentResult):
        return value.model_dump()
    return dict(value)


def _get_nested_value(data: dict[str, Any], field_path: str) -> Any:
    current: Any = data
    for part in field_path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _is_field_missing(field_path: str, merged: dict[str, Any]) -> bool:
    return _get_nested_value(merged, field_path) is None


def _follow_up_question(missing_fields: list[str], prior_question: str | None) -> str:
    if len(missing_fields) == 1 and missing_fields[0] == "goal.deadline_months":
        return "За какой срок ты хочешь накопить?"
    if len(missing_fields) == 1 and missing_fields[0] == "goal.amount":
        return "На какую сумму ты хочешь накопить?"
    if prior_question:
        return prior_question
    return "Уточни, пожалуйста, недостающие данные."


def is_clarification_answer(request: IntentParseRequest) -> bool:
    workflow = request.active_workflow_state()
    return workflow is not None and workflow.status == "awaiting_user_input"


def merge_clarification_answer(
    request: IntentParseRequest,
    parsed: IntentResult,
) -> IntentResult:
    workflow = request.active_workflow_state()
    if workflow is None or workflow.status != "awaiting_user_input":
        return parsed

    prior = _as_dict(workflow.intent_result)
    prior_clarification = dict(prior.get("clarification") or {})
    merged = prior.copy()
    current = parsed.model_dump()

    for key, value in current.items():
        if key in {"clarification"}:
            continue
        if key == "goal" and isinstance(value, dict):
            goal = dict(merged.get("goal") or {})
            goal.update({k: v for k, v in value.items() if v is not None})
            merged["goal"] = goal
            continue
        if key == "budget_plan" and isinstance(value, dict):
            budget_plan = dict(merged.get("budget_plan") or {})
            budget_plan.update({k: v for k, v in value.items() if v is not None})
            merged["budget_plan"] = budget_plan
            continue
        if key == "focus" and isinstance(value, dict):
            focus = dict(merged.get("focus") or {})
            focus.update({k: v for k, v in value.items() if v is not None})
            merged["focus"] = focus
            continue
        if value not in (None, [], {}):
            merged[key] = value

    tracked_fields = list(workflow.missing_fields or prior_clarification.get("missing_fields") or [])
    remaining_missing = [field for field in tracked_fields if _is_field_missing(field, merged)]

    if remaining_missing:
        merged["clarification"] = {
            "required": True,
            "reason": prior_clarification.get("reason") or "missing_required_data",
            "missing_fields": remaining_missing,
            "question": _follow_up_question(
                remaining_missing,
                prior_clarification.get("question"),
            ),
        }
    else:
        merged["clarification"] = {
            "required": False,
            "reason": None,
            "missing_fields": [],
            "question": None,
        }

    return IntentResult.model_validate(merged)
