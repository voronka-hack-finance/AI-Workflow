"""HTTP client errors."""


class HttpClientError(Exception):
    """Base HTTP client error."""


class ServiceUnavailableError(HttpClientError):
    """Raised when a dependency service is unavailable."""


class ServiceTimeoutError(HttpClientError):
    """Raised when a dependency service call times out."""


class InvalidServiceResponseError(HttpClientError):
    """Raised when a dependency returns an invalid HTTP response."""
