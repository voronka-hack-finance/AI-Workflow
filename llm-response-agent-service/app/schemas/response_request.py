"""Response generation request."""
from pydantic import BaseModel


class ResponseGenerateRequest(BaseModel):
    intent_result: dict = {}
    financial_analysis_result: dict = {}
