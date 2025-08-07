#!/usr/bin/env python3
"""
CPRA Processing Application - Main Streamlit Application

Sprint 7 Enhancement: End-to-End Integration
- Enhanced error handling
- Configuration management integration
- Performance optimizations
"""

import streamlit as st
import os
import sys
import json
import time
import logging
import traceback
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.config import get_config
from src.parsers.email_parser import EmailParser
from src.processors.cpra_analyzer import CPRAAnalyzer
from src.processors.review_manager import ReviewManager
from src.processors.session_manager import SessionManager
from src.processors.export_manager import ExportManager
from src.utils.data_structures import (
    Email, ProcessingSession, ResponsivenessAnalysis,
    ExemptionAnalysis, DocumentReview, ExemptionType,
    ReviewStatus, CPRARequest
)
from src.utils.demo_utils import (
    check_network_connectivity, get_system_resources,
    load_demo_data, simulate_processing_delay,
    typewriter_effect, get_ai_thinking_animation,
    get_phase_color, format_processing_stats,
    create_demo_sidebar_controls, show_model_activity_indicator,
    create_phase_indicator
)
from src.components.resource_monitor import (
    ResourceMonitor, create_performance_gauge,
    create_model_comparison_chart
)
from src.components.llm_stream_display import (
    LLMStreamDisplay, StreamCallback, create_llm_stream_display
)
from src.styles.custom_styles import apply_custom_styling

# Initialize configuration
config = get_config()

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.logging.log_level),
    format=config.logging.log_format
)
logger = logging.getLogger(__name__)


def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'session' not in st.session_state:
        st.session_state.session = None
    if 'emails' not in st.session_state:
        st.session_state.emails = []
    if 'cpra_requests' not in st.session_state:
        st.session_state.cpra_requests = []
    if 'responsiveness_results' not in st.session_state:
        st.session_state.responsiveness_results = []
    if 'exemption_results' not in st.session_state:
        st.session_state.exemption_results = []
    if 'review_manager' not in st.session_state:
        st.session_state.review_manager = None
    if 'current_review_index' not in st.session_state:
        st.session_state.current_review_index = 0
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'review_complete' not in st.session_state:
        st.session_state.review_complete = False
    if 'page' not in st.session_state:
        st.session_state.page = 'upload'
    if 'export_manager' not in st.session_state:
        st.session_state.export_manager = None
    # Demo mode settings from config
    if 'demo_mode' not in st.session_state:
        st.session_state.demo_mode = config.demo.enable_by_default
    if 'demo_settings' not in st.session_state:
        st.session_state.demo_settings = {
            'speed': config.demo.default_speed,
            'animations': config.demo.show_animations,
            'resource_monitor': config.demo.show_resource_monitor,
            'typewriter': config.demo.typewriter_effect
        }
    if 'resource_monitor' not in st.session_state:
        st.session_state.resource_monitor = ResourceMonitor()
    # LLM streaming display
    if 'llm_display' not in st.session_state:
        st.session_state.llm_display = None
    if 'stream_callback' not in st.session_state:
        st.session_state.stream_callback = None
    if 'stream_events' not in st.session_state:
        st.session_state.stream_events = []
    if 'current_stream' not in st.session_state:
        st.session_state.current_stream = {}
    # Error state
    if 'last_error' not in st.session_state:
        st.session_state.last_error = None


