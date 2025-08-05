# CPRA Processing Application - Technical Specification

## Project Overview

### Purpose
This application is a demonstration tool for the California Special District's Association presentation on local AI capabilities. It showcases how open-source large language models can process California Public Records Act (CPRA) requests locally, ensuring complete data privacy by never transmitting documents off-device.

### Demo Context
- **Target Audience**: Public agency representatives (non-technical)
- **Presentation Format**: Live demo with laptop in airplane mode
- **Timeline**: 1 week development, 2-3 days preferred
- **Repository**: Public GitHub repo for full transparency
- **Performance Target**: <16GB RAM usage to demonstrate laptop feasibility

### Key Demo Requirements
- **Complete Offline Operation**: Must work with network disabled
- **Visual Processing Feedback**: Real-time indicators showing AI work in progress
- **Professional Presentation**: Clean, polished interface suitable for legal professionals
- **Transparency**: Clean, well-commented code for public review

## Technical Architecture

### Core Stack
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python with Ollama integration
- **AI Models**: Local LLMs (Gemma 3, Llama 3.2 5.4B mini reasoning)
- **Environment**: Ubuntu laptop, CPU-only processing, 32GB RAM
- **Deployment**: Local development server

### System Requirements
- Python 3.8+
- Ollama installed with models pulled locally
- Streamlit
- Standard Python libraries (os, json, re, datetime, pathlib)
- PDF generation library (reportlab or similar)

## Core Functionality

### Data Processing Pipeline

#### Phase 1: Document Ingestion
- **Input**: Single text file containing multiple emails in Outlook export format
- **Processing**: Programmatic parsing to extract individual emails
- **Output**: Structured email objects with metadata (sender, recipient, subject, date, body)

#### Phase 2: Two-Pass AI Analysis

**Pass 1: Responsiveness Analysis**
- **Input**: CPRA requests (1-5 text requests) + individual email
- **AI Task**: Determine if email is responsive to any request
- **Output**: 
  - Responsive: Yes/No for each request
  - Confidence Score: High/Medium/Low
  - Reasoning: Text explanation of determination

**Pass 2: Exemption Analysis**
- **Input**: Email content + exemption definitions
- **AI Task**: Identify applicable CPRA exemptions
- **Target Exemptions**:
  - Attorney-Client Privilege
  - Personnel Records
  - Deliberative Process
- **Output**:
  - Applicable exemptions list
  - Confidence score for each
  - Reasoning for each determination

#### Phase 3: User Review & Export
- **Review Interface**: Document-by-document review with AI recommendations
- **User Actions**: Accept/modify AI determinations
- **Export Functions**:
  - PDF production of responsive, non-exempt documents
  - Privilege log of withheld documents with exemption justifications

### User Interface Requirements

#### Landing Page
- **Upload Area**: Drag-and-drop interface for email text file
- **Request Input**: Text boxes for up to 5 CPRA requests
- **Demo Data Option**: "Load Sample Data" button for backup/testing
- **Processing Controls**: Clear start button, demo mode toggle

#### Processing Interface (Demo Mode)
- **Real-time Visual Feedback**:
  - Progress bar with current document being processed
  - Live statistics counter (X of Y documents processed)
  - Current processing phase indicator ("Analyzing responsiveness...", "Checking exemptions...")
  - Processing time display
  - Model activity indicator (when AI is actively thinking)
- **System Resource Display**: Optional CPU/RAM usage visualization

#### Results Dashboard
- **Document Organization**:
  - Primary grouping: Responsive vs Non-Responsive
  - Secondary grouping: Exemptions Apply vs No Exemptions
  - Tertiary grouping: Confidence levels (High/Medium/Low)
- **Summary Statistics**:
  - Total documents processed
  - Responsive document count
  - Exemption breakdown
  - Review completion status

#### Document Review Interface
- **Document Display**: Clean, readable email presentation in side panel
- **AI Analysis Display**: Clear presentation of AI reasoning and confidence
- **Review Controls**: 
  - Quick accept/reject buttons
  - Manual override options for responsiveness and exemptions
  - "Mark as Reviewed" confirmation
- **Navigation**: Easy movement between documents, filtering options

#### Export Interface
- **Pre-Export Summary**: Final document counts and exemption breakdown
- **Export Options**:
  - Production PDF (responsive, non-exempt documents)
  - Privilege log generation
  - Processing summary report

