#!/bin/bash

# Elastic-ZeroEntropy Demo Runner
echo "🔁 Starting Elastic-ZeroEntropy Demo UI..."

# Check if we're in the right directory
if [ ! -f "examples/demo_ui.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected files: examples/demo_ui.py"
    exit 1
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "📦 Installing demo dependencies..."
    pip install -r examples/requirements_demo.txt
fi

# Run the demo
echo "🚀 Launching demo UI..."
echo "📱 Open your browser to: http://localhost:8501"
echo "⏹️  Press Ctrl+C to stop the demo"
echo ""

cd examples
streamlit run demo_ui.py --server.port 8501 --server.headless false 