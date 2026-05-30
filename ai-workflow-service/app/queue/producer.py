"""RabbitMQ workflow task publisher."""
from __future__ import annotations

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractConnection

from app.core.config import Settings, get_settings
from app.schemas.workflow_task import WorkflowTask


class WorkflowPublisher:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._connection: AbstractConnection | None = None
        self._channel: AbstractChannel | None = None

    @property
    def queue_name(self) -> str:
        return self._settings.rabbitmq_workflow_queue

    async def _ensure_channel(self) -> AbstractChannel:
        if self._channel is not None and not self._channel.is_closed:
            return self._channel

        self._connection = await aio_pika.connect_robust(self._settings.rabbitmq_url)
        self._channel = await self._connection.channel()
        await self._channel.declare_queue(self.queue_name, durable=True)
        return self._channel

    async def publish(self, task: WorkflowTask) -> None:
        channel = await self._ensure_channel()
        message = aio_pika.Message(
            body=task.model_dump_json().encode("utf-8"),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await channel.default_exchange.publish(
            message,
            routing_key=self.queue_name,
        )

    async def close(self) -> None:
        if self._channel is not None and not self._channel.is_closed:
            await self._channel.close()
        if self._connection is not None and not self._connection.is_closed:
            await self._connection.close()
        self._channel = None
        self._connection = None