## Data Specifications

### Email Format Requirements
- **Standard Outlook Export Format**: Consistent header structure
- **Required Fields**: From, To, Date, Subject, Body
- **Chain Threading**: Clear reply/forward indicators
- **Timestamp Format**: Consistent datetime formatting

### Synthetic Email Dataset (30 emails initial)
- **Project Context**: Municipal construction project with delays and change orders
- **Participants**:
  - City agency staff (project managers, engineers)
  - Construction contractor representatives
  - Legal counsel (city attorney, contractor legal)
  - Consultants and subcontractors

### CPRA Request Examples
- **Request 1**: "All documents regarding the roof leak issues on the Community Center construction project"
- **Request 2**: "All documents regarding Change Order #3 and the agency's decision to approve or deny it"
- **Request 3**: "All internal communications about project delays between January and March 2024"

### Email Content Distribution
- **Responsive Documents**: ~60% of emails
- **Non-Responsive**: ~40% of emails
- **Privilege/Exemption Triggers**: ~30% of total emails
- **Email Types**:
  - Individual emails: ~70%
  - Email chains (2-4 emails): ~30%

## Technical Implementation Requirements

### Model Integration
- **Ollama API Integration**: Direct local API calls
- **Prompt Engineering**: 
  - Structured prompts with clear examples
  - JSON output formatting for consistent parsing
  - Few-shot examples for each analysis type
  - Temperature optimization for consistency

### Error Handling
- **File Processing**: Graceful handling of malformed emails
- **Model Communication**: Timeout handling, retry logic
- **User Input**: Validation for CPRA requests and file uploads
- **Demo Continuity**: Fallback modes for live presentation

### Performance Optimization
- **Memory Management**: Efficient handling of email dataset
- **Processing Efficiency**: Batch processing where possible
- **User Experience**: Progress feedback and responsive UI during processing

## Demo-Specific Features

### Demo Mode Enhancements
- **Processing Visualization**: Real-time indication of AI work
- **Transparency Features**: Clear explanation of each processing step
- **Performance Metrics**: Processing time and resource usage display
- **Airplane Mode Verification**: Clear offline status indication

### Presentation Integration
- **Quick Setup**: Fast application startup for live demo
- **Reliable Operation**: Robust error handling for presentation environment
- **Visual Appeal**: Professional interface suitable for legal audience
- **Clear Results**: Easy-to-understand output for non-technical viewers

## Success Criteria

### Functional Requirements
- Successfully parses email text file into individual emails
- Accurately identifies responsive documents based on CPRA requests
- Correctly flags documents with privilege/exemption issues
- Enables user review and modification of AI determinations
- Generates clean PDF output and privilege log

### Demo Requirements
- **Processing Time**: <5 minutes for 30 emails (target: 2-3 minutes)
- **Accuracy**: High success rate on designed test cases
- **User Experience**: Intuitive interface requiring minimal explanation
- **Visual Impact**: Impressive real-time processing display
- **Resource Efficiency**: Demonstrates feasibility on standard hardware

### Quality Standards
- **Code Quality**: Clean, well-commented code suitable for public repository
- **Documentation**: Clear README with setup and usage instructions
- **Transparency**: Full disclosure of demo guardrails and methodology
- **Professional Polish**: Interface quality appropriate for legal professional audience

## Constraints and Assumptions

### Technical Constraints
- **CPU-Only Processing**: No GPU acceleration available
- **Local Models Only**: No internet connectivity during demo
- **Hardware Limits**: 32GB RAM, decent CPU performance
- **Development Time**: Maximum 1 week, preferably 2-3 days

### Demo Constraints
- **Simplified Scope**: Focus on core functionality over edge cases
- **Designed Data**: Synthetic emails optimized for reliable processing
- **Limited Exemptions**: Focus on 3 easily-identifiable exemption types
- **Live Presentation**: Must be robust enough for real-time demonstration

### Quality Expectations
- **Functional Demo**: Real processing, not pre-recorded results
- **Professional Appearance**: Suitable for legal professional audience
- **Public Code**: Clean enough for GitHub publication
- **Educational Value**: Clear demonstration of local AI capabilities

## Next Steps
1. Create detailed implementation plan with development phases
2. Design email generation specification
3. Begin development with Sprint 0 (project setup)
4. Iterative development and testing with synthetic data
5. Final demo preparation and rehearsal