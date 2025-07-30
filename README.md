# elastic-zeroentropy

[![PyPI version](https://badge.fury.io/py/elastic-zeroentropy.svg)](https://badge.fury.io/py/elastic-zeroentropy)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Turn Elasticsearch into a smart search engine in 5 minutes with ZeroEntropy's LLM-powered reranking.**

`elastic-zeroentropy` is a lightweight Python library that seamlessly integrates [ZeroEntropy's state-of-the-art rerankers](https://www.zeroentropy.dev/blog/announcing-zeroentropys-first-reranker) with Elasticsearch to provide intelligent search result reranking. Boost your search relevance by up to 28% NDCG@10 with just a few lines of code.

## 🚀 Quick Start

```python
import asyncio
from elastic_zeroentropy import ElasticZeroEntropyReranker

async def main():
    # Initialize with environment variables or pass config directly
    async with ElasticZeroEntropyReranker() as reranker:
        response = await reranker.search(
            query="machine learning applications",
            index="my_documents"
        )
        
        for result in response.results:
            print(f"🔍 {result.document.title}")
            print(f"   📊 Score: {result.score:.4f}")
            print(f"   📄 {result.document.text[:100]}...")
            print()

asyncio.run(main())
```

## ✨ Features

- **🎯 State-of-the-art reranking**: Powered by ZeroEntropy's zerank-1 and zerank-1-small models
- **⚡ High performance**: Async HTTP requests with connection pooling and retry logic  
- **🔧 Easy configuration**: Environment variables, configuration files, or programmatic setup
- **🛡️ Robust error handling**: Graceful failures with detailed error messages
- **📊 Comprehensive monitoring**: Health checks, debug info, and performance metrics
- **🎛️ Flexible scoring**: Combine Elasticsearch and reranking scores with custom weights
- **🔍 Rich CLI**: Command-line interface for testing and debugging
- **📚 Full type safety**: Complete type hints and Pydantic models
- **🧪 Well tested**: Comprehensive test suite with >95% coverage

## 📦 Installation

Install the base package:
```bash
pip install elastic-zeroentropy
```

Or with optional CLI dependencies:
```bash
pip install "elastic-zeroentropy[cli]"
```

For development:
```bash
pip install "elastic-zeroentropy[dev]"
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Required: ZeroEntropy API key
ZEROENTROPY_API_KEY=your_api_key_here

# Optional: ZeroEntropy settings
ZEROENTROPY_BASE_URL=https://api.zeroentropy.dev/v1
ZEROENTROPY_MODEL=zerank-1

# Optional: Elasticsearch settings  
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_USERNAME=your_username
ELASTICSEARCH_PASSWORD=your_password

# Optional: Search behavior
DEFAULT_TOP_K_INITIAL=100
DEFAULT_TOP_K_RERANK=20
DEFAULT_TOP_K_FINAL=10
DEFAULT_ELASTICSEARCH_WEIGHT=0.3
DEFAULT_RERANK_WEIGHT=0.7
```

Generate a complete template:
```bash
elastic-zeroentropy config-template
```

### Programmatic Configuration

```python
from elastic_zeroentropy import ElasticZeroEntropyConfig

config = ElasticZeroEntropyConfig(
    zeroentropy_api_key="your_api_key",
    elasticsearch_url="http://localhost:9200",
    default_top_k_final=15
)
```

## 🎯 Usage Examples

### Basic Search with Reranking

```python
import asyncio
from elastic_zeroentropy import ElasticZeroEntropyReranker

async def search_example():
    async with ElasticZeroEntropyReranker() as reranker:
        response = await reranker.search(
            query="artificial intelligence applications",
            index="research_papers"
        )
        
        print(f"Found {response.total_hits} total hits")
        print(f"Search took {response.took_ms}ms")
        
        if response.reranking_enabled:
            print(f"Reranking took {response.reranking_took_ms}ms")
            print(f"Model used: {response.model_used}")
        
        for result in response.results:
            print(f"\n📄 {result.document.title or result.document.id}")
            print(f"Score: {result.score:.4f} (ES: {result.elasticsearch_score:.4f}, Rerank: {result.rerank_score:.4f})")
            print(f"Text: {result.document.text[:200]}...")

asyncio.run(search_example())
```

### Advanced Configuration

```python
from elastic_zeroentropy import ElasticZeroEntropyReranker, RerankerConfig

async def advanced_search():
    # Custom reranking configuration
    reranker_config = RerankerConfig(
        top_k_initial=50,      # Retrieve 50 docs from Elasticsearch
        top_k_rerank=15,       # Send top 15 to reranker
        top_k_final=5,         # Return top 5 final results
        model="zerank-1-small", # Use smaller/faster model
        combine_scores=True,   # Combine ES and rerank scores
        score_weights={
            "elasticsearch": 0.2,
            "rerank": 0.8
        }
    )
    
    async with ElasticZeroEntropyReranker() as reranker:
        response = await reranker.search(
            query="deep learning neural networks",
            index="ai_papers",
            reranker_config=reranker_config,
            filters={"category": "machine-learning", "year": {"gte": 2020}},
            return_debug_info=True
        )
        
        # Access debug information
        if response.debug_info:
            print("Debug Info:", response.debug_info)

asyncio.run(advanced_search())
```

### Batch Processing

```python
from elastic_zeroentropy import ElasticZeroEntropyReranker, SearchRequest

async def batch_search():
    requests = [
        SearchRequest(query="machine learning", index="papers"),
        SearchRequest(query="natural language processing", index="papers"),
        SearchRequest(query="computer vision", index="papers"),
    ]
    
    async with ElasticZeroEntropyReranker() as reranker:
        responses = await reranker.search_batch(requests, max_concurrent=2)
        
        for i, response in enumerate(responses):
            print(f"\nQuery {i+1}: {response.query}")
            print(f"Results: {len(response.results)}")

asyncio.run(batch_search())
```

### Custom Elasticsearch Queries

```python
from elastic_zeroentropy import ElasticZeroEntropyReranker, ElasticsearchQuery

async def custom_query_search():
    # Define custom Elasticsearch query
    es_query = ElasticsearchQuery(
        index="documents",
        query={
            "bool": {
                "must": [
                    {"match": {"title": "artificial intelligence"}},
                    {"range": {"publication_date": {"gte": "2023-01-01"}}}
                ],
                "should": [
                    {"match": {"abstract": "machine learning"}}
                ]
            }
        },
        size=50,
        sort=[{"_score": {"order": "desc"}}]
    )
    
    async with ElasticZeroEntropyReranker() as reranker:
        response = await reranker.search(
            query="AI and ML research",  # Used for reranking
            index="documents",           # Will be overridden by es_query.index
            elasticsearch_query=es_query
        )

asyncio.run(custom_query_search())
```

### Search Without Reranking

```python
async def elasticsearch_only():
    async with ElasticZeroEntropyReranker() as reranker:
        response = await reranker.search(
            query="information retrieval",
            index="documents",
            enable_reranking=False  # Skip reranking step
        )
        
        print(f"Elasticsearch-only results: {len(response.results)}")

asyncio.run(elasticsearch_only())
```

## 🖥️ Command Line Interface

The library includes a powerful CLI for testing and debugging:

### Basic Search
```bash
elastic-zeroentropy search "machine learning" my_index --top-k 5
```

### Advanced Search with Filters
```bash
elastic-zeroentropy search \
  "deep learning" \
  research_papers \
  --top-k-initial 100 \
  --top-k-rerank 20 \
  --top-k 10 \
  --model zerank-1-small \
  --filters '{"category": "AI", "year": {"gte": 2020}}' \
  --debug-info
```

### Health Check
```bash
elastic-zeroentropy health
```

### Configuration Management
```bash
# Show current configuration
elastic-zeroentropy config-show

# Generate template .env file
elastic-zeroentropy config-template

# Inspect Elasticsearch index
elastic-zeroentropy inspect my_index --limit 3
```

### Output Formats
```bash
# Table format (default)
elastic-zeroentropy search "AI" papers --output table

# JSON format
elastic-zeroentropy search "AI" papers --output json

# Simple text format  
elastic-zeroentropy search "AI" papers --output simple
```

## 🏥 Health Monitoring

Monitor the health of your Elasticsearch and ZeroEntropy connections:

```python
async def monitor_health():
    async with ElasticZeroEntropyReranker() as reranker:
        health = await reranker.health_check()
        
        print(f"Overall Status: {health.status}")
        print(f"Elasticsearch: {health.elasticsearch['status']}")
        print(f"ZeroEntropy API: {health.zeroentropy['status']}")
        
        if health.status != "healthy":
            print("Issues detected - check your configuration")

asyncio.run(monitor_health())
```

## ⚠️ Error Handling

The library provides specific exceptions for different error conditions:

```python
from elastic_zeroentropy import (
    ElasticZeroEntropyReranker,
    ConfigurationError,
    ZeroEntropyAPIError,
    ElasticsearchError,
    RerankingError
)

async def robust_search():
    try:
        async with ElasticZeroEntropyReranker() as reranker:
            response = await reranker.search("test query", "test_index")
            
    except ConfigurationError as e:
        print(f"Configuration issue: {e.message}")
        print(f"Details: {e.details}")
        
    except ZeroEntropyAPIError as e:
        print(f"ZeroEntropy API error: {e.message}")
        if e.status_code == 429:
            print("Rate limit exceeded - consider reducing request frequency")
            
    except ElasticsearchError as e:
        print(f"Elasticsearch error: {e.message}")
        print(f"Index: {e.details.get('index')}")
        
    except RerankingError as e:
        print(f"Reranking failed: {e.message}")
        print(f"Stage: {e.details.get('stage')}")

asyncio.run(robust_search())
```

## 🎛️ Advanced Features

### Score Combination Strategies

```python
# Rerank scores only
config = RerankerConfig(combine_scores=False)

# Custom weight combination
config = RerankerConfig(
    combine_scores=True,
    score_weights={"elasticsearch": 0.4, "rerank": 0.6}
)

# Elasticsearch scores only (no reranking)
response = await reranker.search(
    query="test",
    index="docs", 
    enable_reranking=False
)
```

### Rate Limiting and Performance

```python
from elastic_zeroentropy import ElasticZeroEntropyConfig

config = ElasticZeroEntropyConfig(
    zeroentropy_api_key="your_key",
    max_concurrent_requests=5,     # Limit concurrent requests
    requests_per_minute=500,       # Rate limiting
    connection_pool_size=20,       # HTTP connection pooling
    zeroentropy_timeout=30.0,      # Request timeout
    zeroentropy_max_retries=3      # Retry attempts
)
```

### Custom Document Processing

```python
from elastic_zeroentropy.models import Document

# Create documents with metadata
documents = [
    Document(
        id="doc1",
        text="Document content here",
        title="Document Title",
        metadata={"category": "research", "author": "John Doe"},
        source="database"
    )
]
```

## 🔧 Development

### Setup Development Environment

```bash
git clone https://github.com/houssamouaziz/elastic-zeroentropy-reranker.git
cd elastic-zeroentropy-reranker

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=elastic_zeroentropy --cov-report=html

# Type checking
mypy src/

# Code formatting
black src/ tests/
isort src/ tests/
```

### Project Structure

```
elastic-zeroentropy-reranker/
├── src/elastic_zeroentropy/     # Main package
│   ├── __init__.py             # Public API
│   ├── config.py               # Configuration management
│   ├── models.py               # Pydantic data models
│   ├── exceptions.py           # Custom exceptions
│   ├── zeroentropy_client.py   # ZeroEntropy API client
│   ├── elasticsearch_client.py # Elasticsearch client
│   ├── reranker.py            # Main reranker class
│   └── cli.py                 # Command-line interface
├── tests/                     # Test suite
├── examples/                  # Usage examples
├── docs/                      # Documentation
├── pyproject.toml            # Package configuration
└── README.md                 # This file
```

## 📊 Performance

Based on ZeroEntropy's benchmarks, you can expect:

- **Accuracy**: Up to 28% improvement in NDCG@10 over baseline search
- **Speed**: ~150ms latency for small payloads, ~315ms for large payloads  
- **Cost**: $0.025 per million tokens (50% less than competitors)
- **Throughput**: Supports high concurrent request volumes with rate limiting

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [ZeroEntropy](https://zeroentropy.dev) for their excellent reranking models
- [Elasticsearch](https://www.elastic.co/) for the search engine
- The Python community for amazing libraries like `httpx`, `pydantic`, and `click`

## 🔗 Links

- **ZeroEntropy**: [Website](https://zeroentropy.dev) | [Documentation](https://docs.zeroentropy.dev/reranker) | [GitHub](https://github.com/ZeroEntropy-AI)
- **Elasticsearch**: [Website](https://www.elastic.co/) | [Python Client](https://elasticsearch-py.readthedocs.io/)
- **Documentation**: [API Reference](docs/) | [Examples](examples/)

---

**Made with ❤️ by the elastic-zeroentropy team**
