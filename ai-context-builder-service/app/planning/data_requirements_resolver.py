"""Resolve aggregated data requirements for expanded functions."""
from __future__ import annotations

from shared_contracts.context_package import DataRequirements
from shared_contracts.intent_result import IntentResult

from app.registry.function_registry import FunctionRegistry


class DataRequirementsResolver:
    def __init__(self, registry: FunctionRegistry | None = None) -> None:
        self._registry = registry or FunctionRegistry()

    def resolve(
        self,
        expanded_functions: list[str],
        intent_result: IntentResult,
    ) -> DataRequirements:
        requirements = self._registry.get_data_requirements(
            expanded_functions,
            comparison_enabled=intent_result.comparison.enabled,
        )
        return self._apply_intent_overrides(requirements, intent_result)

    def _apply_intent_overrides(
        self,
        requirements: DataRequirements,
        intent_result: IntentResult,
    ) -> DataRequirements:
        hard_fields = set(requirements.hard_required_fields)
        soft_fields = set(requirements.soft_required_fields)

        if "goal_analysis" in intent_result.requested_functions:
            if intent_result.goal.amount is None:
                hard_fields.add("goal.amount")
            else:
                hard_fields.discard("goal.amount")
            if intent_result.goal.deadline_months is None:
                hard_fields.add("goal.deadline_months")
            else:
                hard_fields.discard("goal.deadline_months")

        if "category_analysis" in intent_result.requested_functions:
            if not intent_result.focus.category:
                hard_fields.add("focus.category")
            else:
                hard_fields.discard("focus.category")

        return DataRequirements(
            hard_required_data=list(requirements.hard_required_data),
            soft_required_data=list(requirements.soft_required_data),
            optional_data=list(requirements.optional_data),
            hard_required_fields=sorted(hard_fields),
            soft_required_fields=sorted(soft_fields),
            optional_enrichment_fields=list(requirements.optional_enrichment_fields),
        )
