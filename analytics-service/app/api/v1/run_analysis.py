"""Analytics run endpoint."""
from fastapi import APIRouter

from app.runner.analytics_runner import AnalyticsRunner
from app.schemas.context_package import ContextPackageInput
from app.schemas.financial_analysis_result import FinancialAnalysisResult

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

_runner = AnalyticsRunner()


@router.post("/run", response_model=FinancialAnalysisResult)
async def run_analysis(package: ContextPackageInput) -> FinancialAnalysisResult:
    return _runner.run(package)
