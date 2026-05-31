"""RabbitMQ-backed backend data fetcher."""
from __future__ import annotations

from app.data_clients.backend_data_fetcher import BackendDataFetchParams, BackendDataFetchResult
from app.queue.backend_data_client import BackendDataRabbitMQClient


class RabbitMQBackendDataFetcher:
    def __init__(self, client: BackendDataRabbitMQClient) -> None:
        self._client = client

    async def fetch(self, params: BackendDataFetchParams) -> BackendDataFetchResult:
        return await self._client.fetch(params)
