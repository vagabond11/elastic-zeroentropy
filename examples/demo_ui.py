"""
Streamlit Demo UI for Elastic-ZeroEntropy Reranker

A/B testing interface to compare original Elasticsearch results vs reranked results.
Designed with ZeroEntropy's professional dark theme and high-quality UX.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from rich.console import Console
from rich.table import Table

# Add the src directory to the path so we can import our library
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from elastic_zeroentropy import (
    ElasticZeroEntropyReranker,
    RerankerConfig,
    SearchRequest,
    SearchResponse,
)
from elastic_zeroentropy.config import ElasticZeroEntropyConfig

# Initialize rich console for better output formatting
console = Console()


def setup_page_config():
    """Configure Streamlit page settings with ZeroEntropy-style theme."""
    st.set_page_config(
        page_title="Elastic-ZeroEntropy Reranker Demo",
        page_icon="🔁",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Custom CSS for ZeroEntropy-style dark theme
    st.markdown("""
    <style>
    /* ZeroEntropy-inspired dark theme */
    .main {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        color: #ffffff;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a1a 0%, #0f0f0f 100%);
        border-right: 1px solid #333;
    }
    
    /* Headers with gradient text */
    h1, h2, h3 {
        background: linear-gradient(90deg, #00d4ff, #0099cc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }
    
    /* Cards with glassmorphism effect */
    .stCard {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
    }
    
    /* Buttons with gradient */
    .stButton > button {
        background: linear-gradient(90deg, #00d4ff, #0099cc);
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3);
    }
    
    /* Metrics with glow effect */
    .metric-container {
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Tables with dark theme */
    .dataframe {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        overflow: hidden;
    }
    
    .dataframe th {
        background: rgba(0, 212, 255, 0.2);
        color: white;
        font-weight: 600;
    }
    
    .dataframe td {
        color: #e0e0e0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #00d4ff, #0099cc);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        color: #00d4ff;
        font-weight: 600;
    }
    
    /* Success/Error messages */
    .stAlert {
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(90deg, #00d4ff, #0099cc);
        border-radius: 4px;
    }
    
    /* Loading animation */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .loading {
        animation: pulse 2s infinite;
    }
    </style>
    """, unsafe_allow_html=True)


def create_header():
    """Create the main header section with ZeroEntropy branding."""
    st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <h1 style="font-size: 3rem; margin-bottom: 10px;">🔁 Elastic-ZeroEntropy Reranker</h1>
        <p style="font-size: 1.2rem; color: #00d4ff; margin-bottom: 20px;">
            <strong>A/B Test Original Elasticsearch vs LLM-Reranked Results</strong>
        </p>
        <p style="color: #cccccc; max-width: 600px; margin: 0 auto;">
            Compare how ZeroEntropy's LLM-powered reranking improves search relevance with human-level understanding.
        </p>
    </div>
    """, unsafe_allow_html=True)


def create_sidebar():
    """Create the sidebar with configuration options."""
    st.sidebar.markdown("""
    <div style="padding: 20px 0;">
        <h2 style="color: #00d4ff; margin-bottom: 20px;">⚙️ Configuration</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # API Configuration
    st.sidebar.markdown("### 🔑 API Keys")
    zeroentropy_api_key = st.sidebar.text_input(
        "ZeroEntropy API Key",
        type="password",
        help="Get your API key from https://zeroentropy.dev"
    )
    
    elasticsearch_url = st.sidebar.text_input(
        "Elasticsearch URL",
        value="http://localhost:9200",
        help="Your Elasticsearch instance URL"
    )
    
    # Search Configuration
    st.sidebar.markdown("### 🔍 Search Settings")
    index_name = st.sidebar.text_input(
        "Index Name",
        value="documents",
        help="Elasticsearch index to search"
    )
    
    # Reranking Configuration
    st.sidebar.markdown("### 🧠 Reranking Settings")
    top_k_initial = st.sidebar.slider(
        "Initial Results from ES",
        min_value=10,
        max_value=200,
        value=50,
        help="Number of documents to retrieve from Elasticsearch"
    )
    
    top_k_rerank = st.sidebar.slider(
        "Documents to Rerank",
        min_value=5,
        max_value=50,
        value=20,
        help="Number of documents to send for reranking"
    )
    
    top_k_final = st.sidebar.slider(
        "Final Results",
        min_value=5,
        max_value=20,
        value=10,
        help="Number of final results to display"
    )
    
    model = st.sidebar.selectbox(
        "ZeroEntropy Model",
        options=["zerank-1", "zerank-1-small"],
        index=0,
        help="Model to use for reranking"
    )
    
    combine_scores = st.sidebar.checkbox(
        "Combine ES + Rerank Scores",
        value=True,
        help="Mix Elasticsearch and reranking scores"
    )
    
    if combine_scores:
        es_weight = st.sidebar.slider(
            "Elasticsearch Weight",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.1,
            help="Weight for Elasticsearch scores"
        )
        rerank_weight = 1.0 - es_weight
        st.sidebar.metric("Rerank Weight", f"{rerank_weight:.1f}")
    
    # Demo Data
    st.sidebar.markdown("### 📊 Demo Data")
    use_demo_data = st.sidebar.checkbox(
        "Use Demo Data (if no ES connection)",
        value=True,
        help="Use sample data for demonstration"
    )
    
    return {
        "zeroentropy_api_key": zeroentropy_api_key,
        "elasticsearch_url": elasticsearch_url,
        "index_name": index_name,
        "top_k_initial": top_k_initial,
        "top_k_rerank": top_k_rerank,
        "top_k_final": top_k_final,
        "model": model,
        "combine_scores": combine_scores,
        "es_weight": es_weight if combine_scores else 0.0,
        "rerank_weight": rerank_weight if combine_scores else 1.0,
        "use_demo_data": use_demo_data,
    }


def get_demo_data() -> Dict[str, List[Dict]]:
    """Get sample data for demonstration."""
    return {
        "research_papers": [
            {
                "id": "1",
                "title": "Deep Learning Applications in Healthcare",
                "text": "This paper explores how deep learning models can improve medical diagnosis accuracy by analyzing medical images and patient data.",
                "score": 0.85,
                "category": "AI",
                "year": 2023
            },
            {
                "id": "2", 
                "title": "Machine Learning for Drug Discovery",
                "text": "A comprehensive review of machine learning techniques used in pharmaceutical research and drug development processes.",
                "score": 0.78,
                "category": "AI",
                "year": 2023
            },
            {
                "id": "3",
                "title": "Neural Networks in Medical Imaging",
                "text": "Study of convolutional neural networks applied to radiology and medical image analysis for improved diagnostic accuracy.",
                "score": 0.72,
                "category": "AI",
                "year": 2022
            },
            {
                "id": "4",
                "title": "Healthcare Data Analytics",
                "text": "Overview of data analytics methods in healthcare, including patient monitoring and treatment optimization.",
                "score": 0.68,
                "category": "Analytics",
                "year": 2022
            },
            {
                "id": "5",
                "title": "AI in Clinical Decision Support",
                "text": "Artificial intelligence systems that assist healthcare professionals in making clinical decisions and treatment recommendations.",
                "score": 0.65,
                "category": "AI",
                "year": 2023
            },
            {
                "id": "6",
                "title": "Big Data in Healthcare",
                "text": "Analysis of large-scale healthcare datasets for insights into patient outcomes and treatment effectiveness.",
                "score": 0.62,
                "category": "Analytics",
                "year": 2021
            },
            {
                "id": "7",
                "title": "Computer Vision for Medical Diagnosis",
                "text": "Advanced computer vision techniques applied to medical imaging for automated disease detection and diagnosis.",
                "score": 0.58,
                "category": "AI",
                "year": 2023
            },
            {
                "id": "8",
                "title": "Predictive Analytics in Medicine",
                "text": "Using machine learning to predict patient outcomes and identify at-risk individuals for early intervention.",
                "score": 0.55,
                "category": "Analytics",
                "year": 2022
            },
            {
                "id": "9",
                "title": "Natural Language Processing in Healthcare",
                "text": "NLP techniques for processing medical records, clinical notes, and patient communications.",
                "score": 0.52,
                "category": "AI",
                "year": 2023
            },
            {
                "id": "10",
                "title": "Healthcare Information Systems",
                "text": "Overview of electronic health records and healthcare management systems for patient care.",
                "score": 0.48,
                "category": "Systems",
                "year": 2021
            }
        ]
    }


def simulate_reranking(original_results: List[Dict], query: str) -> List[Dict]:
    """Simulate reranking by reordering results based on query relevance."""
    # This is a simplified simulation - in real usage, this would call ZeroEntropy API
    
    # Simulate different relevance scores based on query terms
    query_terms = query.lower().split()
    
    for result in original_results:
        # Calculate simulated rerank score based on query-term matching
        text = f"{result['title']} {result['text']}".lower()
        relevance_score = 0.0
        
        for term in query_terms:
            if term in text:
                relevance_score += 0.2
            if term in result['title'].lower():
                relevance_score += 0.3
            if term in result['text'].lower():
                relevance_score += 0.1
        
        # Add some randomness to make it realistic
        import random
        relevance_score += random.uniform(0, 0.1)
        result['rerank_score'] = min(1.0, relevance_score)
    
    # Sort by rerank score
    reranked = sorted(original_results, key=lambda x: x['rerank_score'], reverse=True)
    
    # Update ranks
    for i, result in enumerate(reranked):
        result['rank'] = i + 1
        result['final_score'] = result['rerank_score']
    
    return reranked


def create_comparison_chart(original_results: List[Dict], reranked_results: List[Dict], config: Dict):
    """Create a beautiful comparison chart using Plotly."""
    # Prepare data for the chart
    original_scores = [r.get('score', 0) for r in original_results[:config["top_k_final"]]]
    reranked_scores = [r.get('rerank_score', 0) for r in reranked_results[:config["top_k_final"]]]
    titles = [r['title'][:30] + "..." if len(r['title']) > 30 else r['title'] for r in original_results[:config["top_k_final"]]]
    
    # Create the comparison chart
    fig = go.Figure()
    
    # Original scores
    fig.add_trace(go.Bar(
        name='Original ES',
        x=titles,
        y=original_scores,
        marker_color='rgba(255, 99, 132, 0.8)',
        hovertemplate='<b>%{x}</b><br>Score: %{y:.3f}<extra></extra>'
    ))
    
    # Reranked scores
    fig.add_trace(go.Bar(
        name='ZeroEntropy Reranked',
        x=titles,
        y=reranked_scores,
        marker_color='rgba(0, 212, 255, 0.8)',
        hovertemplate='<b>%{x}</b><br>Score: %{y:.3f}<extra></extra>'
    ))
    
    # Update layout with ZeroEntropy theme
    fig.update_layout(
        title={
            'text': 'Score Comparison: Original vs Reranked',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#00d4ff'}
        },
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#ffffff'},
        xaxis={
            'title': 'Documents',
            'gridcolor': 'rgba(255,255,255,0.1)',
            'tickangle': -45
        },
        yaxis={
            'title': 'Relevance Score',
            'gridcolor': 'rgba(255,255,255,0.1)',
            'range': [0, 1]
        },
        legend={
            'bgcolor': 'rgba(0,0,0,0.8)',
            'bordercolor': 'rgba(255,255,255,0.2)',
            'borderwidth': 1
        },
        margin={'t': 80, 'b': 100, 'l': 80, 'r': 80}
    )
    
    return fig


def display_results_comparison(
    original_results: List[Dict],
    reranked_results: List[Dict],
    query: str,
    config: Dict
):
    """Display side-by-side comparison of original vs reranked results."""
    
    st.markdown("""
    <div style="margin: 40px 0;">
        <h2 style="text-align: center; color: #00d4ff;">📊 Results Comparison</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-container">
            <h3 style="color: #00d4ff; margin: 0;">Query</h3>
            <p style="margin: 5px 0; font-size: 1.1rem;">{}</p>
        </div>
        """.format(query), unsafe_allow_html=True)
    
    with col2:
        original_avg_score = sum(r.get('score', 0) for r in original_results[:config["top_k_final"]]) / len(original_results[:config["top_k_final"]])
        st.markdown("""
        <div class="metric-container">
            <h3 style="color: #ff6384; margin: 0;">Original Avg</h3>
            <p style="margin: 5px 0; font-size: 1.1rem;">{:.3f}</p>
        </div>
        """.format(original_avg_score), unsafe_allow_html=True)
    
    with col3:
        reranked_avg_score = sum(r.get('rerank_score', 0) for r in reranked_results[:config["top_k_final"]]) / len(reranked_results[:config["top_k_final"]])
        st.markdown("""
        <div class="metric-container">
            <h3 style="color: #00d4ff; margin: 0;">Reranked Avg</h3>
            <p style="margin: 5px 0; font-size: 1.1rem;">{:.3f}</p>
        </div>
        """.format(reranked_avg_score), unsafe_allow_html=True)
    
    with col4:
        improvement = ((reranked_avg_score - original_avg_score) / original_avg_score) * 100 if original_avg_score > 0 else 0
        improvement_color = "#00ff88" if improvement > 0 else "#ff6384"
        st.markdown("""
        <div class="metric-container">
            <h3 style="color: {}; margin: 0;">Improvement</h3>
            <p style="margin: 5px 0; font-size: 1.1rem;">{:+.1f}%</p>
        </div>
        """.format(improvement_color, improvement), unsafe_allow_html=True)
    
    # Comparison chart
    st.markdown("### 📈 Score Comparison Chart")
    chart = create_comparison_chart(original_results, reranked_results, config)
    st.plotly_chart(chart, use_container_width=True)
    
    # Results tables
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔍 **Original Elasticsearch Results**")
        
        # Create DataFrame for original results
        original_df = pd.DataFrame([
            {
                "Rank": result.get("rank", i + 1),
                "Title": result["title"][:40] + "..." if len(result["title"]) > 40 else result["title"],
                "Score": f"{result.get('score', 0):.3f}",
                "Category": result.get("category", "N/A"),
                "Year": result.get("year", "N/A")
            }
            for i, result in enumerate(original_results[:config["top_k_final"]])
        ])
        
        st.dataframe(original_df, use_container_width=True)
        
        # Show original results details
        with st.expander("📄 Original Results Details"):
            for i, result in enumerate(original_results[:config["top_k_final"]]):
                st.markdown(f"**{i+1}. {result['title']}**")
                st.markdown(f"*Score: {result.get('score', 0):.3f}*")
                st.markdown(f"{result['text'][:200]}...")
                st.markdown("---")
    
    with col2:
        st.markdown("### 🧠 **ZeroEntropy Reranked Results**")
        
        # Create DataFrame for reranked results
        reranked_df = pd.DataFrame([
            {
                "Rank": result.get("rank", i + 1),
                "Title": result["title"][:40] + "..." if len(result["title"]) > 40 else result["title"],
                "Score": f"{result.get('rerank_score', 0):.3f}",
                "Category": result.get("category", "N/A"),
                "Year": result.get("year", "N/A")
            }
            for i, result in enumerate(reranked_results[:config["top_k_final"]])
        ])
        
        st.dataframe(reranked_df, use_container_width=True)
        
        # Show reranked results details
        with st.expander("📄 Reranked Results Details"):
            for i, result in enumerate(reranked_results[:config["top_k_final"]]):
                st.markdown(f"**{i+1}. {result['title']}**")
                st.markdown(f"*Score: {result.get('rerank_score', 0):.3f}*")
                st.markdown(f"{result['text'][:200]}...")
                st.markdown("---")


def display_configuration_summary(config: Dict):
    """Display current configuration summary."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Current Settings")
    
    st.sidebar.markdown(f"**Index:** {config['index_name']}")
    st.sidebar.markdown(f"**Model:** {config['model']}")
    st.sidebar.markdown(f"**Initial Results:** {config['top_k_initial']}")
    st.sidebar.markdown(f"**Rerank Count:** {config['top_k_rerank']}")
    st.sidebar.markdown(f"**Final Results:** {config['top_k_final']}")
    st.sidebar.markdown(f"**Score Combination:** {'✅' if config['combine_scores'] else '❌'}")


def main():
    """Main Streamlit application."""
    setup_page_config()
    create_header()
    
    # Get configuration from sidebar
    config = create_sidebar()
    
    # Check if API key is provided
    if not config["zeroentropy_api_key"] and not config["use_demo_data"]:
        st.error("⚠️ Please provide a ZeroEntropy API key or enable demo data mode.")
        st.info("💡 Get your API key from https://zeroentropy.dev")
        return
    
    # Main search interface
    st.markdown("""
    <div style="margin: 40px 0;">
        <h2 style="text-align: center; color: #00d4ff;">🔍 Search Interface</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Query input with better styling
    query = st.text_input(
        "Enter your search query:",
        placeholder="e.g., machine learning healthcare applications",
        help="Enter a search query to compare original vs reranked results"
    )
    
    if not query:
        st.info("💡 Enter a query above to start the A/B test")
        return
    
    # Search button with custom styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Run A/B Test", type="primary", use_container_width=True):
            with st.spinner("Running search and reranking..."):
                
                if config["use_demo_data"]:
                    # Use demo data
                    demo_data = get_demo_data()
                    original_results = demo_data.get(config["index_name"], [])
                    
                    # Simulate reranking
                    reranked_results = simulate_reranking(original_results, query)
                    
                    # Display results
                    display_results_comparison(original_results, reranked_results, query, config)
                    
                    st.success("✅ Demo completed! This shows simulated reranking results.")
                    st.info("💡 Connect to a real Elasticsearch instance and provide a ZeroEntropy API key for live results.")
                    
                else:
                    # Use real Elasticsearch and ZeroEntropy
                    try:
                        # Create configuration
                        elastic_config = ElasticZeroEntropyConfig(
                            zeroentropy_api_key=config["zeroentropy_api_key"],
                            elasticsearch_url=config["elasticsearch_url"],
                            default_top_k_initial=config["top_k_initial"],
                            default_top_k_rerank=config["top_k_rerank"],
                            default_top_k_final=config["top_k_final"],
                            zeroentropy_model=config["model"],
                            default_combine_scores=config["combine_scores"],
                            default_elasticsearch_weight=config["es_weight"],
                            default_rerank_weight=config["rerank_weight"],
                        )
                        
                        # Create reranker config
                        reranker_config = RerankerConfig(
                            top_k_initial=config["top_k_initial"],
                            top_k_rerank=config["top_k_rerank"],
                            top_k_final=config["top_k_final"],
                            model=config["model"],
                            combine_scores=config["combine_scores"],
                            score_weights={
                                "elasticsearch": config["es_weight"],
                                "rerank": config["rerank_weight"]
                            }
                        )
                        
                        # Run search with reranking
                        async def run_search():
                            async with ElasticZeroEntropyReranker(elastic_config) as reranker:
                                response = await reranker.search(
                                    query=query,
                                    index=config["index_name"],
                                    reranker_config=reranker_config,
                                    return_debug_info=True
                                )
                                return response
                        
                        # Run the search
                        response = asyncio.run(run_search())
                        
                        # Convert to display format
                        original_results = []
                        reranked_results = []
                        
                        for result in response.results:
                            doc = {
                                "id": result.document.id,
                                "title": result.document.title or result.document.id,
                                "text": result.document.text,
                                "score": result.elasticsearch_score or 0.0,
                                "rerank_score": result.rerank_score or 0.0,
                                "final_score": result.score,
                                "rank": result.rank,
                                "category": result.document.metadata.get("category", "N/A"),
                                "year": result.document.metadata.get("year", "N/A")
                            }
                            
                            original_results.append(doc.copy())
                            reranked_results.append(doc)
                        
                        # Sort original by ES score, reranked by final score
                        original_results.sort(key=lambda x: x["score"], reverse=True)
                        reranked_results.sort(key=lambda x: x["final_score"], reverse=True)
                        
                        # Display results
                        display_results_comparison(original_results, reranked_results, query, config)
                        
                        # Show performance metrics
                        st.markdown("### ⚡ Performance Metrics")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total Time", f"{response.took_ms}ms")
                        
                        with col2:
                            st.metric("ES Time", f"{response.elasticsearch_took_ms}ms")
                        
                        with col3:
                            if response.reranking_took_ms:
                                st.metric("Reranking Time", f"{response.reranking_took_ms}ms")
                            else:
                                st.metric("Reranking", "Disabled")
                        
                        st.success("✅ Search completed successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Error during search: {str(e)}")
                        st.info("💡 Check your API keys and Elasticsearch connection")
    
    # Display configuration summary
    display_configuration_summary(config)
    
    # Footer with ZeroEntropy branding
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 40px 0; color: #666;">
        <p>🔁 Built with <a href="https://github.com/vagabond11/elastic-zeroentropy" style="color: #00d4ff;">elastic-zeroentropy</a></p>
        <p>Powered by <a href="https://zeroentropy.dev" style="color: #00d4ff;">ZeroEntropy</a> - The Engine For Human-Level Search</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main() 