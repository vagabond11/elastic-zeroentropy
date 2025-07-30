"""Tests for the main reranker functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from elastic_zeroentropy.reranker import ElasticZeroEntropyReranker
from elastic_zeroentropy.config import ElasticZeroEntropyConfig
from elastic_zeroentropy.models import (
    Document,
    SearchResult,
    SearchResponse,
    RerankerConfig,
    ElasticsearchResponse,
    RerankResponse,
    RerankResult,
    HealthCheckResponse,
)
from elastic_zeroentropy.exceptions import ValidationError, RerankingError


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    with patch.dict("os.environ", {"ZEROENTROPY_API_KEY": "test-key"}):
        return ElasticZeroEntropyConfig()


@pytest.fixture
def sample_documents():
    """Create sample documents for testing."""
    return [
        Document(
            id="doc1",
            text="This is about artificial intelligence and machine learning",
            title="AI Overview",
            metadata={"elasticsearch_score": 0.8, "category": "tech"},
        ),
        Document(
            id="doc2",
            text="Python programming for data science applications",
            title="Python Guide",
            metadata={"elasticsearch_score": 0.6, "category": "programming"},
        ),
        Document(
            id="doc3",
            text="Natural language processing techniques and methods",
            title="NLP Methods",
            metadata={"elasticsearch_score": 0.7, "category": "tech"},
        ),
    ]


@pytest.fixture
def mock_elasticsearch_response(sample_documents):
    """Create a mock Elasticsearch response."""
    return ElasticsearchResponse(
        took=50,
        timed_out=False,
        total_hits=100,
        max_score=0.8,
        documents=sample_documents,
        raw_response={"hits": {"total": {"value": 100}}},
    )


@pytest.fixture
def mock_rerank_response():
    """Create a mock ZeroEntropy rerank response."""
    return RerankResponse(
        results=[
            RerankResult(index=2, relevance_score=0.95, document="doc3 text"),
            RerankResult(index=0, relevance_score=0.85, document="doc1 text"),
            RerankResult(index=1, relevance_score=0.75, document="doc2 text"),
        ],
        model="zerank-1",
        usage={"tokens": 150},
        request_id="req-123",
    )


class TestElasticZeroEntropyReranker:
    """Test the main reranker class."""

    @pytest.mark.asyncio
    async def test_initialization(self, mock_config):
        """Test reranker initialization."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        assert reranker.config == mock_config
        assert reranker.elasticsearch_client is not None
        assert reranker.zeroentropy_client is not None

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_config):
        """Test async context manager functionality."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        # Mock the client methods
        reranker.elasticsearch_client.__aenter__ = AsyncMock()
        reranker.elasticsearch_client.__aexit__ = AsyncMock()
        reranker.zeroentropy_client.__aenter__ = AsyncMock()
        reranker.zeroentropy_client.__aexit__ = AsyncMock()

        async with reranker:
            assert reranker is not None

        reranker.elasticsearch_client.__aenter__.assert_called_once()
        reranker.elasticsearch_client.__aexit__.assert_called_once()
        reranker.zeroentropy_client.__aenter__.assert_called_once()
        reranker.zeroentropy_client.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_validation_errors(self, mock_config):
        """Test search input validation."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        # Empty query
        with pytest.raises(ValidationError, match="Query cannot be empty"):
            await reranker.search("", "test-index")

        # Empty index
        with pytest.raises(ValidationError, match="Index cannot be empty"):
            await reranker.search("test query", "")

    @pytest.mark.asyncio
    async def test_search_without_reranking(
        self, mock_config, mock_elasticsearch_response
    ):
        """Test search without reranking enabled."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        # Mock Elasticsearch client
        reranker.elasticsearch_client.search = AsyncMock(
            return_value=mock_elasticsearch_response
        )

        response = await reranker.search(
            query="test query", index="test-index", enable_reranking=False
        )

        assert isinstance(response, SearchResponse)
        assert response.query == "test query"
        assert response.reranking_enabled is False
        assert response.reranking_took_ms is None
        assert len(response.results) == 3

        # Results should maintain original order
        assert response.results[0].document.id == "doc1"
        assert response.results[1].document.id == "doc2"
        assert response.results[2].document.id == "doc3"

    @pytest.mark.asyncio
    async def test_search_with_reranking(
        self, mock_config, mock_elasticsearch_response, mock_rerank_response
    ):
        """Test search with reranking enabled."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        # Mock clients
        reranker.elasticsearch_client.search = AsyncMock(
            return_value=mock_elasticsearch_response
        )
        reranker.zeroentropy_client.rerank = AsyncMock(
            return_value=mock_rerank_response
        )

        response = await reranker.search(
            query="test query", index="test-index", enable_reranking=True
        )

        assert isinstance(response, SearchResponse)
        assert response.query == "test query"
        assert response.reranking_enabled is True
        assert response.reranking_took_ms is not None
        assert len(response.results) == 3

        # Results should be reordered based on rerank scores
        # According to mock_rerank_response, doc3 (index 2) should be first
        assert response.results[0].document.id == "doc3"
        assert response.results[1].document.id == "doc1"
        assert response.results[2].document.id == "doc2"

        # Check that rerank scores are included
        assert response.results[0].rerank_score == 0.95
        assert response.results[1].rerank_score == 0.85
        assert response.results[2].rerank_score == 0.75

    @pytest.mark.asyncio
    async def test_search_with_custom_config(
        self, mock_config, mock_elasticsearch_response, mock_rerank_response
    ):
        """Test search with custom reranker configuration."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        # Mock clients
        reranker.elasticsearch_client.search = AsyncMock(
            return_value=mock_elasticsearch_response
        )
        reranker.zeroentropy_client.rerank = AsyncMock(
            return_value=mock_rerank_response
        )

        custom_config = RerankerConfig(
            top_k_initial=50,
            top_k_rerank=10,
            top_k_final=5,
            model="zerank-1-small",
            combine_scores=False,
            score_weights={"elasticsearch": 0.5, "rerank": 0.5},
        )

        response = await reranker.search(
            query="test query", index="test-index", reranker_config=custom_config
        )

        # Verify Elasticsearch search was called with correct size
        reranker.elasticsearch_client.search.assert_called_once()
        args, kwargs = reranker.elasticsearch_client.search.call_args
        assert kwargs["size"] == 50

        # Verify ZeroEntropy rerank was called with correct model
        reranker.zeroentropy_client.rerank.assert_called_once()
        args, kwargs = reranker.zeroentropy_client.rerank.call_args
        assert kwargs["model"] == "zerank-1-small"

    @pytest.mark.asyncio
    async def test_search_with_filters(self, mock_config, mock_elasticsearch_response):
        """Test search with additional filters."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        reranker.elasticsearch_client.search = AsyncMock(
            return_value=mock_elasticsearch_response
        )

        filters = {"category": "tech", "date_range": {"gte": "2023-01-01"}}

        await reranker.search(
            query="test query",
            index="test-index",
            filters=filters,
            enable_reranking=False,
        )

        # Verify that filters were included in the Elasticsearch query
        args, kwargs = reranker.elasticsearch_client.search.call_args
        query = kwargs["query"]

        assert "bool" in query
        assert "filter" in query["bool"]
        assert len(query["bool"]["filter"]) == 2

    @pytest.mark.asyncio
    async def test_search_with_debug_info(
        self, mock_config, mock_elasticsearch_response, mock_rerank_response
    ):
        """Test search with debug information enabled."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        reranker.elasticsearch_client.search = AsyncMock(
            return_value=mock_elasticsearch_response
        )
        reranker.zeroentropy_client.rerank = AsyncMock(
            return_value=mock_rerank_response
        )

        response = await reranker.search(
            query="test query", index="test-index", return_debug_info=True
        )

        assert response.debug_info is not None
        assert "elasticsearch" in response.debug_info
        assert "reranking" in response.debug_info

        es_debug = response.debug_info["elasticsearch"]
        assert "took_ms" in es_debug
        assert "total_hits" in es_debug
        assert "returned_docs" in es_debug

        rerank_debug = response.debug_info["reranking"]
        assert "model" in rerank_debug
        assert "documents_sent" in rerank_debug
        assert "took_ms" in rerank_debug

    def test_build_elasticsearch_query_simple(self, mock_config):
        """Test building simple Elasticsearch query."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        query = reranker._build_elasticsearch_query("machine learning")

        expected = {
            "multi_match": {
                "query": "machine learning",
                "fields": ["title^2", "text", "content"],
                "type": "best_fields",
                "fuzziness": "AUTO",
            }
        }

        assert query == expected

    def test_build_elasticsearch_query_with_filters(self, mock_config):
        """Test building Elasticsearch query with filters."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        filters = {
            "category": "tech",
            "tags": ["ai", "ml"],
            "score_range": {"gte": 0.5},
        }

        query = reranker._build_elasticsearch_query("machine learning", filters)

        assert "bool" in query
        assert "must" in query["bool"]
        assert "filter" in query["bool"]

        # Check that all filters are present
        filter_terms = query["bool"]["filter"]
        assert len(filter_terms) == 3

        # Find specific filter types
        term_filter = next(f for f in filter_terms if "term" in f)
        terms_filter = next(f for f in filter_terms if "terms" in f)
        range_filter = next(f for f in filter_terms if "score_range" in f)

        assert term_filter["term"]["category"] == "tech"
        assert terms_filter["terms"]["tags"] == ["ai", "ml"]
        assert range_filter["score_range"]["gte"] == 0.5

    @pytest.mark.asyncio
    async def test_rerank_documents_empty_list(self, mock_config):
        """Test reranking with empty document list."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)
        config = RerankerConfig()

        result = await reranker._rerank_documents("query", [], config)
        assert result == []

    @pytest.mark.asyncio
    async def test_rerank_documents_success(
        self, mock_config, sample_documents, mock_rerank_response
    ):
        """Test successful document reranking."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        reranker.zeroentropy_client.rerank = AsyncMock(
            return_value=mock_rerank_response
        )

        config = RerankerConfig()
        result = await reranker._rerank_documents(
            "test query", sample_documents, config
        )

        assert len(result) == 3

        # Results should be sorted by rerank score (highest first)
        assert result[0][1] == 0.95  # doc3
        assert result[1][1] == 0.85  # doc1
        assert result[2][1] == 0.75  # doc2

        # Verify that documents are correctly mapped
        assert result[0][0].id == "doc3"
        assert result[1][0].id == "doc1"
        assert result[2][0].id == "doc2"

    @pytest.mark.asyncio
    async def test_rerank_documents_api_error(self, mock_config, sample_documents):
        """Test reranking with API error."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        reranker.zeroentropy_client.rerank = AsyncMock(
            side_effect=Exception("API Error")
        )

        config = RerankerConfig()

        with pytest.raises(RerankingError, match="Reranking failed: API Error"):
            await reranker._rerank_documents("test query", sample_documents, config)

    def test_combine_results(self, mock_config, sample_documents):
        """Test combining Elasticsearch and reranking results."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        # Create reranked results (doc3, doc1, doc2 in order of relevance)
        reranked_docs = [
            (sample_documents[2], 0.95),  # doc3
            (sample_documents[0], 0.85),  # doc1
            (sample_documents[1], 0.75),  # doc2
        ]

        config = RerankerConfig(
            combine_scores=True, score_weights={"elasticsearch": 0.3, "rerank": 0.7}
        )

        results = reranker._combine_results(sample_documents, reranked_docs, config)

        assert len(results) == 3

        # Check that results are properly ranked
        assert results[0].rank == 1
        assert results[1].rank == 2
        assert results[2].rank == 3

        # Check that both ES and rerank scores are preserved
        assert results[0].elasticsearch_score == 0.7  # doc3's ES score
        assert results[0].rerank_score == 0.95

        # Check that combined scores are calculated
        # (normalized_es_score * 0.3 + rerank_score * 0.7)
        assert results[0].score > 0  # Should be a combined score

    def test_combine_results_rerank_only(self, mock_config, sample_documents):
        """Test combining results using only rerank scores."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        reranked_docs = [
            (sample_documents[2], 0.95),  # doc3
            (sample_documents[0], 0.85),  # doc1
            (sample_documents[1], 0.75),  # doc2
        ]

        config = RerankerConfig(combine_scores=False)

        results = reranker._combine_results(sample_documents, reranked_docs, config)

        # When not combining scores, should use rerank score only
        assert results[0].score == 0.95
        assert results[1].score == 0.85
        assert results[2].score == 0.75

    def test_normalize_score(self, mock_config):
        """Test score normalization."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        scores = [0.1, 0.5, 0.8, 1.0]

        # Test edge cases
        assert reranker._normalize_score(0.1, scores) == 0.0  # min
        assert reranker._normalize_score(1.0, scores) == 1.0  # max
        assert reranker._normalize_score(0.55, scores) == pytest.approx(0.5)  # middle

        # Test with single score
        assert reranker._normalize_score(0.5, [0.5]) == 1.0

        # Test with empty scores
        assert reranker._normalize_score(0.5, []) == 0.0

    def test_convert_to_search_results(self, mock_config, sample_documents):
        """Test converting documents to search results without reranking."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        results = reranker._convert_to_search_results(sample_documents, 2)

        assert len(results) == 2  # Limited to 2
        assert results[0].rank == 1
        assert results[1].rank == 2
        assert results[0].rerank_score is None
        assert results[0].elasticsearch_score == 0.8  # doc1's ES score

    @pytest.mark.asyncio
    async def test_search_batch(self, mock_config):
        """Test batch search functionality."""
        from elastic_zeroentropy.models import SearchRequest

        reranker = ElasticZeroEntropyReranker(config=mock_config)

        # Mock the single search method
        mock_response = SearchResponse(
            query="test",
            results=[],
            total_hits=0,
            took_ms=100,
            elasticsearch_took_ms=50,
            reranking_took_ms=None,
            model_used="zerank-1",
            reranking_enabled=False,
        )

        reranker.search = AsyncMock(return_value=mock_response)

        requests = [
            SearchRequest(query="query1", index="index1"),
            SearchRequest(query="query2", index="index2"),
        ]

        responses = await reranker.search_batch(requests)

        assert len(responses) == 2
        assert reranker.search.call_count == 2

    @pytest.mark.asyncio
    async def test_health_check(self, mock_config):
        """Test health check functionality."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        # Mock client health checks
        es_health = {"status": "healthy", "cluster_health": {"status": "green"}}
        ze_health = {"status": "healthy", "response": {"api": "ok"}}

        reranker.elasticsearch_client.health_check = AsyncMock(return_value=es_health)
        reranker.zeroentropy_client.health_check = AsyncMock(return_value=ze_health)

        health_response = await reranker.health_check()

        assert isinstance(health_response, HealthCheckResponse)
        assert health_response.status == "healthy"
        assert health_response.elasticsearch == es_health
        assert health_response.zeroentropy == ze_health
        assert health_response.version == "0.1.0"

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, mock_config):
        """Test health check with unhealthy components."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        # Mock unhealthy responses
        es_health = {"status": "unhealthy", "error": "Connection failed"}
        ze_health = {"status": "healthy"}

        reranker.elasticsearch_client.health_check = AsyncMock(return_value=es_health)
        reranker.zeroentropy_client.health_check = AsyncMock(return_value=ze_health)

        health_response = await reranker.health_check()

        assert health_response.status == "unhealthy"

    def test_repr(self, mock_config):
        """Test string representation."""
        reranker = ElasticZeroEntropyReranker(config=mock_config)

        repr_str = repr(reranker)
        assert "ElasticZeroEntropyReranker" in repr_str
        assert "elasticsearch" in repr_str
        assert "zeroentropy" in repr_str
