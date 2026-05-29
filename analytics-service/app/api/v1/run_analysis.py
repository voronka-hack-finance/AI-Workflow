"""Analytics run endpoint."""
from fastapi import APIRouter

from app.schemas.context_package import ContextPackageInput
from app.schemas.analysis_result import AnalysisResult

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.post("/run", response_model=AnalysisResult)
async def run_analysis(package: ContextPackageInput) -> AnalysisResult:
    # TODO: call AnalyticsEngine
    return AnalysisResult()
