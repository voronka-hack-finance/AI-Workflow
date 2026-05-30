"""Shared types and enums used across contracts."""
from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel

SchemaVersion = str
RequestId = str
WorkflowRunId = str
UserId = str
ChatId = str


class DateRange(BaseModel):
    start_date: str | None = None
    end_date: str | None = None


class WarningItem(BaseModel):
    code: str | None = None
    message: str


class Metadata(BaseModel):
    model_config = {"extra": "allow"}


class TransactionDirection(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"


class FocusDirection(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"
    ALL = "all"


class PeriodType(StrEnum):
    TODAY = "today"
    YESTERDAY = "yesterday"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    CURRENT_WEEK = "current_week"
    CURRENT_MONTH = "current_month"
    PREVIOUS_MONTH = "previous_month"
    CUSTOM = "custom"
    UNKNOWN = "unknown"


class ComparisonType(StrEnum):
    PREVIOUS_PERIOD = "previous_period"
    PREVIOUS_WEEK = "previous_week"
    PREVIOUS_MONTH = "previous_month"
    CUSTOM = "custom"


class RecommendationHorizon(StrEnum):
    TODAY = "today"
    NEXT_7_DAYS = "next_7_days"
    NEXT_MONTH = "next_month"
    UNTIL_SALARY = "until_salary"
    GOAL_DEADLINE = "goal_deadline"


class BudgetPlanHorizon(StrEnum):
    NEXT_7_DAYS = "next_7_days"
    NEXT_MONTH = "next_month"
    UNTIL_SALARY = "until_salary"


class AgentStyle(StrEnum):
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    STRICT = "strict"


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    STRICT = "strict"


class OutputFormat(StrEnum):
    CHAT_TEXT = "chat_text"
    CARDS = "cards"
    JSON = "json"


class MaxCutLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ClarificationReason(StrEnum):
    MISSING_REQUIRED_DATA = "missing_required_data"
    LOW_INTENT_CONFIDENCE = "low_intent_confidence"
    AMBIGUOUS_REQUEST = "ambiguous_request"


class CalculationMode(StrEnum):
    FULL = "full"
    PARTIAL = "partial"
    CLARIFICATION_REQUIRED = "clarification_required"


class FunctionResultStatus(StrEnum):
    SUCCESS = "success"
    EMPTY_RESULT = "empty_result"
    NEEDS_CLARIFICATION = "needs_clarification"
    ERROR = "error"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContentAgentName(StrEnum):
    SAFETY = "safety"
    SPENDING_DETECTIVE = "spending_detective"
    GROWTH = "growth"
    BUDGET_PLANNER = "budget_planner"
    HABIT_COACH = "habit_coach"


MVP_ANALYTICS_FUNCTIONS: frozenset[str] = frozenset(
    {
        "period_analysis",
        "expense_breakdown",
        "income_analysis",
        "cashflow_analysis",
        "category_analysis",
        "transfer_analysis",
        "spending_leak_detection",
        "budget_recommendation",
        "budget_plan",
        "action_plan",
        "goal_analysis",
        "emergency_fund_analysis",
        "debt_analysis",
    }
)

JsonDict = dict[str, Any]
FieldList = list[str]
