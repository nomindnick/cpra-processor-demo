# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a CPRA (California Public Records Act) Processing Application - a demonstration tool for the California Special District's Association presentation on local AI capabilities. It showcases how open-source large language models can process CPRA requests locally, ensuring complete data privacy by never transmitting documents off-device.

**Demo Context:**
- **Target Audience**: Public agency representatives (non-technical)
- **Presentation Format**: Live demo with laptop in airplane mode
- **Performance Target**: <16GB RAM usage, <5 minutes processing for 30 emails
- **Repository**: Public GitHub repo for full transparency

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Testing
```bash
# Run all unit tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_email_parser.py -v

# Test email parser functionality
python test_parser.py

# Test Ollama connectivity and models
python src/models/ollama_client.py
```

### Application Execution
```bash
# Run main Streamlit application
streamlit run main.py

# Test individual components
python src/parsers/email_parser.py
python src/models/ollama_client.py
```

### Required Ollama Models
Before running the application, ensure these models are available:
```bash
ollama pull gemma3:latest
ollama pull gpt-oss:20b
ollama pull phi4-mini-reasoning:3.8b
```

## Architecture Overview

### Core Components

**Email Processing Pipeline:**
1. `src/parsers/email_parser.py` - Parses Outlook export format emails into structured Email objects
2. `src/models/ollama_client.py` - Handles AI model interactions for responsiveness and exemption analysis
3. `src/utils/data_structures.py` - Defines core data models (Email, ResponsivenessAnalysis, ExemptionAnalysis, etc.)

**Processing Flow:**
1. Email ingestion from Outlook export format
2. Two-pass AI analysis: responsiveness determination + exemption identification
3. User review interface for manual overrides
4. Export generation (planned for future sprints)

### Key Data Structures

- **Email**: Core email representation with parsing metadata
- **ResponsivenessAnalysis**: AI analysis results for CPRA request responsiveness
- **ExemptionAnalysis**: AI analysis for potential exemptions (attorney-client privilege, personnel records, deliberative process)
- **DocumentReview**: User review decisions and overrides
- **ProcessingSession**: Complete session state management

### AI Model Integration

The application supports three target models with different performance characteristics:
- `gemma3:latest` (3.3GB) - Fast, 5.4s response time
- `phi4-mini-reasoning:3.8b` (3.2GB) - Medium speed, 9.6s response time with reasoning capabilities  
- `gpt-oss:20b` (13GB) - Slower, 21.6s response time but potentially highest quality

All AI interactions use structured prompting with JSON response formats for reliable parsing. The system implements:
- **Two-Pass Analysis**: First pass for responsiveness determination, second pass for exemption identification
- **Prompt Engineering**: Structured prompts with clear examples and few-shot examples for consistent output
- **Temperature Optimization**: Optimized for consistency (typically 0.2-0.3 for analysis tasks)

## Development Guidelines

### Sprint-Based Development Philosophy
This project follows an 8-sprint incremental development approach:
- **Testing-First Approach**: Build with small synthetic dataset, expand once proven
- **One Sprint at a Time**: Complete all deliverables before proceeding to next sprint
- **Quality Focus**: Clean, documented code suitable for public GitHub repository
- **Progress Tracking**: Maintain detailed progress tracker (`PROGRESS_TRACKER.md`) for context continuity

### Core Implementation Guidelines

**Email Parser (`src/parsers/email_parser.py`)**
- Handles multiple email separation strategies for Outlook exports
- Creates robust Email objects even when parsing fails (with error tracking)
- Uses regex patterns for header extraction and flexible body parsing
- Must handle standard Outlook export format with From, To, Date, Subject, Body fields

**Ollama Client (`src/models/ollama_client.py`)**
- Implements structured prompting for consistent JSON responses
- Provides methods for both responsiveness and exemption analysis
- Includes comprehensive error handling and timeout management
- Uses retry logic for model communication failures

