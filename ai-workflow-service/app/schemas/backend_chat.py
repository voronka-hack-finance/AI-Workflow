"""Workflow-side DTOs for Backend Chat port (not a backend API contract)."""
from pydantic import BaseModel

from app.workflow.statuses import WorkflowStatus


class WorkflowStatusUpdate(BaseModel):
    request_id: str
    workflow_run_id: str
    user_id: str
    chat_id: str
    status: WorkflowStatus


class ClarificationMessage(BaseModel):
    request_id: str
    workflow_run_id: str
    user_id: str
    chat_id: str
    message_id: str
    question: str


class FinalAnswerMessage(BaseModel):
    request_id: str
    workflow_run_id: str
    user_id: str
    chat_id: str
    message_id: str
    final_answer: str


class ErrorMessage(BaseModel):
    request_id: str
    workflow_run_id: str
    user_id: str
    chat_id: str
    message_id: str
    safe_message: str
