"""Application errors."""


class AppError(Exception):
    """Base application error."""


class ServiceUnavailableError(AppError):
    """Raised when a downstream service is unavailable."""


class ValidationError(AppError):
    """Raised when input validation fails."""


class LLMParseError(AppError):
    """Raised when LLM output cannot be parsed or validated."""
