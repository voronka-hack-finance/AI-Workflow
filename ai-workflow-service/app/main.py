"""FastAPI application entrypoint."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.health import router as health_router
from app.api.v1.workflow import router as workflow_router
from app.clients.mock_backend_chat_client import MockBackendChatClient
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.queue.consumer import WorkflowConsumer
from app.queue.producer import WorkflowPublisher
from app.queue.result_publisher import WorkflowResultPublisher
from app.workflow.orchestrator import WorkflowOrchestrator

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    backend_chat = MockBackendChatClient()
    result_publisher = WorkflowResultPublisher(settings=settings)
    orchestrator = WorkflowOrchestrator(
        backend_chat=backend_chat,
        result_publisher=result_publisher,
    )
    consumer = WorkflowConsumer(settings=settings, orchestrator=orchestrator)
    publisher = WorkflowPublisher(settings=settings)
    app.state.orchestrator = orchestrator
    app.state.workflow_publisher = publisher
    app.state.workflow_result_publisher = result_publisher
    app.state.workflow_consumer = consumer
    # #region agent log
    from app.debug_session_log import debug_session_log

    _rabbit_host = settings.rabbitmq_url.split("@")[-1] if "@" in settings.rabbitmq_url else settings.rabbitmq_url
    debug_session_log(
        location="main.py:lifespan",
        message="workflow_service_startup",
        hypothesis_id="H2",
        data={
            "consumer_enabled": settings.ai_workflow_enable_rabbitmq_consumer,
            "workflow_queue": settings.rabbitmq_workflow_queue,
            "result_queue": settings.rabbitmq_workflow_result_queue,
            "rabbitmq_target": _rabbit_host,
        },
    )
    from app.queue.workflow_job_log import log_service_rabbitmq_config

    log_service_rabbitmq_config(
        service="ai-workflow-service",
        consumer_enabled=settings.ai_workflow_enable_rabbitmq_consumer,
        tasks_queue=settings.rabbitmq_workflow_queue,
        results_queue=settings.rabbitmq_workflow_result_queue,
        rabbitmq_url=settings.rabbitmq_url,
    )
    # #endregion
    if settings.ai_workflow_enable_rabbitmq_consumer:
        await consumer.start()
    try:
        yield
    finally:
        if settings.ai_workflow_enable_rabbitmq_consumer:
            await consumer.stop()
        await publisher.close()
        await result_publisher.close()


app = FastAPI(
    title="AI Workflow Service",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(workflow_router)
