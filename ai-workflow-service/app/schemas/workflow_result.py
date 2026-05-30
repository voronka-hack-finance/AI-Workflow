"""Workflow result schema."""
from pydantic import BaseModel

from app.workflow.statuses import WorkflowStatus


class WorkflowResult(BaseModel):
    request_id: str
    workflow_run_id: str
    status: WorkflowStatus
    final_answer: str | None = None
    error_message: str | None = None
