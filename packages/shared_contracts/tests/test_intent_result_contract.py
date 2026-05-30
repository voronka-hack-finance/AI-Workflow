"""Intent result contract tests."""
import importlib

import pytest
from pydantic import ValidationError

from shared_contracts.intent_result import IntentResult
from conftest import minimal_intent_parser_response, minimal_intent_result


def test_intent_result_can_be_created() -> None:
    result = minimal_intent_result()
    assert result.primary_intent == "budget_recommendation"
    assert result.requested_functions == ["budget_recommendation"]


def test_intent_parser_response_can_be_created() -> None:
    response = minimal_intent_parser_response()
    assert response.schema_version == "1.0"
    assert response.intent_result.primary_intent == "budget_recommendation"


def test_intent_result_rejects_expanded_functions() -> None:
    with pytest.raises(ValidationError):
        IntentResult(expanded_functions=["income_analysis"])


def test_focus_input_supports_multiple_categories() -> None:
    result = IntentResult(
        primary_intent="category_analysis",
        requested_functions=["category_analysis"],
        focus={
            "categories": ["Отели", "Кино"],
            "direction": "expense",
        },
    )
    assert result.focus.categories == ["Отели", "Кино"]
    assert result.focus.category is None


def test_intent_result_rejects_execution_plan() -> None:
    with pytest.raises(ValidationError):
        IntentResult(execution_plan=[])


def test_intent_result_rejects_function_results() -> None:
    with pytest.raises(ValidationError):
        IntentResult(function_results={})


def test_transaction_input_not_in_package() -> None:
    module = importlib.import_module("shared_contracts.normalized_data")
    assert not hasattr(module, "TransactionInput")
