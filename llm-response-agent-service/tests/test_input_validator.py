"""Input validator tests."""
from shared_contracts.common import FunctionResultStatus

from app.validators.input_validator import InputValidator
from tests.conftest import minimal_far, minimal_intent


def test_input_validator_passes_with_valid_payload() -> None:
    result = InputValidator().validate(
        intent=minimal_intent(),
        financial_analysis_result=minimal_far(),
        constraints=minimal_intent().constraints,
        style=minimal_intent().style,
    )
    assert result.validation_status == "passed"
    assert result.can_run_agents is True


def test_input_validator_stops_on_error_function_result() -> None:
    far = minimal_far()
    far.function_results["budget_recommendation"].status = FunctionResultStatus.ERROR
    result = InputValidator().validate(
        intent=minimal_intent(),
        financial_analysis_result=far,
        constraints=minimal_intent().constraints,
        style=minimal_intent().style,
    )
    assert result.can_run_agents is False
    assert result.validation_status == "error"


def test_input_validator_needs_clarification_for_goal() -> None:
    intent = minimal_intent(
        primary_intent="goal_analysis",
        requested_functions=["goal_analysis"],
        goal={"name": "ноутбук", "amount": None, "deadline_months": None},
    )
    far = minimal_far(
        executed_functions=["goal_analysis"],
        function_results={
            "goal_analysis": {
                "function_name": "goal_analysis",
                "status": FunctionResultStatus.SUCCESS,
                "result": {"progress_percent": 10},
                "metadata": {"calculated_at": "2026-05-29T12:00:00Z"},
            }
        },
    )
    result = InputValidator().validate(
        intent=intent,
        financial_analysis_result=far,
        constraints=intent.constraints,
        style=intent.style,
    )
    assert result.can_run_agents is False
    assert result.validation_status == "needs_clarification"
