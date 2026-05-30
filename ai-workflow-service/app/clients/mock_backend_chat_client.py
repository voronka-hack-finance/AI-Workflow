"""In-memory Backend Chat client for tests and dev wiring."""
from __future__ import annotations

from dataclasses import dataclass, field

from app.schemas.backend_chat import (
    ClarificationMessage,
    ErrorMessage,
    FinalAnswerMessage,
    WorkflowStatusUpdate,
)
from app.workflow.statuses import WorkflowStatus


@dataclass
class MockBackendChatClient:
    status_updates: list[WorkflowStatusUpdate] = field(default_factory=list)
    clarifications: list[ClarificationMessage] = field(default_factory=list)
    final_answers: list[FinalAnswerMessage] = field(default_factory=list)
    errors: list[ErrorMessage] = field(default_factory=list)

    async def update_workflow_status(
        self,
        *,
        request_id: str,
        workflow_run_id: str,
        user_id: str,
        chat_id: str,
        status: WorkflowStatus,
    ) -> None:
        self.status_updates.append(
            WorkflowStatusUpdate(
                request_id=request_id,
                workflow_run_id=workflow_run_id,
                user_id=user_id,
                chat_id=chat_id,
                status=status,
            )
        )

    async def send_clarification(
        self,
        *,
        request_id: str,
        workflow_run_id: str,
        user_id: str,
        chat_id: str,
        message_id: str,
        question: str,
    ) -> None:
        self.clarifications.append(
            ClarificationMessage(
                request_id=request_id,
                workflow_run_id=workflow_run_id,
                user_id=user_id,
                chat_id=chat_id,
                message_id=message_id,
                question=question,
            )
        )

    async def send_final_answer(
        self,
        *,
        request_id: str,
        workflow_run_id: str,
        user_id: str,
        chat_id: str,
        message_id: str,
        final_answer: str,
    ) -> None:
        self.final_answers.append(
            FinalAnswerMessage(
                request_id=request_id,
                workflow_run_id=workflow_run_id,
                user_id=user_id,
                chat_id=chat_id,
                message_id=message_id,
                final_answer=final_answer,
            )
        )

    async def send_error(
        self,
        *,
        request_id: str,
        workflow_run_id: str,
        user_id: str,
        chat_id: str,
        message_id: str,
        safe_message: str,
    ) -> None:
        self.errors.append(
            ErrorMessage(
                request_id=request_id,
                workflow_run_id=workflow_run_id,
                user_id=user_id,
                chat_id=chat_id,
                message_id=message_id,
                safe_message=safe_message,
            )
        )