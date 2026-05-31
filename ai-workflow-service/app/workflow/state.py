"""Workflow graph state for LangGraph."""
from __future__ import annotations

from typing import TypedDict

from shared_contracts.context_package import ContextPackage
from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import IntentParserResponse
from shared_contracts.response_agent_result import ResponseAgentResult

from app.schemas.workflow_result import WorkflowResult
from app.schemas.workflow_task import WorkflowTask
from app.workflow.statuses import WorkflowStatus


class WorkflowGraphState(TypedDict, total=False):
    task: WorkflowTask
    intent_response: IntentParserResponse | None
    context_package: ContextPackage | None
    analysis_result: FinancialAnalysisResult | None
    response_result: ResponseAgentResult | None
    final_answer: str | None
    error: BaseException | None
    workflow_status: WorkflowStatus
    error_message: str | None


def initial_state(task: WorkflowTask) -> WorkflowGraphState:
    return WorkflowGraphState(task=task)


def to_workflow_result(state: WorkflowGraphState) -> WorkflowResult:
    task = state["task"]
    status = state.get("workflow_status", WorkflowStatus.FAILED)
    return WorkflowResult(
        request_id=task.request_id,
        workflow_run_id=task.workflow_run_id,
        status=status,
        final_answer=state.get("final_answer"),
        error_message=state.get("error_message"),
    )
