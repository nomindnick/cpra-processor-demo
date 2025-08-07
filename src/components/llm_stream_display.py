#!/usr/bin/env python3
"""
LLM Stream Display Component for real-time visualization of AI processing.

This component provides a beautiful, easy-to-understand display of:
- What prompts are being sent to the AI model
- The AI's thinking process
- The responses being generated
- Processing metrics and performance

Designed for demonstration purposes to make AI processing transparent.
"""

import streamlit as st
import json
import time
from typing import Dict, Optional, Any, List, Tuple
from datetime import datetime
from enum import Enum


class StreamEventType(Enum):
    """Types of streaming events."""
    PROMPT_SYSTEM = "system_prompt"
    PROMPT_USER = "user_prompt"
    PROCESSING_START = "processing_start"
    PROCESSING_END = "processing_end"
    RESPONSE_CHUNK = "response_chunk"
    RESPONSE_COMPLETE = "response_complete"
    ERROR = "error"
    ANALYSIS_RESULT = "analysis_result"


class LLMStreamDisplay:
    """Component for displaying real-time LLM processing streams."""
    
    def __init__(self):
        """Initialize the stream display component."""
        self.active_streams = {}
        self.completed_streams = []
        self.current_email_info = None
        self.current_request_info = None
        
    def create_stream_container(self, container) -> Dict[str, Any]:
        """
        Create the main streaming display container.
        
        Args:
            container: Streamlit container to render in
            
        Returns:
            Dictionary of sub-containers for updates
        """
        with container:
            st.markdown("### AI Processing Stream")
            
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["Live Stream", "Current Analysis", "Metrics"])
            
            with tab1:
                # Live streaming view
                stream_col1, stream_col2 = st.columns([1, 1])
                
                with stream_col1:
                    st.markdown("#### Input to AI")
                    input_container = st.container()
                    
                with stream_col2:
                    st.markdown("#### AI Response")
                    output_container = st.container()
                    
            with tab2:
                # Current analysis details
                analysis_container = st.container()
                
            with tab3:
                # Metrics and performance
                metrics_container = st.container()
                
        return {
            'input': input_container,
            'output': output_container,
            'analysis': analysis_container,
            'metrics': metrics_container
        }
    
    def display_prompt(self, container, prompt_type: str, content: str, 
                      metadata: Optional[Dict] = None):
        """
        Display a prompt being sent to the AI.
        
        Args:
            container: Container to display in
            prompt_type: Type of prompt (system/user)
            content: The prompt content
            metadata: Optional metadata about the prompt
        """
        with container:
            if prompt_type == "system":
                st.info("**System Prompt** (Instructions to AI)")
                # Show truncated version with expander for full
                if len(content) > 500:
                    st.text(content[:500] + "...")
                    with st.expander("Show full system prompt"):
                        st.code(content, language="text")
                else:
                    st.code(content, language="text")
                    
            elif prompt_type == "user":
                st.success("**User Prompt** (Document to analyze)")
                # Parse and display structured content
                if "CPRA REQUEST" in content:
                    self._display_structured_prompt(content)
                else:
                    with st.expander("Show email content"):
                        st.text(content[:1000] + "..." if len(content) > 1000 else content)
                        
            if metadata:
                with st.expander("Prompt metadata"):
                    st.json(metadata)
    
    def _display_structured_prompt(self, content: str):
        """
        Display a structured CPRA analysis prompt.
        
        Args:
            content: The prompt content
        """
        # Extract CPRA requests
        if "CPRA REQUEST(S) TO ANALYZE:" in content:
            parts = content.split("CPRA REQUEST(S) TO ANALYZE:")
            if len(parts) > 1:
                request_part = parts[1].split("EMAIL DOCUMENT TO ANALYZE:")[0]
                email_part = parts[1].split("EMAIL DOCUMENT TO ANALYZE:")[1] if "EMAIL DOCUMENT TO ANALYZE:" in parts[1] else ""
                
                # Display CPRA requests
                st.markdown("**CPRA Requests to evaluate:**")
                for line in request_part.strip().split('\n'):
                    if line.strip() and line.strip().startswith("Request"):
                        st.markdown(f"- {line.strip()}")
                
                # Display email preview
                if email_part:
                    with st.expander("Email document being analyzed"):
                        st.text(email_part[:500] + "..." if len(email_part) > 500 else email_part)
    
    def display_response_stream(self, container, response_chunk: str, 
                               is_complete: bool = False):
        """
        Display streaming response from the AI.
        
        Args:
            container: Container to display in
            response_chunk: Chunk of response text
            is_complete: Whether this is the complete response
        """
        with container:
            if is_complete:
                # Try to parse as JSON for better display
                try:
                    response_json = json.loads(response_chunk)
                    self._display_formatted_response(response_json)
                except json.JSONDecodeError:
                    # Display as text if not JSON
                    st.code(response_chunk, language="text")
            else:
                # Show streaming progress
                st.warning("AI is processing...")
                st.text(response_chunk)
    
    def _display_formatted_response(self, response_json: Dict):
        """
        Display a formatted JSON response from the AI.
        
        Args:
            response_json: Parsed JSON response
        """
        if "responsive" in response_json:
            # Responsiveness analysis result
            st.markdown("**Responsiveness Analysis Result:**")
            
            responsive_list = response_json.get("responsive", [])
            confidence_list = response_json.get("confidence", [])
            reasoning_list = response_json.get("reasoning", [])
            
            for i, (responsive, confidence, reasoning) in enumerate(
                zip(responsive_list, confidence_list, reasoning_list)
            ):
                status_emoji = "✅" if responsive else "❌"
                confidence_color = {
                    "high": "green",
                    "medium": "orange", 
                    "low": "red"
                }.get(confidence.lower(), "gray")
                
                st.markdown(f"""
                **Request {i+1}:** {status_emoji} {'Responsive' if responsive else 'Not Responsive'}
                - **Confidence:** :{confidence_color}[{confidence}]
                - **Reasoning:** {reasoning}
                """)
                
        elif "exemptions" in response_json:
            # Exemption analysis result
            st.markdown("**Exemption Analysis Result:**")
            
            exemptions = response_json.get("exemptions", {})
            
            for exemption_type, data in exemptions.items():
                if data.get("applies"):
                    emoji = "⚠️"
                    status = "FOUND"
                else:
                    emoji = "✅"
                    status = "None"
                    
                st.markdown(f"""
                **{exemption_type.replace('_', ' ').title()}:** {emoji} {status}
                - **Confidence:** {data.get('confidence', 'unknown')}
                - **Reasoning:** {data.get('reasoning', 'No reasoning provided')}
                """)
        else:
            # Generic JSON display
            st.json(response_json)
    
    def display_processing_status(self, container, status: str, 
                                  email_info: Optional[Dict] = None):
        """
        Display current processing status.
        
        Args:
            container: Container to display in
            status: Status message
            email_info: Information about current email
        """
        with container:
            if email_info:
                st.info(f"""
                **Currently Processing:**
                - Email: {email_info.get('subject', 'No subject')}
                - From: {email_info.get('from', 'Unknown')}
                - Status: {status}
                """)
            else:
                st.info(f"**Status:** {status}")
    
    def display_metrics(self, container, metrics: Dict):
        """
        Display processing metrics and performance data.
        
        Args:
            container: Container to display in
            metrics: Dictionary of metrics to display
        """
        with container:
            st.markdown("#### Processing Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Prompt Tokens",
                    metrics.get('prompt_tokens', 0),
                    help="Number of tokens in the prompt"
                )
                
            with col2:
                st.metric(
                    "Response Tokens", 
                    metrics.get('response_tokens', 0),
                    help="Number of tokens in the response"
                )
                
            with col3:
                st.metric(
                    "Processing Time",
                    f"{metrics.get('processing_time', 0):.2f}s",
                    help="Time taken to generate response"
                )
                
            with col4:
                st.metric(
                    "Model",
                    metrics.get('model', 'Unknown'),
                    help="AI model being used"
                )
            
            # Show token/time graph if available
            if metrics.get('token_timeline'):
                st.markdown("##### Token Generation Timeline")
                st.line_chart(metrics['token_timeline'])
    
    def create_compact_display(self, container):
        """
        Create a compact display for sidebar or small spaces.
        
        Args:
            container: Container to render in
        """
        with container:
            st.markdown("#### AI Activity")
            
            # Simple status indicator
            status_placeholder = st.empty()
            
            # Compact metrics
            col1, col2 = st.columns(2)
            with col1:
                tokens_placeholder = st.empty()
            with col2:
                time_placeholder = st.empty()
                
            return {
                'status': status_placeholder,
                'tokens': tokens_placeholder,
                'time': time_placeholder
            }
    
    def update_compact_display(self, placeholders: Dict, status: str, 
                              tokens: int = 0, time_elapsed: float = 0):
        """
        Update compact display with current status.
        
        Args:
            placeholders: Dictionary of placeholder elements
            status: Current status message
            tokens: Token count
            time_elapsed: Time elapsed in seconds
        """
        placeholders['status'].info(status)
        placeholders['tokens'].metric("Tokens", tokens)
        placeholders['time'].metric("Time", f"{time_elapsed:.1f}s")


