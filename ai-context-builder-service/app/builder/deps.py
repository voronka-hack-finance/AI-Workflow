"""Dependency injection for context builder."""
from __future__ import annotations

from functools import lru_cache

from app.builder.context_builder_service import ContextBuilderService
from app.core.config import get_settings
from app.data_clients.factory import create_backend_data_fetcher


@lru_cache
def get_context_builder_service() -> ContextBuilderService:
    settings = get_settings()
    return ContextBuilderService(backend_data_fetcher=create_backend_data_fetcher(settings))
