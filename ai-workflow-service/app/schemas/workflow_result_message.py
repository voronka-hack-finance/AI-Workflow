"""RabbitMQ workflow result message contract (ai.workflow.results)."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

WorkflowResultPublishStatus = Literal["success", "partial", "error"]


class WorkflowResultErrorItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str


class WorkflowResultMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    message_type: Literal["ai.workflow.result"] = "ai.workflow.result"
    request_id: str
    workflow_run_id: str
    user_id: str
    chat_id: str
    message_id: str
    status: WorkflowResultPublishStatus
    content: str
    created_at: str
    errors: list[WorkflowResultErrorItem] = Field(default_factory=list)
    metadata: dict[str, Any] | None = None
