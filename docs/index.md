# elastic-zeroentropy Documentation

Welcome to the elastic-zeroentropy documentation! This library seamlessly integrates ZeroEntropy's state-of-the-art rerankers with Elasticsearch to provide intelligent search result reranking.

## 🚀 Quick Start

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

## 📚 Documentation Sections

### [Installation Guide](installation.md)
Learn how to install and set up elastic-zeroentropy in your project.

### [Configuration](configuration.md)
Detailed guide on configuring the library for your use case.

### [API Reference](api.md)
Complete API documentation for all classes and methods.

### [Examples](examples.md)
Comprehensive examples showing different usage patterns.

### [Advanced Usage](advanced.md)
Advanced features like custom queries, batch processing, and more.

### [Troubleshooting](troubleshooting.md)
Common issues and their solutions.

### [Performance Guide](performance.md)
Tips for optimizing performance and reducing costs.

### [Security](security.md)
Security considerations and best practices.

## 🎯 Key Features

- **State-of-the-art reranking**: Powered by ZeroEntropy's zerank-1 and zerank-1-small models
- **High performance**: Async HTTP requests with connection pooling and retry logic
- **Easy configuration**: Environment variables, configuration files, or programmatic setup
- **Robust error handling**: Graceful failures with detailed error messages
- **Comprehensive monitoring**: Health checks, debug info, and performance metrics
- **Flexible scoring**: Combine Elasticsearch and reranking scores with custom weights
- **Rich CLI**: Command-line interface for testing and debugging
- **Full type safety**: Complete type hints and Pydantic models

## 📊 Performance

- **Accuracy**: Up to 28% improvement in NDCG@10 over baseline search
- **Speed**: ~150ms latency for small payloads, ~315ms for large payloads
- **Cost**: $0.025 per million tokens (50% less than competitors)
- **Throughput**: High concurrent request support with rate limiting

## 🔗 Links

- **PyPI**: https://pypi.org/project/elastic-zeroentropy/
- **GitHub**: https://github.com/houssamouaziz/elastic-zeroentropy
- **ZeroEntropy**: https://zeroentropy.dev
- **Issues**: https://github.com/houssamouaziz/elastic-zeroentropy/issues
- **Discussions**: https://github.com/houssamouaziz/elastic-zeroentropy/discussions

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](../CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details. 