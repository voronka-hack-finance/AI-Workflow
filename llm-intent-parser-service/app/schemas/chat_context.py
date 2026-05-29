"""Chat context schema."""
from pydantic import BaseModel


class ChatContext(BaseModel):
    messages: list[dict] = []
    # TODO: extend per chat API contract
