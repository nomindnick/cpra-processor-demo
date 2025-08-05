#!/bin/bash

# CPRA Processor Demo - Quick Launch Script
# This script launches the demo application with optimal settings

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

clear

echo "================================================"
echo "     CPRA Processor Demo - Quick Launch"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found!"
    print_info "Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Check if Ollama is running
print_status "Checking Ollama service..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_status "Ollama service is running"
else
    print_warning "Ollama service not detected. Starting Ollama..."
    # Try to start Ollama in background
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!
    sleep 3
    
    # Check again
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_status "Ollama service started (PID: $OLLAMA_PID)"
    else
        print_error "Failed to start Ollama service"
        print_info "Please start Ollama manually: ollama serve"
        exit 1
    fi
fi

# Check for required model
print_status "Checking for required AI model..."
if ollama list 2>/dev/null | grep -q "gemma3:latest"; then
    print_status "Primary model (gemma3) is available"
else
    print_error "Primary model (gemma3) not found!"
    print_info "Pulling model (this may take a few minutes)..."
    ollama pull gemma3:latest
fi

# Check network status
print_info "Checking network status..."
if ping -c 1 google.com > /dev/null 2>&1; then
    print_warning "Network is active. For demo, consider enabling airplane mode."
else
    print_status "Network appears to be offline (good for demo!)"
fi

# Clear any previous session data (optional)
read -p "Clear previous session data? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Clearing previous sessions..."
    rm -f sessions/*.json 2>/dev/null || true
    rm -f exports/*.pdf 2>/dev/null || true
    print_status "Previous data cleared"
fi

# Set demo environment variables
export CPRA_DEMO_MODE=true
export CPRA_MODEL_NAME="gemma3:latest"
export CPRA_DEMO_SPEED=1.0

echo ""
echo "================================================"
echo "           Launching Application"
echo "================================================"
echo ""

print_info "Opening browser at http://localhost:8501"
print_info "Press Ctrl+C to stop the application"
echo ""

# Launch Streamlit with optimized settings
streamlit run main.py \
    --server.port 8501 \
    --server.address localhost \
    --server.headless true \
    --browser.gatherUsageStats false \
    --theme.primaryColor "#0068C9" \
    --theme.backgroundColor "#FFFFFF" \
    --theme.secondaryBackgroundColor "#F0F2F6" \
    --theme.textColor "#262730"

# Cleanup on exit
if [ ! -z "$OLLAMA_PID" ]; then
    print_info "Stopping Ollama service..."
    kill $OLLAMA_PID 2>/dev/null || true
fi