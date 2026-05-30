"""Chat context schema."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from shared_contracts.intent_result import IntentResult


class ActiveWorkflow(BaseModel):
    workflow_run_id: str | None = None
    status: str
    missing_fields: list[str] = Field(default_factory=list)
    intent_result: IntentResult | dict[str, Any] | None = None


class ChatContext(BaseModel):
    last_6_messages: list[dict[str, Any]] = Field(default_factory=list)
    chat_summary: str | None = None
    active_workflow: ActiveWorkflow | dict[str, Any] | None = None
