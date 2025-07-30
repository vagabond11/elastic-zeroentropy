# 🚀 Testing & Deployment Guide

Complete guide for testing, tagging, deploying, and showcasing your Elastic-ZeroEntropy reranker.

## 🧪 Testing Strategy

### 1. Local Testing

#### Test the Demo UI
```bash
# Install demo dependencies
cd examples
pip install -r requirements_demo.txt

# Run the demo
streamlit run demo_ui.py

# Or use the quick runner
./run_demo.sh
```

#### Test the Library
```bash
# Install in development mode
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=elastic_zeroentropy --cov-report=html

# Type checking
mypy src/

# Code quality checks
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

### 2. Integration Testing

#### Test with Real Elasticsearch
```bash
# Start Elasticsearch (Docker)
docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.11.0

# Test the library
python -c "
import asyncio
from elastic_zeroentropy import ElasticZeroEntropyReranker

async def test():
    async with ElasticZeroEntropyReranker() as reranker:
        response = await reranker.search('test query', 'test_index')
        print(f'Found {len(response.results)} results')

asyncio.run(test())
"
```

#### Test with ZeroEntropy API
```bash
# Set your API key
export ZEROENTROPY_API_KEY="your_key_here"

# Test reranking
python -c "
import asyncio
from elastic_zeroentropy import ElasticZeroEntropyReranker

async def test():
    async with ElasticZeroEntropyReranker() as reranker:
        response = await reranker.search('machine learning healthcare', 'research_papers')
        print(f'Reranked {len(response.results)} results')
        print(f'Model used: {response.model_used}')
        print(f'Time taken: {response.took_ms}ms')

asyncio.run(test())
"
```

### 3. Performance Testing

#### Benchmark Script
```python
# examples/benchmark.py
import asyncio
import time
from elastic_zeroentropy import ElasticZeroEntropyReranker

async def benchmark():
    queries = [
        "machine learning applications",
        "deep learning neural networks", 
        "artificial intelligence healthcare",
        "natural language processing",
        "computer vision medical imaging"
    ]
    
    async with ElasticZeroEntropyReranker() as reranker:
        for query in queries:
            start = time.time()
            response = await reranker.search(query, "research_papers")
            end = time.time()
            
            print(f"Query: {query}")
            print(f"Results: {len(response.results)}")
            print(f"Time: {(end-start)*1000:.2f}ms")
            print(f"Reranking: {response.reranking_took_ms}ms")
            print("---")

asyncio.run(benchmark())
```

## 🏷️ Version Tagging & Release

### 1. Update Version
```bash
# Update version in pyproject.toml
# Update __version__ in src/elastic_zeroentropy/__init__.py
# Update CHANGELOG.md
```

### 2. Create Git Tag
```bash
# Commit all changes
git add .
git commit -m "Release v0.1.2 - Enhanced demo UI and performance improvements"

# Create and push tag
git tag -a v0.1.2 -m "Release v0.1.2"
git push origin v0.1.2
```

### 3. Build and Deploy to PyPI
```bash
# Build package
python -m build

