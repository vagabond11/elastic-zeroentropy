#!/usr/bin/env python3
"""
Basic usage examples for elastic-zeroentropy library.

This file demonstrates the most common usage patterns for integrating
ZeroEntropy's reranking with Elasticsearch search.
"""

import asyncio
import os
from typing import List

# Import the main components
from elastic_zeroentropy import (
    ElasticZeroEntropyReranker,
    ElasticZeroEntropyConfig,
    RerankerConfig,
    SearchRequest,
    ElasticsearchQuery,
    Document,
)


async def basic_search_example():
    """Basic search with reranking."""
    print("🔍 Basic Search Example")
    print("=" * 50)
    
    # Simple search with default configuration
    async with ElasticZeroEntropyReranker() as reranker:
        response = await reranker.search(
            query="artificial intelligence machine learning",
            index="research_papers"  # Replace with your actual index
        )
        
        print(f"Query: {response.query}")
        print(f"Total hits: {response.total_hits:,}")
        print(f"Search took: {response.took_ms}ms")
        
        if response.reranking_enabled:
            print(f"Reranking took: {response.reranking_took_ms}ms")
            print(f"Model used: {response.model_used}")
        
        print(f"\nTop {len(response.results)} results:")
        for result in response.results:
            print(f"\n📄 Rank {result.rank}: {result.document.title or result.document.id}")
            print(f"   Overall Score: {result.score:.4f}")
            if result.elasticsearch_score:
                print(f"   ES Score: {result.elasticsearch_score:.4f}")
            if result.rerank_score:
                print(f"   Rerank Score: {result.rerank_score:.4f}")
            print(f"   Text: {result.document.text[:150]}...")


async def advanced_configuration_example():
    """Advanced search with custom configuration."""
    print("\n🎛️ Advanced Configuration Example")
    print("=" * 50)
    
    # Custom reranker configuration
    reranker_config = RerankerConfig(
        top_k_initial=50,       # Get 50 docs from Elasticsearch
        top_k_rerank=15,        # Send top 15 for reranking
        top_k_final=5,          # Return final top 5
        model="zerank-1-small", # Use smaller/faster model
        combine_scores=True,    # Combine ES and rerank scores
        score_weights={
            "elasticsearch": 0.2,  # 20% weight to ES scores
            "rerank": 0.8          # 80% weight to rerank scores
        }
    )
    
    # Search with filters and custom config
    async with ElasticZeroEntropyReranker() as reranker:
        response = await reranker.search(
            query="deep learning neural networks",
            index="ai_papers",
            reranker_config=reranker_config,
            filters={
                "category": "machine-learning",
                "publication_year": {"gte": 2020}
            },
            return_debug_info=True
        )
        
        print(f"Advanced search results: {len(response.results)}")
        
        # Show debug information
        if response.debug_info:
            print("\n🐛 Debug Information:")
            es_debug = response.debug_info.get("elasticsearch", {})
            print(f"   ES query time: {es_debug.get('took_ms')}ms")
            print(f"   ES total hits: {es_debug.get('total_hits')}")
            
            rerank_debug = response.debug_info.get("reranking", {})
            print(f"   Rerank time: {rerank_debug.get('took_ms')}ms")
            print(f"   Documents reranked: {rerank_debug.get('documents_sent')}")


async def custom_elasticsearch_query_example():
    """Using custom Elasticsearch queries."""
    print("\n📋 Custom Elasticsearch Query Example")
    print("=" * 50)
    
    # Define a complex Elasticsearch query
    custom_query = ElasticsearchQuery(
        index="documents",
        query={
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": "natural language processing",
                            "fields": ["title^2", "abstract", "content"],
                            "type": "best_fields"
                        }
                    }
                ],
                "filter": [
                    {"term": {"status": "published"}},
                    {"range": {"score": {"gte": 0.5}}}
                ],
                "should": [
                    {"match": {"tags": "nlp"}},
                    {"match": {"tags": "transformers"}}
                ]
            }
        },
        size=30,
        sort=[{"_score": {"order": "desc"}}],
        source=["title", "abstract", "content", "authors", "publication_date"]
    )
    
    async with ElasticZeroEntropyReranker() as reranker:
        response = await reranker.search(
            query="NLP and transformer models",  # This query is used for reranking
            index="documents",                   # Will be overridden by custom_query.index
            elasticsearch_query=custom_query
        )
        
        print(f"Custom query results: {len(response.results)}")
        for result in response.results[:3]:  # Show top 3
            print(f"\n📄 {result.document.title}")
            print(f"   Score: {result.score:.4f}")


async def batch_processing_example():
    """Batch processing multiple queries."""
    print("\n🔄 Batch Processing Example")
    print("=" * 50)
    
    # Define multiple search requests
    search_requests = [
        SearchRequest(
            query="machine learning algorithms",
            index="papers"
        ),
        SearchRequest(
            query="computer vision deep learning",
            index="papers",
            filters={"category": "cv"}
        ),
        SearchRequest(
            query="natural language processing",
            index="papers",
            reranker_config=RerankerConfig(
                top_k_final=3,
                model="zerank-1-small"
            )
        )
    ]
    
    async with ElasticZeroEntropyReranker() as reranker:
        # Process all requests concurrently (max 2 at a time)
        responses = await reranker.search_batch(
            search_requests, 
            max_concurrent=2
        )
        
        for i, response in enumerate(responses):
            print(f"\nQuery {i+1}: '{response.query}'")
            print(f"Results: {len(response.results)}")
            print(f"Time: {response.took_ms}ms")


