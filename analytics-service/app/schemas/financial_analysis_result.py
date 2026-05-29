"""Aggregated financial analysis."""
from pydantic import BaseModel, Field

from app.schemas.function_result import FunctionResult


class FinancialAnalysisResult(BaseModel):
    function_results: list[FunctionResult] = Field(default_factory=list)
