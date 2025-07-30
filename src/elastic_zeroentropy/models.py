"""
Data models for elastic-zeroentropy library.

This module defines all the data structures used throughout the library,
using Pydantic for validation and type safety.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, UTC


class Document(BaseModel):
    """Represents a document with text content and metadata."""

    id: str = Field(..., description="Unique identifier for the document")
    text: str = Field(..., description="Text content of the document")
    title: Optional[str] = Field(None, description="Optional title of the document")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    source: Optional[str] = Field(None, description="Source of the document")
    timestamp: Optional[datetime] = Field(
        None, description="When the document was created/indexed"
    )

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Text content cannot be empty")
        return v.strip()

    @field_validator("id")
    @classmethod
    def id_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Document ID cannot be empty")
        return v.strip()


class SearchResult(BaseModel):
    """Represents a search result with score and ranking information."""

    document: Document = Field(..., description="The document content")
    score: float = Field(..., description="Relevance score")
    rank: int = Field(..., description="Ranking position (1-based)")
    elasticsearch_score: Optional[float] = Field(
        None, description="Original Elasticsearch score"
    )
    rerank_score: Optional[float] = Field(
        None, description="ZeroEntropy reranking score"
    )

    @field_validator("score")
    @classmethod
    def score_must_be_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Score must be non-negative")
        return v

    @field_validator("rank")
    @classmethod
    def rank_must_be_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Rank must be positive (1-based)")
        return v


class ElasticsearchQuery(BaseModel):
    """Represents an Elasticsearch query configuration."""

    index: str = Field(..., description="Elasticsearch index name")
    query: Dict[str, Any] = Field(..., description="Elasticsearch query DSL")
    size: int = Field(
        default=10, description="Number of results to retrieve", ge=1, le=1000
    )
    from_: int = Field(
        default=0, description="Offset for pagination", alias="from", ge=0
    )
    source: Optional[List[str]] = Field(
        None, description="Fields to include in response"
    )
    sort: Optional[List[Dict[str, Any]]] = Field(None, description="Sort configuration")
    timeout: Optional[str] = Field(None, description="Request timeout (e.g., '30s')")

    model_config = {"validate_by_name": True}


class ElasticsearchResponse(BaseModel):
    """Represents an Elasticsearch search response."""

    took: int = Field(..., description="Time taken in milliseconds")
    timed_out: bool = Field(..., description="Whether the request timed out")
    total_hits: int = Field(..., description="Total number of matching documents")
    max_score: Optional[float] = Field(None, description="Maximum relevance score")
    documents: List[Document] = Field(..., description="Retrieved documents")
    raw_response: Dict[str, Any] = Field(..., description="Raw Elasticsearch response")


class RerankRequest(BaseModel):
    """Request payload for ZeroEntropy reranking API."""

    query: str = Field(..., description="Search query text")
    documents: List[str] = Field(
        ..., description="List of document texts to rerank", min_length=1
    )
    model: str = Field(default="zerank-1", description="ZeroEntropy model to use")
    top_k: Optional[int] = Field(
        None, description="Number of top results to return", ge=1
    )

    @field_validator("query")
    @classmethod
    def query_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()

    @field_validator("documents")
    @classmethod
    def documents_must_not_be_empty(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Documents list cannot be empty")
        cleaned_docs = []
        for doc in v:
            if not doc.strip():
                raise ValueError("Document text cannot be empty")
            cleaned_docs.append(doc.strip())
        return cleaned_docs


class RerankResult(BaseModel):
    """Individual result from ZeroEntropy reranking."""

    index: int = Field(..., description="Original index of the document")
    relevance_score: float = Field(..., description="Reranking relevance score")
    document: str = Field(..., description="Document text")


class RerankResponse(BaseModel):
    """Response from ZeroEntropy reranking API."""

    results: List[RerankResult] = Field(..., description="Reranked results")
    model: str = Field(..., description="Model used for reranking")
    usage: Optional[Dict[str, Any]] = Field(None, description="Token usage information")
    request_id: Optional[str] = Field(None, description="Unique request identifier")


class RerankerConfig(BaseModel):
    """Configuration for the reranking process."""

    top_k_initial: int = Field(
        default=100,
        description="Number of documents to retrieve from Elasticsearch",
        ge=1,
        le=10000,
    )
    top_k_rerank: int = Field(
        default=20,
        description="Number of documents to send for reranking",
        ge=1,
        le=1000,
    )
    top_k_final: int = Field(
        default=10, description="Number of final results to return", ge=1, le=100
    )
    model: str = Field(default="zerank-1", description="ZeroEntropy model to use")
    combine_scores: bool = Field(
        default=True, description="Whether to combine ES and rerank scores"
    )
    score_weights: Dict[str, float] = Field(
        default={"elasticsearch": 0.3, "rerank": 0.7},
        description="Weights for combining scores",
    )

    @field_validator("top_k_rerank")
    @classmethod
    def top_k_rerank_must_not_exceed_initial(cls, v: int, info) -> int:
        if "top_k_initial" in info.data and v > info.data["top_k_initial"]:
            raise ValueError("top_k_rerank cannot exceed top_k_initial")
        return v

    @field_validator("top_k_final")
    @classmethod
    def top_k_final_must_not_exceed_rerank(cls, v: int, info) -> int:
        if "top_k_rerank" in info.data and v > info.data["top_k_rerank"]:
            raise ValueError("top_k_final cannot exceed top_k_rerank")
        return v

    @field_validator("score_weights")
    @classmethod
    def score_weights_must_sum_to_one(cls, v: Dict[str, float]) -> Dict[str, float]:
        total = sum(v.values())
        if abs(total - 1.0) > 0.01:  # Allow small floating point errors
            raise ValueError("Score weights must sum to 1.0")
        return v


class HealthCheckResponse(BaseModel):
    """Health check response for monitoring."""

    status: str = Field(..., description="Overall status")
    elasticsearch: Dict[str, Any] = Field(
        ..., description="Elasticsearch connection status"
    )
    zeroentropy: Dict[str, Any] = Field(..., description="ZeroEntropy API status")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Check timestamp"
    )
    version: str = Field(..., description="Library version")


class SearchRequest(BaseModel):
    """High-level search request combining ES query and reranking."""

    query: str = Field(..., description="Search query text")
    elasticsearch_query: Optional[ElasticsearchQuery] = Field(
        None, description="Custom Elasticsearch query"
    )
    reranker_config: Optional[RerankerConfig] = Field(
        None, description="Reranking configuration"
    )
    index: str = Field(..., description="Elasticsearch index to search")
    filters: Optional[Dict[str, Any]] = Field(
        None, description="Additional filters to apply"
    )

    @field_validator("query")
    @classmethod
    def query_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class SearchResponse(BaseModel):
    """Complete search response with reranked results."""

    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="Reranked search results")
    total_hits: int = Field(..., description="Total number of matching documents")
    took_ms: int = Field(..., description="Total time taken in milliseconds")
    elasticsearch_took_ms: int = Field(..., description="Elasticsearch query time")
    reranking_took_ms: Optional[int] = Field(None, description="Reranking time")
    model_used: str = Field(..., description="ZeroEntropy model used for reranking")
    reranking_enabled: bool = Field(..., description="Whether reranking was applied")
    debug_info: Optional[Dict[str, Any]] = Field(None, description="Debug information")
