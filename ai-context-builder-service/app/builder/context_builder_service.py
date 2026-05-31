"""Orchestrate context building pipeline."""
from __future__ import annotations

from shared_contracts.common import DateRange, FocusDirection
from shared_contracts.context_package import (
    AppliedFilters,
    ContextPackage,
    ContextPackageData,
    DataRequirements,
)
from shared_contracts.intent_result import IntentResult

from app.builder.context_package_builder import ContextPackageBuilder
from app.builder.data_quality_builder import DataQualityBuilder
from app.data_adapters.category_mapper import CategoryMapper
from app.data_adapters.transaction_mapper import TransactionMapper
from app.data_adapters.user_context_mapper import UserContextMapper
from app.data_adapters.warnings import NormalizationWarnings
from app.data_clients.backend_data_fetcher import (
    BackendDataFetchParams,
    BackendDataFetcher,
    TransactionFilters,
)
from app.planning.data_requirements_resolver import DataRequirementsResolver
from app.planning.date_resolver import DateResolver
from app.planning.execution_plan_builder import ExecutionPlanBuilder
from app.planning.function_expander import FunctionExpander
from app.schemas.context_builder_request import ContextBuilderRequest


class ContextBuilderService:
    def __init__(
        self,
        backend_data_fetcher: BackendDataFetcher,
        *,
        function_expander: FunctionExpander | None = None,
        execution_plan_builder: ExecutionPlanBuilder | None = None,
        date_resolver: DateResolver | None = None,
        data_requirements_resolver: DataRequirementsResolver | None = None,
        transaction_mapper: TransactionMapper | None = None,
        user_context_mapper: UserContextMapper | None = None,
        category_mapper: CategoryMapper | None = None,
        data_quality_builder: DataQualityBuilder | None = None,
        package_builder: ContextPackageBuilder | None = None,
    ) -> None:
        self._backend_data_fetcher = backend_data_fetcher
        self._function_expander = function_expander or FunctionExpander()
        self._execution_plan_builder = execution_plan_builder or ExecutionPlanBuilder()
        self._date_resolver = date_resolver or DateResolver()
        self._data_requirements_resolver = data_requirements_resolver or DataRequirementsResolver()
        self._transaction_mapper = transaction_mapper or TransactionMapper()
        self._user_context_mapper = user_context_mapper or UserContextMapper()
        self._category_mapper = category_mapper or CategoryMapper()
        self._data_quality_builder = data_quality_builder or DataQualityBuilder()
        self._package_builder = package_builder or ContextPackageBuilder()

    async def build(self, request: ContextBuilderRequest) -> ContextPackage:
        intent_result = request.intent_result
        source_message = request.source_message
        requested_functions = list(intent_result.requested_functions)

        expanded_functions = self._function_expander.expand(requested_functions)
        execution_plan = self._execution_plan_builder.build(expanded_functions)
        resolved_period, resolved_comparison = self._date_resolver.resolve_from_intent(
            intent_result,
            current_date=source_message.current_date,
            timezone=source_message.timezone,
        )
        data_requirements = self._data_requirements_resolver.resolve(
            expanded_functions,
            intent_result,
        )
        applied_filters = self._build_applied_filters(intent_result, resolved_period)

        period_range = DateRange(
            start_date=resolved_period.start_date,
            end_date=resolved_period.end_date,
        )
        comparison_range = DateRange(
            start_date=resolved_comparison.start_date,
            end_date=resolved_comparison.end_date,
        )

        data_types = self._resolve_data_types(data_requirements, intent_result)
        backend_data = await self._backend_data_fetcher.fetch(
            BackendDataFetchParams(
                request_id=request.request_id,
                workflow_run_id=request.workflow_run_id,
                user_id=request.user_id,
                chat_id=request.chat_id,
                data_types=data_types,
                period=period_range,
                comparison_period=comparison_range
                if "previous_period_transactions" in data_types
                else None,
                transaction_filters=self._build_transaction_filters(intent_result),
            )
        )

        normalization = NormalizationWarnings()
        transactions = self._transaction_mapper.map_many(backend_data.transactions, normalization)
        previous_period_transactions = self._transaction_mapper.map_many(
            backend_data.previous_period_transactions,
            normalization,
        )
        # #region agent log
        from app.debug_session_log import debug_session_log

        debug_session_log(
            location="context_builder_service.py:build:after_map",
            message="transactions after backend fetch and map",
            hypothesis_id="H3-H5",
            data={
                "backend_status": backend_data.status,
                "backend_errors": backend_data.errors,
                "backend_raw_count": len(backend_data.transactions),
                "mapped_count": len(transactions),
                "previous_mapped_count": len(previous_period_transactions),
                "normalization_warnings": normalization.warnings,
                "resolved_period": {
                    "start": resolved_period.start_date,
                    "end": resolved_period.end_date,
                },
                "applied_direction": str(applied_filters.direction),
            },
        )
        # #endregion
        user_context = self._user_context_mapper.map_one(backend_data.user_context)
        category_profiles = self._category_mapper.map_many(
            backend_data.category_profiles,
            normalization,
        )

        data = ContextPackageData(
            transactions=transactions,
            previous_period_transactions=previous_period_transactions,
            user_context=user_context,
            category_profiles=category_profiles,
            existing_financial_analysis_result=None,
        )

        data_quality = self._data_quality_builder.build(
            data=data,
            requirements=data_requirements,
            intent_result=intent_result,
            normalization=normalization,
        )

        return self._package_builder.build(
            request_id=request.request_id,
            workflow_run_id=request.workflow_run_id,
            user_id=request.user_id,
            chat_id=request.chat_id,
            source_message=source_message,
            intent_result=intent_result,
            requested_functions=requested_functions,
            expanded_functions=expanded_functions,
            execution_plan=execution_plan,
            resolved_period=resolved_period,
            resolved_comparison=resolved_comparison,
            data_requirements=data_requirements,
            applied_filters=applied_filters,
            data=data,
            data_quality=data_quality,
        )

    def _resolve_data_types(
        self,
        requirements: DataRequirements,
        intent_result: IntentResult,
    ) -> list[str]:
        data_types: set[str] = set(requirements.hard_required_data)
        data_types.update(requirements.soft_required_data)
        data_types.update(requirements.optional_data)
        if intent_result.comparison.enabled:
            data_types.add("previous_period_transactions")
        return sorted(data_types)

    def _build_transaction_filters(self, intent_result: IntentResult) -> TransactionFilters:
        focus = intent_result.focus
        direction: str | None = None
        if focus.direction is not None:
            raw_direction = focus.direction
            if hasattr(raw_direction, "value"):
                raw_direction = raw_direction.value
            direction = str(raw_direction).lower()
        return TransactionFilters(
            direction=direction,
            categories=list(focus.categories),
            mcc=[focus.mcc] if focus.mcc else [],
            account_id=focus.card_id,
            card_last4=None,
        )

    def _build_applied_filters(
        self,
        intent_result: IntentResult,
        resolved_period,
    ) -> AppliedFilters:
        focus = intent_result.focus
        direction = focus.direction or FocusDirection.ALL
        return AppliedFilters(
            period=DateRange(
                start_date=resolved_period.start_date,
                end_date=resolved_period.end_date,
            ),
            direction=direction,
            category=focus.category,
            categories=list(focus.categories),
            merchant=focus.merchant,
            mcc=focus.mcc,
            card_id=focus.card_id,
        )
