"""HTTP data clients stub — to be implemented when backend is ready."""
from __future__ import annotations

from shared_contracts.common import DateRange

from app.schemas.backend_dto import (
    BackendCategoryProfile,
    BackendTransaction,
    BackendUserContext,
)


class HttpDataClientNotConfiguredError(NotImplementedError):
    """Raised when HTTP backend clients are requested but not configured."""


class HttpTransactionsClient:
    async def fetch_transactions(
        self,
        user_id: str,
        period: DateRange,
    ) -> list[BackendTransaction]:
        raise HttpDataClientNotConfiguredError(
            "HTTP transactions client is not configured yet. Use CONTEXT_BUILDER_DATA_PROVIDER=mock."
        )

    async def fetch_previous_period_transactions(
        self,
        user_id: str,
        period: DateRange,
    ) -> list[BackendTransaction]:
        raise HttpDataClientNotConfiguredError(
            "HTTP transactions client is not configured yet. Use CONTEXT_BUILDER_DATA_PROVIDER=mock."
        )


class HttpUserContextClient:
    async def fetch_user_context(self, user_id: str) -> BackendUserContext | None:
        raise HttpDataClientNotConfiguredError(
            "HTTP user context client is not configured yet. Use CONTEXT_BUILDER_DATA_PROVIDER=mock."
        )


class HttpCategoryProfilesClient:
    async def fetch_category_profiles(self, user_id: str) -> list[BackendCategoryProfile]:
        raise HttpDataClientNotConfiguredError(
            "HTTP category profiles client is not configured yet. Use CONTEXT_BUILDER_DATA_PROVIDER=mock."
        )
