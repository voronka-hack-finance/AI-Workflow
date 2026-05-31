"""In-memory mock data provider for development and tests."""
from __future__ import annotations

import json
from pathlib import Path

from shared_contracts.common import DateRange

from app.schemas.backend_dto import (
    BackendCategoryProfile,
    BackendTransaction,
    BackendUserContext,
)

_FIXTURES_PATH = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "mock_backend_data.json"

USER_SCENARIO_MAP: dict[str, str] = {
    "user_missing_savings": "missing_savings",
    "user_unmapped": "unmapped_category",
    "user_empty": "empty",
}


def _load_fixtures() -> dict[str, dict]:
    with _FIXTURES_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


class MockDataProvider:
    def __init__(self, fixtures: dict[str, dict] | None = None) -> None:
        self._fixtures = fixtures or _load_fixtures()

    def _scenario_for_user(self, user_id: str) -> dict:
        scenario_key = USER_SCENARIO_MAP.get(user_id, "default")
        return self._fixtures[scenario_key]

    async def fetch_transactions(
        self,
        user_id: str,
        period: DateRange,
    ) -> list[BackendTransaction]:
        del period
        scenario = self._scenario_for_user(user_id)
        return [BackendTransaction.model_validate(item) for item in scenario["transactions"]]

    async def fetch_previous_period_transactions(
        self,
        user_id: str,
        period: DateRange,
    ) -> list[BackendTransaction]:
        del period
        scenario = self._scenario_for_user(user_id)
        return [
            BackendTransaction.model_validate(item)
            for item in scenario.get("previous_period_transactions", [])
        ]

    async def fetch_user_context(self, user_id: str) -> BackendUserContext | None:
        scenario = self._scenario_for_user(user_id)
        raw = scenario.get("user_context")
        if not raw:
            return None
        return BackendUserContext.model_validate(raw)

    async def fetch_category_profiles(self, user_id: str) -> list[BackendCategoryProfile]:
        scenario = self._scenario_for_user(user_id)
        return [
            BackendCategoryProfile.model_validate(item)
            for item in scenario.get("category_profiles", [])
        ]


class MockTransactionsClient:
    def __init__(self, provider: MockDataProvider) -> None:
        self._provider = provider

    async def fetch_transactions(
        self,
        user_id: str,
        period: DateRange,
    ) -> list[BackendTransaction]:
        return await self._provider.fetch_transactions(user_id, period)

    async def fetch_previous_period_transactions(
        self,
        user_id: str,
        period: DateRange,
    ) -> list[BackendTransaction]:
        return await self._provider.fetch_previous_period_transactions(user_id, period)


class MockUserContextClient:
    def __init__(self, provider: MockDataProvider) -> None:
        self._provider = provider

    async def fetch_user_context(self, user_id: str) -> BackendUserContext | None:
        return await self._provider.fetch_user_context(user_id)


class MockCategoryProfilesClient:
    def __init__(self, provider: MockDataProvider) -> None:
        self._provider = provider

    async def fetch_category_profiles(self, user_id: str) -> list[BackendCategoryProfile]:
        return await self._provider.fetch_category_profiles(user_id)
