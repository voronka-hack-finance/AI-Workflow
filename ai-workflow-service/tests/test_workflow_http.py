"""HTTP workflow trigger endpoint tests."""
from __future__ import annotations

import os
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("AI_WORKFLOW_ENABLE_RABBITMQ_CONSUMER", "false")
os.environ.setdefault("AI_WORKFLOW_ENABLE_HTTP_TRIGGER", "true")

from app.core.config import get_settings
from app.main import app
from app.schemas.workflow_debug_result import WorkflowDebugResult, WorkflowStepDebug
from app.schemas.workflow_result import WorkflowResult
from app.workflow.statuses import WorkflowStatus


def _payload(**overrides: object) -> dict[str, object]:
    body: dict[str, object] = {
        "request_id": "req_001",
        "workflow_run_id": "run_001",
        "user_id": "user_123",
        "chat_id": "chat_001",
        "raw_message": "Куда уходят деньги?",
        "current_date": "2026-05-30",
        "timezone": "Europe/Moscow",
    }
    body.update(overrides)
    return body


@pytest.fixture
def client() -> TestClient:
    mock_orchestrator = AsyncMock()
    mock_orchestrator.run_workflow.return_value = WorkflowResult(
        request_id="req_001",
        workflow_run_id="run_001",
        status=WorkflowStatus.COMPLETED,
        final_answer="Вот ответ.",
    )
    mock_orchestrator.run_workflow_debug.return_value = WorkflowDebugResult(
        request_id="req_001",
        workflow_run_id="run_001",
        user_id="user_123",
        chat_id="chat_001",
        status=WorkflowStatus.COMPLETED,
        stopped_at="parse_intent",
        intent_parser={"intent_result": {"primary_intent": "expense_breakdown"}},
        steps=[
            WorkflowStepDebug(
                step="parse_intent",
                service="llm-intent-parser-service",
                status="ok",
                duration_ms=10,
                response_valid=True,
                result={"intent_result": {"primary_intent": "expense_breakdown"}},
            ),
            WorkflowStepDebug(
                step="build_context",
                service="ai-context-builder-service",
                status="not_run",
            ),
        ],
    )
    mock_publisher = AsyncMock()
    mock_publisher.queue_name = "ai.workflow.tasks"

    with TestClient(app) as test_client:
        test_client.app.state.orchestrator = mock_orchestrator
        test_client.app.state.workflow_publisher = mock_publisher
        test_client.app.state.mock_orchestrator = mock_orchestrator
        test_client.app.state.mock_publisher = mock_publisher
        yield test_client


def test_run_workflow_returns_workflow_result(client: TestClient) -> None:
    response = client.post("/api/v1/workflow/run", json=_payload())
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] == "req_001"
    assert data["workflow_run_id"] == "run_001"
    assert data["status"] == "completed"
    assert data["final_answer"] == "Вот ответ."

    mock_orchestrator = client.app.state.mock_orchestrator
    mock_orchestrator.run_workflow.assert_awaited_once()
    task = mock_orchestrator.run_workflow.await_args.args[0]
    assert task.user_id == "user_123"
    assert task.chat_id == "chat_001"
    assert task.raw_message == "Куда уходят деньги?"


def test_enqueue_workflow_returns_queued_status(client: TestClient) -> None:
    response = client.post("/api/v1/workflow/enqueue", json=_payload())
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] == "req_001"
    assert data["workflow_run_id"] == "run_001"
    assert data["user_id"] == "user_123"
    assert data["chat_id"] == "chat_001"
    assert data["status"] == "queued"
    assert data["queue"] == "ai.workflow.tasks"

    mock_publisher = client.app.state.mock_publisher
    mock_publisher.publish.assert_awaited_once()
    task = mock_publisher.publish.await_args.args[0]
    assert task.request_id == "req_001"
    assert task.message_id == "msg_req_001"


def test_run_workflow_batch_returns_multiple_results(client: TestClient) -> None:
    mock_orchestrator = client.app.state.mock_orchestrator
    mock_orchestrator.run_workflow.side_effect = [
        WorkflowResult(
            request_id="req_001",
            workflow_run_id="run_001",
            status=WorkflowStatus.COMPLETED,
            final_answer="first",
        ),
        WorkflowResult(
            request_id="req_002",
            workflow_run_id="run_002",
            status=WorkflowStatus.COMPLETED,
            final_answer="second",
        ),
    ]

    response = client.post(
        "/api/v1/workflow/run/batch",
        json={
            "items": [
                _payload(),
                _payload(
                    request_id="req_002",
                    workflow_run_id="run_002",
                    raw_message="Дай рекомендацию по бюджету на месяц",
                ),
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["final_answer"] == "first"
    assert data[1]["final_answer"] == "second"
    assert mock_orchestrator.run_workflow.await_count == 2


def test_invalid_payload_returns_422(client: TestClient) -> None:
    response = client.post("/api/v1/workflow/run", json={"raw_message": "hello"})
    assert response.status_code == 422


def test_run_workflow_debug_stop_after_parse_intent(client: TestClient) -> None:
    response = client.post(
        "/api/v1/workflow/run/debug?stop_after=parse_intent",
        json=_payload(),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["stopped_at"] == "parse_intent"
    assert data["intent_parser"]["intent_result"]["primary_intent"] == "expense_breakdown"
    assert data["steps"][0]["status"] == "ok"
    assert data["steps"][1]["status"] == "not_run"

    mock_orchestrator = client.app.state.mock_orchestrator
    mock_orchestrator.run_workflow_debug.assert_awaited_once()
    _, kwargs = mock_orchestrator.run_workflow_debug.await_args
    assert kwargs["stop_after"] == "parse_intent"


def test_run_workflow_debug_full(client: TestClient) -> None:
    response = client.post("/api/v1/workflow/run/debug", json=_payload())
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] == "req_001"
    assert len(data["steps"]) >= 1

    mock_orchestrator = client.app.state.mock_orchestrator
    mock_orchestrator.run_workflow_debug.assert_awaited_once()
    _, kwargs = mock_orchestrator.run_workflow_debug.await_args
    assert kwargs.get("stop_after") is None


def test_invalid_stop_after_returns_422(client: TestClient) -> None:
    response = client.post(
        "/api/v1/workflow/run/debug?stop_after=unknown_step",
        json=_payload(),
    )
    assert response.status_code == 422


def test_http_trigger_disabled_returns_404(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_WORKFLOW_ENABLE_HTTP_TRIGGER", "false")
    get_settings.cache_clear()

    with TestClient(app) as test_client:
        response = test_client.post("/api/v1/workflow/run", json=_payload())
        assert response.status_code == 404

    monkeypatch.setenv("AI_WORKFLOW_ENABLE_HTTP_TRIGGER", "true")
    get_settings.cache_clear()
