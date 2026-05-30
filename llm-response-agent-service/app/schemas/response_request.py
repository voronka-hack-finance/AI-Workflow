"""Response generation request."""
from pydantic import BaseModel, Field


class ResponseGenerateRequest(BaseModel):
    request_id: str = "unknown"
    workflow_run_id: str = "unknown"
    original_user_message: str = ""
    intent_result: dict = Field(default_factory=dict)
    financial_analysis_result: dict = Field(default_factory=dict)
    constraints: dict = Field(default_factory=dict)
    style: dict = Field(default_factory=dict)
