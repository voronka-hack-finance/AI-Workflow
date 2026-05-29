"""ResponseRequest contract."""
from pydantic import BaseModel, Field


class ResponseRequest(BaseModel):
    intent_result: dict = {}
    # TODO: extend fields per architecture docs
