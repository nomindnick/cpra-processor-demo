# CPRA Processing Application

A demonstration tool for processing California Public Records Act (CPRA) requests using local AI models for complete data privacy.

## Project Overview

This application showcases how open-source large language models can process CPRA requests locally, ensuring complete data privacy by never transmitting documents off-device. Built for demonstration to public agency representatives, it provides a complete workflow from email ingestion through document review and export.

### Key Features

- **Complete Offline Operation**: Works with network disabled for maximum privacy
- **Local AI Processing**: Uses Ollama with open-source models (no cloud dependencies)
- **Two-Pass Analysis**: Responsiveness determination + exemption identification
- **User Review Interface**: Manual override capabilities for all AI determinations
- **Professional Export**: PDF production and privilege logs
- **Real-time Processing Feedback**: Visual indicators for demo presentation

## Technical Architecture

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python with Ollama integration
- **AI Models**: Local LLMs (gemma3:latest, gpt-oss:20b, phi4-mini-reasoning:3.8b)
- **Environment**: Ubuntu laptop, CPU-only processing
- **Target Performance**: <16GB RAM usage, <5 minutes processing for 30 emails

## System Requirements

- Python 3.8 or higher
- Ollama installed with target models
- 8GB+ RAM (16GB+ recommended)
- Linux/Ubuntu environment

## Quick Start

### 1. Install Ollama and Models

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull gemma3:latest
ollama pull gpt-oss:20b  
ollama pull phi4-mini-reasoning:3.8b
```

### 2. Clone and Setup Project

```bash
git clone https://github.com/yourusername/cpra-processor-demo.git
cd cpra-processor-demo

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
# Test Ollama connectivity and models
python src/models/ollama_client.py

# Test email parsing
python test_parser.py

# Run unit tests
python -m pytest tests/ -v
```

### 4. Run Application

```bash
# Start Streamlit application (when implemented in Sprint 5)
streamlit run main.py
```

## Project Structure

```
cpra-processor-demo/
├── src/
│   ├── models/
│   │   └── ollama_client.py       # AI model integration
│   ├── parsers/
│   │   └── email_parser.py        # Email parsing logic
│   ├── processors/
│   │   ├── responsiveness_analyzer.py  # CPRA responsiveness analysis
│   │   └── exemption_analyzer.py       # Exemption identification
│   └── utils/
│       └── data_structures.py     # Core data models
├── tests/
│   └── test_email_parser.py       # Unit tests
├── data/
│   └── sample_emails/
│       └── test_emails.txt        # Sample email data
├── requirements.txt               # Python dependencies
├── PROGRESS_TRACKER.md           # Development progress
└── README.md                     # This file
```

## Development Status

### ✅ Sprint 0: Project Foundation (COMPLETED)
- [x] Project structure and dependencies
- [x] Ollama integration with 3 target models
- [x] Email parsing (Outlook export format)
- [x] Core data structures
- [x] Sample data (10 test emails)
- [x] Unit tests (15 tests, 100% passing)

### 🚧 Next Sprints (Planned)
- Sprint 1: Responsiveness Analysis Engine
- Sprint 2: Exemption Analysis Engine
- Sprint 3: User Review System
- Sprint 4: Export Generation
- Sprint 5: Streamlit Interface
- Sprint 6: Demo Mode Features
- Sprint 7: End-to-End Integration
- Sprint 8: Documentation and Polish

## Model Performance

Current test results for the three target models:

| Model | Size | Response Time | Status |
|-------|------|---------------|---------|
| gemma3:latest | 3.3GB | 5.4s | ✅ Fast, good quality |
| phi4-mini-reasoning:3.8b | 3.2GB | 9.6s | ✅ Medium speed, reasoning |
| gpt-oss:20b | 13GB | 21.6s | ✅ Slow, potentially highest quality |

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Test specific functionality
python -m pytest tests/test_email_parser.py -v

# Test Ollama connectivity
python src/models/ollama_client.py
```

## Sample Data

The application includes 10 synthetic test emails representing:

**Responsive Content** (6 emails):
- Roof leak issues and repairs
- Change order discussions  
- Project delay communications
- Structural analysis reports

**Non-Responsive Content** (4 emails):
- Holiday party planning
- Emergency system tests
- HVAC maintenance schedules
- Budget meetings

**Exemption Triggers**:
- Attorney-Client Privilege: Legal analysis communications
- Personnel Records: HR performance reviews
- Deliberative Process: Draft press releases

## CPRA Request Examples

The sample data is designed to work with these test CPRA requests:

1. "All documents regarding the roof leak issues on the Community Center construction project"
2. "All documents regarding Change Order #3 and the agency's decision to approve or deny it"  
3. "All internal communications about project delays between January and March 2024"

## Contributing

This is a demonstration project with a focused scope and timeline. Please see `PROGRESS_TRACKER.md` for current development status and upcoming milestones.

## License

This project is intended for demonstration and educational purposes. Please review with your legal team before using in production environments.

## Demo Day Checklist

- [ ] Airplane mode verification
- [ ] Model loading confirmation
- [ ] Sample data pre-loaded
- [ ] Processing time validation
- [ ] Export functionality tested
- [ ] Error recovery tested

## Support

For technical issues or questions about the implementation, please review:
1. `PROGRESS_TRACKER.md` for development status
2. Test files for usage examples
3. Source code comments for technical details

---

**Note**: This is a demonstration application built for the California Special District's Association presentation on local AI capabilities. It showcases the potential for privacy-preserving document processing using open-source tools.