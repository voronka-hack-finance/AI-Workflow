"""IntentResult contract."""
from pydantic import BaseModel, Field


class IntentResult(BaseModel):
    intent: str = 'unknown'
    # TODO: extend fields per architecture docs
