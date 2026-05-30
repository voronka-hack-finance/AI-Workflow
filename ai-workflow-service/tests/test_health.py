"""Health endpoint tests."""
import os

os.environ.setdefault("AI_WORKFLOW_ENABLE_RABBITMQ_CONSUMER", "false")

from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "ai-workflow-service"