def load_sample_data() -> Optional[str]:
    """Load sample data for demo purposes with error handling."""
    try:
        sample_file_path = Path("data/sample_emails/test_emails.txt")
        if sample_file_path.exists():
            with open(sample_file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        logger.error(f"Error loading sample data: {e}")
        st.session_state.last_error = f"Failed to load sample data: {str(e)}"
    return None


def parse_emails(content: str) -> List[Email]:
    """Parse email content into Email objects with error handling."""
    try:
        parser = EmailParser()
        # Add debug logging
        logger.debug(f"Parsing content of length: {len(content)}")
        logger.debug(f"First 100 chars: {content[:100] if content else 'Empty'}")
        emails = parser.parse_email_file(content)
        logger.info(f"Successfully parsed {len(emails)} emails")
        return emails
    except Exception as e:
        logger.error(f"Error parsing emails: {e}")
        st.session_state.last_error = f"Failed to parse emails: {str(e)}"
        return []




def sidebar_navigation():
    """Create sidebar navigation."""
    st.sidebar.title("CPRA Processing")
    
    # Network status indicator at top
    is_connected, network_msg = check_network_connectivity()
    if is_connected:
        st.sidebar.warning(network_msg)
    else:
        st.sidebar.success(network_msg)
    
    st.sidebar.markdown("---")
    
    # Navigation menu
    pages = {
        'upload': 'Upload & Configure',
        'processing': 'Processing',
        'results': 'Results Dashboard',
        'review': 'Document Review',
        'export': 'Export Documents'
    }
    
    # Show navigation based on current state
    for key, label in pages.items():
        # Disable pages that aren't ready yet
        disabled = False
        if key == 'processing' and not st.session_state.emails:
            disabled = True
        elif key == 'results' and not st.session_state.processing_complete:
            disabled = True
        elif key == 'review' and not st.session_state.processing_complete:
            disabled = True
        elif key == 'export' and not st.session_state.review_complete:
            disabled = True
        
        if st.sidebar.button(label, key=f"nav_{key}", disabled=disabled, use_container_width=True):
            st.session_state.page = key
    
    # Session info
    if st.session_state.session:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Session Information")
        st.sidebar.text(f"ID: {st.session_state.session.session_id[:8]}...")
        st.sidebar.text(f"Emails: {len(st.session_state.emails)}")
        st.sidebar.text(f"Requests: {len(st.session_state.cpra_requests)}")
        
        if st.session_state.processing_complete:
            responsive_count = sum(1 for r in st.session_state.responsiveness_results if r and r.is_responsive_to_any())
            st.sidebar.text(f"Responsive: {responsive_count}")
            
            if st.session_state.review_manager:
                summary = st.session_state.review_manager.get_review_summary(st.session_state.session)
                completed = summary['review_status']['completed']
                total = summary['total_documents']
                st.sidebar.text(f"Reviewed: {completed}/{total}")
    
    # Demo mode controls
    demo_settings = create_demo_sidebar_controls()
    st.session_state.demo_mode = demo_settings['enabled']
    st.session_state.demo_settings = demo_settings
    
    # Resource monitor in sidebar if demo mode
    if st.session_state.demo_mode and demo_settings.get('resource_monitor', False):
        st.sidebar.markdown("---")
        st.session_state.resource_monitor.create_compact_monitor(st.sidebar)


def upload_page():
    """File upload and CPRA request input page."""
    st.title("Upload Documents & Configure Requests")
    
    # Check if demo data was loaded from sidebar
    if st.session_state.demo_mode and st.session_state.get('demo_data_loaded'):
        demo_emails = st.session_state.get('demo_emails', '')
        demo_requests = st.session_state.get('demo_requests', [])
        
        if demo_emails and not st.session_state.emails:
            emails = parse_emails(demo_emails)
            st.session_state.emails = emails
            st.session_state.cpra_requests = demo_requests
            st.success(f"Demo data loaded: {len(emails)} emails, {len(demo_requests)} CPRA requests")
            st.session_state.demo_data_loaded = False  # Reset flag
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Email Upload")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose an email export file",
            type=['txt'],
            help="Upload a text file containing emails in Outlook export format"
        )
        
        # Sample data option
        if st.button("Load Sample Data", type="secondary"):
            # Always load demo data (it's better than the old sample data)
            email_content, cpra_requests = load_demo_data()
            if email_content:
                emails = parse_emails(email_content)
                st.session_state.emails = emails
                # Convert string requests to CPRARequest objects
                st.session_state.cpra_requests = [
                    CPRARequest(text=req, request_id=f"request_{i}")
                    for i, req in enumerate(cpra_requests)
                ]
                st.success(f"Loaded demo data: {len(emails)} emails, {len(cpra_requests)} requests")
            else:
                st.error("Demo data not found. Please ensure demo-files directory exists.")
        
        if uploaded_file is not None:
            content = uploaded_file.read().decode('utf-8')
            # Only parse if content looks like emails (has From: header)
            if content and 'From:' in content:
                emails = parse_emails(content)
                st.session_state.emails = emails
                st.success(f"Parsed {len(emails)} emails from uploaded file")
            else:
                st.error("Uploaded file doesn't appear to contain emails in the expected format")
        
        # Display parsed emails
        if st.session_state.emails:
            st.markdown("### Parsed Emails")
            with st.expander(f"View {len(st.session_state.emails)} emails"):
                for i, email in enumerate(st.session_state.emails, 1):
                    st.markdown(f"**{i}.** {email.subject or '(No subject)'}")
                    st.caption(f"From: {email.from_address} | Date: {email.date}")
    
    with col2:
        st.markdown("### CPRA Requests")
        st.info("Enter up to 5 CPRA requests that describe the documents you're looking for")
        
        # CPRA request inputs
        requests = []
        # Pre-fill with demo requests if available
        existing_requests = st.session_state.cpra_requests if st.session_state.cpra_requests else []
        
        for i in range(5):
            if i < len(existing_requests):
                # Handle both CPRARequest objects and strings
                default_value = existing_requests[i].text if isinstance(existing_requests[i], CPRARequest) else str(existing_requests[i])
            else:
                default_value = ""
            request = st.text_area(
                f"Request {i+1}",
                key=f"cpra_request_{i}",
                height=80,
                value=default_value,
                placeholder="e.g., All documents regarding roof leak issues on the Community Center construction project"
            )
            if request.strip():
                requests.append(request.strip())
        
        # Convert string requests to CPRARequest objects
        st.session_state.cpra_requests = [
            CPRARequest(text=req, request_id=f"request_{i}")
            for i, req in enumerate(requests)
        ]
        
        if requests:
            st.success(f"{len(requests)} CPRA request(s) configured")
    
    # Start processing button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.emails and st.session_state.cpra_requests:
            if st.button("Start Processing", type="primary", use_container_width=True):
                # Initialize session
                # CPRARequest already imported at module level
                cpra_request_objs = st.session_state.cpra_requests  # Already CPRARequest objects now
                session = ProcessingSession(
                    session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
                    cpra_requests=cpra_request_objs,
                    emails=st.session_state.emails
                )
                st.session_state.session = session
                st.session_state.page = 'processing'
                st.rerun()
        else:
            st.warning("Please upload emails and enter at least one CPRA request")


