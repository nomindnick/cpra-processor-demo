# CPRA Processing Application

A demonstration tool for processing California Public Records Act (CPRA) requests using local AI models, ensuring complete data privacy through on-device processing.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.28%2B-red)
![Ollama](https://img.shields.io/badge/ollama-required-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

## 🎯 Project Overview

This application demonstrates how public agencies can leverage open-source large language models to process CPRA requests while maintaining complete data privacy. Built for the California Special District's Association presentation, it showcases a complete workflow from email ingestion through document review and export—all running locally without any cloud dependencies.

### ✨ Key Features

- **🔒 Complete Offline Operation**: Works in airplane mode for maximum privacy
- **🤖 Local AI Processing**: Uses Ollama with open-source models (no cloud APIs)
- **📊 Two-Pass Analysis**: Intelligent responsiveness determination + exemption identification
- **👤 User Review Interface**: Manual override capabilities for all AI determinations
- **📄 Professional Export**: PDF production, privilege logs, and processing reports
- **🎭 Demo Mode**: Real-time processing visualization for presentations
- **⚡ Performance Optimized**: <16GB RAM usage, <5 minutes for 30 emails

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- 8GB+ RAM (16GB recommended)
- Ubuntu/Linux (macOS and Windows with WSL also supported)
- Internet connection for initial setup only

### 1. Install Ollama

```bash
# Linux/macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation
ollama --version
```

### 2. Download AI Models

```bash
# Primary model (fast, 3.3GB)
ollama pull gemma3:latest

# Alternative models (optional)
ollama pull gpt-oss:20b          # Higher quality, 13GB
ollama pull phi4-mini-reasoning:3.8b  # Reasoning capabilities, 3.2GB
```

### 3. Clone and Setup

```bash
# Clone repository
git clone https://github.com/yourusername/cpra-processor-demo.git
cd cpra-processor-demo

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Launch Application

```bash
# Start the Streamlit application
streamlit run main.py

# Application will open at http://localhost:8501
```

## 📖 Usage Guide

### Basic Workflow

1. **Upload Documents**
   - Click "Load Demo Data" for pre-configured test data
   - Or upload your own email export file (Outlook format)

2. **Enter CPRA Requests**
   - Input 1-5 CPRA requests in the text boxes
   - Or use the sample requests provided

3. **Process Documents**
   - Click "Start Processing" to begin AI analysis
   - Watch real-time progress in demo mode
   - Processing includes:
     - Email parsing and validation
     - Responsiveness determination
     - Exemption identification

4. **Review Results**
   - Review AI determinations document by document
   - Override any incorrect classifications
   - Apply batch approvals for efficiency

5. **Export Results**
   - Generate production PDF of responsive documents
   - Create privilege log for withheld documents
   - Save session for later review

### Demo Mode Features

Enable demo mode in the sidebar for presentation features:
- 🎬 Real-time processing animations
- 📊 Live resource monitoring
- ⚡ Processing speed control (0.5x to 3x)
- 🔔 Visual AI activity indicators
- ✈️ Airplane mode verification

### Navigation

The application uses a multi-page structure:
- **📤 Upload**: File upload and request input
- **⚙️ Processing**: Real-time analysis visualization
- **📊 Results**: Document grouping and statistics
- **👁️ Review**: Document-by-document review interface
- **💾 Export**: Generate outputs and save sessions

## 🏗️ Architecture

### Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python with modular architecture
- **AI Models**: Ollama with local LLMs
- **PDF Generation**: ReportLab
- **Resource Monitoring**: psutil

### Project Structure

```
cpra-processor-demo/
├── main.py                    # Streamlit application entry point
├── src/
│   ├── config/               # Configuration management
│   │   └── app_config.py    # Centralized settings
│   ├── models/              # AI model integration
│   │   └── ollama_client.py
│   ├── parsers/             # Document parsing
│   │   └── email_parser.py
│   ├── processors/          # Core processing logic
│   │   ├── cpra_analyzer.py      # CPRA analysis engine
│   │   ├── review_manager.py     # Review state management
│   │   ├── session_manager.py    # Session persistence
│   │   └── export_manager.py     # Export generation
│   ├── utils/               # Utilities and data structures
│   │   ├── data_structures.py    # Core data models
│   │   ├── demo_utils.py        # Demo mode utilities
│   │   ├── pdf_generator.py     # PDF creation
│   │   └── privilege_log.py     # Privilege log generation
│   └── components/          # UI components
│       └── resource_monitor.py   # System monitoring
├── tests/                   # Unit and integration tests
├── demo-files/             # Demo data and documentation
│   ├── synthetic_emails.txt     # 30 sample emails
│   ├── cpra_requests.txt       # Sample CPRA requests
│   └── demo_cpra_requests.md   # Demo guide
├── sessions/               # Saved session files
├── exports/                # Generated export files
└── requirements.txt        # Python dependencies
```

## 🧪 Testing

### Run Tests

```bash
# Run all unit tests
python -m pytest tests/ -v

# Test specific component
python -m pytest tests/test_email_parser.py -v

# Test Ollama connectivity
python src/models/ollama_client.py

# End-to-end test with demo data
python test_end_to_end.py
```

### Test Coverage

- ✅ 83+ unit tests with 100% pass rate
- ✅ Email parsing (15 tests)
- ✅ CPRA analysis (20 tests)
- ✅ Exemption detection (17 tests)
- ✅ Review management (10 tests)
- ✅ Export generation (14 tests)
- ✅ Integration tests (7 tests)

## 📊 Performance

### Model Comparison

| Model | Size | Response Time | Quality | RAM Usage |
|-------|------|--------------|---------|-----------|
| gemma3:latest | 3.3GB | 5-10s | Good | ~4GB |
| phi4-mini-reasoning:3.8b | 3.2GB | 10-15s | Good + Reasoning | ~4GB |
| gpt-oss:20b | 13GB | 20-30s | Highest | ~14GB |

### Processing Benchmarks

- **30 emails**: 2-4 minutes (with gemma3)
- **Memory usage**: <8GB typical, <16GB peak
- **Accuracy**: >90% on test dataset
- **Export time**: <30 seconds

## 🛠️ Configuration

### Environment Variables

```bash
# Model configuration
export CPRA_MODEL_NAME="gemma3:latest"
export CPRA_MODEL_TEMPERATURE="0.2"
export CPRA_MODEL_MAX_TOKENS="800"

# Processing configuration
export CPRA_BATCH_SIZE="5"
export CPRA_PROCESSING_TIMEOUT="30"

# Demo mode
export CPRA_DEMO_MODE="true"
export CPRA_DEMO_SPEED="1.0"
```

### Configuration File

Edit `src/config/app_config.py` for advanced settings:
- Model parameters
- Processing timeouts
- Batch sizes
- Export formats
- Demo mode defaults

## 🐛 Troubleshooting

### Common Issues

**Ollama Connection Error**
```bash
# Check if Ollama is running
ollama list

# Restart Ollama service
systemctl restart ollama  # Linux
brew services restart ollama  # macOS
```

**Model Not Found**
```bash
# List available models
ollama list

# Pull missing model
ollama pull gemma3:latest
```

**Memory Issues**
- Reduce batch size in configuration
- Use smaller model (gemma3 instead of gpt-oss:20b)
- Close other applications

**Slow Processing**
- Ensure no other CPU-intensive tasks running
- Try gemma3 model for faster processing
- Reduce number of concurrent requests

## 📚 Demo Guide

### Pre-Demo Checklist

- [ ] Enable airplane mode to demonstrate offline capability
- [ ] Verify Ollama models are loaded
- [ ] Load demo data (30 emails, 3 CPRA requests)
- [ ] Enable demo mode in sidebar
- [ ] Test processing with sample data
- [ ] Clear any previous sessions

### Presentation Flow

1. **Introduction** (2 min)
   - Show airplane mode status
   - Explain privacy benefits of local processing

2. **Data Upload** (1 min)
   - Load demo emails
   - Show CPRA requests

3. **Processing Demo** (3-4 min)
   - Start processing with demo mode
   - Highlight real-time indicators
   - Show resource usage

4. **Results Review** (2 min)
   - Navigate dashboard
   - Demonstrate filtering
   - Show confidence levels

5. **Export** (1 min)
   - Generate production PDF
   - Create privilege log
   - Save session

### Key Talking Points

- ✅ Complete offline operation (no cloud dependencies)
- ✅ AI identifies responsive documents based on content, not just keywords
- ✅ Automatic flagging of exemptions (attorney-client, personnel, deliberative)
- ✅ Human remains in control with override capabilities
- ✅ Professional outputs suitable for legal compliance
- ✅ Runs on standard hardware (no special requirements)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/cpra-processor-demo.git
cd cpra-processor-demo

# Create development branch
git checkout -b feature/your-feature

# Install in development mode
pip install -e .

# Run tests before committing
python -m pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- California Special District's Association for the opportunity to demonstrate
- Ollama team for making local LLMs accessible
- Streamlit for the excellent web framework
- Open-source AI community for the models

## ⚠️ Disclaimer

This is a demonstration application built for educational purposes. While it showcases the potential for privacy-preserving document processing, please consult with your legal team before using in production environments. The AI determinations should always be reviewed by qualified personnel for accuracy and legal compliance.

## 📞 Support

For technical questions or issues:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review [demo-files/demo_cpra_requests.md](demo-files/demo_cpra_requests.md) for demo guidance
3. See [PROGRESS_TRACKER.md](PROGRESS_TRACKER.md) for development details
4. Open an issue on GitHub for bugs or feature requests

---

**Built with ❤️ for public agencies seeking privacy-preserving AI solutions**