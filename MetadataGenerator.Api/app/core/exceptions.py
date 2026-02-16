"""Application-specific exception types for the Metadata Generator API."""


class ContentUnderstandingError(Exception):
    """Base exception for Content Understanding service errors."""

    def __init__(self, error_code: str, message: str) -> None:
        self.error_code = error_code
        self.message = message
        super().__init__(message)


class ConfigurationError(ContentUnderstandingError):
    """Raised when required service configuration is missing or invalid."""


class TransientError(ContentUnderstandingError):
    """Raised for transient Azure errors (429, 503) after retry exhaustion."""


class AnalysisServiceError(ContentUnderstandingError):
    """Raised for non-transient analysis errors from Azure."""
