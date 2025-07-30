"""
Main reranker class that combines Elasticsearch search with ZeroEntropy reranking.

This module provides the primary interface for the elastic-zeroentropy library,
orchestrating the complete search and reranking workflow.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from .config import ElasticZeroEntropyConfig
from .elasticsearch_client import ElasticsearchClient
from .exceptions import (
    ConfigurationError,
    ElasticZeroEntropyError,
    RerankingError,
    ValidationError,
)
from .models import (
    Document,
    ElasticsearchQuery,
    HealthCheckResponse,
    RerankerConfig,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from .zeroentropy_client import ZeroEntropyClient

logger = logging.getLogger(__name__)


class ElasticZeroEntropyReranker:
    """
    Main reranker class combining Elasticsearch search with ZeroEntropy reranking.

    This class provides the primary interface for performing intelligent search
    with automatic reranking using ZeroEntropy's models.
    """

    def __init__(
        self,
        config: Optional[ElasticZeroEntropyConfig] = None,
        elasticsearch_client: Optional[ElasticsearchClient] = None,
        zeroentropy_client: Optional[ZeroEntropyClient] = None,
    ) -> None:
        """
        Initialize the reranker.

        Args:
            config: Configuration object
            elasticsearch_client: Pre-configured Elasticsearch client
            zeroentropy_client: Pre-configured ZeroEntropy client
        """
        from .config import get_config

        self.config = config or get_config()
        self.elasticsearch_client = elasticsearch_client or ElasticsearchClient(
            self.config
        )
        self.zeroentropy_client = zeroentropy_client or ZeroEntropyClient(self.config)

    async def __aenter__(self) -> "ElasticZeroEntropyReranker":
        """Async context manager entry."""
        await self.elasticsearch_client.__aenter__()
        await self.zeroentropy_client.__aenter__()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.elasticsearch_client.__aexit__(exc_type, exc_val, exc_tb)
        await self.zeroentropy_client.__aexit__(exc_type, exc_val, exc_tb)

    async def search(
        self,
        query: str,
        index: str,
        reranker_config: Optional[RerankerConfig] = None,
        elasticsearch_query: Optional[ElasticsearchQuery] = None,
        filters: Optional[Dict[str, Any]] = None,
        enable_reranking: bool = True,
        return_debug_info: bool = False,
    ) -> SearchResponse:
        """
        Perform search with optional reranking.

        Args:
            query: Search query text
            index: Elasticsearch index to search
            reranker_config: Configuration for reranking
            elasticsearch_query: Custom Elasticsearch query (overrides simple text search)
            filters: Additional filters to apply
            enable_reranking: Whether to apply reranking
            return_debug_info: Whether to include debug information

        Returns:
            Search response with reranked results

        Raises:
            ValidationError: If input validation fails
            RerankingError: If reranking fails
        """
        if not query.strip():
            raise ValidationError("Query cannot be empty", field="query", value=query)

        if not index.strip():
            raise ValidationError("Index cannot be empty", field="index", value=index)

        # Use provided config or create default
        if reranker_config is None:
            reranker_config = RerankerConfig(**self.config.get_reranker_config_dict())

        start_time = time.time()
        debug_info = {} if return_debug_info else None

        try:
            # Step 1: Perform Elasticsearch search
            logger.info(f"Searching for: '{query}' in index '{index}'")

            es_start_time = time.time()

            if elasticsearch_query:
                # Use custom Elasticsearch query
                es_response = await self.elasticsearch_client.search(
                    index=elasticsearch_query.index,
                    query=elasticsearch_query.query,
                    size=elasticsearch_query.size,
                    from_=elasticsearch_query.from_,
                    source=elasticsearch_query.source,
                    sort=elasticsearch_query.sort,
                    timeout=elasticsearch_query.timeout,
                )
            else:
                # Build query based on filters
                es_query = self._build_elasticsearch_query(query, filters)

                es_response = await self.elasticsearch_client.search(
                    index=index, query=es_query, size=reranker_config.top_k_initial
                )

            es_took_ms = int((time.time() - es_start_time) * 1000)

            if debug_info is not None:
                debug_info["elasticsearch"] = {
                    "query": (
                        es_query
                        if not elasticsearch_query
                        else elasticsearch_query.query
                    ),
                    "took_ms": es_took_ms,
                    "total_hits": es_response.total_hits,
                    "returned_docs": len(es_response.documents),
                }

            logger.info(
                f"Elasticsearch returned {len(es_response.documents)} documents in {es_took_ms}ms"
            )

            # Step 2: Apply reranking if enabled and we have enough documents
            reranking_took_ms = None
            model_used = reranker_config.model

            if enable_reranking and len(es_response.documents) > 1:
                logger.info("Applying ZeroEntropy reranking...")

                rerank_start_time = time.time()

                # Select top documents for reranking
                docs_to_rerank = es_response.documents[: reranker_config.top_k_rerank]
                reranked_results = await self._rerank_documents(
                    query, docs_to_rerank, reranker_config
                )

                reranking_took_ms = int((time.time() - rerank_start_time) * 1000)

                if debug_info is not None:
                    debug_info["reranking"] = {
                        "model": model_used,
                        "documents_sent": len(docs_to_rerank),
                        "took_ms": reranking_took_ms,
                        "documents_returned": len(reranked_results),
                    }

                logger.info(f"Reranking completed in {reranking_took_ms}ms")

                # Combine results
                final_results = self._combine_results(
                    es_response.documents, reranked_results, reranker_config
                )

            else:
                # No reranking - convert ES documents to SearchResults
                final_results = self._convert_to_search_results(
                    es_response.documents, reranker_config.top_k_final
                )
                enable_reranking = False

            # Step 3: Limit final results
            final_results = final_results[: reranker_config.top_k_final]

            total_took_ms = int((time.time() - start_time) * 1000)

            response = SearchResponse(
                query=query,
                results=final_results,
                total_hits=es_response.total_hits,
                took_ms=total_took_ms,
                elasticsearch_took_ms=es_took_ms,
                reranking_took_ms=reranking_took_ms,
                model_used=model_used,
                reranking_enabled=enable_reranking,
                debug_info=debug_info,
            )

            logger.info(
                f"Search completed: {len(final_results)} results in {total_took_ms}ms"
            )

            return response

        except Exception as e:
            if isinstance(e, (ValidationError, RerankingError)):
                raise
            raise RerankingError(
                f"Search failed: {e}", query=query, stage="search"
            ) from e

    def _build_elasticsearch_query(
        self, query: str, filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build Elasticsearch query from text query and filters.

        Args:
            query: Text query
            filters: Additional filters

        Returns:
            Elasticsearch query DSL
        """
        # Start with a multi-match query
        base_query = {
            "multi_match": {
                "query": query,
                "fields": ["title^2", "text", "content"],
                "type": "best_fields",
                "fuzziness": "AUTO",
            }
        }

        if not filters:
            return base_query

        # Wrap with bool query to add filters
        bool_query = {"bool": {"must": [base_query], "filter": []}}

        # Add filters
        for field, value in filters.items():
            if isinstance(value, list):
                bool_query["bool"]["filter"].append({"terms": {field: value}})
            elif isinstance(value, dict):
                # Range or other complex filter
                bool_query["bool"]["filter"].append({field: value})
            else:
                bool_query["bool"]["filter"].append({"term": {field: value}})

        return bool_query

    async def _rerank_documents(
        self, query: str, documents: List[Document], config: RerankerConfig
    ) -> List[Tuple[Document, float]]:
        """
        Rerank documents using ZeroEntropy API.

        Args:
            query: Search query
            documents: Documents to rerank
            config: Reranker configuration

        Returns:
            List of (document, rerank_score) tuples, sorted by relevance
        """
        if not documents:
            return []

        try:
            # Prepare document texts for reranking
            doc_texts = []
            for doc in documents:
                # Combine title and text for better reranking
                text_parts = []
                if doc.title:
                    text_parts.append(doc.title)
                text_parts.append(doc.text)
                doc_texts.append(" ".join(text_parts))

            # Call ZeroEntropy API
            rerank_response = await self.zeroentropy_client.rerank(
                query=query,
                documents=doc_texts,
                model=config.model,
                top_k=len(documents),  # Get scores for all documents
            )

            # Create mapping from rerank results back to original documents
            reranked_docs = []
            for result in rerank_response.results:
                if 0 <= result.index < len(documents):
                    doc = documents[result.index]
                    score = result.relevance_score
                    reranked_docs.append((doc, score))

            # Sort by rerank score (highest first)
            reranked_docs.sort(key=lambda x: x[1], reverse=True)

            return reranked_docs

        except Exception as e:
            raise RerankingError(
                f"Reranking failed: {e}",
                query=query,
                document_count=len(documents),
                stage="reranking",
            ) from e

    def _combine_results(
        self,
        original_docs: List[Document],
        reranked_docs: List[Tuple[Document, float]],
        config: RerankerConfig,
    ) -> List[SearchResult]:
        """
        Combine Elasticsearch and reranking results.

        Args:
            original_docs: Original Elasticsearch documents
            reranked_docs: Reranked documents with scores
            config: Reranker configuration

        Returns:
            Combined and scored search results
        """
        # Create mapping from document ID to ES score
        es_scores = {}
        for i, doc in enumerate(original_docs):
            es_score = doc.metadata.get("elasticsearch_score", 0.0)
            es_scores[doc.id] = es_score if es_score is not None else 0.0

        results = []

        for rank, (doc, rerank_score) in enumerate(reranked_docs, 1):
            es_score = es_scores.get(doc.id, 0.0)

            if config.combine_scores:
                # Normalize scores to 0-1 range for combining
                normalized_es_score = self._normalize_score(
                    es_score, es_scores.values()
                )
                normalized_rerank_score = rerank_score  # Assume already normalized

                # Combine scores using weights
                combined_score = (
                    config.score_weights.get("elasticsearch", 0.3) * normalized_es_score
                    + config.score_weights.get("rerank", 0.7) * normalized_rerank_score
                )
            else:
                # Use rerank score only
                combined_score = rerank_score

            result = SearchResult(
                document=doc,
                score=combined_score,
                rank=rank,
                elasticsearch_score=es_score,
                rerank_score=rerank_score,
            )

            results.append(result)

        return results

    def _normalize_score(self, score: float, all_scores: List[float]) -> float:
        """Normalize score to 0-1 range using min-max normalization."""
        if not all_scores:
            return 0.0

        min_score = min(all_scores)
        max_score = max(all_scores)

        if max_score == min_score:
            return 1.0

        return (score - min_score) / (max_score - min_score)

    def _convert_to_search_results(
        self, documents: List[Document], limit: int
    ) -> List[SearchResult]:
        """Convert documents to SearchResult objects without reranking."""
        results = []

        for rank, doc in enumerate(documents[:limit], 1):
            es_score = doc.metadata.get("elasticsearch_score", 0.0)

            result = SearchResult(
                document=doc,
                score=es_score if es_score is not None else 0.0,
                rank=rank,
                elasticsearch_score=es_score,
                rerank_score=None,
            )

            results.append(result)

        return results

    async def search_batch(
        self, requests: List[SearchRequest], max_concurrent: Optional[int] = None
    ) -> List[SearchResponse]:
        """
        Perform multiple searches in parallel.

        Args:
            requests: List of search requests
            max_concurrent: Maximum concurrent searches

        Returns:
            List of search responses
        """
        if not requests:
            return []

        max_concurrent = max_concurrent or self.config.max_concurrent_requests
        semaphore = asyncio.Semaphore(max_concurrent)

        async def search_single(request: SearchRequest) -> SearchResponse:
            async with semaphore:
                return await self.search(
                    query=request.query,
                    index=request.index,
                    reranker_config=request.reranker_config,
                    elasticsearch_query=request.elasticsearch_query,
                    filters=request.filters,
                )

        tasks = [search_single(req) for req in requests]
        return await asyncio.gather(*tasks)

    async def health_check(self) -> HealthCheckResponse:
        """
        Perform comprehensive health check.

        Returns:
            Health check response
        """
        logger.info("Performing health check...")

        # Check Elasticsearch
        es_health = await self.elasticsearch_client.health_check()

        # Check ZeroEntropy API
        ze_health = await self.zeroentropy_client.health_check()

        # Determine overall status
        overall_status = "healthy"
        if es_health["status"] != "healthy" or ze_health["status"] != "healthy":
            overall_status = "unhealthy"

        response = HealthCheckResponse(
            status=overall_status,
            elasticsearch=es_health,
            zeroentropy=ze_health,
            version="0.1.0",
        )

        logger.info(f"Health check completed: {overall_status}")

        return response

    def __repr__(self) -> str:
        """String representation of the reranker."""
        return (
            f"ElasticZeroEntropyReranker("
            f"elasticsearch='{self.config.elasticsearch_url}', "
            f"zeroentropy='{self.config.zeroentropy_base_url}')"
        )
