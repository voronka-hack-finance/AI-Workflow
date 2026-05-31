"""Assemble the final Context Package."""
from __future__ import annotations

from datetime import UTC, datetime

from shared_contracts.context_package import (
    AnalyticsRequest,
    AppliedFilters,
    ContextBuilderMetadata,
    ContextPackage,
    ContextPackageData,
    ContextPackageMetadata,
    DataQuality,
    DataRequirements,
    ExecutionPlanItem,
    ResolvedComparison,
    ResolvedPeriod,
    SourceMessage,
)
from shared_contracts.intent_result import IntentResult

from app.registry.function_registry import REGISTRY_VERSION


class ContextPackageBuilder:
    mapper_version = "v1.0"
    context_builder_version = "v1.0"

    def build(
        self,
        *,
        request_id: str,
        workflow_run_id: str,
        user_id: str,
        chat_id: str,
        source_message: SourceMessage,
        intent_result: IntentResult,
        requested_functions: list[str],
        expanded_functions: list[str],
        execution_plan: list[ExecutionPlanItem],
        resolved_period: ResolvedPeriod,
        resolved_comparison: ResolvedComparison,
        data_requirements: DataRequirements,
        applied_filters: AppliedFilters,
        data: ContextPackageData,
        data_quality: DataQuality,
    ) -> ContextPackage:
        return ContextPackage(
            request_id=request_id,
            workflow_run_id=workflow_run_id,
            user_id=user_id,
            chat_id=chat_id,
            source_message=source_message,
            intent_result=intent_result,
            context_builder=ContextBuilderMetadata(
                requested_functions=requested_functions,
                expanded_functions=expanded_functions,
                execution_plan=execution_plan,
                resolved_period=resolved_period,
                resolved_comparison=resolved_comparison,
                data_requirements=data_requirements,
                applied_filters=applied_filters,
            ),
            data=data,
            data_quality=data_quality,
            analytics_request=AnalyticsRequest(
                mode="run_functions",
                functions_to_execute=list(expanded_functions),
                response_expected="financial_analysis_result",
            ),
            metadata=ContextPackageMetadata(
                context_builder_version=self.context_builder_version,
                function_registry_version=REGISTRY_VERSION,
                mapper_version=self.mapper_version,
                created_at=datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            ),
        )
