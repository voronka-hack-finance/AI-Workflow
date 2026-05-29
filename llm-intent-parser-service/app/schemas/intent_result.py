"""Intent parse response schema."""
from pydantic import BaseModel, Field


class IntentParseResponse(BaseModel):
    intent: str = "unknown"
    confidence: float = 0.0
    entities: dict = Field(default_factory=dict)
    # TODO: align with full intent_result JSON from docs
