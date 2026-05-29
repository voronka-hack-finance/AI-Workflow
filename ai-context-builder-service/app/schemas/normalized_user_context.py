"""Normalized user context."""
from pydantic import BaseModel


class NormalizedUserContext(BaseModel):
    user_id: str
    # TODO: extend
