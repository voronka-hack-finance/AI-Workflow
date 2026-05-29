"""Workflow result schema."""
from pydantic import BaseModel

from app.schemas.workflow_status import WorkflowStatus


class WorkflowResult(BaseModel):
    task_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    # TODO: add final_answer, error details
