"""RabbitMQ connection helpers."""
from __future__ import annotations

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractQueue

from app.core.config import Settings, get_settings


class RabbitMQConnection:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._connection: AbstractConnection | None = None
        self._channel: AbstractChannel | None = None
        self._queue: AbstractQueue | None = None

    @property
    def settings(self) -> Settings:
        return self._settings

    async def connect(self) -> AbstractQueue:
        if self._queue is not None:
            return self._queue

        self._connection = await aio_pika.connect_robust(self._settings.rabbitmq_url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=self._settings.rabbitmq_prefetch_count)
        self._queue = await self._channel.declare_queue(
            self._settings.rabbitmq_workflow_queue,
            durable=True,
        )
        return self._queue

    async def close(self) -> None:
        if self._channel is not None and not self._channel.is_closed:
            await self._channel.close()
        if self._connection is not None and not self._connection.is_closed:
            await self._connection.close()
        self._queue = None
        self._channel = None
        self._connection = None
