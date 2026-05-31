"""Output validator tests with agent_outputs allowed numbers."""
from app.validators.output_validator import OutputValidator
from shared_contracts.response_agent_result import AgentOutput
from tests.conftest import minimal_far, minimal_intent


def test_validator_allows_numbers_from_agent_outputs() -> None:
    intent = minimal_intent()
    far = minimal_far()
    agent_outputs = [
        AgentOutput(
            agent_name="spending_detective",
            status="success",
            summary="Основные расходы сосредоточены на переводах.",
            facts=["За 6 месяцев переводы составили 125000 рублей."],
        )
    ]
    result = OutputValidator().validate(
        final_answer=(
            "За 6 месяцев основные расходы — переводы (125000 рублей). "
            "Рекомендуем пересмотреть регулярные переводы."
        ),
        financial_analysis_result=far,
        constraints=intent.constraints,
        style=intent.style,
        warnings_to_consider=[],
        agent_outputs=agent_outputs,
    )
    assert result.can_send_to_user is True


def test_validator_without_agent_outputs_rejects_unknown_number() -> None:
    intent = minimal_intent()
    far = minimal_far()
    result = OutputValidator().validate(
        final_answer="Вы можете сэкономить 125000 рублей.",
        financial_analysis_result=far,
        constraints=intent.constraints,
        style=intent.style,
        warnings_to_consider=[],
        agent_outputs=[],
    )
    assert result.can_send_to_user is False
