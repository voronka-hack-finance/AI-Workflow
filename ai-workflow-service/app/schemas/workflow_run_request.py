"""HTTP workflow trigger request schemas."""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from app.schemas.workflow_task import WorkflowTask


class WorkflowRunRequest(BaseModel):
    request_id: str
    user_id: str
    chat_id: str
    raw_message: str
    current_date: str
    timezone: str = "Europe/Moscow"
    workflow_run_id: str | None = None
    message_id: str | None = None
    created_at: str | None = None
    chat_context: dict | None = None
    active_workflow: str | None = None

    def to_workflow_task(self) -> WorkflowTask:
        return WorkflowTask(
            request_id=self.request_id,
            workflow_run_id=self.workflow_run_id or f"run_{self.request_id}",
            user_id=self.user_id,
            chat_id=self.chat_id,
            message_id=self.message_id or f"msg_{self.request_id}",
            raw_message=self.raw_message,
            current_date=self.current_date,
            timezone=self.timezone,
            created_at=self.created_at or datetime.now(UTC).replace(microsecond=0).isoformat(),
            chat_context=self.chat_context,
            active_workflow=self.active_workflow,
        )


class WorkflowBatchRunRequest(BaseModel):
    items: list[WorkflowRunRequest] = Field(min_length=1, max_length=10)

    @field_validator("items")
    @classmethod
    def validate_items_not_empty(cls, value: list[WorkflowRunRequest]) -> list[WorkflowRunRequest]:
        if not value:
            raise ValueError("items must contain at least one workflow request")
        return value
