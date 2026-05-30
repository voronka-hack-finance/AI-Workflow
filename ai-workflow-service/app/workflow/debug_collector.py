"""Collect per-step debug metadata for workflow debug runs."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.schemas.workflow_debug_result import WorkflowDebugResult, WorkflowStepDebug
from app.schemas.workflow_result import WorkflowResult
from app.schemas.workflow_task import WorkflowTask
from app.workflow.state import WorkflowGraphState
from app.workflow.statuses import WorkflowStatus

STEP_ORDER = (
    "parse_intent",
    "build_context",
    "run_analytics",
    "generate_response",
)

STEP_SERVICE_NAMES = {
    "parse_intent": "llm-intent-parser-service",
    "build_context": "ai-context-builder-service",
    "run_analytics": "analytics-service",
    "generate_response": "llm-response-agent-service",
}


class WorkflowDebugCollector:
    def __init__(self) -> None:
        self._steps: dict[str, WorkflowStepDebug] = {}

    def init_steps(self) -> None:
        self._steps = {
            step: WorkflowStepDebug(
                step=step,
                service=STEP_SERVICE_NAMES[step],
                status="not_run",
            )
            for step in STEP_ORDER
        }

    def record_ok(
        self,
        step: str,
        *,
        duration_ms: int,
        request_summary: dict[str, Any],
        result: BaseModel,
    ) -> None:
        self._steps[step] = WorkflowStepDebug(
            step=step,
            service=STEP_SERVICE_NAMES[step],
            status="ok",
            duration_ms=duration_ms,
            request_summary=request_summary,
            response_valid=True,
            error=None,
            result=result.model_dump(mode="json"),
        )

    def record_failed(
        self,
        step: str,
        *,
        duration_ms: int,
        request_summary: dict[str, Any],
        error: Exception,
    ) -> None:
        self._steps[step] = WorkflowStepDebug(
            step=step,
            service=STEP_SERVICE_NAMES[step],
            status="failed",
            duration_ms=duration_ms,
            request_summary=request_summary,
            response_valid=False,
            error=str(error) or f"{type(error).__name__}",
            result=None,
        )

    def mark_skipped(self, step: str) -> None:
        if step not in self._steps:
            return
        current = self._steps[step]
        if current.status == "not_run":
            self._steps[step] = current.model_copy(update={"status": "skipped"})

    def steps(self) -> list[WorkflowStepDebug]:
        return [self._steps[step] for step in STEP_ORDER if step in self._steps]

    def step_result(self, step: str) -> dict[str, Any] | None:
        debug_step = self._steps.get(step)
        if debug_step is None:
            return None
        return debug_step.result

    def last_completed_step(self) -> str | None:
        completed: list[str] = []
        for step in STEP_ORDER:
            debug_step = self._steps.get(step)
            if debug_step is not None and debug_step.status == "ok":
                completed.append(step)
        return completed[-1] if completed else None


def build_debug_result(
    task: WorkflowTask,
    collector: WorkflowDebugCollector,
    *,
    workflow_result: WorkflowResult | None = None,
    status: WorkflowStatus | None = None,
    final_answer: str | None = None,
    error_message: str | None = None,
    stopped_at: str | None = None,
    final_state: WorkflowGraphState | None = None,
) -> WorkflowDebugResult:
    resolved_status = status
    resolved_final_answer = final_answer
    resolved_error_message = error_message

    if workflow_result is not None:
        resolved_status = workflow_result.status
        resolved_final_answer = workflow_result.final_answer
        resolved_error_message = workflow_result.error_message

    if final_state is not None and resolved_status is None:
        from app.workflow.state import to_workflow_result

        derived = to_workflow_result(final_state)
        resolved_status = derived.status
        resolved_final_answer = derived.final_answer
        resolved_error_message = derived.error_message

    return WorkflowDebugResult(
        request_id=task.request_id,
        workflow_run_id=task.workflow_run_id,
        user_id=task.user_id,
        chat_id=task.chat_id,
        status=resolved_status or WorkflowStatus.FAILED,
        final_answer=resolved_final_answer,
        error_message=resolved_error_message,
        stopped_at=stopped_at or collector.last_completed_step(),
        intent_parser=collector.step_result("parse_intent"),
        steps=collector.steps(),
    )
