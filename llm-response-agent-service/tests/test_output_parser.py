"""Output parser tests."""
from shared_contracts.intent_result import StyleInput

from app.llm.output_parser import parse_agent_output, parse_editor_output


def test_parse_editor_output_accepts_plain_text() -> None:
    style = StyleInput()
    result = parse_editor_output("Вот рекомендации по бюджету.", style)
    assert result.final_answer == "Вот рекомендации по бюджету."


def test_parse_editor_output_accepts_json() -> None:
    style = StyleInput()
    result = parse_editor_output('{"format":"chat_text","final_answer":"Готово."}', style)
    assert result.final_answer == "Готово."


def test_parse_agent_output_accepts_plain_text() -> None:
    result = parse_agent_output("Сфокусируйтесь на расходах.", "budget_planner")
    assert result.agent_name == "budget_planner"
    assert result.summary == "Сфокусируйтесь на расходах."
