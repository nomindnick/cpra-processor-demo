#!/bin/bash

# CPRA Processor Demo - Setup Script
# This script sets up the complete environment for the CPRA Processor Demo

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

echo "================================================"
echo "   CPRA Processor Demo - Environment Setup"
echo "================================================"
echo ""

# Check Python version
print_status "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
    PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        print_status "Python $PYTHON_VERSION found (3.8+ required)"
    else
        print_error "Python 3.8+ required, found $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check for Ollama
print_status "Checking for Ollama..."
if command -v ollama &> /dev/null; then
    print_status "Ollama is installed"
else
    print_warning "Ollama not found. Installing..."
    curl -fsSL https://ollama.ai/install.sh | sh
    if [ $? -eq 0 ]; then
        print_status "Ollama installed successfully"
    else
        print_error "Failed to install Ollama"
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt --quiet
print_status "Dependencies installed"

# Check and pull Ollama models
print_status "Checking Ollama models..."

check_and_pull_model() {
    MODEL=$1
    if ollama list | grep -q "$MODEL"; then
        print_status "Model $MODEL already available"
    else
        print_warning "Pulling model $MODEL (this may take a few minutes)..."
        ollama pull $MODEL
        if [ $? -eq 0 ]; then
            print_status "Model $MODEL pulled successfully"
        else
            print_error "Failed to pull model $MODEL"
            return 1
        fi
    fi
}

# Pull required models
check_and_pull_model "gemma3:latest"

# Optional models (don't fail if these don't work)
print_status "Checking optional models..."
check_and_pull_model "phi4-mini-reasoning:3.8b" || print_warning "Optional model phi4-mini-reasoning not available"
check_and_pull_model "gpt-oss:20b" || print_warning "Optional model gpt-oss:20b not available"

# Create necessary directories
print_status "Creating project directories..."
mkdir -p sessions exports data/sample_emails

# Test Ollama connectivity
print_status "Testing Ollama connectivity..."
python3 -c "
import sys
sys.path.insert(0, '.')
from src.models.ollama_client import OllamaClient
client = OllamaClient()
if client.test_connectivity():
    print('Ollama connectivity test passed')
    sys.exit(0)
else:
    print('Ollama connectivity test failed')
    sys.exit(1)
" || {
    print_warning "Ollama connectivity test failed. Make sure Ollama service is running."
    print_warning "Try: ollama serve"
}

# Run tests
print_status "Running unit tests..."
python -m pytest tests/ -v --tb=short -q || print_warning "Some tests failed. Check test output for details."

# Verify demo data
print_status "Verifying demo data..."
if [ -f "demo-files/synthetic_emails.txt" ] && [ -f "demo-files/cpra_requests.txt" ]; then
    print_status "Demo data files found"
else
    print_error "Demo data files missing"
fi

echo ""
echo "================================================"
echo "             Setup Complete!"
echo "================================================"
echo ""
echo "To start the application:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the application:"
echo "     streamlit run main.py"
echo ""
echo "Or use the quick launcher:"
echo "     ./demo.sh"
echo ""
print_status "Setup completed successfully!"