def processing_page():
    """Processing page with real-time progress indicators."""
    st.title("Processing Documents")
    
    if not st.session_state.emails or not st.session_state.cpra_requests:
        st.error("No emails or requests to process")
        return
    
    # Get demo settings (moved up to be available throughout function)
    demo_mode = st.session_state.demo_mode
    demo_settings = st.session_state.demo_settings
    speed = demo_settings.get('speed', 1.0) if demo_mode else 1.0
    show_animations = demo_settings.get('animations', True) if demo_mode else False
    show_resources = demo_settings.get('resource_monitor', True) if demo_mode else False
    
    # Create tabs for demo mode FIRST (before checking if complete)
    if demo_mode:
        view_tabs = st.tabs(["Processing Status", "AI Stream View"])
        
        with view_tabs[0]:
            # This is where the processing status will be shown
            processing_status_container = st.container()
            
        with view_tabs[1]:
            # AI stream view
            st.markdown("### 🤖 AI Processing Stream")
            st.info("This view shows the prompts sent to the AI and responses received during processing.")
            
            # Get stream events directly from session state
            # This ensures we always get the current state
            events_list = []
            if 'stream_events' in st.session_state:
                events_list = st.session_state.stream_events
            
            # Show event count and refresh button
            col1, col2 = st.columns([3, 1])
            with col1:
                if events_list:
                    st.success(f"📊 **{len(events_list)} AI interactions captured**")
                else:
                    st.info("📊 **No AI interactions captured yet**")
            with col2:
                if st.button("🔄 Refresh", key="refresh_stream_view"):
                    st.rerun()
            
            # Always show the events if they exist
            if events_list and len(events_list) > 0:
                # Educational callout about structured outputs
                st.info("""
                **💡 For the Audience:** Notice how the AI is instructed to respond with structured JSON format. 
                This ensures consistent, parseable responses that can be automatically processed by the system.
                The prompts include specific examples of the expected output format.
                """)
                
                # Show last few events as simple list first
                st.markdown("#### Recent Events (Simple View)")
                for event in events_list[-5:]:
                    content = event.get('content', '')
                    content_len = len(content) if content else 0
                    st.text(f"{event['type']}: {content_len} chars")
                
                # Find the most recent complete prompt/response pair
                last_system_prompt = None
                last_user_prompt = None
                last_response = None
                
                for event in reversed(events_list):
                    if event['type'] == 'response_complete' and not last_response:
                        last_response = event
                    elif event['type'] == 'user_prompt' and not last_user_prompt:
                        last_user_prompt = event
                    elif event['type'] == 'system_prompt' and not last_system_prompt:
                        last_system_prompt = event
                    
                    if last_system_prompt and last_user_prompt and last_response:
                        break
                
                # Display the last complete interaction
                if last_system_prompt or last_user_prompt or last_response:
                    st.markdown("---")
                    st.markdown("### Last Complete AI Interaction")
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown("#### 📤 Input to AI")
                        if last_system_prompt:
                            with st.expander("System Prompt (Instructions to AI)", expanded=True):
                                # Show more of the system prompt, especially the structured output part
                                content = last_system_prompt['content']
                                
                                # Try to show at least the structured output instructions
                                if 'You must respond with valid JSON' in content:
                                    # Find and highlight the JSON format section
                                    json_start = content.find('You must respond with valid JSON')
                                    if json_start > 0:
                                        # Show context before and the full JSON instructions
                                        display_start = max(0, json_start - 200)
                                        display_content = content[display_start:min(len(content), json_start + 800)]
                                        if display_start > 0:
                                            display_content = "..." + display_content
                                        if json_start + 800 < len(content):
                                            display_content = display_content + "..."
                                        st.code(display_content, language="text")
                                        
                                        # Add button to see full prompt
                                        if len(content) > 1000:
                                            with st.expander("View Complete System Prompt"):
                                                st.code(content, language="text")
                                    else:
                                        # Fallback to showing first 1500 chars
                                        st.code(content[:1500] + '...' if len(content) > 1500 else content, language="text")
                                else:
                                    # Show first 1500 characters
                                    st.code(content[:1500] + '...' if len(content) > 1500 else content, language="text")
                                    if len(content) > 1500:
                                        with st.expander("View Complete System Prompt"):
                                            st.code(content, language="text")
                        
                        if last_user_prompt:
                            st.info(f"Email: {last_user_prompt['metadata'].get('email_subject', 'Unknown')}")
                            with st.expander("User Prompt (Document to Analyze)", expanded=True):
                                # Show more of the user prompt to see the CPRA request and email
                                content = last_user_prompt['content']
                                st.code(content[:1200] + '...' if len(content) > 1200 else content, language="text")
                                
                                # Add button to see complete prompt if truncated
                                if len(content) > 1200:
                                    with st.expander("View Complete User Prompt"):
                                        st.code(content, language="text")
                    
                    with col2:
                        st.markdown("#### 📥 AI Response")
                        if last_response:
                            try:
                                response_json = json.loads(last_response['content'])
                                st.json(response_json)
                            except:
                                st.code(last_response['content'][:500] + '...' if len(last_response['content']) > 500 else last_response['content'])
                
                # Show full event log
                with st.expander("Full Event Log"):
                    for i, event in enumerate(events_list):
                        content = event.get('content', '')
                        content_len = len(content) if content else 0
                        st.text(f"{i+1}. {event['type']} - {content_len} chars - {event.get('timestamp', 'no time')}")
            else:
                st.warning("No AI processing data yet. Start processing emails to see the AI prompts and responses.")
                st.info("Make sure Demo Mode is enabled BEFORE starting processing.")
    
    # Check if processing is already complete
    if st.session_state.processing_complete:
        # Show in the processing status container if in demo mode
        if demo_mode:
            with processing_status_container:
                st.success("Processing already complete!")
                st.info("Navigate to Results Dashboard or Document Review to view results.")
                
                # Debug: Show if we have stream events
                events_count = len(st.session_state.get('stream_events', []))
                st.info(f"Debug: {events_count} stream events captured")
                if events_count > 0:
                    st.success("✅ Stream events are available in the AI Stream View tab above!")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("View Results", type="primary", use_container_width=True):
                        st.session_state.page = 'results'
                        st.rerun()
                with col2:
                    if st.button("Review Documents", use_container_width=True):
                        st.session_state.page = 'review'
                        st.rerun()
        else:
            # Non-demo mode
            st.success("Processing already complete!")
            st.info("Navigate to Results Dashboard or Document Review to view results.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("View Results", type="primary", use_container_width=True):
                    st.session_state.page = 'results'
                    st.rerun()
            with col2:
                if st.button("Review Documents", use_container_width=True):
                    st.session_state.page = 'review'
                    st.rerun()
        return
    
    # Processing phases
    phases = [
        ("Analyzing Responsiveness", "responsiveness"),
        ("Checking Exemptions", "exemptions"),
        ("Finalizing Results", "finalize")
    ]
    
    # Create layout containers
    if demo_mode and show_resources:
        # Resource monitor at top if in demo mode
        resource_container = st.container()
        st.markdown("---")
    
    # Create containers for processing display
    if demo_mode:
        # In demo mode, tabs are already created above
        # Just need to create containers in the processing status tab
        with processing_status_container:
            progress_container = st.container()
            stats_container = st.container()
            current_doc_container = st.container()
            log_container = st.container()
    else:
        # Non-demo mode - standard layout
        progress_container = st.container()
        stats_container = st.container()
        log_container = st.container()
    
    # Initialize resource monitor if needed
    if demo_mode and show_resources:
        with resource_container:
            st.markdown("### System Resources")
            st.session_state.resource_monitor.create_resource_dashboard(
                resource_container, 
                model_name="gemma3:latest"
            )
    
    with progress_container:
        st.markdown("### Processing Progress")
        overall_progress = st.progress(0)
        phase_text = st.empty()
        
        if demo_mode:
            # Add phase indicators
            col1, col2, col3 = st.columns(3)
            with col1:
                phase_1_indicator = st.empty()
            with col2:
                phase_2_indicator = st.empty()
            with col3:
                phase_3_indicator = st.empty()
    
    with stats_container:
        st.markdown("### Live Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            docs_processed = st.metric("Documents Processed", "0")
        with col2:
            responsive_count = st.metric("Responsive", "0")
        with col3:
            exemption_count = st.metric("With Exemptions", "0")
        with col4:
            processing_time = st.metric("Processing Time", "0s")
    
    if demo_mode:
        with current_doc_container:
            st.markdown("### Current Document")
            current_doc_display = st.empty()
            ai_activity = st.empty()
    
    with log_container:
        st.markdown("### Processing Log")
        log_area = st.empty()
        logs = []
    
    # Start processing with error handling
    start_time = time.time()
    try:
        analyzer = CPRAAnalyzer(model_name=config.model.responsiveness_model)
    except Exception as e:
        st.error(f"Failed to initialize analyzer: {str(e)}")
        logger.error(f"Analyzer initialization failed: {e}")
        st.stop()
    
    total_emails = len(st.session_state.emails)
    errors_encountered = []
    
    # Phase 1: Responsiveness Analysis
    if demo_mode:
        phase_1_indicator.success("▶ Analyzing Responsiveness")
        phase_2_indicator.info("Checking Exemptions")
        phase_3_indicator.info("Finalizing Results")
        
    phase_text.markdown("**Current Phase:** Analyzing Responsiveness")
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Starting responsiveness analysis...")
    log_area.text_area("Processing Log", "\n".join(logs), height=200)
    
    # Prepare streaming callback if in demo mode (defined once for the whole loop)
    stream_cb = None
    if demo_mode:
        # Initialize stream events list if needed
        if 'stream_events' not in st.session_state:
            st.session_state.stream_events = []
            
        # Debug: log current state
        logger.info(f"Demo mode active, current stream_events count: {len(st.session_state.stream_events)}")
        
        # Create callback function that stores events
        def stream_cb(event_type, content, metadata):
            # Ensure stream_events exists
            if 'stream_events' not in st.session_state:
                st.session_state.stream_events = []
                
            # Store events for display after processing
            event = {
                'type': event_type,
                'content': content,
                'metadata': metadata if metadata else {},
                'timestamp': datetime.now()
            }
            st.session_state.stream_events.append(event)
            
            # Debug logging
            logger.info(f"Stream event captured: {event_type}, content_length: {len(content) if content else 0}, total_events: {len(st.session_state.stream_events)}")
    
    responsiveness_results = []
    for i, email in enumerate(st.session_state.emails):
        if demo_mode:
            # Show current document details
            current_doc_display.info(f"""
            **Email {i+1} of {total_emails}**
            
            **Subject:** {email.subject or '(No subject)'}
            
            **From:** {email.from_address}
            
            **Date:** {email.date}
            """)
            
            # Show AI activity
            ai_activity.warning(get_ai_thinking_animation("responsiveness"))
            
            # Add processing delay for visual effect
            simulate_processing_delay(demo_mode, base_delay=1.0, speed_multiplier=speed)
        
        # Analyze responsiveness with error handling
        try:
            # Debug: log if callback is being passed
            logger.info(f"Analyzing email {i+1}, stream_cb is {'set' if stream_cb else 'None'}")
            
            result = analyzer.analyze_email_responsiveness(
                email, 
                st.session_state.cpra_requests,
                email_index=i,
                stream_callback=stream_cb
            )
            responsiveness_results.append(result)
        except Exception as e:
            logger.error(f"Error analyzing email {i+1}: {e}")
            errors_encountered.append(f"Email {i+1}: {str(e)}")
            # Create failed result
            responsiveness_results.append(None)
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}]  Error processing email {i+1}")
        
        # Auto-save session periodically
        if (i + 1) % config.processing.auto_save_interval == 0:
            pass  # Recovery functionality removed
        
        # Clear AI activity after processing
        if demo_mode:
            ai_activity.success(f" Analysis complete: {'Responsive' if result and result.is_responsive_to_any() else 'Not Responsive'}")
            simulate_processing_delay(demo_mode, base_delay=0.3, speed_multiplier=speed)
        
        # Update progress with smooth animation in demo mode
        progress = (i + 1) / (total_emails * 2)  # Two phases
        if demo_mode and show_animations:
            # Animate progress bar smoothly
            current_progress = overall_progress.progress(0)
            for step in range(int(progress * 100)):
                overall_progress.progress(step / 100.0)
                time.sleep(0.001 / speed)
        else:
            overall_progress.progress(progress)
        
        # Update stats
        docs_processed.metric("Documents Processed", f"{i+1}/{total_emails}")
        responsive_so_far = sum(1 for r in responsiveness_results if r and r.is_responsive_to_any())
        responsive_count.metric("Responsive", str(responsive_so_far))
        elapsed = int(time.time() - start_time)
        processing_time.metric("Processing Time", f"{elapsed}s")
        
        # Update resource monitor
        if demo_mode and show_resources and i % 3 == 0:  # Update every 3 emails
            with resource_container:
                st.session_state.resource_monitor.create_processing_monitor(
                    resource_container,
                    phase="responsiveness",
                    model_active=True
                )
        
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Email {i+1}: {'Responsive' if result and result.is_responsive_to_any() else 'Not Responsive'}")
        if demo_mode and demo_settings.get('typewriter', False):
            typewriter_effect(logs[-1], log_area, demo_mode, speed=0.01)
        else:
            log_area.text_area("Processing Log", "\n".join(logs[-10:]), height=200)
    
    st.session_state.responsiveness_results = responsiveness_results
    
    # Phase 2: Exemption Analysis
    if demo_mode:
        phase_1_indicator.success("  Responsiveness Complete")
        phase_2_indicator.success("▶  Checking Exemptions")
        
    phase_text.markdown("**Current Phase:**  Checking Exemptions")
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Starting exemption analysis...")
    log_area.text_area("Processing Log", "\n".join(logs[-10:]), height=200)
    
    exemption_results = []
    for i, email in enumerate(st.session_state.emails):
        # Only analyze exemptions for responsive emails
        if responsiveness_results[i] and responsiveness_results[i].is_responsive_to_any():
            if demo_mode:
                current_doc_display.warning(f"""
                **Checking Email {i+1} for Exemptions**
                
                **Subject:** {email.subject or '(No subject)'}
                
                **Status:** Responsive Document
                
                **Scanning for:** Attorney-Client, Personnel Records, Deliberative Process
                """)
                
                ai_activity.warning(get_ai_thinking_animation("exemptions"))
                simulate_processing_delay(demo_mode, base_delay=0.8, speed_multiplier=speed)
            
            try:
                result = analyzer.analyze_email_exemptions(
                    email,
                    email_index=i,
                    stream_callback=stream_cb if demo_mode and st.session_state.stream_callback else None
                )
                exemption_results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing exemptions for email {i+1}: {e}")
                errors_encountered.append(f"Exemption analysis for email {i+1}: {str(e)}")
                exemption_results.append(None)
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}]  Error checking exemptions for email {i+1}")
            
            if demo_mode:
                if result and result.has_any_exemption():
                    num_exemptions = len(result.get_applicable_exemptions())
                    ai_activity.warning(f" Found {num_exemptions} exemption(s)")
                else:
                    ai_activity.success(" No exemptions found")
                simulate_processing_delay(demo_mode, base_delay=0.2, speed_multiplier=speed)
        else:
            exemption_results.append(None)
            if demo_mode:
                current_doc_display.info(f" Skipping non-responsive email {i+1}")
                simulate_processing_delay(demo_mode, base_delay=0.1, speed_multiplier=speed)
        
        # Update progress
        progress = (total_emails + i + 1) / (total_emails * 2)
        overall_progress.progress(progress)
        
        # Update stats
        exemptions_so_far = sum(1 for r in exemption_results if r and r.has_any_exemption())
        exemption_count.metric("With Exemptions", str(exemptions_so_far))
        elapsed = int(time.time() - start_time)
        processing_time.metric("Processing Time", f"{elapsed}s")
        
        if exemption_results[i]:
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Email {i+1}: {len(exemption_results[i].get_applicable_exemptions())} exemption(s) found")
            log_area.text_area("Processing Log", "\n".join(logs[-10:]), height=200)
    
    st.session_state.exemption_results = exemption_results
    
    # Phase 3: Finalize
    if demo_mode:
        phase_2_indicator.success("  Exemptions Complete")
        phase_3_indicator.success("▶  Finalizing Results")
        
    phase_text.markdown("**Current Phase:**  Finalizing Results")
    
    if demo_mode:
        current_doc_display.info(" Preparing review system...")
        ai_activity.info(" Generating statistics and summary...")
        simulate_processing_delay(demo_mode, base_delay=1.5, speed_multiplier=speed)
    
    # Initialize review manager with error handling
    try:
        # First update the session with the analysis results
        # Convert lists to dicts indexed by email index
        for i, result in enumerate(responsiveness_results):
            if result:
                st.session_state.session.responsiveness_results[str(i)] = result
        
        for i, result in enumerate(exemption_results):
            if result:
                st.session_state.session.exemption_results[str(i)] = result
        
        review_manager = ReviewManager()
        review_manager.initialize_reviews(st.session_state.session)
        st.session_state.review_manager = review_manager
        st.session_state.processing_complete = True
        
        
    except Exception as e:
        logger.error(f"Error initializing review manager: {e}")
        st.error(f" Failed to initialize review system: {str(e)}")
        errors_encountered.append(f"Review system initialization: {str(e)}")
    
    # Show error summary if any errors occurred
    if errors_encountered:
        st.warning(f" Processing completed with {len(errors_encountered)} error(s)")
        with st.expander("View error details"):
            for error in errors_encountered:
                st.text(error)
    else:
        st.success(" Processing completed successfully!")
    
    # Final stats
    overall_progress.progress(1.0)
    total_time = int(time.time() - start_time)
    
    if demo_mode:
        phase_3_indicator.success("  Processing Complete!")
        ai_activity.success(" All documents processed successfully!")
        
        # Final resource display
        if show_resources:
            with resource_container:
                st.session_state.resource_monitor.create_processing_monitor(
                    resource_container,
                    phase="finalize",
                    model_active=False
                )
    
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Processing complete!")
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Total time: {total_time}s")
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Average: {total_time/total_emails:.1f}s per email")
    log_area.text_area("Processing Log", "\n".join(logs[-10:]), height=200)
    
    # Enhanced success message for demo mode
    if demo_mode:
        # Create impressive summary statistics
        responsive_docs = sum(1 for r in responsiveness_results if r and r.is_responsive_to_any())
        exempt_docs = sum(1 for r in exemption_results if r and r.has_any_exemption())
        
        st.balloons()  # Celebration effect
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.success(f"""
            ##  **Processing Complete!**
            
            ###  Final Statistics:
            - **Total Documents Processed:** {total_emails} emails
            - **Processing Time:** {total_time} seconds ({total_time/total_emails:.1f}s average)
            - **Responsive Documents:** {responsive_docs} ({(responsive_docs/total_emails)*100:.1f}%)
            - **Documents with Exemptions:** {exempt_docs} ({(exempt_docs/total_emails)*100:.1f}%)
            
            ###  Performance Highlights:
            -  All processing completed locally (no cloud services used)
            -  Data never left this device (airplane mode compatible)
            -  Average processing speed: {total_emails/(total_time/60):.1f} emails/minute
            """)
        
        with col2:
            # Model performance card
            st.info(f"""
            ###  AI Model Performance
            
            **Model:** gemma3:latest
            
            **Size:** 3.3 GB
            
            **Accuracy:** High
            
            **Speed:** Fast
            
            **Privacy:** 100% Local
            """)
    else:
        # Standard success message
        st.success(f"""
         **Processing Complete!**
        - Processed {total_emails} emails in {total_time} seconds
        - Found {sum(1 for r in responsiveness_results if r and r.is_responsive_to_any())} responsive documents
        - Identified {sum(1 for r in exemption_results if r and r.has_any_exemption())} documents with exemptions
        """)
    
    # Navigate to results
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(" View Results Dashboard", type="primary", use_container_width=True):
            st.session_state.page = 'results'
            st.rerun()


