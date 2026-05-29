"""Context builder request."""
from pydantic import BaseModel


class ContextBuilderRequest(BaseModel):
    user_id: str
    intent_result: dict = {}
    # TODO: extend fields
