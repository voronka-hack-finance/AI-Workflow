"""Workflow result RabbitMQ message builder tests."""
from __future__ import annotations

import json

import pytest

from app.core.errors import SAFE_USER_ERROR_MESSAGE
from app.queue.result_builder import build_workflow_result_message
from app.schemas.workflow_result import WorkflowResult
from app.schemas.workflow_result_message import WorkflowResultMessage
from app.workflow.statuses import WorkflowStatus
from tests.conftest import minimal_intent_response, sample_task


def test_build_success_message_has_correlation_fields() -> None:
    task = sample_task()
    result = WorkflowResult(
        request_id=task.request_id,
        workflow_run_id=task.workflow_run_id,
        status=WorkflowStatus.COMPLETED,
        final_answer="Ответ ассистента",
    )

    message = build_workflow_result_message(
        task,
        result,
        final_state={"task": task, "intent_response": minimal_intent_response()},
        created_at="2026-05-30T12:00:00Z",
    )

    assert message.schema_version == "1.0"
    assert message.message_type == "ai.workflow.result"
    assert message.request_id == task.request_id
    assert message.workflow_run_id == task.workflow_run_id
    assert message.user_id == task.user_id
    assert message.chat_id == task.chat_id
    assert message.message_id == task.message_id
    assert message.status == "success"
    assert message.content == "Ответ ассистента"
    assert message.created_at == "2026-05-30T12:00:00Z"
    assert message.errors == []
    assert message.metadata == {"intent": "budget_recommendation"}


def test_build_error_message_always_has_content() -> None:
    task = sample_task()
    result = WorkflowResult(
        request_id=task.request_id,
        workflow_run_id=task.workflow_run_id,
        status=WorkflowStatus.FAILED,
        error_message="Не удалось обработать запрос",
    )

    message = build_workflow_result_message(task, result)

    assert message.status == "error"
    assert message.content == "Не удалось обработать запрос"
    assert len(message.errors) == 1
    assert message.errors[0].code == "workflow_failed"


def test_build_error_message_fallback_content() -> None:
    task = sample_task()
    result = WorkflowResult(
        request_id=task.request_id,
        workflow_run_id=task.workflow_run_id,
        status=WorkflowStatus.FAILED,
    )

    message = build_workflow_result_message(task, result)

    assert message.content == SAFE_USER_ERROR_MESSAGE


def test_workflow_result_message_extra_forbidden() -> None:
    with pytest.raises(Exception):
        WorkflowResultMessage.model_validate(
            {
                "schema_version": "1.0",
                "message_type": "ai.workflow.result",
                "request_id": "req",
                "workflow_run_id": "run",
                "user_id": "user",
                "chat_id": "chat",
                "message_id": "msg",
                "status": "success",
                "content": "ok",
                "created_at": "2026-05-30T12:00:00Z",
                "unexpected": True,
            }
        )


def test_message_json_roundtrip() -> None:
    task = sample_task()
    result = WorkflowResult(
        request_id=task.request_id,
        workflow_run_id=task.workflow_run_id,
        status=WorkflowStatus.COMPLETED,
        final_answer="ok",
    )
    message = build_workflow_result_message(task, result, created_at="2026-05-30T12:00:00Z")
    payload = json.loads(message.model_dump_json())

    assert payload["message_type"] == "ai.workflow.result"
    assert payload["chat_id"] == task.chat_id
    assert payload["message_id"] == task.message_id
