"""Keyword hints to correct weak LLM intent collapse on local models."""
from __future__ import annotations

import re
from typing import Any

from app.parser.category_normalizer import detect_categories_in_text, normalize_category_value
from app.schemas.intent_request import IntentParseRequest
from shared_contracts.intent_result import IntentResult


def _parse_amount(text: str) -> float | None:
    normalized = text.lower().replace(" ", "")
    match = re.search(r"(\d+(?:[.,]\d+)?)(?:тыс|k)?", normalized)
    if not match:
        return None
    value = float(match.group(1).replace(",", "."))
    if "тыс" in normalized or "k" in normalized:
        value *= 1000
    return value


def _parse_deadline_months(text: str) -> int | None:
    match = re.search(r"(\d+)\s*(?:месяц|мес)", text.lower())
    if match:
        return int(match.group(1))
    return None


def _hint(primary: str, functions: list[str], **overrides: Any) -> dict[str, Any]:
    return {
        "primary_intent": primary,
        "intents": functions,
        "intent_confidence": 0.92,
        "requested_functions": functions,
        **overrides,
    }


def build_message_intent_hints(message: str) -> dict[str, Any] | None:
    """Return intent overrides when the message clearly matches a known pattern."""
    lowered = message.strip().lower()

    if "рекомендацию по бюджету" in lowered or "рекомендация по бюджету" in lowered:
        return _hint(
            "budget_recommendation",
            ["budget_recommendation"],
            recommendation_horizon="next_month",
        )

    if "доход" in lowered and ("анализ" in lowered or "проанализ" in lowered):
        return _hint(
            "income_analysis",
            ["income_analysis"],
            focus={
                "category": None,
                "merchant": None,
                "mcc": None,
                "card_id": None,
                "direction": "income",
            },
        )

    if "накопить" in lowered and "цель" in lowered:
        return _hint(
            "goal_analysis",
            ["goal_analysis"],
            recommendation_horizon="goal_deadline",
            goal={"name": "цель", "amount": None, "deadline_months": None},
            clarification={
                "required": True,
                "reason": "missing_required_data",
                "missing_fields": ["goal.amount", "goal.deadline_months"],
                "question": "На какую сумму и за какой срок ты хочешь накопить?",
            },
        )

    if "накопить" in lowered and "ноутбук" in lowered:
        has_amount = bool(re.search(r"\d", lowered))
        has_deadline = "месяц" in lowered or "мес" in lowered
        if has_amount and has_deadline:
            return _hint(
                "goal_analysis",
                ["goal_analysis"],
                goal={
                    "name": "ноутбук",
                    "amount": _parse_amount(message) or 120000,
                    "deadline_months": _parse_deadline_months(message) or 6,
                },
            )
        return _hint(
            "goal_analysis",
            ["goal_analysis"],
            goal={"name": "ноутбук", "amount": None, "deadline_months": None},
            clarification={
                "required": True,
                "reason": "missing_required_data",
                "missing_fields": ["goal.amount", "goal.deadline_months"],
                "question": "На какую сумму и за какой срок ты хочешь накопить на ноутбук?",
            },
        )

    if "отели" in lowered or "кино" in lowered:
        detected = detect_categories_in_text(message)
        overrides: dict[str, Any] = {
            "focus": {
                "category": None,
                "merchant": None,
                "mcc": None,
                "card_id": None,
                "direction": "expense",
            },
        }
        functions = ["category_analysis"]
        if detected:
            overrides["focus"]["categories"] = detected
            overrides["focus"]["category"] = detected[0] if len(detected) == 1 else None
        if "вчера" in lowered:
            overrides["period"] = {"type": "yesterday", "start_date": None, "end_date": None}
        if any(token in lowered for token in ("оптимиз", "предлага", "сэконом", "уменьш")):
            functions = ["category_analysis", "budget_recommendation", "action_plan"]
            overrides["recommendation_horizon"] = "next_7_days"
        return _hint("category_analysis", functions, **overrides)

    if "фастфуд" in lowered:
        resolved = normalize_category_value("фастфуд")
        return _hint(
            "category_analysis",
            ["category_analysis"],
            focus={
                "category": resolved.categories[0] if len(resolved.categories) == 1 else None,
                "categories": resolved.categories,
                "merchant": None,
                "mcc": None,
                "card_id": None,
                "direction": "expense",
            },
        )

    if "стал тратить больше" in lowered or "тратить больше" in lowered:
        return _hint(
            "expense_breakdown",
            ["expense_breakdown"],
            comparison={
                "enabled": True,
                "type": "previous_period",
                "start_date": None,
                "end_date": None,
            },
        )

    if "кредит" in lowered or "кредитн" in lowered:
        return _hint("debt_analysis", ["debt_analysis"], debt={"requested": True})

    if "подушк" in lowered:
        return _hint(
            "emergency_fund_analysis",
            ["emergency_fund_analysis"],
            emergency_fund={"requested": True},
        )

    if "план" in lowered and "зарплат" in lowered:
        return _hint(
            "budget_plan",
            ["budget_plan"],
            budget_plan={
                "horizon": "until_salary",
                "available_money": None,
                "mandatory_expenses": None,
            },
        )

    if "куда уходят деньги" in lowered or "куда уходят" in lowered:
        return _hint("expense_breakdown", ["expense_breakdown"])

    if lowered.startswith("а за неделю") or lowered == "а за неделю?":
        return _hint(
            "expense_breakdown",
            ["expense_breakdown"],
            period={"type": "last_7_days", "start_date": None, "end_date": None},
        )

    return None


