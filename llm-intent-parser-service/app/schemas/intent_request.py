"""Intent parse request schema."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, model_validator

from app.schemas.chat_context import ActiveWorkflow, ChatContext


class IntentParseRequest(BaseModel):
    request_id: str
    user_id: str
    chat_id: str
    raw_message: str
    current_date: str
    timezone: str = "UTC"
    chat_context: ChatContext | None = None
    active_workflow: ActiveWorkflow | dict[str, Any] | None = None

    @model_validator(mode="after")
    def merge_active_workflow(self) -> IntentParseRequest:
        if self.active_workflow is None:
            return self

        context = self.chat_context or ChatContext()
        if context.active_workflow is None:
            if isinstance(self.active_workflow, ActiveWorkflow):
                context.active_workflow = self.active_workflow
            else:
                context.active_workflow = ActiveWorkflow.model_validate(self.active_workflow)
            self.chat_context = context
        return self

    def resolved_chat_context(self) -> ChatContext:
        return self.chat_context or ChatContext()

    def active_workflow_state(self) -> ActiveWorkflow | None:
        context = self.resolved_chat_context()
        workflow = context.active_workflow
        if workflow is None:
            return None
        if isinstance(workflow, ActiveWorkflow):
            return workflow
        return ActiveWorkflow.model_validate(workflow)
