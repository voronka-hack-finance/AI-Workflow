"""Contract validation tests."""
import pytest
from pydantic import ValidationError

from app.core.errors import LLMParseError
from app.llm.provider_factory import create_llm_provider
from app.parser.validator import validate_intent_payload
from shared_contracts.intent_result import IntentParserResponse, IntentResult


def test_intent_parser_response_shape() -> None:
    response = IntentParserResponse(
        request_id="req_001",
        user_id="user_123",
        chat_id="chat_001",
        raw_message="test",
        intent_result=IntentResult(requested_functions=["budget_recommendation"]),
    )
    assert response.schema_version == "1.0"
    assert response.intent_result.primary_intent == "unknown"


def test_unknown_function_rejected() -> None:
    with pytest.raises(LLMParseError):
        validate_intent_payload({"requested_functions": ["unknown_function"]})


def test_dependency_leakage_rejected() -> None:
    with pytest.raises(LLMParseError, match="dependencies not present in intents"):
        validate_intent_payload(
            {
                "primary_intent": "budget_recommendation",
                "intents": ["budget_recommendation"],
                "requested_functions": [
                    "income_analysis",
                    "expense_breakdown",
                    "cashflow_analysis",
                    "budget_recommendation",
                ],
            }
        )


def test_multi_intent_without_dependency_leakage_allowed() -> None:
    result = validate_intent_payload(
        {
            "primary_intent": "expense_breakdown",
            "intents": ["expense_breakdown", "goal_analysis"],
            "requested_functions": ["expense_breakdown", "goal_analysis"],
        }
    )
    assert result.requested_functions == ["expense_breakdown", "goal_analysis"]


def test_forbidden_fields_rejected() -> None:
    with pytest.raises(LLMParseError):
        validate_intent_payload({"expanded_functions": ["income_analysis"]})


def test_normalizes_local_llm_schema_mistakes() -> None:
    result = validate_intent_payload(
        {
            "primary_intent": "action_plan",
            "intents": ["action_plan", "debt_analysis"],
            "requested_functions": ["action_plan", "debt_analysis"],
            "period": {"type": "current_month"},
            "comparison": {"enabled": False},
            "focus": {"direction": "all"},
            "recommendation_horizon": "next_7_days",
            "goal": None,
            "budget_plan": None,
            "debt": {"requested": True},
            "emergency_fund": {"requested": False},
            "style": "balanced",
            "constraints": [],
            "clarification": ["Какие именно кредиты вас беспокоят?"],
        }
    )
    assert result.goal.name is None
    assert result.budget_plan.horizon is None
    assert result.style.agent_style == "balanced"
    assert result.constraints.protected_categories == []
    assert result.clarification.required is False
    assert result.clarification.question is None


def test_normalizes_clarification_field_paths_and_null_fields() -> None:
    result = validate_intent_payload(
        {
            "primary_intent": "goal_analysis",
            "intents": ["goal_analysis"],
            "requested_functions": ["goal_analysis"],
            "goal": {},
            "budget_plan": {},
            "style": "balanced",
            "constraints": {},
            "clarification": ["goal.amount", "goal.deadline_months"],
        }
    )
    assert result.clarification.required is False
    assert result.clarification.missing_fields == []


def test_strips_goal_clarification_for_action_plan() -> None:
    result = validate_intent_payload(
        {
            "primary_intent": "action_plan",
            "intents": ["action_plan", "budget_recommendation"],
            "requested_functions": ["action_plan", "budget_recommendation"],
            "clarification": {
                "required": True,
                "reason": "Goal amount is missing.",
                "missing_fields": ["goal.amount"],
                "question": "How much money are you trying to save?",
            },
        }
    )
    assert result.clarification.required is False
    assert result.clarification.missing_fields == []


def test_normalizes_income_analysis_payload() -> None:
    result = validate_intent_payload(
        {
            "primary_intent": "income_analysis",
            "intents": ["income_analysis"],
            "requested_functions": ["income_analysis"],
            "style": "balanced",
            "constraints": {},
            "clarification": None,
            "goal": None,
            "budget_plan": None,
        }
    )
    assert result.style.agent_style == "balanced"
    assert result.clarification.required is False
    assert result.goal.name is None


def test_syncs_intents_with_requested_functions() -> None:
    result = validate_intent_payload(
        {
            "primary_intent": "category_analysis",
            "intents": ["category_analysis", "action_plan"],
            "requested_functions": ["category_analysis", "budget_recommendation"],
        }
    )
    assert "budget_recommendation" in result.intents


def test_normalizes_clarification_object_array() -> None:
    result = validate_intent_payload(
        {
            "primary_intent": "goal_analysis",
            "intents": ["goal_analysis"],
            "requested_functions": ["goal_analysis"],
            "clarification": [
                {
                    "required": True,
                    "reason": "goal.amount is missing",
                    "missing_fields": ["goal.amount"],
                    "question": "Could you please specify the amount you want to save?",
                }
            ],
        }
    )
    assert result.clarification.required is False
    assert result.clarification.missing_fields == []


def test_combined_category_value_normalizes_to_all() -> None:
    result = validate_intent_payload(
        {
            "primary_intent": "category_analysis",
            "intents": ["category_analysis"],
            "requested_functions": ["category_analysis"],
            "focus": {"category": "Отели и Кино", "direction": "expense"},
        }
    )
    assert result.focus.categories == ["Отели", "Кино"]
    assert result.focus.category is None
    assert result.clarification.required is False


def test_normalizes_empty_clarification_list() -> None:
    result = validate_intent_payload(
        {
            "primary_intent": "income_analysis",
            "intents": ["income_analysis"],
            "requested_functions": ["income_analysis"],
            "clarification": [],
        }
    )
    assert result.clarification.required is False


def test_fills_empty_intents_from_requested_functions() -> None:
    result = validate_intent_payload(
        {
            "primary_intent": "category_analysis",
            "intents": [],
            "requested_functions": ["category_analysis"],
        }
    )
    assert result.intents == ["category_analysis"]


def test_intent_result_rejects_execution_plan() -> None:
    with pytest.raises(ValidationError):
        IntentResult(execution_plan=[])


def test_openai_compatible_provider_factory() -> None:
    from app.core.config import Settings

    provider = create_llm_provider(
        Settings(
            INTENT_PARSER_LLM_PROVIDER="openai_compatible",
            INTENT_PARSER_LLM_MODEL="test-model",
        )
    )
    assert provider.__class__.__name__ == "OpenAICompatibleProvider"