class StreamCallback:
    """Callback handler for streaming events."""
    
    def __init__(self, display: LLMStreamDisplay, containers: Dict[str, Any]):
        """
        Initialize the callback handler.
        
        Args:
            display: LLMStreamDisplay instance
            containers: Dictionary of containers for updates
        """
        self.display = display
        self.containers = containers
        self.start_time = None
        self.current_response = ""
        self.metrics = {
            'prompt_tokens': 0,
            'response_tokens': 0,
            'processing_time': 0,
            'model': ''
        }
    
    def on_prompt(self, prompt_type: str, content: str, metadata: Optional[Dict] = None):
        """
        Handle prompt event.
        
        Args:
            prompt_type: Type of prompt (system/user)
            content: Prompt content
            metadata: Optional metadata
        """
        # Estimate token count (rough approximation)
        self.metrics['prompt_tokens'] = len(content.split()) * 1.3
        
        if 'input' in self.containers:
            self.display.display_prompt(
                self.containers['input'],
                prompt_type,
                content,
                metadata
            )
    
    def on_processing_start(self, email_info: Optional[Dict] = None):
        """
        Handle processing start event.
        
        Args:
            email_info: Information about email being processed
        """
        self.start_time = time.time()
        self.current_response = ""
        
        if 'output' in self.containers:
            self.display.display_processing_status(
                self.containers['output'],
                "AI is analyzing document...",
                email_info
            )
    
    def on_response_chunk(self, chunk: str):
        """
        Handle response chunk event.
        
        Args:
            chunk: Chunk of response text
        """
        self.current_response += chunk
        
        if 'output' in self.containers:
            self.display.display_response_stream(
                self.containers['output'],
                self.current_response,
                is_complete=False
            )
    
    def on_response_complete(self, full_response: str, model: str = ""):
        """
        Handle response complete event.
        
        Args:
            full_response: Complete response text
            model: Model that generated the response
        """
        if self.start_time:
            self.metrics['processing_time'] = time.time() - self.start_time
        
        # Estimate response tokens
        self.metrics['response_tokens'] = len(full_response.split()) * 1.3
        self.metrics['model'] = model
        
        if 'output' in self.containers:
            self.display.display_response_stream(
                self.containers['output'],
                full_response,
                is_complete=True
            )
            
        if 'metrics' in self.containers:
            self.display.display_metrics(
                self.containers['metrics'],
                self.metrics
            )
    
    def on_error(self, error_message: str):
        """
        Handle error event.
        
        Args:
            error_message: Error message to display
        """
        if 'output' in self.containers:
            with self.containers['output']:
                st.error(f"Error during processing: {error_message}")


def create_llm_stream_display() -> Tuple[LLMStreamDisplay, StreamCallback]:
    """
    Factory function to create display and callback instances.
    
    Returns:
        Tuple of (display_instance, callback_handler)
    """
    display = LLMStreamDisplay()
    # Containers will be set when integrated into main app
    callback = StreamCallback(display, {})
    return display, callback