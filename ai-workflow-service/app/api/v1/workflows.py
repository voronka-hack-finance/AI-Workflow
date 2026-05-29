"""Workflow HTTP API (skeleton)."""
from fastapi import APIRouter

from app.schemas.workflow_task import WorkflowTask
from app.schemas.workflow_result import WorkflowResult

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


@router.post("", response_model=WorkflowResult)
async def trigger_workflow(task: WorkflowTask) -> WorkflowResult:
    # TODO: enqueue workflow task to RabbitMQ
    return WorkflowResult(task_id=task.task_id, status="pending")
