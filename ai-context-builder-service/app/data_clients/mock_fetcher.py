"""Mock backend data fetcher for tests and local dev without RabbitMQ."""
from __future__ import annotations

from shared_contracts.common import DateRange

from app.data_clients.backend_data_fetcher import (
    BackendDataFetchParams,
    BackendDataFetchResult,
)
from app.data_clients.mock_provider import MockDataProvider
from app.schemas.backend_dto import BackendCategoryProfile, BackendTransaction, BackendUserContext


class MockBackendDataFetcher:
    def __init__(self, provider: MockDataProvider | None = None) -> None:
        self._provider = provider or MockDataProvider()

    async def fetch(self, params: BackendDataFetchParams) -> BackendDataFetchResult:
        transactions = await self._provider.fetch_transactions(params.user_id, params.period)
        previous: list[BackendTransaction] = []
        if (
            params.comparison_period is not None
            and "previous_period_transactions" in params.data_types
        ):
            previous = await self._provider.fetch_previous_period_transactions(
                params.user_id,
                params.comparison_period,
            )

        raw_user_context = await self._provider.fetch_user_context(params.user_id)
        user_context: BackendUserContext | None = raw_user_context
        raw_categories = await self._provider.fetch_category_profiles(params.user_id)
        category_profiles: list[BackendCategoryProfile] = raw_categories

        return BackendDataFetchResult(
            transactions=transactions,
            previous_period_transactions=previous,
            user_context=user_context,
            category_profiles=category_profiles,
            status="success",
        )
