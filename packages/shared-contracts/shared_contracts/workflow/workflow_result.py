"""WorkflowResult contract."""
from pydantic import BaseModel, Field


class WorkflowResult(BaseModel):
    task_id: str
    # TODO: extend fields per architecture docs
