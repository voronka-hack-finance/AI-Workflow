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
from app.queue.workflow_job_log import log_workflow_job
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
        # #region agent log
        from app.debug_session_log import debug_session_log

        _rabbit_host = (
            self._settings.rabbitmq_url.split("@")[-1]
            if "@" in self._settings.rabbitmq_url
            else self._settings.rabbitmq_url
        )
        debug_session_log(
            location="consumer.py:start",
            message="consumer_bound",
            hypothesis_id="H1",
            data={
                "queue": self._settings.rabbitmq_workflow_queue,
                "rabbitmq_target": _rabbit_host,
            },
        )
        # #endregion
        declaration = self._queue.declaration_result
        messages_ready = declaration.message_count if declaration is not None else "unknown"
        consumers = declaration.consumer_count if declaration is not None else "unknown"
        log_workflow_job(
            "LISTENING",
            queue=self._settings.rabbitmq_workflow_queue,
            broker=(
                self._settings.rabbitmq_url.split("@")[-1]
                if "@" in self._settings.rabbitmq_url
                else self._settings.rabbitmq_url
            ),
            messages_ready=messages_ready,
            consumers_on_queue=consumers,
            consumer_tag=self._consumer_tag,
            prefetch=self._settings.rabbitmq_prefetch_count,
        )
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
        # #region agent log
        from app.debug_session_log import debug_session_log

        debug_session_log(
            location="consumer.py:_on_message",
            message="raw_amqp_message_received",
            hypothesis_id="H1",
            data={"body_bytes": len(message.body)},
        )
        # #endregion
        log_workflow_job(
            "AMQP_RECEIVED",
            delivery_tag=message.delivery_tag,
            body_bytes=len(message.body),
            redelivered=message.redelivered,
        )
        async with self._semaphore:
            await self._process_message(message)

    async def _process_message(self, message: AbstractIncomingMessage) -> None:
        try:
            task = parse_workflow_message(message.body)
        except RabbitMQMessageError as exc:
            # #region agent log
            from app.debug_session_log import debug_session_log

            debug_session_log(
                location="consumer.py:_process_message",
                message="invalid_workflow_task_payload",
                hypothesis_id="H4",
                data={"error": str(exc), "body_bytes": len(message.body)},
            )
            # #endregion
            log_workflow_job(
                "REJECT_INVALID_PAYLOAD",
                error=str(exc),
                body_bytes=len(message.body),
            )
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
        log_workflow_job(
            "PULLED_FROM_QUEUE",
            request_id=task.request_id,
            workflow_run_id=task.workflow_run_id,
            user_id=task.user_id,
            chat_id=task.chat_id,
            message_id=task.message_id,
        )
        logger.info("Processing workflow task", extra=log_extra)
        # #region agent log
        from app.debug_session_log import debug_session_log

        debug_session_log(
            location="consumer.py:_process_message",
            message="workflow_task_parsed",
            hypothesis_id="H1",
            data={
                "request_id": task.request_id,
                "workflow_run_id": task.workflow_run_id,
                "chat_id": task.chat_id,
                "message_id": task.message_id,
            },
        )
        # #endregion

        log_workflow_job("PROCESSING_START", workflow_run_id=task.workflow_run_id)
        try:
            result = await self._orchestrator.run_workflow(task)
        except Exception as exc:
            log_workflow_job(
                "NACK_REQUEUE",
                workflow_run_id=task.workflow_run_id,
                error_type=type(exc).__name__,
            )
            logger.exception(
                "Transient workflow processing error",
                extra={**log_extra, "event": "message_processing_error"},
            )
            await message.nack(requeue=True)
            return

        log_workflow_job(
            "ACK_DONE",
            workflow_run_id=task.workflow_run_id,
            status=str(result.status),
            has_final_answer=bool(result.final_answer),
        )
        logger.info(
            "Workflow task processed",
            extra={**log_extra, "event": "message_processed", "status": result.status},
        )
        # #region agent log
        debug_session_log(
            location="consumer.py:_process_message",
            message="workflow_task_finished",
            hypothesis_id="H5",
            data={
                "workflow_run_id": task.workflow_run_id,
                "status": str(result.status),
                "has_final_answer": bool(result.final_answer),
                "has_error_message": bool(result.error_message),
            },
        )
        # #endregion
        await message.ack()

    async def process_payload(self, payload: dict[str, Any]) -> None:
        """Process a raw payload without RabbitMQ (for tests)."""
        task = parse_workflow_message(json_bytes(payload))
        await self._orchestrator.run_workflow(task)


def json_bytes(payload: dict[str, Any]) -> bytes:
    import json

    return json.dumps(payload).encode("utf-8")
