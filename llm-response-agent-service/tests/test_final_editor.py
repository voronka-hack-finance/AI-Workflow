"""Final editor tests."""
import pytest

from app.llm.provider_factory import create_llm_provider
from app.response_pipeline.final_editor import FinalEditor
from shared_contracts.response_agent_result import AgentOutput, InputValidationResult
from tests.conftest import minimal_intent


@pytest.mark.asyncio
async def test_final_editor_mock_compose() -> None:
    editor = FinalEditor()
    outputs = [
        AgentOutput(
            agent_name="budget_planner",
            status="success",
            summary="Можно сократить траты на 6000.",
        )
    ]
    result = await editor.compose(
        original_user_message="Дай рекомендацию",
        agent_outputs=outputs,
        style=minimal_intent().style,
        warnings=[],
        provider=create_llm_provider(),
    )
    assert result.final_answer.strip()
    assert "Дай рекомендацию" in result.final_answer


def test_final_editor_safe_message() -> None:
    editor = FinalEditor()
    result = editor.compose_safe_message(
        input_validation=InputValidationResult(
            validation_status="needs_clarification",
            can_run_agents=False,
            message="Нужна сумма цели.",
        ),
        style=minimal_intent().style,
    )
    assert "уточните" in result.final_answer.lower()
