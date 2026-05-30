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
from app.workflow.orchestrator import WorkflowOrchestrator

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    backend_chat = MockBackendChatClient()
    orchestrator = WorkflowOrchestrator(backend_chat=backend_chat)
    consumer = WorkflowConsumer(settings=settings, orchestrator=orchestrator)
    publisher = WorkflowPublisher(settings=settings)
    app.state.orchestrator = orchestrator
    app.state.workflow_publisher = publisher
    app.state.workflow_consumer = consumer
    if settings.ai_workflow_enable_rabbitmq_consumer:
        await consumer.start()
    try:
        yield
    finally:
        if settings.ai_workflow_enable_rabbitmq_consumer:
            await consumer.stop()
        await publisher.close()


app = FastAPI(
    title="AI Workflow Service",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(workflow_router)
