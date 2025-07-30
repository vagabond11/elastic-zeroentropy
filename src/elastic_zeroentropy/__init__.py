"""
elastic-zeroentropy: Turn Elasticsearch into a smart search engine with ZeroEntropy's reranking.

A lightweight Python library that integrates ZeroEntropy's state-of-the-art rerankers
with Elasticsearch to provide intelligent search result reranking.
"""

from .config import ElasticZeroEntropyConfig
from .elasticsearch_client import ElasticsearchClient
from .exceptions import (
    ConfigurationError,
    ElasticsearchError,
    ElasticZeroEntropyError,
    RerankingError,
    ZeroEntropyAPIError,
)
from .models import (
    Document,
    ElasticsearchQuery,
    ElasticsearchResponse,
    RerankRequest,
    RerankResponse,
    RerankerConfig,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from .reranker import ElasticZeroEntropyReranker
from .zeroentropy_client import ZeroEntropyClient

__version__ = "0.1.1"
__author__ = "Houssam Aït"
__email__ = "houssam@example.com"

__all__ = [
    # Main classes
    "ElasticZeroEntropyReranker",
    "ZeroEntropyClient",
    "ElasticsearchClient",
    # Configuration
    "ElasticZeroEntropyConfig",
    "RerankerConfig",
    # Models
    "Document",
    "SearchResult",
    "SearchRequest",
    "SearchResponse",
    "RerankRequest",
    "RerankResponse",
    "ElasticsearchQuery",
    "ElasticsearchResponse",
    # Exceptions
    "ElasticZeroEntropyError",
    "ElasticsearchError",
    "ZeroEntropyAPIError",
    "ConfigurationError",
    "RerankingError",
]
