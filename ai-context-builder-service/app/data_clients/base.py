"""Data client protocols for backend/data services."""
from __future__ import annotations

from typing import Protocol

from shared_contracts.common import DateRange

from app.schemas.backend_dto import (
    BackendCategoryProfile,
    BackendTransaction,
    BackendUserContext,
)


class TransactionsClientProtocol(Protocol):
    async def fetch_transactions(
        self,
        user_id: str,
        period: DateRange,
    ) -> list[BackendTransaction]: ...


class UserContextClientProtocol(Protocol):
    async def fetch_user_context(self, user_id: str) -> BackendUserContext | None: ...


class CategoryProfilesClientProtocol(Protocol):
    async def fetch_category_profiles(self, user_id: str) -> list[BackendCategoryProfile]: ...


class DataClientsBundle:
    def __init__(
        self,
        transactions: TransactionsClientProtocol,
        user_context: UserContextClientProtocol,
        category_profiles: CategoryProfilesClientProtocol,
    ) -> None:
        self.transactions = transactions
        self.user_context = user_context
        self.category_profiles = category_profiles
