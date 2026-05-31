"""Context package builder tests."""
from shared_contracts.common import CalculationMode, PeriodType
from shared_contracts.context_package import (
    AppliedFilters,
    ContextPackageData,
    DataQuality,
    DataRequirements,
    ResolvedComparison,
    ResolvedPeriod,
)

from app.builder.context_package_builder import ContextPackageBuilder
from tests.conftest import budget_intent, sample_source_message


def test_context_package_builder_shape() -> None:
    builder = ContextPackageBuilder()
    intent = budget_intent()
    package = builder.build(
        request_id="req_001",
        workflow_run_id="run_001",
        user_id="user_123",
        chat_id="chat_001",
        source_message=sample_source_message(),
        intent_result=intent,
        requested_functions=["budget_recommendation"],
        expanded_functions=["income_analysis", "budget_recommendation"],
        execution_plan=[],
        resolved_period=ResolvedPeriod(
            type=PeriodType.CURRENT_MONTH,
            start_date="2026-05-01",
            end_date="2026-05-31",
        ),
        resolved_comparison=ResolvedComparison(enabled=False),
        data_requirements=DataRequirements(hard_required_data=["transactions"]),
        applied_filters=AppliedFilters(
            period={"start_date": "2026-05-01", "end_date": "2026-05-31"},
        ),
        data=ContextPackageData(),
        data_quality=DataQuality(calculation_mode=CalculationMode.FULL),
    )

    assert package.package_type == "analytics_context_package"
    assert package.context_builder.expanded_functions == [
        "income_analysis",
        "budget_recommendation",
    ]
    assert package.analytics_request.mode == "run_functions"
    assert package.analytics_request.response_expected == "financial_analysis_result"
    assert package.metadata.function_registry_version == "v1.0"