async def error_handling_example():
    """Demonstrate error handling."""
    print("\n⚠️ Error Handling Example")
    print("=" * 50)
    
    from elastic_zeroentropy.exceptions import (
        ConfigurationError,
        ZeroEntropyAPIError,
        ElasticsearchError,
        RerankingError
    )
    
    # Example with invalid configuration
    try:
        invalid_config = ElasticZeroEntropyConfig(
            zeroentropy_api_key="invalid_key",
            elasticsearch_url="http://nonexistent:9200"
        )
        
        async with ElasticZeroEntropyReranker(config=invalid_config) as reranker:
            await reranker.search("test query", "test_index")
            
    except ConfigurationError as e:
        print(f"Configuration Error: {e.message}")
        if e.details:
            print(f"Details: {e.details}")
            
    except ZeroEntropyAPIError as e:
        print(f"ZeroEntropy API Error: {e.message}")
        if hasattr(e, 'status_code'):
            print(f"Status Code: {e.status_code}")
            
    except ElasticsearchError as e:
        print(f"Elasticsearch Error: {e.message}")
        if e.details:
            print(f"Details: {e.details}")
            
    except RerankingError as e:
        print(f"Reranking Error: {e.message}")
        print(f"Stage: {e.details.get('stage', 'unknown')}")
        
    except Exception as e:
        print(f"Unexpected Error: {e}")


async def health_monitoring_example():
    """Monitor system health."""
    print("\n🏥 Health Monitoring Example")
    print("=" * 50)
    
    async with ElasticZeroEntropyReranker() as reranker:
        health = await reranker.health_check()
        
        print(f"Overall Status: {health.status.upper()}")
        print(f"Timestamp: {health.timestamp}")
        print(f"Library Version: {health.version}")
        
        print(f"\nElasticsearch Status: {health.elasticsearch['status']}")
        if health.elasticsearch.get("cluster_health"):
            cluster = health.elasticsearch["cluster_health"]
            print(f"Cluster Status: {cluster.get('status')}")
            print(f"Number of Nodes: {cluster.get('number_of_nodes')}")
        
        print(f"\nZeroEntropy API Status: {health.zeroentropy['status']}")
        if "error" in health.zeroentropy:
            print(f"Error: {health.zeroentropy['error']}")


async def search_without_reranking_example():
    """Search using only Elasticsearch (no reranking)."""
    print("\n🔍 Elasticsearch-Only Search Example")
    print("=" * 50)
    
    async with ElasticZeroEntropyReranker() as reranker:
        response = await reranker.search(
            query="information retrieval systems",
            index="documents",
            enable_reranking=False  # Disable reranking
        )
        
        print(f"Elasticsearch-only results: {len(response.results)}")
        print(f"Reranking enabled: {response.reranking_enabled}")
        print(f"Total time: {response.took_ms}ms")
        
        for result in response.results[:3]:
            print(f"\n📄 {result.document.title or result.document.id}")
            print(f"   ES Score: {result.elasticsearch_score:.4f}")
            print(f"   Rerank Score: {result.rerank_score}")  # Should be None


async def programmatic_config_example():
    """Example of programmatic configuration."""
    print("\n⚙️ Programmatic Configuration Example")
    print("=" * 50)
    
    # Create configuration programmatically
    config = ElasticZeroEntropyConfig(
        zeroentropy_api_key=os.getenv("ZEROENTROPY_API_KEY", "demo_key"),
        zeroentropy_model="zerank-1-small",
        elasticsearch_url="http://localhost:9200",
        default_top_k_final=8,
        max_concurrent_requests=5,
        enable_rate_limiting=True,
        requests_per_minute=500
    )
    
    print(f"Configuration created:")
    print(f"  ZeroEntropy Model: {config.zeroentropy_model}")
    print(f"  Elasticsearch URL: {config.elasticsearch_url}")
    print(f"  Max Concurrent Requests: {config.max_concurrent_requests}")
    print(f"  Rate Limiting: {config.enable_rate_limiting}")
    
    # Use the custom configuration
    reranker = ElasticZeroEntropyReranker(config=config)
    print(f"Reranker created with custom config: {reranker}")


def main():
    """Run all examples."""
    print("🚀 Elastic-ZeroEntropy Library Examples")
    print("=" * 60)
    print()
    
    # Check for required environment variables
    if not os.getenv("ZEROENTROPY_API_KEY"):
        print("⚠️  Warning: ZEROENTROPY_API_KEY not set!")
        print("   Some examples may fail. Please set your API key.")
        print()
    
    # Run examples
    examples = [
        basic_search_example,
        advanced_configuration_example,
        custom_elasticsearch_query_example,
        batch_processing_example,
        search_without_reranking_example,
        programmatic_config_example,
        health_monitoring_example,
        error_handling_example,
    ]
    
    for example in examples:
        try:
            asyncio.run(example())
        except Exception as e:
            print(f"❌ Example failed: {e}")
        print()


if __name__ == "__main__":
    main() 