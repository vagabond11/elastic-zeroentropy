"""
Custom exceptions for elastic-zeroentropy library.

This module defines all the exceptions that can be raised by the library,
providing specific error types for different failure modes.
"""

from typing import Any, Dict, Optional


class ElasticZeroEntropyError(Exception):
    """Base exception for all elastic-zeroentropy errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(ElasticZeroEntropyError):
    """Raised when there's an issue with configuration."""

    def __init__(
        self,
        message: str,
        missing_keys: Optional[list] = None,
        invalid_values: Optional[Dict[str, Any]] = None,
    ) -> None:
        details = {}
        if missing_keys:
            details["missing_keys"] = missing_keys
        if invalid_values:
            details["invalid_values"] = invalid_values
        super().__init__(message, details)


class ZeroEntropyAPIError(ElasticZeroEntropyError):
    """Raised when ZeroEntropy API calls fail."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        request_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = {}
        if status_code is not None:
            details["status_code"] = status_code
        if response_body:
            details["response_body"] = response_body
        if request_id:
            details["request_id"] = request_id
        # Merge any additional kwargs into details
        details.update(kwargs)
        super().__init__(message, details)


class ElasticsearchError(ElasticZeroEntropyError):
    """Raised when Elasticsearch operations fail."""

    def __init__(
        self,
        message: str,
        index: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
        elasticsearch_error: Optional[Exception] = None,
    ) -> None:
        details = {}
        if index:
            details["index"] = index
        if query:
            details["query"] = query
        if elasticsearch_error:
            details["elasticsearch_error"] = str(elasticsearch_error)
        super().__init__(message, details)


class RerankingError(ElasticZeroEntropyError):
    """Raised when reranking operations fail."""

    def __init__(
        self,
        message: str,
        query: Optional[str] = None,
        document_count: Optional[int] = None,
        stage: Optional[str] = None,
    ) -> None:
        details = {}
        if query:
            details["query"] = query
        if document_count is not None:
            details["document_count"] = document_count
        if stage:
            details["stage"] = stage
        super().__init__(message, details)


class RateLimitError(ZeroEntropyAPIError):
    """Raised when API rate limits are exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if retry_after is not None:
            self.details["retry_after"] = retry_after


class AuthenticationError(ZeroEntropyAPIError):
    """Raised when API authentication fails."""

    def __init__(
        self, message: str = "Authentication failed - check your API key", **kwargs: Any
    ) -> None:
        # Ensure status_code is set to 401 for authentication errors
        kwargs["status_code"] = 401
        super().__init__(message, **kwargs)


class QuotaExceededError(ZeroEntropyAPIError):
    """Raised when API quota is exceeded."""

    def __init__(self, message: str = "API quota exceeded", **kwargs: Any) -> None:
        # Ensure status_code is set to 429 for quota exceeded errors
        kwargs["status_code"] = 429
        super().__init__(message, **kwargs)


class TimeoutError(ElasticZeroEntropyError):
    """Raised when operations timeout."""

    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[float] = None,
        operation: Optional[str] = None,
    ) -> None:
        details = {}
        if timeout_seconds is not None:
            details["timeout_seconds"] = timeout_seconds
        if operation:
            details["operation"] = operation
        super().__init__(message, details)


class ValidationError(ElasticZeroEntropyError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        expected_type: Optional[str] = None,
    ) -> None:
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        if expected_type:
            details["expected_type"] = expected_type
        super().__init__(message, details)
