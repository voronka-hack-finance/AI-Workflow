"""Workflow result publisher tests."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.queue.result_builder import build_workflow_result_message
from app.queue.result_publisher import WorkflowResultPublisher
from app.schemas.workflow_result import WorkflowResult
from app.workflow.orchestrator import WorkflowOrchestrator
from app.workflow.statuses import WorkflowStatus
from tests.conftest import (
    minimal_analysis_result,
    minimal_context_package,
    minimal_intent_response,
    minimal_response_result,
    sample_task,
)


@pytest.mark.asyncio
async def test_orchestrator_publishes_result_after_success() -> None:
    task = sample_task()
    result_publisher = AsyncMock()
    result_publisher.publish = AsyncMock()

    intent_parser = AsyncMock()
    context_builder = AsyncMock()
    analytics = AsyncMock()
    response_agent = AsyncMock()
    backend_chat = AsyncMock()

    intent_parser.parse_intent.return_value = minimal_intent_response()
    context_builder.build_context.return_value = minimal_context_package()
    analytics.run_analysis.return_value = minimal_analysis_result()
    response_agent.generate_response.return_value = minimal_response_result()

    orchestrator = WorkflowOrchestrator(
        intent_parser=intent_parser,
        context_builder=context_builder,
        analytics=analytics,
        response_agent=response_agent,
        backend_chat=backend_chat,
        result_publisher=result_publisher,
    )

    await orchestrator.run_workflow(task)

    result_publisher.publish.assert_awaited_once()
    published = result_publisher.publish.await_args.args[0]
    assert published.workflow_run_id == task.workflow_run_id
    assert published.chat_id == task.chat_id
    assert published.message_id == task.message_id
    assert published.user_id == task.user_id
    assert published.request_id == task.request_id
    assert published.status == "success"
    assert published.content == "Вот рекомендация по бюджету."


@pytest.mark.asyncio
async def test_publisher_retries_before_success() -> None:
    message = build_workflow_result_message(
        sample_task(),
        WorkflowResult(
            request_id="req_001",
            workflow_run_id="run_001",
            status=WorkflowStatus.COMPLETED,
            final_answer="ok",
        ),
        created_at="2026-05-30T12:00:00Z",
    )
    publisher = WorkflowResultPublisher()
    channel = MagicMock()
    channel.is_closed = False
    channel.default_exchange.publish = AsyncMock(
        side_effect=[RuntimeError("broker down"), RuntimeError("broker down"), None]
    )

    with patch.object(publisher, "_ensure_channel", AsyncMock(return_value=channel)):
        await publisher.publish(message)

    assert channel.default_exchange.publish.await_count == 3


@pytest.mark.asyncio
async def test_publisher_raises_after_max_retries() -> None:
    message = build_workflow_result_message(
        sample_task(),
        WorkflowResult(
            request_id="req_001",
            workflow_run_id="run_001",
            status=WorkflowStatus.FAILED,
            error_message="fail",
        ),
        created_at="2026-05-30T12:00:00Z",
    )
    publisher = WorkflowResultPublisher()
    channel = MagicMock()
    channel.is_closed = False
    channel.default_exchange.publish = AsyncMock(side_effect=RuntimeError("broker down"))

    with patch.object(publisher, "_ensure_channel", AsyncMock(return_value=channel)):
        with pytest.raises(RuntimeError, match="broker down"):
            await publisher.publish(message)

    assert channel.default_exchange.publish.await_count == 3
