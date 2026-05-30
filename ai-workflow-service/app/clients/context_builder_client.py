"""HTTP client for AI Context Builder Service."""
from __future__ import annotations

from shared_contracts.context_package import ContextPackage, SourceMessage
from shared_contracts.intent_result import IntentParserResponse

from app.clients.base import BaseServiceClient
from app.core.config import Settings, get_settings
from app.schemas.workflow_task import WorkflowTask


class ContextBuilderClient(BaseServiceClient):
    def __init__(self, settings: Settings | None = None) -> None:
        config = settings or get_settings()
        super().__init__(
            base_url=config.context_builder_service_url,
            service_name="ai-context-builder-service",
            timeout=config.ai_workflow_http_timeout_seconds,
            max_retries=config.ai_workflow_http_max_retries,
        )

    async def build_context(
        self,
        task: WorkflowTask,
        intent_response: IntentParserResponse,
    ) -> ContextPackage:
        payload = {
            "request_id": task.request_id,
            "workflow_run_id": task.workflow_run_id,
            "user_id": task.user_id,
            "chat_id": task.chat_id,
            "source_message": SourceMessage(
                raw_message=task.raw_message,
                current_date=task.current_date,
                timezone=task.timezone,
            ).model_dump(),
            "intent_result": intent_response.intent_result.model_dump(),
        }
        return await self._post(
            "/api/v1/context/build",
            payload,
            ContextPackage,
            request_id=task.request_id,
            workflow_run_id=task.workflow_run_id,
        )
