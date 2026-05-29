"""Intent parse request schema."""
from pydantic import BaseModel, Field

from app.schemas.chat_context import ChatContext


class IntentParseRequest(BaseModel):
    raw_message: str
    chat_context: ChatContext | None = None
    active_workflow: str | None = None
    current_date: str | None = None
    timezone: str = "UTC"
