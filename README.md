# 🔁 ZeroEntropy Reranker for Elasticsearch

**Boost your Elasticsearch results with LLM reranking in 5 minutes.**  
This open-source tool adds a smart reranking layer to your existing Elastic queries using [ZeroEntropy's](https://zeroentropy.ai) API.

🧠 Built for developers who want great search results without rebuilding their stack.

[![PyPI version](https://badge.fury.io/py/elastic-zeroentropy.svg)](https://badge.fury.io/py/elastic-zeroentropy)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Built with FastAPI](https://img.shields.io/badge/Built%20with-FastAPI-green)](https://fastapi.tiangolo.com/)
[![ZeroEntropy API](https://img.shields.io/badge/Powered%20by-ZeroEntropy-blue)](https://zeroentropy.ai)
[![Elastic Compatible](https://img.shields.io/badge/Elastic-Compatible-orange)](https://www.elastic.co/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

---

## 🎯 The Problem

Most Elasticsearch users struggle with:
- **Vague queries** that return irrelevant results
- **Complex search intent** that BM25 can't understand  
- **Ambiguous terms** that need contextual understanding
- **No AI skills** to implement vector search

**Solution**: Add LLM-powered reranking without changing your existing setup.

---

## ✨ Features

- 🔌 **Plug-and-play**: Drop-in proxy or client wrapper
- 🧠 **LLM-powered relevance** via ZeroEntropy API
- ⚡ **Works with any Elasticsearch** or OpenSearch backend
- 🔍 **Hybrid-ready**: Rerank BM25 + vector results
- 📊 **Side-by-side comparison**: Original vs reranked output
- 🚀 **5-minute setup**: No AI expertise required
- 💰 **Cost-effective**: Only rerank top N results

---

## 🚀 Quick Demo

### 🖥️ Interactive Demo UI
Try our **live A/B testing interface** to compare original vs reranked results:

```bash
# Quick start (recommended)
./run_demo.sh

# Or manual setup
cd examples
pip install -r requirements_demo.txt
streamlit run demo_ui.py
```

**Features:**
- 🔄 Side-by-side comparison
- ⚙️ Interactive parameter controls  
- 📊 Real-time performance metrics
- 🎯 Demo mode (no API keys needed)

### 💻 Code Example
```python
import asyncio
from elastic_zeroentropy import ElasticZeroEntropyReranker

async def main():
    async with ElasticZeroEntropyReranker() as reranker:
        response = await reranker.search(
            query="machine learning applications in healthcare",
            index="research_papers"
        )
        
        for result in response.results:
            print(f"🔍 {result.document.title}")
            print(f"   📊 Score: {result.score:.4f}")
            print(f"   📄 {result.document.text[:100]}...")

asyncio.run(main())
```

**Before vs After:**
| Query | Original Elastic | Reranked (ZeroEntropy) |
|-------|------------------|-------------------------|
| "books about hope and war" | 🔻 Generic results | ✅ Contextually relevant |
| "machine learning healthcare" | 🔻 Broad matches | ✅ Domain-specific papers |
| "python async programming" | 🔻 Mixed relevance | ✅ Focused tutorials |

---

## 📦 Installation

```bash
pip install elastic-zeroentropy
```

Or with CLI tools:
```bash
pip install "elastic-zeroentropy[cli]"
```

---

## ⚡ 5-Minute Setup

### 1. Get ZeroEntropy API Key
```bash
# Sign up at https://zeroentropy.ai
export ZEROENTROPY_API_KEY="your_api_key_here"
```

### 2. Configure Elasticsearch
```bash
export ELASTICSEARCH_URL="http://localhost:9200"
```

### 3. Run Your First Search
```python
from elastic_zeroentropy import ElasticZeroEntropyReranker

async with ElasticZeroEntropyReranker() as reranker:
    results = await reranker.search("your query", "your_index")
```

---

## 🎛️ Advanced Usage

### Custom Reranking Configuration
```python
from elastic_zeroentropy import RerankerConfig

config = RerankerConfig(
    top_k_initial=100,      # Get 100 docs from Elasticsearch
    top_k_rerank=20,        # Send top 20 to reranker
    top_k_final=10,         # Return top 10 final results
    model="zerank-1-small", # Use faster model
    combine_scores=True,    # Mix ES + rerank scores
    score_weights={
        "elasticsearch": 0.3,
        "rerank": 0.7
    }
)

response = await reranker.search(
    query="deep learning neural networks",
    index="ai_papers",
    reranker_config=config
)
```

### Batch Processing
```python
from elastic_zeroentropy import SearchRequest

requests = [
    SearchRequest(query="machine learning", index="papers"),
    SearchRequest(query="natural language processing", index="papers"),
    SearchRequest(query="computer vision", index="papers"),
]

responses = await reranker.search_batch(requests, max_concurrent=3)
```

### Health Monitoring
```python
health = await reranker.health_check()
print(f"Status: {health.status}")
print(f"Elasticsearch: {health.elasticsearch['status']}")
print(f"ZeroEntropy: {health.zeroentropy['status']}")
```

---

## 🖥️ Command Line Interface

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

---

## 🏗️ Architecture

```
User Query → Elasticsearch → Top N Results → ZeroEntropy API → Reranked Results
```

1. **Elasticsearch Search**: Get initial results using your existing queries
2. **Document Selection**: Choose top N documents for reranking
3. **ZeroEntropy Reranking**: Send to LLM for contextual relevance scoring
4. **Score Combination**: Mix Elasticsearch and rerank scores (optional)
5. **Final Results**: Return intelligently reranked results

---

## 🎯 Performance

Based on ZeroEntropy's benchmarks:
- **Accuracy**: Up to 28% improvement in NDCG@10
- **Speed**: ~150ms latency for small payloads
- **Cost**: $0.025 per million tokens (50% less than competitors)
- **Throughput**: High concurrent request support

---

## 🔧 Configuration

### Environment Variables
```bash
# Required
ZEROENTROPY_API_KEY=your_api_key_here

# Optional
ZEROENTROPY_BASE_URL=https://api.zeroentropy.dev/v1
ZEROENTROPY_MODEL=zerank-1
ELASTICSEARCH_URL=http://localhost:9200
DEFAULT_TOP_K_INITIAL=100
DEFAULT_TOP_K_RERANK=20
DEFAULT_TOP_K_FINAL=10
```

### Programmatic Configuration
```python
from elastic_zeroentropy import ElasticZeroEntropyConfig

config = ElasticZeroEntropyConfig(
    zeroentropy_api_key="your_key",
    elasticsearch_url="http://localhost:9200",
    default_top_k_final=15
)
```

---

## 🧩 Coming Soon

- [ ] **Smart Reranking**: Only rerank when needed (query classifier)
- [x] **UI Toggle**: Compare original vs reranked results ✅
- [ ] **LangChain Integration**: Plugin for LangChain workflows
- [x] **Streamlit App**: Interactive demo and testing ✅
- [ ] **More Models**: Support for additional ZeroEntropy models
- [ ] **Caching**: Intelligent result caching for repeated queries

---

## 🤝 Contributing

We're building a better search UX together! PRs, feedback, and ideas welcome.

### Development Setup
```bash
git clone https://github.com/vagabond11/elastic-zeroentropy.git
cd elastic-zeroentropy
pip install -e ".[dev]"
pytest
```

### Areas to Contribute
- 🎨 **UI/UX**: Better demos and visualizations
- 🔧 **Integrations**: LangChain, Streamlit, FastAPI plugins
- 📊 **Analytics**: Search quality metrics and monitoring
- 🌐 **Documentation**: Examples, tutorials, case studies

---

## 📊 Community Stats

[![GitHub stars](https://img.shields.io/github/stars/vagabond11/elastic-zeroentropy)](https://github.com/vagabond11/elastic-zeroentropy/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/vagabond11/elastic-zeroentropy)](https://github.com/vagabond11/elastic-zeroentropy/network/members)
[![GitHub issues](https://img.shields.io/github/issues/vagabond11/elastic-zeroentropy)](https://github.com/vagabond11/elastic-zeroentropy/issues)
[![PyPI downloads](https://img.shields.io/pypi/dm/elastic-zeroentropy)](https://pypi.org/project/elastic-zeroentropy/)

---

## 🏆 Why This Works

**Most Elastic users struggle with vague, complex, or ambiguous queries.**

This tool reranks the top N results using LLM-based contextual understanding via ZeroEntropy.

**No vectors? No problem.**  
**No AI skills needed.**

Just drop in the reranker and get smarter search results instantly.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🔗 Links

- **📦 PyPI**: https://pypi.org/project/elastic-zeroentropy/
- **🐙 GitHub**: https://github.com/vagabond11/elastic-zeroentropy
- **🤖 ZeroEntropy**: https://zeroentropy.ai
- **📋 Issues**: https://github.com/vagabond11/elastic-zeroentropy/issues
- **💬 Discussions**: https://github.com/vagabond11/elastic-zeroentropy/discussions

---

**Made with ❤️ by the elastic-zeroentropy team**

*Keywords: elasticsearch, search, ai-search, reranking, llm, zeroentropy, semantic-search, bm25, relevance, hybrid-search, open-source-search*
