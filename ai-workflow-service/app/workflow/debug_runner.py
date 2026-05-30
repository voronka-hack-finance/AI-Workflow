"""Debug workflow execution helpers."""
from __future__ import annotations

import time
from typing import Any

from pydantic import BaseModel

from app.schemas.workflow_debug_result import WorkflowDebugResult
from app.schemas.workflow_task import WorkflowTask
from app.workflow.debug_collector import STEP_ORDER, WorkflowDebugCollector, build_debug_result
from app.workflow.deps import WorkflowDeps
from app.workflow.state import WorkflowGraphState, initial_state, to_workflow_result
from app.workflow.statuses import WorkflowStatus

HTTP_STEP_NODES = {
    "parse_intent": "parse_intent",
    "build_context": "build_context",
    "run_analytics": "run_analytics",
    "generate_response": "generate_response",
}


def _intent_parse_request_summary(task: WorkflowTask) -> dict[str, Any]:
    return {
        "request_id": task.request_id,
        "raw_message": task.raw_message,
        "current_date": task.current_date,
        "timezone": task.timezone,
        "chat_context": task.chat_context,
        "active_workflow": task.active_workflow,
    }


def _build_context_request_summary(
    task: WorkflowTask,
    state: WorkflowGraphState,
) -> dict[str, Any]:
    intent_response = state.get("intent_response")
    summary: dict[str, Any] = {
        "request_id": task.request_id,
        "workflow_run_id": task.workflow_run_id,
    }
    if intent_response is not None:
        summary["primary_intent"] = intent_response.intent_result.primary_intent
        summary["requested_functions"] = intent_response.intent_result.requested_functions
    return summary


def _run_analytics_request_summary(state: WorkflowGraphState) -> dict[str, Any]:
    context_package = state.get("context_package")
    if context_package is None:
        return {}
    return {
        "request_id": context_package.request_id,
        "workflow_run_id": context_package.workflow_run_id,
        "functions_to_execute": (
            context_package.analytics_request.functions_to_execute
            if context_package.analytics_request is not None
            else []
        ),
    }


def _generate_response_request_summary(state: WorkflowGraphState) -> dict[str, Any]:
    task = state["task"]
    analysis_result = state.get("analysis_result")
    summary: dict[str, Any] = {
        "request_id": task.request_id,
        "workflow_run_id": task.workflow_run_id,
        "original_user_message": task.raw_message,
    }
    if analysis_result is not None:
        summary["executed_functions"] = analysis_result.executed_functions
    return summary


def _request_summary_for_step(step: str, task: WorkflowTask, state: WorkflowGraphState) -> dict[str, Any]:
    if step == "parse_intent":
        return _intent_parse_request_summary(task)
    if step == "build_context":
        return _build_context_request_summary(task, state)
    if step == "run_analytics":
        return _run_analytics_request_summary(state)
    if step == "generate_response":
        return _generate_response_request_summary(state)
    return {}


def _result_from_node_update(step: str, node_update: dict[str, Any]) -> BaseModel | None:
    if step == "parse_intent":
        return node_update.get("intent_response")
    if step == "build_context":
        return node_update.get("context_package")
    if step == "run_analytics":
        return node_update.get("analysis_result")
    if step == "generate_response":
        return node_update.get("response_result")
    return None


async def run_workflow_debug_parse_intent_only(
    deps: WorkflowDeps,
    task: WorkflowTask,
) -> WorkflowDebugResult:
    collector = WorkflowDebugCollector()
    collector.init_steps()
    started = time.perf_counter()
    request_summary = _intent_parse_request_summary(task)

    try:
        intent_response = await deps.intent_parser.parse_intent(task)
    except Exception as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        collector.record_failed(
            "parse_intent",
            duration_ms=duration_ms,
            request_summary=request_summary,
            error=exc,
        )
        return build_debug_result(
            task,
            collector,
            status=WorkflowStatus.FAILED,
            error_message=str(exc),
            stopped_at="parse_intent",
        )

    duration_ms = int((time.perf_counter() - started) * 1000)
    collector.record_ok(
        "parse_intent",
        duration_ms=duration_ms,
        request_summary=request_summary,
        result=intent_response,
    )
    return build_debug_result(
        task,
        collector,
        status=WorkflowStatus.COMPLETED,
        stopped_at="parse_intent",
    )


async def run_workflow_debug_full(
    deps: WorkflowDeps,
    graph: Any,
    task: WorkflowTask,
) -> WorkflowDebugResult:
    del deps
    collector = WorkflowDebugCollector()
    collector.init_steps()

    state: WorkflowGraphState = initial_state(task)
    failed_step: str | None = None
    timer_started = time.perf_counter()

    async for update in graph.astream(state, stream_mode="updates"):
        duration_ms = int((time.perf_counter() - timer_started) * 1000)
        timer_started = time.perf_counter()

        for node_name, node_update in update.items():
            state = {**state, **node_update}
            step = HTTP_STEP_NODES.get(node_name)
            if step is None:
                continue

            request_summary = _request_summary_for_step(step, task, state)
            error = node_update.get("error")
            if error is not None:
                collector.record_failed(
                    step,
                    duration_ms=duration_ms,
                    request_summary=request_summary,
                    error=error if isinstance(error, Exception) else RuntimeError(str(error)),
                )
                failed_step = step
                break

            result = _result_from_node_update(step, node_update)
            if result is not None:
                collector.record_ok(
                    step,
                    duration_ms=duration_ms,
                    request_summary=request_summary,
                    result=result,
                )
            if failed_step is not None:
                break
        if failed_step is not None:
            break

    workflow_result = to_workflow_result(state)
    return build_debug_result(
        task,
        collector,
        workflow_result=workflow_result,
        final_state=state,
    )


async def run_workflow_debug(
    deps: WorkflowDeps,
    graph: Any,
    task: WorkflowTask,
    *,
    stop_after: str | None = None,
) -> WorkflowDebugResult:
    if stop_after == "parse_intent":
        return await run_workflow_debug_parse_intent_only(deps, task)
    return await run_workflow_debug_full(deps, graph, task)
