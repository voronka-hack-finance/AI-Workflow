"""Factory for backend data fetchers."""
from __future__ import annotations

from app.core.config import Settings
from app.data_clients.backend_data_fetcher import BackendDataFetcher
from app.data_clients.mock_fetcher import MockBackendDataFetcher
from app.data_clients.rabbitmq_fetcher import RabbitMQBackendDataFetcher
from app.queue.backend_data_client import BackendDataRabbitMQClient

_rabbitmq_client: BackendDataRabbitMQClient | None = None


def get_rabbitmq_client(settings: Settings) -> BackendDataRabbitMQClient:
    global _rabbitmq_client
    if _rabbitmq_client is None:
        _rabbitmq_client = BackendDataRabbitMQClient(settings)
    return _rabbitmq_client


async def close_rabbitmq_client() -> None:
    global _rabbitmq_client
    if _rabbitmq_client is not None:
        await _rabbitmq_client.close()
        _rabbitmq_client = None


def create_backend_data_fetcher(settings: Settings) -> BackendDataFetcher:
    provider_name = settings.context_builder_data_provider.strip().lower()

    if provider_name == "mock":
        return MockBackendDataFetcher()

    if provider_name == "rabbitmq":
        return RabbitMQBackendDataFetcher(get_rabbitmq_client(settings))

    raise ValueError(
        f"Unsupported CONTEXT_BUILDER_DATA_PROVIDER: {provider_name}. "
        "Allowed values: mock, rabbitmq"
    )