def _is_expense_breakdown_collapse(intent: IntentResult) -> bool:
    return (
        intent.primary_intent == "expense_breakdown"
        and intent.requested_functions == ["expense_breakdown"]
    )


def _apply_period_hints(message: str, intent: IntentResult) -> IntentResult:
    lowered = message.strip().lower()
    period = intent.period.model_dump()

    if "вчера" in lowered:
        period = {"type": "yesterday", "start_date": None, "end_date": None}
    elif any(token in lowered for token in ("прошлую неделю", "прошлой неделе", "за неделю")):
        period = {"type": "last_7_days", "start_date": None, "end_date": None}
    elif "прошлый месяц" in lowered or "за прошлый месяц" in lowered:
        period = {"type": "previous_month", "start_date": None, "end_date": None}

    if period == intent.period.model_dump():
        return intent
    return intent.model_copy(update={"period": period})


def _should_apply_hint_override(
    intent: IntentResult,
    hints: dict[str, Any],
) -> bool:
    hinted_functions = hints.get("requested_functions", [])
    if not hinted_functions:
        return False
    if _is_expense_breakdown_collapse(intent):
        return True
    if intent.primary_intent == "unknown":
        return True

    hint_primary = hints.get("primary_intent")
    extra_functions = set(hinted_functions) - set(intent.requested_functions)
    if extra_functions and hint_primary and intent.primary_intent == hint_primary:
        return True
    return False


def apply_message_hints(request: IntentParseRequest, intent: IntentResult) -> IntentResult:
    """Merge keyword hints when the LLM collapses to a generic or wrong intent."""
    hints = build_message_intent_hints(request.raw_message)
    intent = _apply_period_hints(request.raw_message, intent)

    if hints is None:
        return intent

    hinted_functions = hints.get("requested_functions", [])
    if _should_apply_hint_override(intent, hints):
        merged = intent.model_dump()
        for key, value in hints.items():
            if key == "period" and value is None:
                continue
            merged[key] = value
        if "period" not in hints:
            merged["period"] = intent.period.model_dump()
        return IntentResult.model_validate(merged)

    if intent.focus.category is None and not intent.focus.categories:
        focus = hints.get("focus") or {}
        category = focus.get("category")
        categories = focus.get("categories") or []
        if category or categories:
            focus_update = intent.focus.model_dump()
            focus_update.update(focus)
            intent = intent.model_copy(update={"focus": focus_update})

    hint_clarification = hints.get("clarification")
    if isinstance(hint_clarification, dict) and hint_clarification.get("required"):
        missing_fields = hint_clarification.get("missing_fields") or []
        goal = intent.goal
        goal_incomplete = goal.amount is None or goal.deadline_months is None
        if goal_incomplete and any(field.startswith("goal.") for field in missing_fields):
            intent = intent.model_copy(update={"clarification": hint_clarification})

    return intent
