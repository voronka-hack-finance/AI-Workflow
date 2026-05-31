"""Build RabbitMQ workflow result messages from pipeline output."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.core.errors import SAFE_USER_ERROR_MESSAGE
from app.schemas.workflow_result import WorkflowResult
from app.schemas.workflow_result_message import (
    WorkflowResultErrorItem,
    WorkflowResultMessage,
    WorkflowResultPublishStatus,
)
from app.schemas.workflow_task import WorkflowTask
from app.workflow.state import WorkflowGraphState
from app.workflow.statuses import WorkflowStatus

_DEFAULT_ERROR_CODE = "workflow_failed"


def _utc_now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def map_publish_status(workflow_status: WorkflowStatus) -> WorkflowResultPublishStatus:
    if workflow_status == WorkflowStatus.COMPLETED:
        return "success"
    return "error"


def resolve_content(result: WorkflowResult, publish_status: WorkflowResultPublishStatus) -> str:
    if publish_status == "error":
        return result.error_message or SAFE_USER_ERROR_MESSAGE
    return result.final_answer or SAFE_USER_ERROR_MESSAGE


def extract_metadata(state: WorkflowGraphState | None) -> dict[str, Any] | None:
    if state is None:
        return None

    metadata: dict[str, Any] = {}
    intent_response = state.get("intent_response")
    if intent_response is not None:
        metadata["intent"] = intent_response.intent_result.primary_intent

    response_result = state.get("response_result")
    if response_result is not None and response_result.routing.selected_agents:
        metadata["agent_key"] = response_result.routing.selected_agents[0]

    return metadata or None


def build_workflow_result_message(
    task: WorkflowTask,
    result: WorkflowResult,
    *,
    final_state: WorkflowGraphState | None = None,
    created_at: str | None = None,
) -> WorkflowResultMessage:
    publish_status = map_publish_status(result.status)
    content = resolve_content(result, publish_status)
    errors: list[WorkflowResultErrorItem] = []
    if publish_status == "error":
        errors.append(
            WorkflowResultErrorItem(
                code=_DEFAULT_ERROR_CODE,
                message=result.error_message or SAFE_USER_ERROR_MESSAGE,
            )
        )

    return WorkflowResultMessage(
        request_id=task.request_id,
        workflow_run_id=task.workflow_run_id,
        user_id=task.user_id,
        chat_id=task.chat_id,
        message_id=task.message_id,
        status=publish_status,
        content=content,
        created_at=created_at or _utc_now_iso(),
        errors=errors,
        metadata=extract_metadata(final_state),
    )
