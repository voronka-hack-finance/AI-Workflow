"""Pipeline continues without clarification stops."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.clients.mock_backend_chat_client import MockBackendChatClient
from app.schemas.workflow_task import WorkflowTask
from app.workflow.orchestrator import WorkflowOrchestrator
from app.workflow.statuses import WorkflowStatus
from tests.conftest import (
    minimal_analysis_result,
    minimal_context_package,
    minimal_intent_response,
    minimal_response_result,
)


def _orchestrator(
    backend_chat: MockBackendChatClient,
    *,
    intent=None,
    context=None,
    analysis=None,
    response=None,
) -> WorkflowOrchestrator:
    intent_parser = AsyncMock()
    context_builder = AsyncMock()
    analytics = AsyncMock()
    response_agent = AsyncMock()

    intent_parser.parse_intent.return_value = intent or minimal_intent_response()
    context_builder.build_context.return_value = context or minimal_context_package()
    analytics.run_analysis.return_value = analysis or minimal_analysis_result()
    response_agent.generate_response.return_value = response or minimal_response_result()

    return WorkflowOrchestrator(
        intent_parser=intent_parser,
        context_builder=context_builder,
        analytics=analytics,
        response_agent=response_agent,
        backend_chat=backend_chat,
    )


@pytest.mark.asyncio
async def test_pipeline_continues_when_clarification_signals_present(
    backend_chat: MockBackendChatClient,
    task: WorkflowTask,
) -> None:
    orchestrator = _orchestrator(
        backend_chat,
        intent=minimal_intent_response(clarification_required=True),
        context=minimal_context_package(can_run_analytics=False),
        analysis=minimal_analysis_result(needs_clarification=True),
        response=minimal_response_result(needs_clarification=True),
    )

    result = await orchestrator.run_workflow(task)

    assert result.status == WorkflowStatus.COMPLETED
    assert backend_chat.clarifications == []
    assert backend_chat.final_answers
    orchestrator._context_builder.build_context.assert_awaited_once()
    orchestrator._analytics.run_analysis.assert_awaited_once()
    orchestrator._response_agent.generate_response.assert_awaited_once()
