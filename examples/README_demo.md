# 🔁 Elastic-ZeroEntropy Demo UI

Interactive A/B testing interface to compare original Elasticsearch results vs ZeroEntropy reranked results.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd examples
pip install -r requirements_demo.txt
```

### 2. Run the Demo
```bash
streamlit run demo_ui.py
```

### 3. Open in Browser
Navigate to `http://localhost:8501`

## 🎯 Features

- **A/B Testing**: Side-by-side comparison of original vs reranked results
- **Interactive Controls**: Adjust reranking parameters in real-time
- **Demo Mode**: Works without API keys using sample data
- **Performance Metrics**: See timing and improvement statistics
- **Configuration Panel**: Easy access to all settings

## 🎛️ Configuration Options

### API Settings
- **ZeroEntropy API Key**: Your API key from zeroentropy.ai
- **Elasticsearch URL**: Your ES instance URL

### Search Settings
- **Index Name**: Elasticsearch index to search
- **Initial Results**: Number of docs to retrieve from ES
- **Documents to Rerank**: Number of docs to send for reranking
- **Final Results**: Number of results to display

### Reranking Settings
- **Model**: Choose between zerank-1 or zerank-1-small
- **Score Combination**: Mix ES and rerank scores
- **Weights**: Adjust ES vs rerank score weights

## 📊 Demo Mode

The demo includes sample data so you can test the interface without:
- ZeroEntropy API key
- Elasticsearch connection

Just enable "Use Demo Data" in the sidebar!

## 🎨 Screenshots

### Main Interface
![Main Interface](screenshots/main_interface.png)

### Results Comparison
![Results Comparison](screenshots/results_comparison.png)

### Configuration Panel
![Configuration Panel](screenshots/config_panel.png)

## 🔧 Customization

### Adding Your Own Data
1. Modify the `get_demo_data()` function in `demo_ui.py`
2. Add your own sample documents
3. Update the data structure to match your schema

### Styling
The demo uses Streamlit's built-in styling. You can customize by:
1. Modifying the `setup_page_config()` function
2. Adding custom CSS via `st.markdown()`
3. Using Streamlit's theming options

## 🚀 Deployment

### Local Development
```bash
streamlit run demo_ui.py --server.port 8501
```

### Production Deployment
```bash
# Using Streamlit Cloud
streamlit run demo_ui.py --server.port $PORT --server.address 0.0.0.0
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements_demo.txt .
RUN pip install -r requirements_demo.txt

COPY demo_ui.py .

EXPOSE 8501
CMD ["streamlit", "run", "demo_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🤝 Contributing

Want to improve the demo? Here are some ideas:

- [ ] Add more visualization types (charts, graphs)
- [ ] Include query suggestions
- [ ] Add export functionality
- [ ] Create different demo datasets
- [ ] Add performance benchmarking

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/vagabond11/elastic-zeroentropy/issues)
- **Discussions**: [GitHub Discussions](https://github.com/vagabond11/elastic-zeroentropy/discussions)
- **Documentation**: [Main README](../README.md) 