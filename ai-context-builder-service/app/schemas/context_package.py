"""Context package response."""
from pydantic import BaseModel, Field

from app.schemas.data_quality import DataQuality


class ContextPackage(BaseModel):
    user_id: str
    execution_plan: list[str] = Field(default_factory=list)
    data_quality: DataQuality | None = None
    # TODO: normalized data blocks
