"""HTTP client for LLM Response Agent Service."""
from __future__ import annotations

from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import IntentResult
from shared_contracts.response_agent_result import ResponseAgentResult

from app.clients.base import BaseServiceClient
from app.core.config import Settings, get_settings
from app.schemas.workflow_task import WorkflowTask


class ResponseAgentClient(BaseServiceClient):
    def __init__(self, settings: Settings | None = None) -> None:
        config = settings or get_settings()
        super().__init__(
            base_url=config.response_agent_service_url,
            service_name="llm-response-agent-service",
            timeout=config.ai_workflow_http_timeout_seconds,
            max_retries=config.ai_workflow_http_max_retries,
        )

    async def generate_response(
        self,
        task: WorkflowTask,
        intent_result: IntentResult,
        financial_analysis_result: FinancialAnalysisResult,
    ) -> ResponseAgentResult:
        payload = {
            "request_id": task.request_id,
            "workflow_run_id": task.workflow_run_id,
            "original_user_message": task.raw_message,
            "intent_result": intent_result.model_dump(),
            "financial_analysis_result": financial_analysis_result.model_dump(),
            "constraints": intent_result.constraints.model_dump(),
            "style": intent_result.style.model_dump(),
        }
        return await self._post(
            "/api/v1/response/generate",
            payload,
            ResponseAgentResult,
            request_id=task.request_id,
            workflow_run_id=task.workflow_run_id,
        )
