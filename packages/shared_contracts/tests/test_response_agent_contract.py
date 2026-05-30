"""Response agent result contract tests."""
import pytest
from pydantic import ValidationError

from shared_contracts.response_agent_result import ResponseAgentResult
from conftest import minimal_response_agent_result


def test_response_agent_result_can_be_created() -> None:
    result = minimal_response_agent_result()
    assert result.editor_output.final_answer == "Вот рекомендация по бюджету."


def test_response_agent_result_stores_final_answer_in_editor_output() -> None:
    result = minimal_response_agent_result()
    assert result.editor_output.final_answer
    assert "final_answer" not in ResponseAgentResult.model_fields


def test_response_agent_result_rejects_root_final_answer() -> None:
    payload = minimal_response_agent_result().model_dump()
    payload["final_answer"] = "duplicate answer"
    with pytest.raises(ValidationError):
        ResponseAgentResult(**payload)


def test_response_agent_result_has_required_sections() -> None:
    fields = set(ResponseAgentResult.model_fields)
    assert {"input_validation", "routing", "agent_outputs", "editor_output", "output_validation"} <= fields
    assert "agent_consilium" not in fields
