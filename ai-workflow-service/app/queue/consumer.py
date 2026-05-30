"""RabbitMQ workflow consumer."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from app.clients.mock_backend_chat_client import MockBackendChatClient
from app.core.config import Settings, get_settings
from app.core.errors import RabbitMQMessageError
from app.queue.message import parse_workflow_message
from app.queue.rabbitmq import RabbitMQConnection
from app.workflow.orchestrator import WorkflowOrchestrator

logger = logging.getLogger(__name__)


class WorkflowConsumer:
    """Consumes workflow tasks from RabbitMQ."""

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        orchestrator: WorkflowOrchestrator | None = None,
        rabbitmq: RabbitMQConnection | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        backend_chat = MockBackendChatClient()
        self._orchestrator = orchestrator or WorkflowOrchestrator(backend_chat=backend_chat)
        self._rabbitmq = rabbitmq or RabbitMQConnection(self._settings)
        self._semaphore = asyncio.Semaphore(self._settings.ai_workflow_max_concurrent_runs)
        self._consumer_tag: str | None = None
        self._queue: aio_pika.abc.AbstractQueue | None = None
        self._stopped = asyncio.Event()

    async def start(self) -> None:
        self._queue = await self._rabbitmq.connect()
        self._consumer_tag = await self._queue.consume(self._on_message, no_ack=False)
        logger.info(
            "Workflow consumer started",
            extra={
                "event": "consumer_started",
                "queue": self._settings.rabbitmq_workflow_queue,
                "prefetch_count": self._settings.rabbitmq_prefetch_count,
            },
        )

    async def stop(self) -> None:
        if self._queue is not None and self._consumer_tag is not None:
            await self._queue.cancel(self._consumer_tag)
        await self._rabbitmq.close()
        self._stopped.set()
        logger.info("Workflow consumer stopped", extra={"event": "consumer_stopped"})

    async def _on_message(self, message: AbstractIncomingMessage) -> None:
        async with self._semaphore:
            await self._process_message(message)

    async def _process_message(self, message: AbstractIncomingMessage) -> None:
        try:
            task = parse_workflow_message(message.body)
        except RabbitMQMessageError:
            logger.error(
                "Invalid RabbitMQ message",
                extra={"event": "invalid_message", "error_type": "RabbitMQMessageError"},
            )
            await message.reject(requeue=False)
            return

        log_extra = {
            "request_id": task.request_id,
            "workflow_run_id": task.workflow_run_id,
            "event": "message_received",
        }
        logger.info("Processing workflow task", extra=log_extra)

        try:
            result = await self._orchestrator.run_workflow(task)
        except Exception:
            logger.exception(
                "Transient workflow processing error",
                extra={**log_extra, "event": "message_processing_error"},
            )
            await message.nack(requeue=True)
            return

        logger.info(
            "Workflow task processed",
            extra={**log_extra, "event": "message_processed", "status": result.status},
        )
        await message.ack()

    async def process_payload(self, payload: dict[str, Any]) -> None:
        """Process a raw payload without RabbitMQ (for tests)."""
        task = parse_workflow_message(json_bytes(payload))
        await self._orchestrator.run_workflow(task)


def json_bytes(payload: dict[str, Any]) -> bytes:
    import json

    return json.dumps(payload).encode("utf-8")
