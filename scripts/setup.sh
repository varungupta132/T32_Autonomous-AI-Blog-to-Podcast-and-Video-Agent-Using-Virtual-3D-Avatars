#!/bin/bash

# Setup script for AI Blog-to-Podcast Generator

echo "=================================="
echo "AI Blog-to-Podcast Generator Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if Ollama is installed
echo ""
echo "Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is installed"
    ollama --version
else
    echo "✗ Ollama not found"
    echo "Please install from: https://ollama.com/download"
    exit 1
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Pull default model
echo ""
echo "Pulling default AI model (llama2)..."
ollama pull llama2

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p audio_segments
mkdir -p final_podcasts

echo ""
echo "=================================="
echo "Setup complete!"
echo "=================================="
echo ""
echo "Run the application:"
echo "  python web_podcast_ollama.py"
echo ""
