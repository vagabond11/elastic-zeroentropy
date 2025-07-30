"""
elastic-zeroentropy: Turn Elasticsearch into a smart search engine with ZeroEntropy's reranking.

A lightweight Python library that integrates ZeroEntropy's state-of-the-art rerankers
with Elasticsearch to provide intelligent search result reranking.
"""

from .config import ElasticZeroEntropyConfig
from .exceptions import (
    ElasticZeroEntropyError,
    ElasticsearchError,
    ZeroEntropyAPIError,
    ConfigurationError,
    RerankingError,
)
from .models import (
    Document,
    SearchResult,
    RerankRequest,
    RerankResponse,
    ElasticsearchQuery,
    ElasticsearchResponse,
)
from .reranker import ElasticZeroEntropyReranker
from .zeroentropy_client import ZeroEntropyClient
from .elasticsearch_client import ElasticsearchClient

__version__ = "0.1.0"
__author__ = "Houssam Aït"
__email__ = "houssam@example.com"

__all__ = [
    # Main classes
    "ElasticZeroEntropyReranker",
    "ZeroEntropyClient",
    "ElasticsearchClient",
    # Configuration
    "ElasticZeroEntropyConfig",
    # Models
    "Document",
    "SearchResult",
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
