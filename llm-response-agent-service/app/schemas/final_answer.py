"""Final edited answer."""
from pydantic import BaseModel


class FinalAnswer(BaseModel):
    text: str = ""
