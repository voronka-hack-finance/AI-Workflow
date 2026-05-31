"""Internal RabbitMQ message schemas for backend data jobs."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class PeriodPayload(BaseModel):
    start_date: str
    end_date: str


class TransactionFiltersPayload(BaseModel):
    direction: Literal["income", "expense", "all"] | None = None
    categories: list[str] = Field(default_factory=list)
    mcc: list[str] = Field(default_factory=list)
    account_id: str | None = None
    card_last4: str | None = None


class BackendDataRequestMessage(BaseModel):
    schema_version: str = "1.0"
    message_type: Literal["ai.backend_data.request"] = "ai.backend_data.request"
    correlation_id: str
    request_id: str
    workflow_run_id: str
    user_id: str
    chat_id: str
    data_types: list[str]
    period: PeriodPayload
    comparison_period: PeriodPayload | None = None
    transaction_filters: TransactionFiltersPayload = Field(default_factory=TransactionFiltersPayload)


class BackendDataErrorItem(BaseModel):
    code: str
    message: str


class BackendDataResponseData(BaseModel):
    transactions: dict[str, Any] | None = None
    previous_period_transactions: dict[str, Any] | None = None
    accounts: dict[str, Any] | None = None
    goals: dict[str, Any] | None = None
    expected_incomes: dict[str, Any] | None = None
    user_context: dict[str, Any] | None = None
    category_profiles: list[dict[str, Any]] | None = None


class BackendDataResponseMessage(BaseModel):
    schema_version: str = "1.0"
    message_type: Literal["ai.backend_data.response"] = "ai.backend_data.response"
    correlation_id: str
    status: Literal["success", "partial", "error"]
    data: BackendDataResponseData = Field(default_factory=BackendDataResponseData)
    errors: list[BackendDataErrorItem] = Field(default_factory=list)
