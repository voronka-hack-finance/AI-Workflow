"""Base HTTP client for AI services."""
from __future__ import annotations

import logging
import time
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from app.core.errors import ContractValidationError
from shared_http import ServiceHttpClient

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class BaseServiceClient:
    def __init__(
        self,
        *,
        base_url: str,
        service_name: str,
        timeout: float,
        max_retries: int,
    ) -> None:
        self._service_name = service_name
        self._http = ServiceHttpClient(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

    async def _post(
        self,
        path: str,
        payload: dict[str, Any],
        response_model: type[T],
        *,
        request_id: str | None = None,
        workflow_run_id: str | None = None,
    ) -> T:
        started = time.perf_counter()
        log_extra = {
            "service_name": "ai-workflow-service",
            "dependency": self._service_name,
            "request_id": request_id,
            "workflow_run_id": workflow_run_id,
            "event": "dependency_call",
        }
        try:
            raw = await self._http.post_json(path, payload)
            result = response_model.model_validate(raw)
        except ValidationError as exc:
            logger.exception(
                "Contract validation failed",
                extra={**log_extra, "error_type": "ContractValidationError"},
            )
            raise ContractValidationError(str(exc)) from exc
        else:
            duration_ms = int((time.perf_counter() - started) * 1000)
            logger.info(
                "Dependency call succeeded",
                extra={**log_extra, "status": "ok", "duration_ms": duration_ms},
            )
            return result
