"""RabbitMQ publisher for workflow results (ai.workflow.results)."""
from __future__ import annotations

import asyncio
import logging

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractConnection

from app.core.config import Settings, get_settings
from app.queue.workflow_job_log import log_workflow_result
from app.schemas.workflow_result_message import WorkflowResultMessage

logger = logging.getLogger(__name__)

_PUBLISH_MAX_ATTEMPTS = 3
_PUBLISH_RETRY_DELAY_SECONDS = 0.5


class WorkflowResultPublisher:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._connection: AbstractConnection | None = None
        self._channel: AbstractChannel | None = None

    @property
    def queue_name(self) -> str:
        return self._settings.rabbitmq_workflow_result_queue

    async def _ensure_channel(self) -> AbstractChannel:
        if self._channel is not None and not self._channel.is_closed:
            return self._channel

        self._connection = await aio_pika.connect_robust(self._settings.rabbitmq_url)
        self._channel = await self._connection.channel()
        await self._channel.declare_queue(self.queue_name, durable=True)
        return self._channel

    async def publish(self, message: WorkflowResultMessage) -> None:
        last_error: Exception | None = None
        for attempt in range(1, _PUBLISH_MAX_ATTEMPTS + 1):
            try:
                await self._publish_once(message)
                log_workflow_result(
                    "PUBLISHED",
                    queue=self.queue_name,
                    workflow_run_id=message.workflow_run_id,
                    chat_id=message.chat_id,
                    message_id=message.message_id,
                    status=message.status,
                    attempt=attempt,
                )
                logger.info(
                    "workflow_result_published",
                    extra={
                        "event": "workflow_result_published",
                        "workflow_run_id": message.workflow_run_id,
                        "chat_id": message.chat_id,
                        "message_id": message.message_id,
                        "status": message.status,
                        "queue": self.queue_name,
                    },
                )
                return
            except Exception as exc:
                last_error = exc
                log_workflow_result(
                    "PUBLISH_FAILED",
                    queue=self.queue_name,
                    workflow_run_id=message.workflow_run_id,
                    attempt=attempt,
                    error_type=type(exc).__name__,
                )
                logger.warning(
                    "workflow_result_publish_failed",
                    extra={
                        "event": "workflow_result_publish_failed",
                        "workflow_run_id": message.workflow_run_id,
                        "chat_id": message.chat_id,
                        "message_id": message.message_id,
                        "attempt": attempt,
                        "max_attempts": _PUBLISH_MAX_ATTEMPTS,
                        "error_type": type(exc).__name__,
                    },
                )
                if attempt < _PUBLISH_MAX_ATTEMPTS:
                    await asyncio.sleep(_PUBLISH_RETRY_DELAY_SECONDS)

        assert last_error is not None
        raise last_error

    async def _publish_once(self, message: WorkflowResultMessage) -> None:
        channel = await self._ensure_channel()
        body = aio_pika.Message(
            body=message.model_dump_json().encode("utf-8"),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await channel.default_exchange.publish(body, routing_key=self.queue_name)

    async def close(self) -> None:
        if self._channel is not None and not self._channel.is_closed:
            await self._channel.close()
        if self._connection is not None and not self._connection.is_closed:
            await self._connection.close()
        self._channel = None
        self._connection = None
