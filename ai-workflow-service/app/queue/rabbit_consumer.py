"""RabbitMQ workflow consumer."""
from app.orchestrator.workflow_orchestrator import WorkflowOrchestrator


class RabbitWorkflowConsumer:
    """Consumes workflow tasks from RabbitMQ."""

    def __init__(self, orchestrator: WorkflowOrchestrator | None = None) -> None:
        self._orchestrator = orchestrator or WorkflowOrchestrator()

    async def start(self) -> None:
        # TODO: connect to RabbitMQ and consume workflow queue
        pass

    async def stop(self) -> None:
        # TODO: graceful shutdown
        pass
