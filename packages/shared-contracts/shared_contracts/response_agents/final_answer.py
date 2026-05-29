"""FinalAnswer contract."""
from pydantic import BaseModel, Field


class FinalAnswer(BaseModel):
    text: str = ''
    # TODO: extend fields per architecture docs
