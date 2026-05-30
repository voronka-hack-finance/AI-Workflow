"""Financial analysis result contract models."""
from __future__ import annotations

from pydantic import BaseModel, Field

from shared_contracts.common import (
    JsonDict,
    Priority,
    RequestId,
    RiskLevel,
    SchemaVersion,
    UserId,
    FunctionResultStatus,
    WarningItem,
)
from shared_contracts.intent_result import PeriodInput


class FunctionResultMetadata(BaseModel):
    rules_version: str = "v1.0"
    calculated_at: str


class FunctionResult(BaseModel):
    function_name: str
    status: FunctionResultStatus | str
    input_used: JsonDict = Field(default_factory=dict)
    result: JsonDict = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    metadata: FunctionResultMetadata


class AnalysisResult(BaseModel):
    risk_score: float = 0.0
    risk_level: RiskLevel | str | None = None
    main_problem: str | None = None
    problem_tags: list[str] = Field(default_factory=list)
    recommendation_type: str | None = None
    category_to_optimize: list[str] = Field(default_factory=list)
    expected_savings: float = 0.0
    priority: Priority | str | None = None


class FinancialAnalysisMetadata(BaseModel):
    rules_version: str = "v1.0"
    calculated_at: str


class FinancialAnalysisResult(BaseModel):
    schema_version: SchemaVersion = "1.0"
    request_id: RequestId
    user_id: UserId
    period: PeriodInput
    executed_functions: list[str] = Field(default_factory=list)
    function_results: dict[str, FunctionResult] = Field(default_factory=dict)
    analysis_result: AnalysisResult = Field(default_factory=AnalysisResult)
    warnings: list[str | WarningItem] = Field(default_factory=list)
    metadata: FinancialAnalysisMetadata
