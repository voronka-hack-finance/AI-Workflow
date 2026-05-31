"""Backend data fetch abstraction (mock or RabbitMQ)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from shared_contracts.common import DateRange

from app.schemas.backend_dto import (
    BackendCategoryProfile,
    BackendTransaction,
    BackendUserContext,
)


@dataclass(frozen=True)
class TransactionFilters:
    direction: str | None = None
    categories: list[str] = field(default_factory=list)
    mcc: list[str] = field(default_factory=list)
    account_id: str | None = None
    card_last4: str | None = None


@dataclass(frozen=True)
class BackendDataFetchParams:
    request_id: str
    workflow_run_id: str
    user_id: str
    chat_id: str
    data_types: list[str]
    period: DateRange
    comparison_period: DateRange | None
    transaction_filters: TransactionFilters


@dataclass
class BackendDataFetchResult:
    transactions: list[BackendTransaction] = field(default_factory=list)
    previous_period_transactions: list[BackendTransaction] = field(default_factory=list)
    user_context: BackendUserContext | None = None
    category_profiles: list[BackendCategoryProfile] = field(default_factory=list)
    status: str = "success"
    errors: list[dict[str, str]] = field(default_factory=list)


class BackendDataFetcher(Protocol):
    async def fetch(self, params: BackendDataFetchParams) -> BackendDataFetchResult: ...
