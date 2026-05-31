"""Final editor degraded answer tests."""
from app.response_pipeline.final_editor import FinalEditor
from shared_contracts.response_agent_result import AgentOutput, AgentRecommendation
from tests.conftest import minimal_intent


def test_compose_degraded_prefers_last_editor_answer() -> None:
    editor = FinalEditor()
    long_answer = (
        "За последние 6 месяцев основные расходы пришлись на переводы и супермаркеты. "
        "Рекомендуем сократить импульсные покупки в супермаркетах и пересмотреть подписки."
    )
    result = editor.compose_degraded(
        agent_outputs=[
            AgentOutput(
                agent_name="spending_detective",
                status="success",
                summary="Короткое summary.",
            )
        ],
        style=minimal_intent().style,
        last_editor_answer=long_answer,
    )
    assert result.final_answer == long_answer
    assert not result.final_answer.startswith("Запрос:")


def test_compose_degraded_builds_from_agent_outputs_without_request_echo() -> None:
    editor = FinalEditor()
    result = editor.compose_degraded(
        agent_outputs=[
            AgentOutput(
                agent_name="spending_detective",
                status="success",
                summary="Основные расходы на переводах.",
                facts=["Переводы — 60% бюджета."],
                recommendations=[
                    AgentRecommendation(
                        title="Пересмотр переводов",
                        description="Проверьте регулярные автоплатежи.",
                    )
                ],
            )
        ],
        style=minimal_intent().style,
        last_editor_answer=None,
    )
    assert "Запрос:" not in result.final_answer
    assert "переводах" in result.final_answer.lower()
    assert "Пересмотр переводов" in result.final_answer
