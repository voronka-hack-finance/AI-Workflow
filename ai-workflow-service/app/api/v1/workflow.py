"""Workflow HTTP trigger endpoints."""
from __future__ import annotations

from typing import Literal

import aio_pika
from fastapi import APIRouter, HTTPException, Query, Request

from app.core.config import get_settings
from app.queue.producer import WorkflowPublisher
from app.schemas.workflow_debug_result import WorkflowDebugResult
from app.schemas.workflow_enqueue_response import WorkflowEnqueueResponse
from app.schemas.workflow_result import WorkflowResult
from app.schemas.workflow_run_request import WorkflowBatchRunRequest, WorkflowRunRequest
from app.workflow.orchestrator import WorkflowOrchestrator
from app.workflow.statuses import WorkflowStatus

router = APIRouter(prefix="/api/v1/workflow", tags=["workflow"])


def _ensure_http_trigger_enabled() -> None:
    if not get_settings().ai_workflow_enable_http_trigger:
        raise HTTPException(status_code=404, detail="HTTP workflow trigger is disabled")


@router.post("/run", response_model=WorkflowResult)
async def run_workflow(request: WorkflowRunRequest, http_request: Request) -> WorkflowResult:
    _ensure_http_trigger_enabled()
    orchestrator: WorkflowOrchestrator = http_request.app.state.orchestrator
    return await orchestrator.run_workflow(request.to_workflow_task())


@router.post("/run/debug", response_model=WorkflowDebugResult)
async def run_workflow_debug(
    request: WorkflowRunRequest,
    http_request: Request,
    stop_after: Literal["parse_intent"] | None = Query(default=None),
) -> WorkflowDebugResult:
    _ensure_http_trigger_enabled()
    orchestrator: WorkflowOrchestrator = http_request.app.state.orchestrator
    return await orchestrator.run_workflow_debug(
        request.to_workflow_task(),
        stop_after=stop_after,
    )


@router.post("/run/batch", response_model=list[WorkflowResult])
async def run_workflow_batch(
    request: WorkflowBatchRunRequest,
    http_request: Request,
) -> list[WorkflowResult]:
    _ensure_http_trigger_enabled()
    orchestrator: WorkflowOrchestrator = http_request.app.state.orchestrator
    results: list[WorkflowResult] = []
    for item in request.items:
        results.append(await orchestrator.run_workflow(item.to_workflow_task()))
    return results


@router.post("/enqueue", response_model=WorkflowEnqueueResponse)
async def enqueue_workflow(
    request: WorkflowRunRequest,
    http_request: Request,
) -> WorkflowEnqueueResponse:
    _ensure_http_trigger_enabled()
    task = request.to_workflow_task()
    publisher: WorkflowPublisher = http_request.app.state.workflow_publisher
    try:
        await publisher.publish(task)
    except (aio_pika.exceptions.AMQPError, OSError, ConnectionError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Failed to publish workflow task to RabbitMQ",
        ) from exc

    return WorkflowEnqueueResponse(
        request_id=task.request_id,
        workflow_run_id=task.workflow_run_id,
        user_id=task.user_id,
        chat_id=task.chat_id,
        status=WorkflowStatus.QUEUED,
        queue=publisher.queue_name,
    )
