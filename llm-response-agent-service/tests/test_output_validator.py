"""Output validator tests."""
from app.validators.output_validator import OutputValidator
from tests.conftest import minimal_far, minimal_intent


def test_output_validator_passes_for_mock_answer() -> None:
    intent = minimal_intent()
    far = minimal_far()
    result = OutputValidator().validate(
        final_answer="Можно оптимизировать бюджет и сэкономить 6000.",
        financial_analysis_result=far,
        constraints=intent.constraints,
        style=intent.style,
        warnings_to_consider=[],
    )
    assert result.validation_status == "passed"
    assert result.can_send_to_user is True


def test_output_validator_catches_hallucinated_number() -> None:
    intent = minimal_intent()
    far = minimal_far()
    result = OutputValidator().validate(
        final_answer="Вы можете сэкономить 999999 рублей.",
        financial_analysis_result=far,
        constraints=intent.constraints,
        style=intent.style,
        warnings_to_consider=[],
    )
    assert result.validation_status == "failed"
    assert result.can_send_to_user is False
