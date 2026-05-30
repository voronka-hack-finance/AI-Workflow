"""Analytics run endpoint."""
from fastapi import APIRouter

from app.schemas.context_package import ContextPackageInput
from app.schemas.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.financial_analysis_result import FinancialAnalysisMetadata
from shared_contracts.intent_result import PeriodInput

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.post("/run", response_model=FinancialAnalysisResult)
async def run_analysis(package: ContextPackageInput) -> FinancialAnalysisResult:
    # TODO: call AnalyticsEngine
    _ = package
    return FinancialAnalysisResult(
        request_id="stub-request",
        user_id=package.user_id,
        period=PeriodInput(type="unknown"),
        metadata=FinancialAnalysisMetadata(calculated_at="2026-01-01T00:00:00Z"),
    )
