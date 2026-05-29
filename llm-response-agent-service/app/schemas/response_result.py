"""Response API result."""
from pydantic import BaseModel

from app.schemas.final_answer import FinalAnswer


class ResponseGenerateResult(BaseModel):
    answer: str = ""
    final_answer: FinalAnswer | None = None
