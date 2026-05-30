"""Backend Chat client port."""
from typing import Protocol

from app.schemas.backend_chat import (
    ClarificationMessage,
    ErrorMessage,
    FinalAnswerMessage,
    WorkflowStatusUpdate,
)
from app.workflow.statuses import WorkflowStatus

# HttpBackendChatClient: Phase 08 after backend API contract approval.


class BackendChatClient(Protocol):
    async def update_workflow_status(
        self,
        *,
        request_id: str,
        workflow_run_id: str,
        user_id: str,
        chat_id: str,
        status: WorkflowStatus,
    ) -> None: ...

    async def send_clarification(
        self,
        *,
        request_id: str,
        workflow_run_id: str,
        user_id: str,
        chat_id: str,
        message_id: str,
        question: str,
    ) -> None: ...

    async def send_final_answer(
        self,
        *,
        request_id: str,
        workflow_run_id: str,
        user_id: str,
        chat_id: str,
        message_id: str,
        final_answer: str,
    ) -> None: ...

    async def send_error(
        self,
        *,
        request_id: str,
        workflow_run_id: str,
        user_id: str,
        chat_id: str,
        message_id: str,
        safe_message: str,
    ) -> None: ...


__all__ = [
    "BackendChatClient",
    "ClarificationMessage",
    "ErrorMessage",
    "FinalAnswerMessage",
    "WorkflowStatusUpdate",
]
