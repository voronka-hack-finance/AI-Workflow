"""LangGraph workflow node implementations."""
from __future__ import annotations

import logging
from collections.abc import Callable, Coroutine
from typing import Any

from app.core.errors import safe_user_message
from app.workflow.deps import WorkflowDeps
from app.workflow.state import WorkflowGraphState
from app.workflow.statuses import WorkflowStatus

logger = logging.getLogger(__name__)

NodeFn = Callable[[WorkflowGraphState], Coroutine[Any, Any, dict[str, Any]]]


def _task_ids(state: WorkflowGraphState) -> dict[str, str]:
    task = state["task"]
    return {
        "request_id": task.request_id,
        "workflow_run_id": task.workflow_run_id,
        "user_id": task.user_id,
        "chat_id": task.chat_id,
    }


def make_parse_intent(deps: WorkflowDeps) -> NodeFn:
    async def parse_intent(state: WorkflowGraphState) -> dict[str, Any]:
        try:
            intent_response = await deps.intent_parser.parse_intent(state["task"])
        except Exception as exc:
            logger.exception(
                "parse_intent failed",
                extra={**_task_ids(state), "event": "node_error", "node": "parse_intent"},
            )
            return {"error": exc}
        return {"intent_response": intent_response, "error": None}

    return parse_intent


def make_build_context(deps: WorkflowDeps) -> NodeFn:
    async def build_context(state: WorkflowGraphState) -> dict[str, Any]:
        try:
            context_package = await deps.context_builder.build_context(
                state["task"],
                state["intent_response"],
            )
        except Exception as exc:
            logger.exception(
                "build_context failed",
                extra={**_task_ids(state), "event": "node_error", "node": "build_context"},
            )
            return {"error": exc}
        return {"context_package": context_package, "error": None}

    return build_context


def make_run_analytics(deps: WorkflowDeps) -> NodeFn:
    async def run_analytics(state: WorkflowGraphState) -> dict[str, Any]:
        try:
            analysis_result = await deps.analytics.run_analysis(state["context_package"])
        except Exception as exc:
            logger.exception(
                "run_analytics failed",
                extra={**_task_ids(state), "event": "node_error", "node": "run_analytics"},
            )
            return {"error": exc}
        return {"analysis_result": analysis_result, "error": None}

    return run_analytics


def make_generate_response(deps: WorkflowDeps) -> NodeFn:
    async def generate_response(state: WorkflowGraphState) -> dict[str, Any]:
        try:
            response_result = await deps.response_agent.generate_response(
                state["task"],
                state["intent_response"].intent_result,
                state["analysis_result"],
            )
        except Exception as exc:
            logger.exception(
                "generate_response failed",
                extra={**_task_ids(state), "event": "node_error", "node": "generate_response"},
            )
            return {"error": exc}
        return {"response_result": response_result, "error": None}

    return generate_response


def make_send_final_answer(deps: WorkflowDeps) -> NodeFn:
    async def send_final_answer(state: WorkflowGraphState) -> dict[str, Any]:
        task = state["task"]
        final_answer = state["response_result"].editor_output.final_answer
        await deps.backend_chat.send_final_answer(
            request_id=task.request_id,
            workflow_run_id=task.workflow_run_id,
            user_id=task.user_id,
            chat_id=task.chat_id,
            message_id=task.message_id,
            final_answer=final_answer,
        )
        await deps.backend_chat.update_workflow_status(
            request_id=task.request_id,
            workflow_run_id=task.workflow_run_id,
            user_id=task.user_id,
            chat_id=task.chat_id,
            status=WorkflowStatus.COMPLETED,
        )
        logger.info(
            "Workflow completed",
            extra={**_task_ids(state), "event": "workflow_completed"},
        )
        return {
            "final_answer": final_answer,
            "workflow_status": WorkflowStatus.COMPLETED,
        }

    return send_final_answer


def make_fail_workflow(deps: WorkflowDeps) -> NodeFn:
    async def fail_workflow(state: WorkflowGraphState) -> dict[str, Any]:
        task = state["task"]
        error = state.get("error") or RuntimeError("Unknown workflow error")
        message = safe_user_message(error)
        logger.error(
            "Workflow failed",
            extra={
                **_task_ids(state),
                "event": "workflow_failed",
                "error_type": type(error).__name__,
            },
        )
        await deps.backend_chat.update_workflow_status(
            request_id=task.request_id,
            workflow_run_id=task.workflow_run_id,
            user_id=task.user_id,
            chat_id=task.chat_id,
            status=WorkflowStatus.FAILED,
        )
        await deps.backend_chat.send_error(
            request_id=task.request_id,
            workflow_run_id=task.workflow_run_id,
            user_id=task.user_id,
            chat_id=task.chat_id,
            message_id=task.message_id,
            safe_message=message,
        )
        return {
            "workflow_status": WorkflowStatus.FAILED,
            "error_message": message,
        }

    return fail_workflow
