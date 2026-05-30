"""Application errors."""
from shared_http.errors import (
    InvalidServiceResponseError,
    ServiceTimeoutError,
    ServiceUnavailableError,
)


class AppError(Exception):
    """Base application error."""


class ContractValidationError(AppError):
    """Raised when a service response fails contract validation."""


class WorkflowStateError(AppError):
    """Raised when workflow state is invalid."""


class RabbitMQMessageError(AppError):
    """Raised when a RabbitMQ message payload is invalid."""


SAFE_USER_ERROR_MESSAGE = (
    "Не удалось обработать запрос. Попробуйте повторить позже или уточните вопрос."
)


def safe_user_message(error: Exception) -> str:
    """Return a safe user-facing message without technical details."""
    return SAFE_USER_ERROR_MESSAGE


__all__ = [
    "AppError",
    "ContractValidationError",
    "InvalidServiceResponseError",
    "RabbitMQMessageError",
    "ServiceTimeoutError",
    "ServiceUnavailableError",
    "WorkflowStateError",
    "safe_user_message",
]
