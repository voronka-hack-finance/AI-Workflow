"""Context builder request schema."""
from pydantic import BaseModel

from shared_contracts.context_package import SourceMessage
from shared_contracts.intent_result import IntentResult


class ContextBuilderRequest(BaseModel):
    request_id: str
    workflow_run_id: str
    user_id: str
    chat_id: str
    source_message: SourceMessage
    intent_result: IntentResult
