"""Workflow debug runner tests."""
from __future__ import annotations

from typing import Literal
from unittest.mock import AsyncMock

import pytest

from app.schemas.workflow_debug_result import WorkflowDebugResult, WorkflowStepDebug
from app.workflow.orchestrator import WorkflowOrchestrator
from app.workflow.statuses import WorkflowStatus
from tests.conftest import minimal_intent_response, sample_task


@pytest.fixture
def debug_orchestrator(backend_chat) -> WorkflowOrchestrator:
    intent_parser = AsyncMock()
    intent_parser.parse_intent.return_value = minimal_intent_response()
    return WorkflowOrchestrator(
        intent_parser=intent_parser,
        backend_chat=backend_chat,
    )


@pytest.mark.asyncio
async def test_run_workflow_debug_stop_after_parse_intent(debug_orchestrator: WorkflowOrchestrator) -> None:
    task = sample_task()
    result = await debug_orchestrator.run_workflow_debug(task, stop_after="parse_intent")

    assert result.status == WorkflowStatus.COMPLETED
    assert result.stopped_at == "parse_intent"
    assert result.intent_parser is not None
    assert result.intent_parser["intent_result"]["primary_intent"] == "budget_recommendation"
    assert len(result.steps) == 4
    assert result.steps[0].step == "parse_intent"
    assert result.steps[0].status == "ok"
    assert result.steps[0].response_valid is True
    assert result.steps[1].status == "not_run"


@pytest.mark.asyncio
async def test_run_workflow_debug_parse_intent_failure(debug_orchestrator: WorkflowOrchestrator) -> None:
    task = sample_task()
    debug_orchestrator._intent_parser.parse_intent.side_effect = RuntimeError("parser down")

    result = await debug_orchestrator.run_workflow_debug(task, stop_after="parse_intent")

    assert result.status == WorkflowStatus.FAILED
    assert result.steps[0].status == "failed"
    assert result.steps[0].error == "parser down"
    assert result.intent_parser is None
