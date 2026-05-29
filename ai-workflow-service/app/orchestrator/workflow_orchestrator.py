"""Workflow orchestration."""
from app.schemas.workflow_task import WorkflowTask
from app.schemas.workflow_result import WorkflowResult
from app.schemas.workflow_status import WorkflowStatus


class WorkflowOrchestrator:
    """Coordinates intent -> context -> analytics -> response pipeline."""

    async def run_workflow(self, task: WorkflowTask) -> WorkflowResult:
        # TODO: implement actual workflow execution
        # TODO: call intent_parser, context_builder, analytics, response_agent clients
        return WorkflowResult(task_id=task.task_id, status=WorkflowStatus.PENDING)
