"""Context package contract models."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from shared_contracts.common import (
    CalculationMode,
    ChatId,
    DateRange,
    FocusDirection,
    RequestId,
    SchemaVersion,
    UserId,
    WorkflowRunId,
)
from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import ComparisonInput, IntentResult, PeriodInput
from shared_contracts.normalized_data import (
    CategoryProfile,
    TransactionNormalized,
    UserFinancialContextNormalized,
)


class SourceMessage(BaseModel):
    raw_message: str
    current_date: str
    timezone: str


class ExecutionPlanItem(BaseModel):
    step: int
    function_name: str
    depends_on: list[str] = Field(default_factory=list)


class ResolvedPeriod(PeriodInput):
    source: str = "DateResolver"


class ResolvedComparison(ComparisonInput):
    source: str = "DateResolver"


class DataRequirements(BaseModel):
    hard_required_data: list[str] = Field(default_factory=list)
    soft_required_data: list[str] = Field(default_factory=list)
    optional_data: list[str] = Field(default_factory=list)
    hard_required_fields: list[str] = Field(default_factory=list)
    soft_required_fields: list[str] = Field(default_factory=list)
    optional_enrichment_fields: list[str] = Field(default_factory=list)


class AppliedFilters(BaseModel):
    period: DateRange
    direction: FocusDirection | str | None = None
    category: str | None = None
    categories: list[str] = Field(default_factory=list)
    merchant: str | None = None
    mcc: str | None = None
    card_id: str | None = None


class ContextBuilderMetadata(BaseModel):
    requested_functions: list[str] = Field(default_factory=list)
    expanded_functions: list[str] = Field(default_factory=list)
    execution_plan: list[ExecutionPlanItem] = Field(default_factory=list)
    resolved_period: ResolvedPeriod
    resolved_comparison: ResolvedComparison
    data_requirements: DataRequirements = Field(default_factory=DataRequirements)
    applied_filters: AppliedFilters


class ContextPackageData(BaseModel):
    transactions: list[TransactionNormalized] = Field(default_factory=list)
    previous_period_transactions: list[TransactionNormalized] = Field(default_factory=list)
    user_context: UserFinancialContextNormalized = Field(
        default_factory=UserFinancialContextNormalized
    )
    category_profiles: list[CategoryProfile] = Field(default_factory=list)
    existing_financial_analysis_result: FinancialAnalysisResult | None = None


class DataCoverage(BaseModel):
    transactions_count: int = 0
    previous_period_transactions_count: int = 0
    has_user_context: bool = False
    has_category_profiles: bool = False
    has_existing_financial_analysis_result: bool = False


class DataQuality(BaseModel):
    can_run_analytics: bool = True
    calculation_mode: CalculationMode | str = CalculationMode.FULL
    has_missing_hard_required_data: bool = False
    has_missing_soft_required_data: bool = False
    missing_hard_required_data: list[str] = Field(default_factory=list)
    missing_soft_required_data: list[str] = Field(default_factory=list)
    missing_optional_data: list[str] = Field(default_factory=list)
    missing_hard_required_fields: list[str] = Field(default_factory=list)
    missing_soft_required_fields: list[str] = Field(default_factory=list)
    missing_optional_enrichment_fields: list[str] = Field(default_factory=list)
    normalization_warnings: list[str] = Field(default_factory=list)
    unmapped_categories: list[str] = Field(default_factory=list)
    ambiguous_transactions: list[str] = Field(default_factory=list)
    data_coverage: DataCoverage = Field(default_factory=DataCoverage)


class AnalyticsRequest(BaseModel):
    mode: str = "run_functions"
    functions_to_execute: list[str] = Field(default_factory=list)
    response_expected: str = "financial_analysis_result"


class ContextPackageMetadata(BaseModel):
    context_builder_version: str = "v1.0"
    function_registry_version: str = "v1.0"
    mapper_version: str = "v1.0"
    created_at: str


class ContextPackage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: SchemaVersion = "1.0"
    package_type: str = "analytics_context_package"
    request_id: RequestId
    workflow_run_id: WorkflowRunId
    user_id: UserId
    chat_id: ChatId
    source_message: SourceMessage
    intent_result: IntentResult
    context_builder: ContextBuilderMetadata
    data: ContextPackageData = Field(default_factory=ContextPackageData)
    data_quality: DataQuality = Field(default_factory=DataQuality)
    analytics_request: AnalyticsRequest = Field(default_factory=AnalyticsRequest)
    metadata: ContextPackageMetadata
