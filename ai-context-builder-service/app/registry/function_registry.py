"""Function Registry — dependencies and data requirements for analytics functions."""
from __future__ import annotations

from shared_contracts.common import MVP_ANALYTICS_FUNCTIONS
from shared_contracts.context_package import DataRequirements

from app.registry.function_dependencies import (
    FUNCTION_DEPENDENCIES,
    REGISTRY_VERSION,
    get_dependencies,
)
from app.registry.function_requirements import (
    COMPARISON_DATA_REQUIREMENT,
    OPTIONAL_ENRICHMENT_DEFAULT,
    get_requirements,
    merge_requirements,
)


class UnknownFunctionError(ValueError):
    """Raised when an unknown analytics function is requested."""


class CyclicDependencyError(ValueError):
    """Raised when function dependencies contain a cycle."""


class FunctionRegistry:
    version = REGISTRY_VERSION

    def is_known(self, function_name: str) -> bool:
        return function_name in MVP_ANALYTICS_FUNCTIONS

    def validate_known(self, function_name: str) -> str:
        if not self.is_known(function_name):
            raise UnknownFunctionError(f"Unknown MVP analytics function: {function_name}")
        return function_name

    def get_dependencies(self, function_name: str) -> list[str]:
        self.validate_known(function_name)
        return get_dependencies(function_name)

    def expand(self, requested_functions: list[str]) -> list[str]:
        if not requested_functions:
            return []

        for name in requested_functions:
            self.validate_known(name)

        expanded: list[str] = []
        seen: set[str] = set()
        visiting: set[str] = set()

        def visit(name: str) -> None:
            if name in seen:
                return
            if name in visiting:
                raise CyclicDependencyError(f"Cyclic dependency detected at: {name}")
            visiting.add(name)
            for dep in get_dependencies(name):
                visit(dep)
            visiting.remove(name)
            if name not in seen:
                seen.add(name)
                expanded.append(name)

        for name in requested_functions:
            visit(name)

        return expanded

    def get_data_requirements(
        self,
        expanded_functions: list[str],
        *,
        comparison_enabled: bool = False,
    ) -> DataRequirements:
        per_function = [get_requirements(name) for name in expanded_functions]
        merged = merge_requirements(per_function)
        merged = merge_requirements([merged, OPTIONAL_ENRICHMENT_DEFAULT])
        if comparison_enabled:
            merged = merge_requirements([merged, COMPARISON_DATA_REQUIREMENT])
        return merged

    @property
    def all_functions(self) -> frozenset[str]:
        return MVP_ANALYTICS_FUNCTIONS

    @property
    def dependency_map(self) -> dict[str, list[str]]:
        return dict(FUNCTION_DEPENDENCIES)
