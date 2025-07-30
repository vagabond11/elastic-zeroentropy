"""
ZeroEntropy API client for elastic-zeroentropy library.

This module provides an async HTTP client for communicating with the ZeroEntropy
reranking API with robust error handling, retries, and rate limiting.
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .config import ElasticZeroEntropyConfig
from .exceptions import (
    AuthenticationError,
    QuotaExceededError,
    RateLimitError,
)
from .exceptions import TimeoutError as LibTimeoutError
from .exceptions import (
    ValidationError,
    ZeroEntropyAPIError,
)
from .models import RerankRequest, RerankResponse

logger = logging.getLogger(__name__)


class ZeroEntropyClient:
    """
    Async HTTP client for ZeroEntropy reranking API.

    Provides robust error handling, automatic retries, rate limiting,
    and comprehensive logging for all API interactions.
    """

    def __init__(
        self,
        config: Optional[ElasticZeroEntropyConfig] = None,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """
        Initialize ZeroEntropy client.

        Args:
            config: Configuration object. If None, loads from environment.
            client: Optional pre-configured httpx client.
        """
        from .config import get_config

        self.config = config or get_config()
        self._client = client
        self._rate_limiter: Optional[asyncio.Semaphore] = None
        self._last_request_time = 0.0

        if self.config.enable_rate_limiting:
            # Simple rate limiting with semaphore
            requests_per_second = self.config.requests_per_minute / 60
            self._rate_limiter = asyncio.Semaphore(int(requests_per_second))

    async def __aenter__(self) -> "ZeroEntropyClient":
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def _ensure_client(self) -> None:
        """Ensure HTTP client is initialized."""
        if self._client is None:
            timeout = httpx.Timeout(self.config.zeroentropy_timeout)
            limits = httpx.Limits(
                max_connections=self.config.connection_pool_size,
                max_keepalive_connections=self.config.connection_pool_size // 2,
            )

            self._client = httpx.AsyncClient(
                timeout=timeout,
                limits=limits,
                headers=self.config.get_zeroentropy_headers(),
                follow_redirects=True,
            )

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _handle_rate_limiting(self) -> None:
        """Apply rate limiting if enabled."""
        if not self.config.enable_rate_limiting or self._rate_limiter is None:
            return

        # Acquire semaphore for rate limiting
        await self._rate_limiter.acquire()

        # Calculate delay needed to maintain rate limit
        now = time.time()
        time_since_last = now - self._last_request_time
        min_interval = 60.0 / self.config.requests_per_minute

        if time_since_last < min_interval:
            delay = min_interval - time_since_last
            await asyncio.sleep(delay)

        self._last_request_time = time.time()

        # Release semaphore after a short delay
        asyncio.create_task(self._release_rate_limit_after_delay())

    async def _release_rate_limit_after_delay(self) -> None:
        """Release rate limiting semaphore after a delay."""
        await asyncio.sleep(1.0)  # Hold for 1 second
        if self._rate_limiter:
            self._rate_limiter.release()

    def _handle_http_error(self, response: httpx.Response) -> None:
        """
        Handle HTTP errors and raise appropriate exceptions.

        Args:
            response: HTTP response object

        Raises:
            ZeroEntropyAPIError: For various API error conditions
        """
        status_code = response.status_code

        try:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Unknown error")
            request_id = error_data.get("request_id")
        except (json.JSONDecodeError, KeyError):
            error_message = f"HTTP {status_code}: {response.text}"
            request_id = None

        # Map HTTP status codes to specific exceptions
        if status_code == 401:
            raise AuthenticationError(
                error_message,
                status_code=status_code,
                response_body=response.text,
                request_id=request_id,
            )
        elif status_code == 429:
            retry_after = response.headers.get("Retry-After")
            if "rate limit" in error_message.lower():
                raise RateLimitError(
                    error_message,
                    status_code=status_code,
                    response_body=response.text,
                    request_id=request_id,
                    retry_after=int(retry_after) if retry_after else None,
                )
            else:
                raise QuotaExceededError(
                    error_message,
                    status_code=status_code,
                    response_body=response.text,
                    request_id=request_id,
                )
        elif status_code == 400:
            raise ValidationError(
                f"Invalid request: {error_message}",
                field="request",
                value=response.text,
            )
        elif status_code >= 500:
            raise ZeroEntropyAPIError(
                f"Server error: {error_message}",
                status_code=status_code,
                response_body=response.text,
                request_id=request_id,
            )
        else:
            raise ZeroEntropyAPIError(
                error_message,
                status_code=status_code,
                response_body=response.text,
                request_id=request_id,
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(
            (
                httpx.TimeoutException,
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                ZeroEntropyAPIError,
            )
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retries and error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters

        Returns:
            Parsed JSON response

        Raises:
            ZeroEntropyAPIError: For API errors
            TimeoutError: For timeout errors
        """
        await self._ensure_client()
        await self._handle_rate_limiting()

        url = urljoin(self.config.zeroentropy_base_url + "/", endpoint.lstrip("/"))

        try:
            if self.config.enable_request_logging:
                logger.debug(f"Making {method} request to {url}")
                if data:
                    logger.debug(f"Request data: {json.dumps(data, indent=2)}")

            response = await self._client.request(
                method=method, url=url, json=data, params=params
            )

            if self.config.enable_request_logging:
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")

            # Handle non-success status codes
            if not response.is_success:
                self._handle_http_error(response)

            result = response.json()

            if self.config.enable_request_logging:
                logger.debug(f"Response data: {json.dumps(result, indent=2)}")

            return result

        except httpx.TimeoutException as e:
            raise LibTimeoutError(
                f"Request timeout after {self.config.zeroentropy_timeout}s",
                timeout_seconds=self.config.zeroentropy_timeout,
                operation=f"{method} {endpoint}",
            ) from e
        except httpx.RequestError as e:
            raise ZeroEntropyAPIError(
                f"Request failed: {e}", details={"endpoint": endpoint, "error": str(e)}
            ) from e

    async def health_check(self) -> Dict[str, Any]:
        """
        Check API health and connectivity.

        Returns:
            Health check response

        Raises:
            ZeroEntropyAPIError: If health check fails
        """
        try:
            # Simple request to check connectivity
            # Note: Adjust endpoint based on actual ZeroEntropy API
            response = await self._make_request("GET", "/health")
            return {"status": "healthy", "response": response, "timestamp": time.time()}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "timestamp": time.time()}

    async def rerank(
        self,
        query: str,
        documents: List[str],
        model: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> RerankResponse:
        """
        Rerank documents using ZeroEntropy API.

        Args:
            query: Search query text
            documents: List of document texts to rerank
            model: Model to use (defaults to config default)
            top_k: Number of top results to return

        Returns:
            Reranking response with scored results

        Raises:
            ValidationError: If input validation fails
            ZeroEntropyAPIError: If API call fails
        """
        if not query.strip():
            raise ValidationError("Query cannot be empty", field="query", value=query)

        if not documents:
            raise ValidationError(
                "Documents list cannot be empty", field="documents", value=documents
            )

        # Clean and validate documents
        clean_documents = []
        for i, doc in enumerate(documents):
            if not isinstance(doc, str):
                raise ValidationError(
                    f"Document at index {i} must be a string",
                    field=f"documents[{i}]",
                    value=doc,
                    expected_type="str",
                )
            if not doc.strip():
                raise ValidationError(
                    f"Document at index {i} cannot be empty",
                    field=f"documents[{i}]",
                    value=doc,
                )
            clean_documents.append(doc.strip())

        # Prepare request
        request_data = RerankRequest(
            query=query.strip(),
            documents=clean_documents,
            model=model or self.config.zeroentropy_model,
            top_k=top_k,
        )

        logger.info(f"Reranking {len(documents)} documents for query: {query[:100]}...")

        try:
            # Make API request
            response_data = await self._make_request(
                "POST",
                "/rerank",  # Adjust endpoint based on actual ZeroEntropy API
                data=request_data.model_dump(exclude_none=True),
            )

            # Parse and validate response
            response = RerankResponse(**response_data)

            logger.info(f"Successfully reranked {len(response.results)} documents")

            return response

        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            raise

    async def rerank_batch(
        self, requests: List[RerankRequest], max_concurrent: Optional[int] = None
    ) -> List[RerankResponse]:
        """
        Rerank multiple queries in parallel.

        Args:
            requests: List of rerank requests
            max_concurrent: Maximum concurrent requests (defaults to config value)

        Returns:
            List of reranking responses

        Raises:
            ZeroEntropyAPIError: If any request fails
        """
        if not requests:
            return []

        max_concurrent = max_concurrent or self.config.max_concurrent_requests
        semaphore = asyncio.Semaphore(max_concurrent)

        async def rerank_single(request: RerankRequest) -> RerankResponse:
            async with semaphore:
                return await self.rerank(
                    query=request.query,
                    documents=request.documents,
                    model=request.model,
                    top_k=request.top_k,
                )

        tasks = [rerank_single(req) for req in requests]
        return await asyncio.gather(*tasks)

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"ZeroEntropyClient(base_url='{self.config.zeroentropy_base_url}')"
