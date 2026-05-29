"""Workflow task schema."""
from pydantic import BaseModel


class WorkflowTask(BaseModel):
    task_id: str
    user_id: str
    message_id: str
    raw_message: str = ""
    # TODO: extend with chat_context, active_workflow
