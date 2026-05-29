"""Context package input for analytics."""
from pydantic import BaseModel, Field


class ContextPackageInput(BaseModel):
    user_id: str = ""
    execution_plan: list[str] = Field(default_factory=list)
