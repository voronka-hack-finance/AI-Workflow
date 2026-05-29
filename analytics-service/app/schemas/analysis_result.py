"""Full analysis response."""
from pydantic import BaseModel

from app.schemas.financial_analysis_result import FinancialAnalysisResult


class AnalysisResult(BaseModel):
    financial_analysis: FinancialAnalysisResult = FinancialAnalysisResult()
