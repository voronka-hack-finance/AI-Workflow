"""RabbitMQ client for backend data request/reply."""
from __future__ import annotations

import asyncio
import json
import logging
from uuid import uuid4

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractIncomingMessage

from app.core.config import Settings
from app.core.errors import BackendDataTimeoutError, BackendDataValidationError
from app.data_adapters.gateway_raw_mapper import (
    map_category_profiles,
    map_transactions_page,
    map_user_context,
)
from app.data_clients.backend_data_fetcher import (
    BackendDataFetchParams,
    BackendDataFetchResult,
    TransactionFilters,
)
from app.queue.messages import (
    BackendDataRequestMessage,
    BackendDataResponseMessage,
    PeriodPayload,
    TransactionFiltersPayload,
)

logger = logging.getLogger(__name__)


class BackendDataRabbitMQClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._connection: AbstractConnection | None = None
        self._channel: AbstractChannel | None = None
        self._pending: dict[str, asyncio.Future[BackendDataResponseMessage]] = {}
        self._connect_lock = asyncio.Lock()

    async def connect(self) -> None:
        async with self._connect_lock:
            if self._channel is not None:
                return

            self._connection = await aio_pika.connect_robust(self._settings.rabbitmq_url)
            self._channel = await self._connection.channel()
            response_queue = await self._channel.declare_queue(
                self._settings.rabbitmq_backend_data_response_queue,
                durable=True,
            )
            await response_queue.consume(self._on_response, no_ack=False)
            await self._channel.declare_queue(
                self._settings.rabbitmq_backend_data_request_queue,
                durable=True,
            )
            logger.info(
                "backend_data_rabbitmq_connected",
                extra={
                    "event": "backend_data_rabbitmq_connected",
                    "request_queue": self._settings.rabbitmq_backend_data_request_queue,
                    "response_queue": self._settings.rabbitmq_backend_data_response_queue,
                },
            )

    async def close(self) -> None:
        if self._channel is not None and not self._channel.is_closed:
            await self._channel.close()
        if self._connection is not None and not self._connection.is_closed:
            await self._connection.close()
        self._channel = None
        self._connection = None

    async def fetch(self, params: BackendDataFetchParams) -> BackendDataFetchResult:
        await self.connect()
        assert self._channel is not None

        correlation_id = str(uuid4())
        comparison_period = None
        if params.comparison_period is not None:
            comparison_period = PeriodPayload(
                start_date=params.comparison_period.start_date,
                end_date=params.comparison_period.end_date,
            )

        request_message = BackendDataRequestMessage(
            correlation_id=correlation_id,
            request_id=params.request_id,
            workflow_run_id=params.workflow_run_id,
            user_id=params.user_id,
            chat_id=params.chat_id,
            data_types=params.data_types,
            period=PeriodPayload(
                start_date=params.period.start_date,
                end_date=params.period.end_date,
            ),
            comparison_period=comparison_period,
            transaction_filters=_to_filters_payload(params.transaction_filters),
        )

        loop = asyncio.get_running_loop()
        future: asyncio.Future[BackendDataResponseMessage] = loop.create_future()
        self._pending[correlation_id] = future

        body = request_message.model_dump(mode="json")
        # #region agent log
        from app.debug_session_log import debug_session_log

        debug_session_log(
            location="backend_data_client.py:fetch:request",
            message="backend data request published",
            hypothesis_id="H1-H2",
            data={
                "user_id": params.user_id,
                "request_id": params.request_id,
                "period_start": params.period.start_date,
                "period_end": params.period.end_date,
                "data_types": params.data_types,
                "direction_filter": params.transaction_filters.direction,
                "categories_filter": params.transaction_filters.categories,
            },
        )
        # #endregion
        await self._channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                correlation_id=correlation_id,
            ),
            routing_key=self._settings.rabbitmq_backend_data_request_queue,
        )
        logger.info(
            "backend_data_request_published",
            extra={
                "event": "backend_data_request_published",
                "request_id": params.request_id,
                "workflow_run_id": params.workflow_run_id,
                "user_id": params.user_id,
                "chat_id": params.chat_id,
                "correlation_id": correlation_id,
                "data_types": params.data_types,
            },
        )

        try:
            response = await asyncio.wait_for(
                future,
                timeout=self._settings.context_builder_backend_data_timeout_seconds,
            )
        except TimeoutError as exc:
            self._pending.pop(correlation_id, None)
            raise BackendDataTimeoutError(
                f"Backend data response timeout after "
                f"{self._settings.context_builder_backend_data_timeout_seconds}s"
            ) from exc

        return _to_fetch_result(response)

    async def _on_response(self, message: AbstractIncomingMessage) -> None:
        async with message.process():
            try:
                payload = json.loads(message.body.decode("utf-8"))
                response = BackendDataResponseMessage.model_validate(payload)
            except Exception:
                logger.exception(
                    "backend_data_response_invalid",
                    extra={"event": "backend_data_response_invalid"},
                )
                return

            future = self._pending.get(response.correlation_id)
            if future is None or future.done():
                return

            logger.info(
                "backend_data_response_received",
                extra={
                    "event": "backend_data_response_received",
                    "correlation_id": response.correlation_id,
                    "status": response.status,
                    "transaction_count": len(
                        (response.data.transactions or {}).get("items", [])
                    ),
                },
            )
            future.set_result(response)


def _to_filters_payload(filters: TransactionFilters) -> TransactionFiltersPayload:
    direction = filters.direction
    if direction in {"income", "expense", "all"}:
        normalized_direction = direction
    else:
        normalized_direction = None
    return TransactionFiltersPayload(
        direction=normalized_direction,
        categories=list(filters.categories),
        mcc=list(filters.mcc),
        account_id=filters.account_id,
        card_last4=filters.card_last4,
    )


def _to_fetch_result(response: BackendDataResponseMessage) -> BackendDataFetchResult:
    if response.message_type != "ai.backend_data.response":
        raise BackendDataValidationError("Unexpected backend data response message_type")

    data = response.data
    raw_tx = data.transactions or {}
    raw_items = raw_tx.get("items") or []
    sample_keys = list(raw_items[0].keys()) if raw_items else []
    # #region agent log
    from app.debug_session_log import debug_session_log

    debug_session_log(
        location="backend_data_client.py:_to_fetch_result",
        message="backend data response received",
        hypothesis_id="H1-H3-H4",
        data={
            "status": response.status,
            "errors": [{"code": e.code, "message": e.message} for e in response.errors],
            "raw_transaction_count": len(raw_items),
            "raw_previous_count": len((data.previous_period_transactions or {}).get("items") or []),
            "sample_item_keys": sample_keys,
            "transactions_payload_keys": list(raw_tx.keys()) if raw_tx else [],
        },
    )
    # #endregion
    return BackendDataFetchResult(
        transactions=map_transactions_page(data.transactions),
        previous_period_transactions=map_transactions_page(data.previous_period_transactions),
        user_context=map_user_context(data.user_context),
        category_profiles=map_category_profiles(data.category_profiles),
        status=response.status,
        errors=[{"code": item.code, "message": item.message} for item in response.errors],
    )

