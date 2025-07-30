"""
Elasticsearch client wrapper for elastic-zeroentropy library.

This module provides a simplified interface for Elasticsearch operations
with error handling, connection management, and document parsing.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import (
    ConnectionError as ESConnectionError,
    RequestError as ESRequestError,
    NotFoundError as ESNotFoundError,
    AuthenticationException as ESAuthenticationException,
    TransportError as ESTransportError,
)

from .config import ElasticZeroEntropyConfig
from .exceptions import (
    ElasticsearchError,
    ConfigurationError,
    TimeoutError as LibTimeoutError,
)
from .models import Document, ElasticsearchQuery, ElasticsearchResponse

logger = logging.getLogger(__name__)


class ElasticsearchClient:
    """
    Wrapper around AsyncElasticsearch with error handling and convenience methods.

    Provides a simplified interface for common search operations while handling
    connection management, authentication, and error translation.
    """

    def __init__(
        self,
        config: Optional[ElasticZeroEntropyConfig] = None,
        client: Optional[AsyncElasticsearch] = None,
    ) -> None:
        """
        Initialize Elasticsearch client.

        Args:
            config: Configuration object. If None, loads from environment.
            client: Optional pre-configured Elasticsearch client.
        """
        from .config import get_config

        self.config = config or get_config()
        self._client = client

    async def __aenter__(self) -> "ElasticsearchClient":
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def _ensure_client(self) -> None:
        """Ensure Elasticsearch client is initialized."""
        if self._client is None:
            # Prepare connection parameters
            connection_params = {
                "hosts": [self.config.elasticsearch_url],
                "timeout": self.config.elasticsearch_timeout,
                "max_retries": self.config.elasticsearch_max_retries,
                "retry_on_timeout": True,
                "verify_certs": self.config.elasticsearch_verify_certs,
            }

            # Add authentication if configured
            auth_config = self.config.get_elasticsearch_auth()
            if auth_config:
                connection_params.update(auth_config)

            try:
                self._client = AsyncElasticsearch(**connection_params)

                # Test connection
                await self._client.ping()
                logger.info(
                    f"Connected to Elasticsearch at {self.config.elasticsearch_url}"
                )

            except Exception as e:
                raise ElasticsearchError(
                    f"Failed to connect to Elasticsearch: {e}", elasticsearch_error=e
                ) from e

    async def close(self) -> None:
        """Close the Elasticsearch client."""
        if self._client is not None:
            await self._client.close()
            self._client = None

    def _handle_elasticsearch_error(
        self, error: Exception, operation: str, **kwargs: Any
    ) -> None:
        """
        Handle Elasticsearch errors and raise appropriate exceptions.

        Args:
            error: Original Elasticsearch exception
            operation: Description of the operation that failed
            **kwargs: Additional context for the error
        """
        if isinstance(error, ESAuthenticationException):
            raise ElasticsearchError(
                f"Authentication failed for {operation}",
                elasticsearch_error=error,
                **kwargs,
            ) from error
        elif isinstance(error, ESConnectionError):
            raise ElasticsearchError(
                f"Connection failed for {operation}",
                elasticsearch_error=error,
                **kwargs,
            ) from error
        elif isinstance(error, ESNotFoundError):
            raise ElasticsearchError(
                f"Resource not found for {operation}",
                elasticsearch_error=error,
                **kwargs,
            ) from error
        elif isinstance(error, ESRequestError):
            raise ElasticsearchError(
                f"Invalid request for {operation}: {error}",
                elasticsearch_error=error,
                **kwargs,
            ) from error
        elif isinstance(error, ESTransportError):
            if "timeout" in str(error).lower():
                raise LibTimeoutError(
                    f"Timeout during {operation}",
                    timeout_seconds=self.config.elasticsearch_timeout,
                    operation=operation,
                ) from error
            else:
                raise ElasticsearchError(
                    f"Transport error for {operation}: {error}",
                    elasticsearch_error=error,
                    **kwargs,
                ) from error
        else:
            raise ElasticsearchError(
                f"Unexpected error for {operation}: {error}",
                elasticsearch_error=error,
                **kwargs,
            ) from error

    def _extract_documents_from_response(
        self, response: Dict[str, Any]
    ) -> List[Document]:
        """
        Extract documents from Elasticsearch response.

        Args:
            response: Raw Elasticsearch response

        Returns:
            List of Document objects
        """
        documents = []

        hits = response.get("hits", {}).get("hits", [])
        for hit in hits:
            doc_id = hit.get("_id", "")
            source = hit.get("_source", {})

            # Extract text content (try common field names)
            text = ""
            for field in ["text", "content", "body", "description", "title"]:
                if field in source and source[field]:
                    text = str(source[field])
                    break

            if not text:
                # Fallback: concatenate all string fields
                text_parts = []
                for key, value in source.items():
                    if isinstance(value, str) and value.strip():
                        text_parts.append(value)
                text = " ".join(text_parts)

            # Extract title
            title = source.get("title") or source.get("name") or None

            # Extract timestamp
            timestamp = None
            for field in ["timestamp", "created_at", "updated_at", "@timestamp"]:
                if field in source:
                    try:
                        if isinstance(source[field], str):
                            timestamp = datetime.fromisoformat(
                                source[field].replace("Z", "+00:00")
                            )
                        elif isinstance(source[field], (int, float)):
                            timestamp = datetime.fromtimestamp(source[field])
                        break
                    except (ValueError, TypeError):
                        continue

            # Create document with metadata
            metadata = dict(source)
            metadata.update(
                {
                    "elasticsearch_score": hit.get("_score"),
                    "elasticsearch_index": hit.get("_index"),
                    "elasticsearch_type": hit.get("_type"),
                }
            )

            # Remove text fields from metadata to avoid duplication
            for field in ["text", "content", "body", "title", "name"]:
                metadata.pop(field, None)

            documents.append(
                Document(
                    id=doc_id,
                    text=text,
                    title=title,
                    metadata=metadata,
                    timestamp=timestamp,
                )
            )

        return documents

    async def health_check(self) -> Dict[str, Any]:
        """
        Check Elasticsearch cluster health.

        Returns:
            Health check response
        """
        await self._ensure_client()

        try:
            # Test basic connectivity
            ping_result = await self._client.ping()

            # Get cluster health
            health = await self._client.cluster.health()

            return {
                "status": "healthy" if ping_result else "unhealthy",
                "ping": ping_result,
                "cluster_health": health,
                "elasticsearch_version": await self._get_version(),
            }

        except Exception as e:
            logger.warning(f"Elasticsearch health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "ping": False,
            }

    async def _get_version(self) -> Optional[str]:
        """Get Elasticsearch version."""
        try:
            info = await self._client.info()
            return info.get("version", {}).get("number")
        except Exception:
            return None

    async def search(
        self,
        index: str,
        query: Dict[str, Any],
        size: int = 10,
        from_: int = 0,
        source: Optional[List[str]] = None,
        sort: Optional[List[Dict[str, Any]]] = None,
        timeout: Optional[str] = None,
    ) -> ElasticsearchResponse:
        """
        Perform search query on Elasticsearch.

        Args:
            index: Index name to search
            query: Elasticsearch query DSL
            size: Number of results to return
            from_: Offset for pagination
            source: Fields to include in response
            sort: Sort configuration
            timeout: Query timeout

        Returns:
            Parsed search response

        Raises:
            ElasticsearchError: If search fails
        """
        await self._ensure_client()

        # Prepare search parameters
        search_params = {
            "index": index,
            "body": {
                "query": query,
                "size": size,
                "from": from_,
            },
        }

        if source:
            search_params["body"]["_source"] = source
        if sort:
            search_params["body"]["sort"] = sort
        if timeout:
            search_params["timeout"] = timeout

        try:
            logger.debug(f"Searching index '{index}' with query: {query}")

            response = await self._client.search(**search_params)

            # Extract documents
            documents = self._extract_documents_from_response(response)

            # Create response object
            total_hits = response["hits"]["total"]
            if isinstance(total_hits, dict):
                total_hits = total_hits["value"]

            elasticsearch_response = ElasticsearchResponse(
                took=response["took"],
                timed_out=response["timed_out"],
                total_hits=total_hits,
                max_score=response["hits"]["max_score"],
                documents=documents,
                raw_response=response,
            )

            logger.info(
                f"Found {total_hits} total hits, returned {len(documents)} documents"
            )

            return elasticsearch_response

        except Exception as e:
            self._handle_elasticsearch_error(e, "search", index=index, query=query)

    async def search_simple(
        self,
        index: str,
        query_text: str,
        fields: Optional[List[str]] = None,
        size: int = 10,
        from_: int = 0,
    ) -> ElasticsearchResponse:
        """
        Perform simple text search.

        Args:
            index: Index name to search
            query_text: Text to search for
            fields: Fields to search in (if None, searches all text fields)
            size: Number of results to return
            from_: Offset for pagination

        Returns:
            Search response
        """
        # Build simple multi-match query
        if fields:
            query = {
                "multi_match": {
                    "query": query_text,
                    "fields": fields,
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                }
            }
        else:
            query = {"query_string": {"query": query_text, "default_operator": "AND"}}

        return await self.search(index=index, query=query, size=size, from_=from_)

    async def get_index_mapping(self, index: str) -> Dict[str, Any]:
        """
        Get mapping for an index.

        Args:
            index: Index name

        Returns:
            Index mapping
        """
        await self._ensure_client()

        try:
            response = await self._client.indices.get_mapping(index=index)
            return response
        except Exception as e:
            self._handle_elasticsearch_error(e, "get mapping", index=index)

    async def index_exists(self, index: str) -> bool:
        """
        Check if an index exists.

        Args:
            index: Index name

        Returns:
            True if index exists
        """
        await self._ensure_client()

        try:
            return await self._client.indices.exists(index=index)
        except Exception as e:
            logger.warning(f"Error checking if index '{index}' exists: {e}")
            return False

    async def get_index_stats(self, index: str) -> Dict[str, Any]:
        """
        Get statistics for an index.

        Args:
            index: Index name

        Returns:
            Index statistics
        """
        await self._ensure_client()

        try:
            response = await self._client.indices.stats(index=index)
            return response
        except Exception as e:
            self._handle_elasticsearch_error(e, "get stats", index=index)

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"ElasticsearchClient(url='{self.config.elasticsearch_url}')"
