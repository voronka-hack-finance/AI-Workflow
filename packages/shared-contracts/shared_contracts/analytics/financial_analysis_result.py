"""FinancialAnalysisResult contract."""
from pydantic import BaseModel, Field


class FinancialAnalysisResult(BaseModel):
    summary: dict = {}
    # TODO: extend fields per architecture docs
