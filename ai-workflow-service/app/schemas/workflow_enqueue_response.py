"""HTTP workflow enqueue response schema."""
from pydantic import BaseModel

from app.workflow.statuses import WorkflowStatus


class WorkflowEnqueueResponse(BaseModel):
    request_id: str
    workflow_run_id: str
    user_id: str
    chat_id: str
    status: WorkflowStatus
    queue: str