# Check build
twine check dist/*

# Upload to PyPI
twine upload dist/*

# Or upload to Test PyPI first
twine upload --repository testpypi dist/*
```

### 4. GitHub Release
```bash
# Create GitHub release with:
# - Release notes from CHANGELOG.md
# - Attach demo screenshots
# - Include installation instructions
```

## 📸 Screenshot Strategy

### 1. Demo UI Screenshots

#### **Main Interface** (1920x1080)
- **What to capture**: Full demo UI with search interface
- **Key elements**: Header, search box, configuration sidebar
- **Purpose**: Show professional design and ZeroEntropy branding

#### **Results Comparison** (1920x1080)
- **What to capture**: Side-by-side results with charts
- **Key elements**: Performance metrics, comparison chart, data tables
- **Purpose**: Demonstrate A/B testing capabilities

#### **Configuration Panel** (800x600)
- **What to capture**: Sidebar with all settings
- **Key elements**: API keys, reranking settings, demo mode toggle
- **Purpose**: Show customization options

#### **Performance Metrics** (1200x800)
- **What to capture**: Metrics dashboard with timing info
- **Key elements**: Query time, reranking time, improvement percentage
- **Purpose**: Highlight performance benefits

### 2. Code Examples Screenshots

#### **Quick Start Code** (800x400)
- **What to capture**: Simple 5-line code example
- **Key elements**: Import, async context, search call
- **Purpose**: Show ease of use

#### **Advanced Configuration** (800x500)
- **What to capture**: Custom reranker config
- **Key elements**: RerankerConfig, score weights, model selection
- **Purpose**: Show advanced capabilities

### 3. Before/After Comparisons

#### **Search Results** (1600x900)
- **What to capture**: Original vs reranked results side-by-side
- **Key elements**: Score differences, ranking changes
- **Purpose**: Demonstrate improvement

#### **Performance Chart** (1200x600)
- **What to capture**: Interactive Plotly chart
- **Key elements**: Bar chart comparing scores
- **Purpose**: Visualize improvements

## 🎨 Screenshot Guidelines

### Technical Requirements
- **Resolution**: Minimum 1920x1080 for main screenshots
- **Format**: PNG with transparent background where possible
- **Quality**: High DPI (2x or 3x for retina displays)
- **Browser**: Chrome with dark theme extensions disabled

### Visual Guidelines
- **Theme**: Match ZeroEntropy's dark theme
- **Colors**: Use #00d4ff (ZeroEntropy blue) for highlights
- **Typography**: Clean, modern fonts
- **Spacing**: Generous whitespace for professional look

### Content Guidelines
- **Queries**: Use realistic, domain-specific queries
- **Data**: Use diverse, relevant sample data
- **Metrics**: Show positive improvements
- **Text**: Keep UI text clean and professional

## 🚀 Deployment Options

### 1. Streamlit Cloud (Recommended)
```bash
# Deploy to Streamlit Cloud
# 1. Push to GitHub
# 2. Connect Streamlit Cloud to your repo
# 3. Set deployment path to examples/demo_ui.py
# 4. Add requirements_demo.txt
# 5. Deploy
```

### 2. Heroku
```bash
# Create Procfile
echo "web: streamlit run examples/demo_ui.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# Create runtime.txt
echo "python-3.9.18" > runtime.txt

# Deploy
heroku create elastic-zeroentropy-demo
git push heroku main
```

### 3. Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY examples/requirements_demo.txt .
RUN pip install -r requirements_demo.txt

COPY examples/demo_ui.py .
COPY src/ ./src/

EXPOSE 8501
CMD ["streamlit", "run", "demo_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 4. Vercel/Netlify
```bash
# Create requirements.txt for deployment
pip freeze > requirements.txt

# Deploy using their Python support
```

## 📊 Testing Checklist

### ✅ Pre-Release Testing
- [ ] All unit tests pass
- [ ] Integration tests with real ES
- [ ] ZeroEntropy API integration works
- [ ] Demo UI runs without errors
- [ ] Performance benchmarks completed
- [ ] Documentation updated
- [ ] Version numbers updated
- [ ] CHANGELOG updated

### ✅ Screenshot Checklist
- [ ] Main interface screenshot
- [ ] Results comparison screenshot
- [ ] Configuration panel screenshot
- [ ] Performance metrics screenshot
- [ ] Code examples screenshots
- [ ] Before/after comparisons
- [ ] Interactive chart screenshots

### ✅ Deployment Checklist
- [ ] PyPI package uploaded
- [ ] GitHub release created
- [ ] Demo deployed to Streamlit Cloud
- [ ] Documentation updated with demo links
- [ ] Social media assets ready
- [ ] ZeroEntropy team notified

## 🎯 Marketing Assets

### Screenshots for Social Media
1. **Twitter/X**: Main interface + results comparison
2. **LinkedIn**: Professional demo with metrics
3. **GitHub**: Code examples + performance charts
4. **Blog**: Before/after comparisons

### Video Content
1. **Demo Walkthrough**: 2-3 minute demo video
2. **Quick Start**: 30-second setup video
3. **Performance Demo**: Side-by-side comparison

### Documentation Updates
1. **README**: Add demo links and screenshots
2. **PyPI**: Update description with demo
3. **GitHub**: Add demo to repository description

## 🔗 Quick Commands

### Test Everything
```bash
# Run all tests
make test

# Run demo
./run_demo.sh

# Check code quality
make lint

# Build package
make build
```

### Deploy Everything
```bash
# Tag and release
git tag -a v0.1.2 -m "Release v0.1.2"
git push origin v0.1.2

# Build and upload
python -m build
twine upload dist/*

# Deploy demo
# (Follow Streamlit Cloud deployment)
```

This comprehensive guide ensures your library is thoroughly tested, professionally presented, and ready for maximum impact! 🚀 