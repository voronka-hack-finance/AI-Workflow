"""Expand requested_functions into full dependency set."""
from __future__ import annotations

from app.registry.function_registry import FunctionRegistry


class FunctionExpander:
    def __init__(self, registry: FunctionRegistry | None = None) -> None:
        self._registry = registry or FunctionRegistry()

    def expand(self, requested_functions: list[str]) -> list[str]:
        return self._registry.expand(requested_functions)
