"""Workflow orchestrator tests."""
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


@pytest.fixture
def orchestrator_with_mocks(backend_chat: MockBackendChatClient) -> WorkflowOrchestrator:
    intent_parser = AsyncMock()
    context_builder = AsyncMock()
    analytics = AsyncMock()
    response_agent = AsyncMock()

    intent_parser.parse_intent.return_value = minimal_intent_response()
    context_builder.build_context.return_value = minimal_context_package()
    analytics.run_analysis.return_value = minimal_analysis_result()
    response_agent.generate_response.return_value = minimal_response_result()

    return WorkflowOrchestrator(
        intent_parser=intent_parser,
        context_builder=context_builder,
        analytics=analytics,
        response_agent=response_agent,
        backend_chat=backend_chat,
    )


@pytest.mark.asyncio
async def test_happy_path_reads_final_answer_from_editor_output(
    orchestrator_with_mocks: WorkflowOrchestrator,
    backend_chat: MockBackendChatClient,
    task: WorkflowTask,
) -> None:
    result = await orchestrator_with_mocks.run_workflow(task)

    assert result.status == WorkflowStatus.COMPLETED
    assert result.final_answer == "Вот рекомендация по бюджету."
    assert backend_chat.final_answers[-1].final_answer == "Вот рекомендация по бюджету."
    assert backend_chat.status_updates[0].status == WorkflowStatus.RUNNING
    assert backend_chat.status_updates[-1].status == WorkflowStatus.COMPLETED


@pytest.mark.asyncio
async def test_request_and_workflow_ids_propagated(
    orchestrator_with_mocks: WorkflowOrchestrator,
    task: WorkflowTask,
) -> None:
    result = await orchestrator_with_mocks.run_workflow(task)

    assert result.request_id == "req_001"
    assert result.workflow_run_id == "run_001"

    intent_parser = orchestrator_with_mocks._intent_parser
    intent_parser.parse_intent.assert_awaited_once_with(task)

    context_builder = orchestrator_with_mocks._context_builder
    context_builder.build_context.assert_awaited_once()
    called_task, called_intent = context_builder.build_context.await_args.args
    assert called_task.request_id == "req_001"
    assert called_intent.request_id == "req_001"

    analytics = orchestrator_with_mocks._analytics
    context_arg = analytics.run_analysis.await_args.args[0]
    assert context_arg.request_id == "req_001"
    assert context_arg.workflow_run_id == "run_001"