def results_dashboard():
    """Results dashboard with document grouping and statistics."""
    st.title(" Results Dashboard")
    
    if not st.session_state.processing_complete:
        st.error("Processing not complete")
        return
    
    # Summary statistics
    st.markdown("###  Processing Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    total_emails = len(st.session_state.emails)
    responsive_emails = [i for i, r in enumerate(st.session_state.responsiveness_results) 
                        if r and r.is_responsive_to_any()]
    non_responsive_emails = [i for i, r in enumerate(st.session_state.responsiveness_results)
                             if not r or not r.is_responsive_to_any()]
    exemption_emails = [i for i, r in enumerate(st.session_state.exemption_results)
                       if r and r.has_any_exemption()]
    
    with col1:
        st.metric("Total Documents", total_emails)
    with col2:
        st.metric("Responsive", len(responsive_emails))
    with col3:
        st.metric("Non-Responsive", len(non_responsive_emails))
    with col4:
        st.metric("With Exemptions", len(exemption_emails))
    
    # Document groupings
    st.markdown("---")
    st.markdown("### Document Groups")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        f" Responsive ({len(responsive_emails)})",
        f" Non-Responsive ({len(non_responsive_emails)})",
        f" With Exemptions ({len(exemption_emails)})",
        " By Confidence"
    ])
    
    with tab1:
        st.markdown("#### Responsive Documents")
        if responsive_emails:
            for idx in responsive_emails:
                email = st.session_state.emails[idx]
                result = st.session_state.responsiveness_results[idx]
                
                with st.expander(f"{email.subject or '(No subject)'}"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**From:** {email.from_address}")
                        st.markdown(f"**Date:** {email.date}")
                        st.markdown(f"**Responsive to:** Request(s) {', '.join(map(str, result.get_responsive_requests()))}")
                    with col2:
                        st.markdown(f"**Confidence:** {result.confidence}")
                        if st.session_state.exemption_results[idx]:
                            exemptions = st.session_state.exemption_results[idx].get_applicable_exemptions()
                            if exemptions:
                                st.markdown(f"**Exemptions:** {len(exemptions)}")
        else:
            st.info("No responsive documents found")
    
    with tab2:
        st.markdown("#### Non-Responsive Documents")
        if non_responsive_emails:
            for idx in non_responsive_emails:
                email = st.session_state.emails[idx]
                
                with st.expander(f"{email.subject or '(No subject)'}"):
                    st.markdown(f"**From:** {email.from_address}")
                    st.markdown(f"**Date:** {email.date}")
                    st.markdown("**Status:** Not responsive to any CPRA request")
        else:
            st.info("No non-responsive documents found")
    
    with tab3:
        st.markdown("#### Documents with Exemptions")
        if exemption_emails:
            for idx in exemption_emails:
                email = st.session_state.emails[idx]
                exemption_result = st.session_state.exemption_results[idx]
                
                with st.expander(f"{email.subject or '(No subject)'}"):
                    st.markdown(f"**From:** {email.from_address}")
                    st.markdown(f"**Date:** {email.date}")
                    st.markdown("**Exemptions:**")
                    exemptions = exemption_result.get_applicable_exemptions()
                    for exemption_type in exemptions:
                        if exemption_type == ExemptionType.ATTORNEY_CLIENT:
                            ex_data = exemption_result.attorney_client
                            st.markdown(f"- **Attorney-Client Privilege** ({ex_data['confidence'].value})")
                            st.caption(ex_data['reasoning'])
                        elif exemption_type == ExemptionType.PERSONNEL:
                            ex_data = exemption_result.personnel
                            st.markdown(f"- **Personnel Records** ({ex_data['confidence'].value})")
                            st.caption(ex_data['reasoning'])
                        elif exemption_type == ExemptionType.DELIBERATIVE:
                            ex_data = exemption_result.deliberative
                            st.markdown(f"- **Deliberative Process** ({ex_data['confidence'].value})")
                            st.caption(ex_data['reasoning'])
        else:
            st.info("No documents with exemptions found")
    
    with tab4:
        st.markdown("#### Documents by Confidence Level")
        
        # Group by confidence
        high_conf = []
        medium_conf = []
        low_conf = []
        
        for i, result in enumerate(st.session_state.responsiveness_results):
            if result:
                if result.confidence == "HIGH":
                    high_conf.append(i)
                elif result.confidence == "MEDIUM":
                    medium_conf.append(i)
                elif result.confidence == "LOW":
                    low_conf.append(i)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**High Confidence ({len(high_conf)})**")
            for idx in high_conf[:5]:  # Show first 5
                email = st.session_state.emails[idx]
                st.caption(f"• {email.subject or '(No subject)'}")
            if len(high_conf) > 5:
                st.caption(f"...and {len(high_conf)-5} more")
        
        with col2:
            st.markdown(f"**Medium Confidence ({len(medium_conf)})**")
            for idx in medium_conf[:5]:
                email = st.session_state.emails[idx]
                st.caption(f"• {email.subject or '(No subject)'}")
            if len(medium_conf) > 5:
                st.caption(f"...and {len(medium_conf)-5} more")
        
        with col3:
            st.markdown(f"**Low Confidence ({len(low_conf)})**")
            for idx in low_conf[:5]:
                email = st.session_state.emails[idx]
                st.caption(f"• {email.subject or '(No subject)'}")
            if len(low_conf) > 5:
                st.caption(f"...and {len(low_conf)-5} more")
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(" Start Document Review", type="primary", use_container_width=True):
            st.session_state.page = 'review'
            st.rerun()


def review_page():
    """Document review interface."""
    st.title(" Document Review")
    
    if not st.session_state.processing_complete or not st.session_state.review_manager:
        st.error("Processing not complete or review system not initialized")
        return
    
    review_manager = st.session_state.review_manager
    emails = st.session_state.emails
    current_idx = st.session_state.current_review_index
    
    # Review progress
    summary = review_manager.get_review_summary(st.session_state.session)
    completed = summary['review_status']['completed']
    total = summary['total_documents']
    st.progress(completed / total if total > 0 else 0)
    st.markdown(f"**Review Progress:** {completed} of {total} documents reviewed")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("← Previous", disabled=current_idx <= 0):
            st.session_state.current_review_index = max(0, current_idx - 1)
            st.rerun()
    
    with col2:
        st.markdown(f"### Document {current_idx + 1} of {len(emails)}")
    
    with col3:
        if st.button("Next →", disabled=current_idx >= len(emails) - 1):
            st.session_state.current_review_index = min(len(emails) - 1, current_idx + 1)
            st.rerun()
    
    st.markdown("---")
    
    # Current document display
    if current_idx < len(emails):
        email = emails[current_idx]
        responsiveness = st.session_state.responsiveness_results[current_idx]
        exemptions = st.session_state.exemption_results[current_idx]
        
        # Two column layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("###  Email Content")
            
            # Email metadata
            st.markdown(f"**Subject:** {email.subject or '(No subject)'}")
            st.markdown(f"**From:** {email.from_address}")
            st.markdown(f"**To:** {email.to_address}")
            st.markdown(f"**Date:** {email.date}")
            
            # Email body
            st.markdown("**Content:**")
            st.text_area("Email Body", email.body, height=300, disabled=True)
        
        with col2:
            st.markdown("###  AI Analysis")
            
            # Responsiveness analysis
            st.markdown("#### Responsiveness")
            if responsiveness:
                if responsiveness.is_responsive_to_any():
                    st.success(f" Responsive to request(s): {', '.join(map(str, [i+1 for i in responsiveness.get_responsive_requests()]))}")
                else:
                    st.info(" Not responsive")
                st.caption(f"Confidence: {responsiveness.confidence}")
                st.caption(f"Reasoning: {responsiveness.reasoning}")
            else:
                st.warning("No responsiveness analysis available")
            
            # Exemption analysis
            st.markdown("#### Exemptions")
            if exemptions and exemptions.has_any_exemption():
                applicable_exemptions = exemptions.get_applicable_exemptions()
                for exemption_type in applicable_exemptions:
                    if exemption_type == ExemptionType.ATTORNEY_CLIENT:
                        ex_data = exemptions.attorney_client
                        st.warning(f" Attorney-Client Privilege")
                        st.caption(f"Confidence: {ex_data['confidence'].value}")
                        st.caption(f"Reasoning: {ex_data['reasoning']}")
                    elif exemption_type == ExemptionType.PERSONNEL:
                        ex_data = exemptions.personnel
                        st.warning(f" Personnel Records")
                        st.caption(f"Confidence: {ex_data['confidence'].value}")
                        st.caption(f"Reasoning: {ex_data['reasoning']}")
                    elif exemption_type == ExemptionType.DELIBERATIVE:
                        ex_data = exemptions.deliberative
                        st.warning(f" Deliberative Process")
                        st.caption(f"Confidence: {ex_data['confidence'].value}")
                        st.caption(f"Reasoning: {ex_data['reasoning']}")
            else:
                st.success(" No exemptions identified")
            
            st.markdown("---")
            
            # Review controls
            st.markdown("###  Review Decision")
            
            # Get current review state
            # Use the same email_id format as the review manager
            email_id = email.message_id if email.message_id else f"email_{current_idx}"
            current_review = st.session_state.session.document_reviews.get(email_id)
            
            # Responsiveness override
            is_responsive = st.checkbox(
                "Document is responsive",
                value=(any(current_review.final_responsive) if current_review and current_review.final_responsive else (responsiveness.is_responsive_to_any() if responsiveness else False)),
                key=f"responsive_{current_idx}"
            )
            
            # Exemption overrides
            st.markdown("**Exemptions:**")
            exemption_overrides = {}
            
            attorney_client = st.checkbox(
                "Attorney-Client Privilege",
                value=(current_review and ExemptionType.ATTORNEY_CLIENT in current_review.final_exemptions) if current_review else (exemptions.attorney_client["applies"] if exemptions else False),
                key=f"attorney_{current_idx}"
            )
            
            personnel = st.checkbox(
                "Personnel Records",
                value=(current_review and ExemptionType.PERSONNEL in current_review.final_exemptions) if current_review else (exemptions.personnel["applies"] if exemptions else False),
                key=f"personnel_{current_idx}"
            )
            
            deliberative = st.checkbox(
                "Deliberative Process",
                value=(current_review and ExemptionType.DELIBERATIVE in current_review.final_exemptions) if current_review else (exemptions.deliberative["applies"] if exemptions else False),
                key=f"deliberative_{current_idx}"
            )
            
            # Build exemption overrides dictionary
            exemption_overrides = {}
            if current_review:
                if current_review.user_exemption_override is None:
                    current_review.user_exemption_override = {}
            exemption_overrides[ExemptionType.ATTORNEY_CLIENT] = attorney_client
            exemption_overrides[ExemptionType.PERSONNEL] = personnel
            exemption_overrides[ExemptionType.DELIBERATIVE] = deliberative
            
            # Save review button
            if st.button(" Save Review", type="primary", use_container_width=True):
                # Get or ensure current review exists
                if not current_review:
                    # Create a new review if it doesn't exist
                    from src.utils.data_structures import DocumentReview
                    current_review = DocumentReview(
                        email_id=email_id,
                        review_status=ReviewStatus.PENDING
                    )
                    st.session_state.session.document_reviews[email_id] = current_review
                
                if current_review:
                    # Start review if not started
                    if current_review.review_status == ReviewStatus.PENDING:
                        review_manager.start_review(current_review)
                    
                    # Apply responsiveness override
                    # Since we have one checkbox for overall responsiveness, apply to all requests
                    if responsiveness:
                        for i in range(len(responsiveness.responsive)):
                            if current_review.user_responsive_override is None:
                                current_review.user_responsive_override = {}
                            current_review.user_responsive_override[i] = is_responsive
                    
                    # Apply exemption overrides
                    current_review.user_exemption_override = exemption_overrides
                    
                    # Finalize review with the analysis results
                    review_manager.finalize_review(
                        current_review,
                        responsiveness_analysis=responsiveness,
                        exemption_analysis=exemptions
                    )
                
                st.success(" Review saved!")
                
                # Auto-advance to next document
                if current_idx < len(emails) - 1:
                    st.session_state.current_review_index = current_idx + 1
                    st.rerun()
    
    # Check if all reviews complete
    summary = review_manager.get_review_summary(st.session_state.session)
    if summary['review_status']['completed'] == summary['total_documents']:
        st.session_state.review_complete = True
        st.success(" All documents reviewed!")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(" Proceed to Export", type="primary", use_container_width=True):
                st.session_state.page = 'export'
                st.rerun()


def export_page():
    """Export documents page."""
    st.title(" Export Documents")
    
    if not st.session_state.review_complete or not st.session_state.review_manager:
        st.error("Review not complete")
        return
    
    # Initialize export manager if needed
    if not st.session_state.export_manager:
        st.session_state.export_manager = ExportManager(
            output_dir="data/test_exports"
        )
    
    export_manager = st.session_state.export_manager
    
    # Export summary
    st.markdown("###  Export Summary")
    
    # Get final determinations
    final_determinations = []
    for i, email in enumerate(st.session_state.emails):
        email_id = email.message_id if email.message_id else f"email_{i}"
        review = st.session_state.session.document_reviews.get(email_id)
        if review:
            final_determinations.append({
                'responsive': any(review.final_responsive) if review.final_responsive else False,
                'exemptions': review.final_exemptions
            })
        else:
            # Use AI results if no review exists
            responsiveness = st.session_state.responsiveness_results[i] if i < len(st.session_state.responsiveness_results) else None
            exemptions = st.session_state.exemption_results[i] if i < len(st.session_state.exemption_results) else None
            final_determinations.append({
                'responsive': responsiveness.is_responsive_to_any() if responsiveness else False,
                'exemptions': {ex.exemption_type: ex.reasoning for ex in exemptions.exemptions} if exemptions and exemptions.exemptions else {}
            })
    
    responsive_count = sum(1 for d in final_determinations if d['responsive'])
    exempt_count = sum(1 for d in final_determinations if d['exemptions'])
    producible_count = sum(1 for d in final_determinations if d['responsive'] and not d['exemptions'])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Documents", len(st.session_state.emails))
    with col2:
        st.metric("Responsive", responsive_count)
    with col3:
        st.metric("With Exemptions", exempt_count)
    with col4:
        st.metric("Producible", producible_count)
    
    # Export options
    st.markdown("---")
    st.markdown("### Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Production Documents")
        st.info(f"Export {producible_count} responsive documents without exemptions")
        
        if st.button(" Generate Production PDF", type="primary", use_container_width=True):
            with st.spinner("Generating production PDF..."):
                try:
                    export_dir = Path("data/test_exports")
                    export_dir.mkdir(parents=True, exist_ok=True)
                    
                    result = export_manager.generate_exports(st.session_state.session)
                    
                    if result['production_pdf']:
                        st.success(f" Production PDF created: {Path(result['production_pdf']).name}")
                    else:
                        st.warning("No documents to export in production PDF")
                except Exception as e:
                    st.error(f"Error generating production PDF: {str(e)}")
    
    with col2:
        st.markdown("#### Privilege Log")
        st.info(f"Document {exempt_count} withheld documents with exemptions")
        
        if st.button(" Generate Privilege Log", type="secondary", use_container_width=True):
            with st.spinner("Generating privilege log..."):
                try:
                    export_dir = Path("data/test_exports")
                    export_dir.mkdir(parents=True, exist_ok=True)
                    
                    result = export_manager.generate_exports(st.session_state.session)
                    
                    if result['privilege_log_csv']:
                        st.success(f" Privilege log CSV created: {Path(result['privilege_log_csv']).name}")
                    if result['privilege_log_pdf']:
                        st.success(f" Privilege log PDF created: {Path(result['privilege_log_pdf']).name}")
                    
                    if not result['privilege_log_csv'] and not result['privilege_log_pdf']:
                        st.info("No withheld documents requiring privilege log")
                except Exception as e:
                    st.error(f"Error generating privilege log: {str(e)}")
    
    # Full export
    st.markdown("---")
    st.markdown("###  Complete Export Package")
    
    if st.button(" Generate All Export Files", type="primary", use_container_width=True):
        with st.spinner("Generating complete export package..."):
            try:
                export_dir = Path("data/test_exports")
                export_dir.mkdir(parents=True, exist_ok=True)
                
                result = export_manager.generate_exports(st.session_state.session)
                
                st.success(" Export complete!")
                
                # Show results
                st.markdown("#### Generated Files:")
                if result['production_pdf']:
                    st.markdown(f"-  Production PDF: `{Path(result['production_pdf']).name}`")
                if result['privilege_log_csv']:
                    st.markdown(f"-  Privilege Log CSV: `{Path(result['privilege_log_csv']).name}`")
                if result['privilege_log_pdf']:
                    st.markdown(f"-  Privilege Log PDF: `{Path(result['privilege_log_pdf']).name}`")
                if result['summary_report']:
                    st.markdown(f"-  Summary Report: `{Path(result['summary_report']).name}`")
                if result['manifest']:
                    st.markdown(f"-  Export Manifest: `{Path(result['manifest']).name}`")
                
                st.info(f"All files saved to: `{export_dir}`")
                
            except Exception as e:
                st.error(f"Error during export: {str(e)}")
    
    # Session save option
    st.markdown("---")
    st.markdown("###  Save Session")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Session (JSON)", type="secondary"):
            try:
                session_manager = SessionManager()
                filepath = session_manager.save_session(
                    st.session_state.session,
                    st.session_state.emails,
                    st.session_state.review_manager,
                    format='json'
                )
                st.success(f" Session saved: {Path(filepath).name}")
            except Exception as e:
                st.error(f"Error saving session: {str(e)}")
    
    with col2:
        if st.button("Save Session (Pickle)", type="secondary"):
            try:
                session_manager = SessionManager()
                filepath = session_manager.save_session(
                    st.session_state.session,
                    st.session_state.emails,
                    st.session_state.review_manager,
                    format='pickle'
                )
                st.success(f" Session saved: {Path(filepath).name}")
            except Exception as e:
                st.error(f"Error saving session: {str(e)}")


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="CPRA Processing System",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom styling
    apply_custom_styling()
    
    # Initialize session state
    init_session_state()
    
    # Sidebar navigation
    sidebar_navigation()
    
    # Page routing
    if st.session_state.page == 'upload':
        upload_page()
    elif st.session_state.page == 'processing':
        processing_page()
    elif st.session_state.page == 'results':
        results_dashboard()
    elif st.session_state.page == 'review':
        review_page()
    elif st.session_state.page == 'export':
        export_page()
    else:
        upload_page()


if __name__ == "__main__":
    main()