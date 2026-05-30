"""HTTP client wrapper with retries."""
from __future__ import annotations

import asyncio
from typing import Any, Callable, TypeVar

import httpx

from shared_http.errors import (
    InvalidServiceResponseError,
    ServiceTimeoutError,
    ServiceUnavailableError,
)

T = TypeVar("T")

RETRYABLE_STATUS_CODES = {502, 503, 504}


class ServiceHttpClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        max_retries: int = 2,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries

    async def post_json(
        self,
        path: str,
        json: dict[str, Any],
        *,
        validate: Callable[[dict[str, Any]], T] | None = None,
    ) -> dict[str, Any] | T:
        last_error: Exception | None = None
        attempts = self._max_retries + 1

        for attempt in range(attempts):
            try:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.post(
                        f"{self._base_url}{path}",
                        json=json,
                    )
            except httpx.TimeoutException as exc:
                detail = str(exc).strip() or f"timed out after {self._timeout}s"
                last_error = ServiceTimeoutError(f"{self._base_url}{path}: {detail}")
            except httpx.RequestError as exc:
                last_error = ServiceUnavailableError(str(exc))
            else:
                if response.status_code in RETRYABLE_STATUS_CODES:
                    last_error = ServiceUnavailableError(
                        f"HTTP {response.status_code} from {path}"
                    )
                elif response.status_code >= 400:
                    raise InvalidServiceResponseError(
                        f"HTTP {response.status_code} from {path}: {response.text[:200]}"
                    )
                else:
                    try:
                        payload = response.json()
                    except ValueError as exc:
                        raise InvalidServiceResponseError(
                            f"Non-JSON response from {path}"
                        ) from exc
                    if validate is not None:
                        return validate(payload)
                    return payload

            if attempt < attempts - 1:
                await asyncio.sleep(0.1 * (attempt + 1))

        assert last_error is not None
        raise last_error
