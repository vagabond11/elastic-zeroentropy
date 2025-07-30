#!/usr/bin/env python3
"""
Basic usage example for elastic-zeroentropy.

This example demonstrates the fundamental usage of the library
for performing searches with automatic reranking.
"""

import asyncio
import os
from elastic_zeroentropy import ElasticZeroEntropyReranker


async def basic_search_example():
    """Demonstrate basic search functionality."""
    print("🔍 Basic Search Example")
    print("=" * 50)
    
    # Initialize the reranker
    async with ElasticZeroEntropyReranker() as reranker:
        # Perform a search
        response = await reranker.search(
            query="machine learning applications",
            index="documents"
        )
        
        print(f"📊 Found {response.total_hits} total hits")
        print(f"⏱️  Search took {response.took_ms}ms")
        
        if response.reranking_enabled:
            print(f"🔄 Reranking took {response.reranking_took_ms}ms")
            print(f"🤖 Model used: {response.model_used}")
        
        print("\n📄 Top Results:")
        for i, result in enumerate(response.results[:3], 1):
            print(f"\n{i}. {result.document.title or result.document.id}")
            print(f"   📊 Score: {result.score:.4f}")
            if result.elasticsearch_score and result.rerank_score:
                print(f"   🔍 ES Score: {result.elasticsearch_score:.4f}")
                print(f"   🎯 Rerank Score: {result.rerank_score:.4f}")
            print(f"   📝 {result.document.text[:100]}...")


async def search_without_reranking():
    """Demonstrate search without reranking."""
    print("\n🔍 Search Without Reranking")
    print("=" * 50)
    
    async with ElasticZeroEntropyReranker() as reranker:
        response = await reranker.search(
            query="artificial intelligence",
            index="documents",
            enable_reranking=False
        )
        
        print(f"📊 Found {response.total_hits} results (Elasticsearch only)")
        print(f"⏱️  Search took {response.took_ms}ms")
        print(f"🔄 Reranking enabled: {response.reranking_enabled}")


async def advanced_configuration():
    """Demonstrate advanced configuration options."""
    print("\n⚙️  Advanced Configuration")
    print("=" * 50)
    
    from elastic_zeroentropy import RerankerConfig
    
    # Custom reranking configuration
    config = RerankerConfig(
        top_k_initial=50,      # Retrieve 50 docs from Elasticsearch
        top_k_rerank=15,       # Send top 15 to reranker
        top_k_final=5,         # Return top 5 final results
        model="zerank-1-small", # Use smaller/faster model
        combine_scores=True,    # Combine ES and rerank scores
        score_weights={
            "elasticsearch": 0.2,
            "rerank": 0.8
        }
    )
    
    async with ElasticZeroEntropyReranker() as reranker:
        response = await reranker.search(
            query="deep learning neural networks",
            index="documents",
            reranker_config=config,
            return_debug_info=True
        )
        
        print(f"📊 Found {response.total_hits} results")
        print(f"🎯 Using custom configuration:")
        print(f"   - Initial docs: {config.top_k_initial}")
        print(f"   - Reranked docs: {config.top_k_rerank}")
        print(f"   - Final results: {config.top_k_final}")
        print(f"   - Model: {config.model}")
        
        if response.debug_info:
            print(f"🔍 Debug info available: {len(response.debug_info)} items")


async def batch_processing():
    """Demonstrate batch processing capabilities."""
    print("\n📦 Batch Processing")
    print("=" * 50)
    
    from elastic_zeroentropy import SearchRequest
    
    # Create multiple search requests
    requests = [
        SearchRequest(query="machine learning", index="documents"),
        SearchRequest(query="natural language processing", index="documents"),
        SearchRequest(query="computer vision", index="documents"),
    ]
    
    async with ElasticZeroEntropyReranker() as reranker:
        responses = await reranker.search_batch(requests, max_concurrent=2)
        
        for i, response in enumerate(responses, 1):
            print(f"\n🔍 Query {i}: '{response.query}'")
            print(f"   📊 Results: {len(response.results)}")
            print(f"   ⏱️  Time: {response.took_ms}ms")


async def health_check():
    """Demonstrate health checking."""
    print("\n🏥 Health Check")
    print("=" * 50)
    
    async with ElasticZeroEntropyReranker() as reranker:
        health = await reranker.health_check()
        
        print(f"📊 Overall Status: {health.status}")
        print(f"🔍 Elasticsearch: {health.elasticsearch['status']}")
        print(f"🤖 ZeroEntropy: {health.zeroentropy['status']}")
        print(f"📦 Version: {health.version}")
        
        if health.status != "healthy":
            print("⚠️  Issues detected - check your configuration")


def main():
    """Run all examples."""
    print("🚀 elastic-zeroentropy Examples")
    print("=" * 50)
    
    # Check if API key is configured
    if not os.getenv("ZEROENTROPY_API_KEY"):
        print("⚠️  Warning: ZEROENTROPY_API_KEY not set")
        print("   Set your API key to run these examples:")
        print("   export ZEROENTROPY_API_KEY=your_api_key_here")
        print("\n📖 Examples will show structure but may not work without API key")
    
    # Run examples
    asyncio.run(basic_search_example())
    asyncio.run(search_without_reranking())
    asyncio.run(advanced_configuration())
    asyncio.run(batch_processing())
    asyncio.run(health_check())
    
    print("\n✅ All examples completed!")


if __name__ == "__main__":
    main() 