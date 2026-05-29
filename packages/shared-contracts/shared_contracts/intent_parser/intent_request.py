"""IntentRequest contract."""
from pydantic import BaseModel, Field


class IntentRequest(BaseModel):
    raw_message: str = ''
    # TODO: extend fields per architecture docs
