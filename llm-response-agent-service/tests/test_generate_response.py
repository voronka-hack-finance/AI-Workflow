"""Response agent endpoint tests."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_generate_response_returns_non_empty_dev_answer() -> None:
    response = client.post(
        "/api/v1/response/generate",
        json={
            "request_id": "req_002",
            "workflow_run_id": "run_002",
            "original_user_message": "проанализируй мои доходы",
            "intent_result": {
                "primary_intent": "income_analysis",
                "requested_functions": ["income_analysis"],
                "focus": {"direction": "income"},
            },
            "financial_analysis_result": {
                "request_id": "req_002",
                "user_id": "user_123",
                "period": {"type": "current_month"},
                "metadata": {"calculated_at": "2026-05-30T12:00:00Z"},
            },
        },
    )

    assert response.status_code == 200
    final_answer = response.json()["editor_output"]["final_answer"]
    assert final_answer.strip()
    assert "проанализируй мои доходы" in final_answer
