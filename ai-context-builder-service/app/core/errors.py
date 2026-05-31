"""Application errors."""


class AppError(Exception):
    """Base application error."""


class ServiceUnavailableError(AppError):
    """Raised when a downstream service is unavailable."""


class ValidationError(AppError):
    """Raised when input validation fails."""


class BackendDataTimeoutError(AppError):
    """Raised when backend data job response times out."""


class BackendDataValidationError(AppError):
    """Raised when backend data response fails contract validation."""
