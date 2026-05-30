"""Clarification flow tests."""
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
async def test_intent_clarification_stops_pipeline(
    backend_chat: MockBackendChatClient,
    task: WorkflowTask,
) -> None:
    orchestrator = _orchestrator(
        backend_chat,
        intent=minimal_intent_response(clarification_required=True),
    )

    result = await orchestrator.run_workflow(task)

    assert result.status == WorkflowStatus.AWAITING_USER_INPUT
    assert backend_chat.clarifications[-1].question == "Какой период вас интересует?"
    orchestrator._context_builder.build_context.assert_not_awaited()


@pytest.mark.asyncio
async def test_context_clarification_stops_before_analytics(
    backend_chat: MockBackendChatClient,
    task: WorkflowTask,
) -> None:
    orchestrator = _orchestrator(
        backend_chat,
        context=minimal_context_package(can_run_analytics=False),
    )

    result = await orchestrator.run_workflow(task)

    assert result.status == WorkflowStatus.AWAITING_USER_INPUT
    assert backend_chat.clarifications
    orchestrator._analytics.run_analysis.assert_not_awaited()


@pytest.mark.asyncio
async def test_analytics_clarification_stops_before_response_agent(
    backend_chat: MockBackendChatClient,
    task: WorkflowTask,
) -> None:
    orchestrator = _orchestrator(
        backend_chat,
        analysis=minimal_analysis_result(needs_clarification=True),
    )

    result = await orchestrator.run_workflow(task)

    assert result.status == WorkflowStatus.AWAITING_USER_INPUT
    assert "Нужны данные о цели" in backend_chat.clarifications[-1].question
    orchestrator._response_agent.generate_response.assert_not_awaited()


@pytest.mark.asyncio
async def test_response_agent_clarification_stops_before_final_answer(
    backend_chat: MockBackendChatClient,
    task: WorkflowTask,
) -> None:
    orchestrator = _orchestrator(
        backend_chat,
        response=minimal_response_result(needs_clarification=True),
    )

    result = await orchestrator.run_workflow(task)

    assert result.status == WorkflowStatus.AWAITING_USER_INPUT
    assert not backend_chat.final_answers
