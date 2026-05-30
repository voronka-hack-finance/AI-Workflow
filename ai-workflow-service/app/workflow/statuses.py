"""Workflow status enum."""
from enum import StrEnum


class WorkflowStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    AWAITING_USER_INPUT = "awaiting_user_input"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
