"""Workflow debug response schemas."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.workflow.statuses import WorkflowStatus


class WorkflowStepDebug(BaseModel):
    step: str
    service: str
    status: str
    duration_ms: int | None = None
    request_summary: dict[str, Any] = Field(default_factory=dict)
    response_valid: bool | None = None
    error: str | None = None
    result: dict[str, Any] | None = None


class WorkflowDebugResult(BaseModel):
    request_id: str
    workflow_run_id: str
    user_id: str
    chat_id: str
    status: WorkflowStatus
    final_answer: str | None = None
    error_message: str | None = None
    stopped_at: str | None = None
    intent_parser: dict[str, Any] | None = None
    steps: list[WorkflowStepDebug] = Field(default_factory=list)
