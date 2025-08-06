#!/usr/bin/env python3
"""
Demo utilities for enhanced visual processing demonstration.

Sprint 6 Implementation: Demo Mode Features
- Network connectivity checking
- Demo data loading
- Animation helpers
- Processing delays for visual impact
"""

import time
import socket
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import psutil
import streamlit as st


def check_network_connectivity() -> Tuple[bool, str]:
    """
    Check if network connectivity is available.
    
    Returns:
        Tuple of (is_connected, status_message)
    """
    try:
        # Try to create a socket connection to common DNS servers
        socket.create_connection(("8.8.8.8", 53), timeout=1)
        return True, "Online"
    except (socket.error, socket.timeout):
        return False, "Offline (Airplane Mode)"


def get_system_resources() -> Dict[str, float]:
    """
    Get current system resource usage.
    
    Returns:
        Dictionary with CPU and memory usage percentages
    """
    return {
        'cpu_percent': psutil.cpu_percent(interval=0.1),
        'memory_percent': psutil.virtual_memory().percent,
        'memory_used_gb': psutil.virtual_memory().used / (1024**3),
        'memory_total_gb': psutil.virtual_memory().total / (1024**3)
    }


def load_demo_data() -> Tuple[str, List[str]]:
    """
    Load demonstration data from demo-files directory.
    
    Returns:
        Tuple of (email_content, cpra_requests)
    """
    demo_dir = Path("demo-files")
    
    # Load emails
    email_file = demo_dir / "synthetic_emails.txt"
    if email_file.exists():
        with open(email_file, 'r', encoding='utf-8') as f:
            email_content = f.read()
    else:
        # Fallback to test data if demo files not available
        test_file = Path("data/sample_emails/test_emails.txt")
        if test_file.exists():
            with open(test_file, 'r', encoding='utf-8') as f:
                email_content = f.read()
        else:
            email_content = ""
    
    # Load CPRA requests
    requests_file = demo_dir / "cpra_requests.txt"
    cpra_requests = []
    if requests_file.exists():
        with open(requests_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Parse requests - look for "Request 1:", "Request 2:", etc.
            lines = content.split('\n')
            current_request = ""
            in_request = False
            
            for line in lines:
                if line.startswith("Request ") and ":" in line:
                    # Start of a new request
                    if current_request:
                        cpra_requests.append(current_request.strip())
                    in_request = True
                    current_request = ""
                elif in_request and line.strip():
                    # Continue building the request
                    if not line.startswith("===") and not line.startswith("---"):
                        current_request += line.strip() + " "
                elif in_request and not line.strip():
                    # End of request on empty line
                    if current_request:
                        cpra_requests.append(current_request.strip())
                        current_request = ""
                        in_request = False
            
            # Don't forget the last request
            if current_request:
                cpra_requests.append(current_request.strip())
    
    # Fallback requests if none found
    if not cpra_requests:
        cpra_requests = [
            "All documents regarding roof leaks, water damage, or water intrusion at the Community Center",
            "All documents related to Change Order #3 including electrical upgrades and cost negotiations",
            "All emails discussing construction delays or schedule impacts between January and April 2024"
        ]
    
    return email_content, cpra_requests


def simulate_processing_delay(demo_mode: bool, base_delay: float = 0.5, speed_multiplier: float = 1.0):
    """
    Add configurable delay for visual impact during demo.
    
    Args:
        demo_mode: Whether demo mode is active
        base_delay: Base delay in seconds
        speed_multiplier: Speed multiplier (0.5 = half speed, 2.0 = double speed)
    """
    if demo_mode:
        actual_delay = base_delay / speed_multiplier
        time.sleep(actual_delay)


def typewriter_effect(text: str, container, demo_mode: bool, speed: float = 0.03):
    """
    Display text with typewriter effect for dramatic impact.
    
    Args:
        text: Text to display
        container: Streamlit container to update
        demo_mode: Whether to use effect
        speed: Seconds between characters
    """
    if not demo_mode:
        container.text(text)
        return
    
    displayed = ""
    placeholder = container.empty()
    
    for char in text:
        displayed += char
        placeholder.text(displayed)
        time.sleep(speed)


def get_ai_thinking_animation(phase: str = "analyzing") -> str:
    """
    Get animated text for AI thinking indicator.
    
    Args:
        phase: Current processing phase
    
    Returns:
        Animated string for status display
    """
    animations = {
        "analyzing": ["AI Analyzing", "AI Analyzing.", "AI Analyzing..", "AI Analyzing..."],
        "responsiveness": ["Checking Responsiveness", "Checking Responsiveness.", "Checking Responsiveness..", "Checking Responsiveness..."],
        "exemptions": ["Scanning for Exemptions", "Scanning for Exemptions.", "Scanning for Exemptions..", "Scanning for Exemptions..."],
        "thinking": ["AI Processing", "AI Processing.", "AI Processing..", "AI Processing..."]
    }
    
    # Get animation frames for the phase
    frames = animations.get(phase, animations["thinking"])
    
    # Return a frame based on current time
    import time
    frame_index = int(time.time() * 2) % len(frames)
    return frames[frame_index]


def get_phase_color(phase: str) -> str:
    """
    Get color for processing phase indicator.
    
    Args:
        phase: Processing phase name
    
    Returns:
        Color name for Streamlit
    """
    colors = {
        "responsiveness": "blue",
        "exemptions": "orange", 
        "finalize": "green",
        "idle": "gray"
    }
    return colors.get(phase, "gray")


def format_processing_stats(
    emails_processed: int,
    total_emails: int,
    responsive_count: int,
    exemption_count: int,
    elapsed_time: float
) -> Dict[str, str]:
    """
    Format processing statistics for display.
    
    Args:
        emails_processed: Number of emails processed
        total_emails: Total number of emails
        responsive_count: Number of responsive documents
        exemption_count: Number of documents with exemptions
        elapsed_time: Elapsed processing time in seconds
    
    Returns:
        Dictionary of formatted statistics
    """
    avg_time = elapsed_time / emails_processed if emails_processed > 0 else 0
    
    return {
        "progress": f"{emails_processed}/{total_emails}",
        "progress_percent": f"{(emails_processed/total_emails)*100:.1f}%",
        "responsive": str(responsive_count),
        "responsive_percent": f"{(responsive_count/emails_processed)*100:.1f}%" if emails_processed > 0 else "0%",
        "exemptions": str(exemption_count),
        "exemption_percent": f"{(exemption_count/emails_processed)*100:.1f}%" if emails_processed > 0 else "0%",
        "elapsed": f"{elapsed_time:.1f}s",
        "average": f"{avg_time:.1f}s/email",
        "estimated_remaining": f"{(total_emails - emails_processed) * avg_time:.0f}s" if emails_processed > 0 else "N/A"
    }


def create_demo_sidebar_controls():
    """
    Create demo mode controls in the sidebar.
    
    Returns:
        Dictionary of demo settings
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Demo Controls")
    
    demo_settings = {}
    
    # Demo mode toggle
    demo_settings['enabled'] = st.sidebar.checkbox(
        "Demo Mode",
        value=st.session_state.get('demo_mode', False),
        help="Enable visual enhancements for presentation"
    )
    
    if demo_settings['enabled']:
        # Processing speed
        demo_settings['speed'] = st.sidebar.slider(
            "Processing Speed",
            min_value=0.5,
            max_value=3.0,
            value=1.0,
            step=0.5,
            format="%.1fx",
            help="Adjust processing animation speed"
        )
        
        # Visual effects
        demo_settings['animations'] = st.sidebar.checkbox(
            "Enable Animations",
            value=True,
            help="Show animated progress indicators"
        )
        
        demo_settings['typewriter'] = st.sidebar.checkbox(
            "Typewriter Effect",
            value=True,
            help="Display logs with typewriter effect"
        )
        
        demo_settings['resource_monitor'] = st.sidebar.checkbox(
            "Show Resources",
            value=True,
            help="Display system resource usage"
        )
        
        # Auto-load demo data
        if st.sidebar.button("Load Demo Data", type="secondary"):
            email_content, cpra_requests = load_demo_data()
            st.session_state['demo_data_loaded'] = True
            st.session_state['demo_emails'] = email_content
            st.session_state['demo_requests'] = cpra_requests
            st.sidebar.success("Demo data loaded!")
    
    return demo_settings


def show_model_activity_indicator(container, is_active: bool, model_name: str = "gemma3"):
    """
    Display model activity indicator.
    
    Args:
        container: Streamlit container
        is_active: Whether model is currently active
        model_name: Name of the active model
    """
    if is_active:
        # Animated indicator
        animation = get_ai_thinking_animation("thinking")
        container.info(f"{animation} | Model: {model_name}")
    else:
        container.empty()


def create_phase_indicator(phase: str, is_active: bool = False) -> str:
    """
    Create a visual phase indicator.
    
    Args:
        phase: Phase name
        is_active: Whether this phase is currently active
    
    Returns:
        Formatted phase indicator string
    """
    indicators = {
        "upload": "Upload",
        "responsiveness": "Responsiveness Analysis",
        "exemptions": "Exemption Detection",
        "review": "Review",
        "export": "Export"
    }
    
    indicator = indicators.get(phase, phase)
    
    if is_active:
        # Add active indicator
        return f"► {indicator}"
    else:
        return f"  {indicator}"


def estimate_model_memory_usage(model_name: str) -> float:
    """
    Estimate memory usage for a given model.
    
    Args:
        model_name: Name of the Ollama model
    
    Returns:
        Estimated memory usage in GB
    """
    model_sizes = {
        "gemma3:latest": 3.3,
        "phi4-mini-reasoning:3.8b": 3.2,
        "gpt-oss:20b": 13.0,
        "llama3.2:latest": 5.4
    }
    
    return model_sizes.get(model_name, 4.0)  # Default 4GB


def format_bytes(bytes_value: float) -> str:
    """
    Format bytes into human-readable format.
    
    Args:
        bytes_value: Number of bytes
    
    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"