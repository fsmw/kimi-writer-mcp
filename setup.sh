#!/bin/bash
# Quick setup script for Kimi Writer MCP Server

echo "🚀 Setting up Kimi Writer MCP Server..."
echo "========================================"

# Check if we're in the right directory
if [ ! -f "mcp-server.py" ]; then
    echo "❌ Please run this script from the kimi-writer-mcp directory"
    exit 1
fi

echo "📁 Current directory: $(pwd)"

# Install MCP dependencies
echo "📦 Installing MCP server dependencies..."
pip install -r requirements.txt

# Install extended dependencies for PDF/EPUB
echo "📦 Installing extended dependencies (PDF/EPUB)..."
pip install -r requirements-extended.txt

# Check Kimi Writer directory
echo "🔍 Checking Kimi Writer directory..."
if [ -d "../kimi-writer" ]; then
    echo "✅ Kimi Writer found at ../kimi-writer"
    
    # Install Kimi Writer dependencies
    echo "📦 Installing Kimi Writer dependencies..."
    cd ../kimi-writer
    pip install -r requirements.txt
    cd ../kimi-writer-mcp
    echo "✅ Kimi Writer dependencies installed"
else
    echo "❌ Kimi Writer not found at ../kimi-writer"
    echo "   Please ensure Kimi Writer is in the parent directory"
fi

# Test the installation
echo "🧪 Testing installation..."
python start.py --check

echo ""
echo "🎉 Setup completed!"
echo ""
echo "📋 Next steps:"
echo "   1. Test the server: python test-client.py"
echo "   2. Test document generation: python test-documents.py"
echo "   3. Start the server: python mcp-server.py"
echo ""
echo "📚 For more information, see README.md"