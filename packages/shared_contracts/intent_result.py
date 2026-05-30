"""Intent result contract models."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from shared_contracts.common import (
    AgentStyle,
    BudgetPlanHorizon,
    ChatId,
    ClarificationReason,
    Difficulty,
    FocusDirection,
    MaxCutLevel,
    MVP_ANALYTICS_FUNCTIONS,
    OutputFormat,
    PeriodType,
    RecommendationHorizon,
    RequestId,
    SchemaVersion,
    UserId,
    ComparisonType,
)


class PeriodInput(BaseModel):
    type: PeriodType | str = PeriodType.UNKNOWN
    start_date: str | None = None
    end_date: str | None = None


class ComparisonInput(BaseModel):
    enabled: bool = False
    type: ComparisonType | str | None = None
    start_date: str | None = None
    end_date: str | None = None


class FocusInput(BaseModel):
    category: str | None = None
    categories: list[str] = Field(default_factory=list)
    merchant: str | None = None
    mcc: str | None = None
    card_id: str | None = None
    direction: FocusDirection | str | None = None


class GoalInput(BaseModel):
    name: str | None = None
    amount: float | None = None
    deadline_months: int | None = None


class BudgetPlanInput(BaseModel):
    horizon: BudgetPlanHorizon | str | None = None
    available_money: float | None = None
    mandatory_expenses: float | None = None


class DebtInput(BaseModel):
    requested: bool = False


class EmergencyFundInput(BaseModel):
    requested: bool = False


class StyleInput(BaseModel):
    agent_style: AgentStyle | str = AgentStyle.BALANCED
    difficulty: Difficulty | str = Difficulty.MEDIUM
    output_format: OutputFormat | str = OutputFormat.CHAT_TEXT


class ConstraintsInput(BaseModel):
    protected_categories: list[str] = Field(default_factory=list)
    allowed_to_cut: list[str] = Field(default_factory=list)
    max_cut_level: MaxCutLevel | str | None = None


class ClarificationInput(BaseModel):
    required: bool = False
    reason: ClarificationReason | str | None = None
    missing_fields: list[str] = Field(default_factory=list)
    question: str | None = None


class IntentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    primary_intent: str = "unknown"
    intents: list[str] = Field(default_factory=list)
    intent_confidence: float = 0.0
    requested_functions: list[str] = Field(default_factory=list)
    period: PeriodInput = Field(default_factory=PeriodInput)
    comparison: ComparisonInput = Field(default_factory=ComparisonInput)
    focus: FocusInput = Field(default_factory=FocusInput)
    recommendation_horizon: RecommendationHorizon | str | None = None
    goal: GoalInput = Field(default_factory=GoalInput)
    budget_plan: BudgetPlanInput = Field(default_factory=BudgetPlanInput)
    debt: DebtInput = Field(default_factory=DebtInput)
    emergency_fund: EmergencyFundInput = Field(default_factory=EmergencyFundInput)
    style: StyleInput = Field(default_factory=StyleInput)
    constraints: ConstraintsInput = Field(default_factory=ConstraintsInput)
    clarification: ClarificationInput = Field(default_factory=ClarificationInput)


class IntentParserResponse(BaseModel):
    schema_version: SchemaVersion = "1.0"
    request_id: RequestId
    user_id: UserId
    chat_id: ChatId
    raw_message: str
    intent_result: IntentResult


def validate_mvp_function_name(function_name: str) -> str:
    if function_name not in MVP_ANALYTICS_FUNCTIONS:
        raise ValueError(f"Unknown MVP analytics function: {function_name}")
    return function_name
