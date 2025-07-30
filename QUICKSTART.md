# Quick Start Guide

Get elastic-zeroentropy running in 5 minutes!

## 1. Installation

```bash
pip install elastic-zeroentropy
```

## 2. Setup Environment

Copy the example environment file:
```bash
cp env.example .env
```

Edit `.env` with your credentials:
```bash
# Required: Get your API key from https://zeroentropy.dev
ZEROENTROPY_API_KEY=your_api_key_here

# Optional: Elasticsearch settings
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_USERNAME=your_username
ELASTICSEARCH_PASSWORD=your_password
```

## 3. Basic Usage

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
            print(f"🔍 {result.document.title}")
            print(f"   📊 Score: {result.score:.4f}")
            print(f"   📄 {result.document.text[:100]}...")
            print()

asyncio.run(main())
```

## 4. CLI Usage

Test your setup:
```bash
# Health check
elastic-zeroentropy health

# Search with CLI
elastic-zeroentropy search "machine learning" my_index --top-k 5

# Show configuration
elastic-zeroentropy config-show
```

## 5. Advanced Configuration

```python
from elastic_zeroentropy import ElasticZeroEntropyReranker, RerankerConfig

async def advanced_search():
    config = RerankerConfig(
        top_k_initial=50,      # Get 50 docs from Elasticsearch
        top_k_rerank=15,       # Send top 15 to reranker
        top_k_final=5,         # Return top 5 results
        model="zerank-1-small", # Use smaller/faster model
        combine_scores=True,    # Combine ES and rerank scores
        score_weights={
            "elasticsearch": 0.3,
            "rerank": 0.7
        }
    )
    
    async with ElasticZeroEntropyReranker() as reranker:
        response = await reranker.search(
            query="deep learning neural networks",
            index="ai_papers",
            reranker_config=config,
            filters={"category": "machine-learning", "year": {"gte": 2020}}
        )
        
        print(f"Found {len(response.results)} results")
        print(f"Search took {response.took_ms}ms")
        if response.reranking_enabled:
            print(f"Reranking took {response.reranking_took_ms}ms")

asyncio.run(advanced_search())
```

## 6. Error Handling

```python
from elastic_zeroentropy import (
    ElasticZeroEntropyReranker,
    ConfigurationError,
    ZeroEntropyAPIError,
    ElasticsearchError
)

async def robust_search():
    try:
        async with ElasticZeroEntropyReranker() as reranker:
            response = await reranker.search("test query", "test_index")
            
    except ConfigurationError as e:
        print(f"Configuration issue: {e.message}")
        
    except ZeroEntropyAPIError as e:
        print(f"ZeroEntropy API error: {e.message}")
        if e.status_code == 429:
            print("Rate limit exceeded - consider reducing request frequency")
            
    except ElasticsearchError as e:
        print(f"Elasticsearch error: {e.message}")

asyncio.run(robust_search())
```

## 7. Health Monitoring

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

## 8. Batch Processing

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
            print(f"Query {i+1}: {response.query}")
            print(f"Results: {len(response.results)}")

asyncio.run(batch_search())
```

## 9. Custom Elasticsearch Queries

```python
from elastic_zeroentropy import ElasticZeroEntropyReranker, ElasticsearchQuery

async def custom_query_search():
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

## 10. Next Steps

- Read the [full documentation](README.md)
- Check out [examples](examples/)
- Explore the [CLI interface](README.md#command-line-interface)
- Join the [community](https://github.com/houssamouaziz/elastic-zeroentropy)

## Troubleshooting

### Common Issues

1. **Configuration Error**: Make sure your `.env` file has the required `ZEROENTROPY_API_KEY`
2. **Elasticsearch Connection**: Verify your Elasticsearch instance is running and accessible
3. **Rate Limiting**: If you get 429 errors, reduce request frequency or increase rate limits
4. **Authentication**: Check your Elasticsearch credentials if using authentication

### Getting Help

- Check the [documentation](README.md)
- Review [examples](examples/)
- Open an [issue](https://github.com/houssamouaziz/elastic-zeroentropy/issues)
- Use the CLI health check: `elastic-zeroentropy health` 