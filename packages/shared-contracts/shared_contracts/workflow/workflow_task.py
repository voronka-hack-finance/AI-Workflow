"""WorkflowTask contract."""
from pydantic import BaseModel, Field


class WorkflowTask(BaseModel):
    task_id: str
    # TODO: extend fields per architecture docs
