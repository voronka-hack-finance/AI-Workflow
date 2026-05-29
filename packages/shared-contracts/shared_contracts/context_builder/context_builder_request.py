"""ContextBuilderRequest contract."""
from pydantic import BaseModel, Field


class ContextBuilderRequest(BaseModel):
    user_id: str
    # TODO: extend fields per architecture docs
