"""Workflow task schema."""
from pydantic import BaseModel, ConfigDict


class WorkflowTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    workflow_run_id: str
    user_id: str
    chat_id: str
    message_id: str
    raw_message: str
    current_date: str
    timezone: str
    created_at: str
    chat_context: dict | None = None
    active_workflow: str | None = None
