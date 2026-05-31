"""Response agent endpoint tests."""
from fastapi.testclient import TestClient

from tests.conftest import generate_payload


def test_generate_response_returns_non_empty_answer(client: TestClient) -> None:
    response = client.post("/api/v1/response/generate", json=generate_payload())
    assert response.status_code == 200
    body = response.json()
    final_answer = body["editor_output"]["final_answer"]
    assert final_answer.strip()
    assert "final_answer" not in body


def test_generate_response_matches_contract_shape(client: TestClient) -> None:
    response = client.post("/api/v1/response/generate", json=generate_payload())
    body = response.json()
    for key in (
        "schema_version",
        "request_id",
        "workflow_run_id",
        "input",
        "input_validation",
        "routing",
        "agent_outputs",
        "editor_output",
        "output_validation",
    ):
        assert key in body
    assert "budget_planner" in body["routing"]["selected_agents"]
    assert body["agent_outputs"]
    assert body["editor_output"]["format"] == "chat_text"


def test_generate_response_clarification_when_agents_cannot_run(client: TestClient) -> None:
    payload = generate_payload()
    payload["intent_result"] = {
        "primary_intent": "goal_analysis",
        "requested_functions": ["goal_analysis"],
        "goal": {"name": "ноутбук", "amount": None, "deadline_months": None},
    }
    response = client.post("/api/v1/response/generate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["input_validation"]["can_run_agents"] is False
    assert body["routing"]["selected_agents"] == []
    assert body["agent_outputs"] == []
    assert body["editor_output"]["final_answer"].strip()
