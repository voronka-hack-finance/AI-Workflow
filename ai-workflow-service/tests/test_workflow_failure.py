"""Workflow failure path tests."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.clients.mock_backend_chat_client import MockBackendChatClient
from app.core.errors import ContractValidationError
from app.schemas.workflow_task import WorkflowTask
from app.workflow.orchestrator import WorkflowOrchestrator
from app.workflow.statuses import WorkflowStatus
from shared_http.errors import ServiceTimeoutError
from tests.conftest import (
    minimal_analysis_result,
    minimal_context_package,
    minimal_intent_response,
    minimal_response_result,
)


def _orchestrator(
    backend_chat: MockBackendChatClient,
    *,
    intent_parser: AsyncMock | None = None,
) -> WorkflowOrchestrator:
    intent = intent_parser or AsyncMock()
    if intent_parser is None:
        intent.parse_intent.return_value = minimal_intent_response()

    context_builder = AsyncMock()
    context_builder.build_context.return_value = minimal_context_package()

    analytics = AsyncMock()
    analytics.run_analysis.return_value = minimal_analysis_result()

    response_agent = AsyncMock()
    response_agent.generate_response.return_value = minimal_response_result()

    return WorkflowOrchestrator(
        intent_parser=intent,
        context_builder=context_builder,
        analytics=analytics,
        response_agent=response_agent,
        backend_chat=backend_chat,
    )


@pytest.mark.asyncio
async def test_contract_validation_error_goes_to_fail_workflow(
    backend_chat: MockBackendChatClient,
    task: WorkflowTask,
) -> None:
    intent_parser = AsyncMock()
    intent_parser.parse_intent.side_effect = ContractValidationError("invalid response")

    orchestrator = _orchestrator(backend_chat, intent_parser=intent_parser)
    result = await orchestrator.run_workflow(task)

    assert result.status == WorkflowStatus.FAILED
    assert result.error_message
    assert backend_chat.errors
    assert backend_chat.status_updates[-1].status == WorkflowStatus.FAILED
    orchestrator._context_builder.build_context.assert_not_awaited()


@pytest.mark.asyncio
async def test_service_timeout_goes_to_fail_workflow(
    backend_chat: MockBackendChatClient,
    task: WorkflowTask,
) -> None:
    intent_parser = AsyncMock()
    intent_parser.parse_intent.side_effect = ServiceTimeoutError("timeout")

    orchestrator = _orchestrator(backend_chat, intent_parser=intent_parser)
    result = await orchestrator.run_workflow(task)

    assert result.status == WorkflowStatus.FAILED
    assert backend_chat.errors[-1].safe_message
    orchestrator._context_builder.build_context.assert_not_awaited()