**Error Handling Philosophy**
- Fail gracefully with clear user messaging
- Provide fallback options where possible
- Prioritize demo continuity over perfect error recovery
- Log errors for debugging without exposing technical details to users

**Data Consistency**
- All analysis results link to emails via message_id or email index
- Timestamps and processing metadata tracked throughout pipeline
- Failed operations create trackable objects rather than silent failures

## Sample Data & CPRA Requests

The synthetic email dataset represents a municipal construction project with delays and change orders:

**Project Context**: Community Center construction project with:
- City agency staff (project managers, engineers)
- Construction contractor representatives  
- Legal counsel (city attorney, contractor legal)
- Consultants and subcontractors

**Email Distribution**:
- **Responsive Documents**: ~60% of emails
- **Non-Responsive**: ~40% of emails  
- **Privilege/Exemption Triggers**: ~30% of total emails
- **Individual emails**: ~70%, **Email chains**: ~30%

**Target CPRA Requests**:
1. "All documents regarding the roof leak issues on the Community Center construction project"
2. "All documents regarding Change Order #3 and the agency's decision to approve or deny it"  
3. "All internal communications about project delays between January and March 2024"

**Content Types**:
- **Responsive content**: Roof issues, change orders, project delays, structural reports
- **Non-responsive content**: Holiday planning, system tests, maintenance, budget meetings  
- **Exemption triggers**: Attorney-client privilege, personnel records, deliberative process

## Development Sprint Plan

### Phase 1: Backend Core Processing
- **Sprint 1**: Responsiveness Analysis Engine - CPRA request matching with confidence scoring
- **Sprint 2**: Exemption Analysis Engine - Attorney-client privilege, personnel records, deliberative process

### Phase 2: Backend Data Management  
- **Sprint 3**: User Review System - Override functionality and review state tracking
- **Sprint 4**: Export Generation - PDF production and privilege log creation

### Phase 3: Frontend Development
- **Sprint 5**: Core Streamlit Interface - File upload, document review, results dashboard
- **Sprint 6**: Demo Mode Features - Real-time processing visualization for presentation impact

### Phase 4: Integration and Polish
- **Sprint 7**: End-to-End Integration - Complete workflow testing and error handling
- **Sprint 8**: Demo Preparation - Documentation, sample data loading, GitHub repository prep

**Current Status**: Sprint 0 (COMPLETED) - Foundation with Ollama integration, email parsing, core data structures, and unit tests

## Demo Mode Requirements

### Visual Processing Features
- **Real-time Processing Indicators**: Progress bars, live statistics counter, processing phase indicators
- **Model Activity Visualization**: Clear indication when AI is actively analyzing documents
- **Processing Time Display**: Live timing for demo impact
- **System Resource Monitoring**: Optional CPU/RAM usage visualization
- **Airplane Mode Verification**: Clear offline status indication for presentation

### User Interface Requirements
- **Professional Appearance**: Clean interface suitable for legal professional audience
- **Document Organization**: Primary grouping by responsive/non-responsive, secondary by exemptions, tertiary by confidence
- **Intuitive Navigation**: Minimal explanation required for non-technical audience
- **Export Interface**: Pre-export summary, production PDF, privilege log generation

## Testing Strategy & Performance Targets

### Quality Standards
- Unit tests focus on email parsing functionality (15 tests, 100% passing)
- Integration tests verify Ollama model connectivity and response parsing
- Sample data provides realistic test scenarios for CPRA request processing
- Error handling tests ensure graceful failure modes
- End-to-end testing with complete 30-email dataset

### Performance Requirements
- **Memory Usage**: <16GB RAM (demonstrates laptop feasibility)
- **Processing Time**: <5 minutes for 30 emails (target: 2-3 minutes for demo)
- **Offline Operation**: Complete functionality without network access (after model downloads)
- **Demo Reliability**: Must work consistently in presentation environment

### Key Metrics to Track
- Processing performance (time per email, total processing time)
- Memory usage (peak RAM consumption)
- Model accuracy (success rate on designed test cases)
- Error rates (frequency and types of processing errors)