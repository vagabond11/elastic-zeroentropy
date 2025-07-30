"""Tests for ZeroEntropy API client."""

import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from elastic_zeroentropy.config import ElasticZeroEntropyConfig
from elastic_zeroentropy.exceptions import (
    AuthenticationError,
    QuotaExceededError,
    RateLimitError,
)
from elastic_zeroentropy.exceptions import TimeoutError as LibTimeoutError
from elastic_zeroentropy.exceptions import (
    ValidationError,
    ZeroEntropyAPIError,
)
from elastic_zeroentropy.models import RerankRequest, RerankResponse, RerankResult
from elastic_zeroentropy.zeroentropy_client import ZeroEntropyClient


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    with patch.dict("os.environ", {"ZEROENTROPY_API_KEY": "test-api-key"}):
        return ElasticZeroEntropyConfig()


@pytest.fixture
def mock_rerank_response_data():
    """Create mock rerank response data."""
    return {
        "results": [
            {"index": 0, "relevance_score": 0.95, "document": "First document text"},
            {"index": 1, "relevance_score": 0.85, "document": "Second document text"},
        ],
        "model": "zerank-1",
        "usage": {"tokens": 150},
        "request_id": "req-123",
    }


class TestZeroEntropyClient:
    """Test ZeroEntropy API client."""

    def test_initialization(self, mock_config):
        """Test client initialization."""
        client = ZeroEntropyClient(config=mock_config)

        assert client.config == mock_config
        assert client._client is None
        # Rate limiter is created when rate limiting is enabled (default: True)
        if mock_config.enable_rate_limiting:
            assert client._rate_limiter is not None
        else:
            assert client._rate_limiter is None

    def test_initialization_with_rate_limiting(self, mock_config):
        """Test client initialization with rate limiting enabled."""
        mock_config.enable_rate_limiting = True
        mock_config.requests_per_minute = 60

        client = ZeroEntropyClient(config=mock_config)

        assert client._rate_limiter is not None

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_config):
        """Test async context manager."""
        client = ZeroEntropyClient(config=mock_config)

        with patch.object(client, "_ensure_client") as mock_ensure:
            with patch.object(client, "close") as mock_close:
                async with client as ctx_client:
                    assert ctx_client is client
                    mock_ensure.assert_called_once()

                mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_ensure_client(self, mock_config):
        """Test HTTP client initialization."""
        client = ZeroEntropyClient(config=mock_config)

        with patch(
            "elastic_zeroentropy.zeroentropy_client.httpx.AsyncClient"
        ) as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            await client._ensure_client()

            assert client._client is mock_client
            mock_client_class.assert_called_once()

            # Check that timeout and limits were configured
            call_kwargs = mock_client_class.call_args[1]
            assert "timeout" in call_kwargs
            assert "limits" in call_kwargs
            assert "headers" in call_kwargs

    @pytest.mark.asyncio
    async def test_close(self, mock_config):
        """Test client cleanup."""
        client = ZeroEntropyClient(config=mock_config)

        mock_client = AsyncMock()
        client._client = mock_client

        await client.close()

        mock_client.aclose.assert_called_once()
        assert client._client is None

    @pytest.mark.asyncio
    async def test_rate_limiting(self, mock_config):
        """Test rate limiting functionality."""
        mock_config.enable_rate_limiting = True
        mock_config.requests_per_minute = 60  # 1 per second

        client = ZeroEntropyClient(config=mock_config)

        # Mock semaphore
        mock_semaphore = AsyncMock()
        client._rate_limiter = mock_semaphore

        await client._handle_rate_limiting()

        mock_semaphore.acquire.assert_called_once()

    def test_handle_http_error_401(self, mock_config):
        """Test handling 401 authentication errors."""
        client = ZeroEntropyClient(config=mock_config)

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": {"message": "Invalid API key"}}
        mock_response.text = "Unauthorized"

        with pytest.raises(AuthenticationError) as exc_info:
            client._handle_http_error(mock_response)

        assert "Invalid API key" in str(exc_info.value)

    def test_handle_http_error_429_rate_limit(self, mock_config):
        """Test handling 429 rate limit errors."""
        client = ZeroEntropyClient(config=mock_config)

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": {"message": "Rate limit exceeded"}}
        mock_response.headers.get.return_value = "60"
        mock_response.text = "Too Many Requests"

        with pytest.raises(RateLimitError) as exc_info:
            client._handle_http_error(mock_response)

        assert exc_info.value.details["retry_after"] == 60

    def test_handle_http_error_429_quota(self, mock_config):
        """Test handling 429 quota exceeded errors."""
        client = ZeroEntropyClient(config=mock_config)

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": {"message": "Quota exceeded"}}
        mock_response.headers.get.return_value = None
        mock_response.text = "Quota Exceeded"

        with pytest.raises(QuotaExceededError):
            client._handle_http_error(mock_response)

    def test_handle_http_error_400(self, mock_config):
        """Test handling 400 validation errors."""
        client = ZeroEntropyClient(config=mock_config)

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {"message": "Invalid request format"}
        }
        mock_response.text = "Bad Request"

        with pytest.raises(ValidationError):
            client._handle_http_error(mock_response)

    def test_handle_http_error_500(self, mock_config):
        """Test handling 500 server errors."""
        client = ZeroEntropyClient(config=mock_config)

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "error": {"message": "Internal server error"}
        }
        mock_response.text = "Internal Server Error"

        with pytest.raises(ZeroEntropyAPIError) as exc_info:
            client._handle_http_error(mock_response)

        assert "Server error" in str(exc_info.value)

    def test_handle_http_error_json_decode_error(self, mock_config):
        """Test handling responses with invalid JSON."""
        client = ZeroEntropyClient(config=mock_config)

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Internal Server Error"

        with pytest.raises(ZeroEntropyAPIError) as exc_info:
            client._handle_http_error(mock_response)

        assert "HTTP 500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_make_request_success(self, mock_config, mock_rerank_response_data):
        """Test successful API request."""
        client = ZeroEntropyClient(config=mock_config)

        # Mock HTTP client
        mock_http_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json.return_value = mock_rerank_response_data
        mock_http_client.request.return_value = mock_response

        client._client = mock_http_client

        with patch.object(client, "_handle_rate_limiting") as mock_rate_limit:
            result = await client._make_request(
                "POST", "/rerank", data={"query": "test", "documents": ["doc1"]}
            )

        assert result == mock_rerank_response_data
        mock_rate_limit.assert_called_once()
        mock_http_client.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_http_error(self, mock_config):
        """Test API request with HTTP error."""
        client = ZeroEntropyClient(config=mock_config)

        # Mock HTTP client
        mock_http_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.is_success = False
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": {"message": "Unauthorized"}}
        mock_response.text = "Unauthorized"
        mock_http_client.request.return_value = mock_response

        client._client = mock_http_client

        with patch.object(client, "_handle_rate_limiting"):
            with pytest.raises(AuthenticationError):
                await client._make_request("GET", "/test")

    @pytest.mark.asyncio
    async def test_make_request_timeout(self, mock_config):
        """Test API request timeout."""
        client = ZeroEntropyClient(config=mock_config)

        # Mock HTTP client
        mock_http_client = AsyncMock()
        mock_http_client.request.side_effect = httpx.TimeoutException(
            "Request timed out"
        )

        client._client = mock_http_client

        with patch.object(client, "_handle_rate_limiting"):
            with pytest.raises(LibTimeoutError) as exc_info:
                await client._make_request("GET", "/test")

        assert "Request timeout" in str(exc_info.value)
        assert (
            exc_info.value.details["timeout_seconds"] == mock_config.zeroentropy_timeout
        )

    @pytest.mark.asyncio
    async def test_make_request_connection_error(self, mock_config):
        """Test API request connection error."""
        client = ZeroEntropyClient(config=mock_config)

        # Mock HTTP client
        mock_http_client = AsyncMock()
        mock_http_client.request.side_effect = httpx.ConnectError("Connection failed")

        client._client = mock_http_client

        with patch.object(client, "_handle_rate_limiting"):
            with pytest.raises(ZeroEntropyAPIError) as exc_info:
                await client._make_request("GET", "/test")

        assert "Request failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_health_check_success(self, mock_config):
        """Test successful health check."""
        client = ZeroEntropyClient(config=mock_config)

        with patch.object(client, "_make_request") as mock_request:
            mock_request.return_value = {"status": "ok"}

            result = await client.health_check()

            assert result["status"] == "healthy"
            assert "response" in result
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_health_check_failure(self, mock_config):
        """Test failed health check."""
        client = ZeroEntropyClient(config=mock_config)

        with patch.object(client, "_make_request") as mock_request:
            mock_request.side_effect = ZeroEntropyAPIError("API unavailable")

            result = await client.health_check()

            assert result["status"] == "unhealthy"
            assert "error" in result
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_rerank_success(self, mock_config, mock_rerank_response_data):
        """Test successful reranking request."""
        client = ZeroEntropyClient(config=mock_config)

        with patch.object(client, "_make_request") as mock_request:
            mock_request.return_value = mock_rerank_response_data

            response = await client.rerank(
                query="test query",
                documents=["doc1", "doc2"],
                model="zerank-1",
                top_k=5,
            )

            assert isinstance(response, RerankResponse)
            assert len(response.results) == 2
            assert response.model == "zerank-1"
            assert response.results[0].relevance_score == 0.95

    @pytest.mark.asyncio
    async def test_rerank_validation_errors(self, mock_config):
        """Test rerank input validation."""
        client = ZeroEntropyClient(config=mock_config)

        # Empty query
        with pytest.raises(ValidationError, match="Query cannot be empty"):
            await client.rerank("", ["doc1"])

        # Empty documents
        with pytest.raises(ValidationError, match="Documents list cannot be empty"):
            await client.rerank("query", [])

        # Non-string document
        with pytest.raises(ValidationError, match="must be a string"):
            await client.rerank("query", ["doc1", 123])

        # Empty document text
        with pytest.raises(ValidationError, match="cannot be empty"):
            await client.rerank("query", ["doc1", ""])

    @pytest.mark.asyncio
    async def test_rerank_api_error(self, mock_config):
        """Test rerank with API error."""
        client = ZeroEntropyClient(config=mock_config)

        with patch.object(client, "_make_request") as mock_request:
            mock_request.side_effect = ZeroEntropyAPIError("API Error")

            with pytest.raises(ZeroEntropyAPIError):
                await client.rerank("query", ["doc1"])

    @pytest.mark.asyncio
    async def test_rerank_batch_success(self, mock_config, mock_rerank_response_data):
        """Test successful batch reranking."""
        client = ZeroEntropyClient(config=mock_config)

        requests = [
            RerankRequest(query="query1", documents=["doc1", "doc2"]),
            RerankRequest(query="query2", documents=["doc3", "doc4"]),
        ]

        with patch.object(client, "rerank") as mock_rerank:
            mock_response = RerankResponse(**mock_rerank_response_data)
            mock_rerank.return_value = mock_response

            responses = await client.rerank_batch(requests)

            assert len(responses) == 2
            assert mock_rerank.call_count == 2

    @pytest.mark.asyncio
    async def test_rerank_batch_empty(self, mock_config):
        """Test batch reranking with empty list."""
        client = ZeroEntropyClient(config=mock_config)

        responses = await client.rerank_batch([])
        assert responses == []

    @pytest.mark.asyncio
    async def test_rerank_batch_with_semaphore(
        self, mock_config, mock_rerank_response_data
    ):
        """Test batch reranking respects concurrency limits."""
        client = ZeroEntropyClient(config=mock_config)

        requests = [
            RerankRequest(query=f"query{i}", documents=[f"doc{i}"]) for i in range(5)
        ]

        # Track semaphore usage
        acquire_calls = []
        release_calls = []

        class MockSemaphore:
            async def __aenter__(self):
                acquire_calls.append(asyncio.get_event_loop().time())
                return self

            async def __aexit__(self, *args):
                release_calls.append(asyncio.get_event_loop().time())

        with patch.object(client, "rerank") as mock_rerank:
            mock_response = RerankResponse(**mock_rerank_response_data)
            mock_rerank.return_value = mock_response

            with patch("asyncio.Semaphore") as mock_semaphore_class:
                mock_semaphore_class.return_value = MockSemaphore()

                responses = await client.rerank_batch(requests, max_concurrent=3)

                assert len(responses) == 5
                assert len(acquire_calls) == 5
                assert len(release_calls) == 5

    def test_repr(self, mock_config):
        """Test string representation."""
        client = ZeroEntropyClient(config=mock_config)

        repr_str = repr(client)
        assert "ZeroEntropyClient" in repr_str
        assert mock_config.zeroentropy_base_url in repr_str
