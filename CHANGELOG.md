# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-07-30

### 🎉 Initial Release

This is the first public release of elastic-zeroentropy, a Python library that seamlessly integrates ZeroEntropy's state-of-the-art rerankers with Elasticsearch.

### ✨ Added

- **Core Functionality**
  - `ElasticZeroEntropyReranker` - Main reranker class for intelligent search
  - `ZeroEntropyClient` - Async HTTP client for ZeroEntropy API
  - `ElasticsearchClient` - Async client for Elasticsearch operations
  - `ElasticZeroEntropyConfig` - Comprehensive configuration management

- **Search Features**
  - Automatic reranking with ZeroEntropy models (zerank-1, zerank-1-small)
  - Flexible score combination strategies
  - Custom Elasticsearch queries
  - Batch processing with concurrency control
  - Search filters and aggregations
  - Debug information and performance metrics

- **Configuration & Setup**
  - Environment variable support
  - Configuration file loading
  - Programmatic configuration
  - Rate limiting and connection pooling
  - Health monitoring

- **Error Handling**
  - Comprehensive exception hierarchy
  - Detailed error messages and context
  - Graceful failure handling
  - Retry logic with exponential backoff

- **Command Line Interface**
  - Interactive search commands
  - Configuration management
  - Health checking
  - Index inspection
  - Multiple output formats (table, JSON, simple)

- **Developer Experience**
  - Full type hints and Pydantic models
  - Comprehensive test suite (>95% coverage)
  - Code formatting with Black and isort
  - Linting with flake8 and mypy
  - Pre-commit hooks
  - GitHub Actions CI/CD

- **Documentation**
  - Comprehensive README with examples
  - API documentation
  - Usage examples and tutorials
  - Contributing guidelines
  - Security policy

### 🔧 Technical Details

- **Dependencies**: httpx, elasticsearch, pydantic, pydantic-settings, tenacity, python-dotenv
- **Optional Dependencies**: click, rich (for CLI)
- **Python Support**: 3.8, 3.9, 3.10, 3.11, 3.12
- **License**: MIT
- **Test Coverage**: >95%

### 🚀 Performance

- **Accuracy**: Up to 28% improvement in NDCG@10 over baseline search
- **Speed**: ~150ms latency for small payloads, ~315ms for large payloads
- **Cost**: $0.025 per million tokens (50% less than competitors)
- **Throughput**: High concurrent request support with rate limiting

### 📦 Installation

```bash
# Basic installation
pip install elastic-zeroentropy

# With CLI support
pip install "elastic-zeroentropy[cli]"

# For development
pip install "elastic-zeroentropy[dev]"
```

### 🎯 Quick Start

```python
import asyncio
from elastic_zeroentropy import ElasticZeroEntropyReranker

async def main():
    async with ElasticZeroEntropyReranker() as reranker:
        response = await reranker.search(
            query="machine learning applications",
            index="my_documents"
        )
        for result in response.results:
            print(f"📄 {result.document.title}")
            print(f"   📊 Score: {result.score:.4f}")

asyncio.run(main())
```

### 🔗 Links

- **PyPI**: https://pypi.org/project/elastic-zeroentropy/
- **GitHub**: https://github.com/houssamouaziz/elastic-zeroentropy-reranker
- **Documentation**: https://github.com/houssamouaziz/elastic-zeroentropy-reranker#readme
- **ZeroEntropy**: https://zeroentropy.dev

---

## [Unreleased]

### Planned Features
- Additional ZeroEntropy models support
- Advanced scoring algorithms
- Real-time search capabilities
- Integration with more search engines
- Enhanced monitoring and analytics 