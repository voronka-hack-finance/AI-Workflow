"""HTTP client for Analytics Service."""
from __future__ import annotations

from shared_contracts.context_package import ContextPackage
from shared_contracts.financial_analysis_result import FinancialAnalysisResult

from app.clients.base import BaseServiceClient
from app.core.config import Settings, get_settings


class AnalyticsClient(BaseServiceClient):
    def __init__(self, settings: Settings | None = None) -> None:
        config = settings or get_settings()
        super().__init__(
            base_url=config.analytics_service_url,
            service_name="analytics-service",
            timeout=config.ai_workflow_http_timeout_seconds,
            max_retries=config.ai_workflow_http_max_retries,
        )

    async def run_analysis(self, context_package: ContextPackage) -> FinancialAnalysisResult:
        return await self._post(
            "/api/v1/analytics/run",
            context_package.model_dump(),
            FinancialAnalysisResult,
            request_id=context_package.request_id,
            workflow_run_id=context_package.workflow_run_id,
        )
