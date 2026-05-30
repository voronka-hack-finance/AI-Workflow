"""HTTP client for LLM Intent Parser Service."""
from __future__ import annotations

from shared_contracts.intent_result import IntentParserResponse

from app.clients.base import BaseServiceClient
from app.core.config import Settings, get_settings
from app.schemas.workflow_task import WorkflowTask


class IntentParserClient(BaseServiceClient):
    def __init__(self, settings: Settings | None = None) -> None:
        config = settings or get_settings()
        super().__init__(
            base_url=config.intent_parser_service_url,
            service_name="llm-intent-parser-service",
            timeout=config.intent_parser_http_timeout_seconds,
            max_retries=config.ai_workflow_http_max_retries,
        )

    async def parse_intent(self, task: WorkflowTask) -> IntentParserResponse:
        payload = {
            "request_id": task.request_id,
            "user_id": task.user_id,
            "chat_id": task.chat_id,
            "raw_message": task.raw_message,
            "current_date": task.current_date,
            "timezone": task.timezone,
            "chat_context": task.chat_context,
            "active_workflow": task.active_workflow,
        }
        return await self._post(
            "/api/v1/intent/parse",
            payload,
            IntentParserResponse,
            request_id=task.request_id,
            workflow_run_id=task.workflow_run_id,
        )
