#!/usr/bin/env python3
"""
Resource monitoring component for demo mode.

Sprint 6 Implementation: System Resource Monitoring
- CPU usage tracking
- Memory usage display
- Model size indicator
- Network status display
"""

import streamlit as st
import psutil
import time
from typing import Dict, Optional
from src.utils.demo_utils import (
    check_network_connectivity,
    get_system_resources,
    estimate_model_memory_usage,
    format_bytes
)


class ResourceMonitor:
    """System resource monitoring for demo mode."""
    
    def __init__(self):
        """Initialize resource monitor."""
        self.last_update = time.time()
        self.update_interval = 1.0  # Update every second
        
    def create_resource_dashboard(self, container, model_name: str = "gemma3:latest"):
        """
        Create a resource monitoring dashboard.
        
        Args:
            container: Streamlit container to render in
            model_name: Name of the active model
        """
        # Get current resources
        resources = get_system_resources()
        network_status, network_msg = check_network_connectivity()
        
        # Create columns for metrics
        col1, col2, col3, col4 = container.columns(4)
        
        with col1:
            # CPU Usage with color coding
            cpu_color = self._get_usage_color(resources['cpu_percent'])
            st.metric(
                "🖥️ CPU Usage",
                f"{resources['cpu_percent']:.1f}%",
                delta=None,
                help="Current CPU utilization"
            )
            # Progress bar for visual impact
            st.progress(min(resources['cpu_percent'] / 100, 1.0))
        
        with col2:
            # Memory Usage
            mem_color = self._get_usage_color(resources['memory_percent'])
            st.metric(
                "💾 RAM Usage",
                f"{resources['memory_percent']:.1f}%",
                delta=f"{resources['memory_used_gb']:.1f}/{resources['memory_total_gb']:.1f} GB",
                help="System memory utilization"
            )
            st.progress(min(resources['memory_percent'] / 100, 1.0))
        
        with col3:
            # Model Memory
            model_size = estimate_model_memory_usage(model_name)
            st.metric(
                "🧠 Model Size",
                f"{model_size:.1f} GB",
                delta=None,
                help=f"Estimated memory for {model_name}"
            )
            # Show as portion of total RAM
            model_percent = (model_size / resources['memory_total_gb']) * 100
            st.progress(min(model_percent / 100, 1.0))
        
        with col4:
            # Network Status
            if network_status:
                st.error(network_msg)  # Show online as error (should be offline for demo)
                st.caption("⚠️ Disable network for demo")
            else:
                st.success(network_msg)  # Show offline as success (airplane mode)
                st.caption("✅ Ready for offline demo")
    
    def create_compact_monitor(self, container):
        """
        Create a compact resource monitor for sidebar.
        
        Args:
            container: Streamlit container to render in
        """
        resources = get_system_resources()
        network_status, network_msg = check_network_connectivity()
        
        container.markdown("### 📊 System Resources")
        
        # CPU and Memory bars
        container.markdown(f"**CPU:** {resources['cpu_percent']:.1f}%")
        container.progress(min(resources['cpu_percent'] / 100, 1.0))
        
        container.markdown(f"**RAM:** {resources['memory_percent']:.1f}%")
        container.progress(min(resources['memory_percent'] / 100, 1.0))
        
        # Network status badge
        if network_status:
            container.error(f"Status: {network_msg}")
        else:
            container.success(f"Status: {network_msg}")
    
    def create_processing_monitor(self, container, phase: str = "idle", model_active: bool = False):
        """
        Create a processing-specific monitor.
        
        Args:
            container: Streamlit container
            phase: Current processing phase
            model_active: Whether model is actively processing
        """
        resources = get_system_resources()
        
        # Create metrics row
        col1, col2, col3 = container.columns(3)
        
        with col1:
            # Processing Phase
            phase_emoji = {
                "idle": "⏸️",
                "responsiveness": "🔍",
                "exemptions": "🛡️",
                "finalize": "✅"
            }
            st.metric(
                "Phase",
                phase.title(),
                delta=phase_emoji.get(phase, "⚙️"),
                help="Current processing phase"
            )
        
        with col2:
            # Model Activity
            if model_active:
                st.metric(
                    "AI Status",
                    "🧠 Active",
                    delta=f"CPU: {resources['cpu_percent']:.0f}%",
                    help="Model is processing"
                )
            else:
                st.metric(
                    "AI Status",
                    "💤 Idle",
                    delta=None,
                    help="Model is waiting"
                )
        
        with col3:
            # Performance
            st.metric(
                "Performance",
                f"{resources['memory_used_gb']:.1f} GB",
                delta=f"of {resources['memory_total_gb']:.1f} GB",
                help="Memory usage"
            )
    
    def _get_usage_color(self, percentage: float) -> str:
        """
        Get color based on usage percentage.
        
        Args:
            percentage: Usage percentage (0-100)
        
        Returns:
            Color name for display
        """
        if percentage < 50:
            return "green"
        elif percentage < 75:
            return "yellow"
        else:
            return "red"
    
    def should_update(self) -> bool:
        """
        Check if monitor should update based on interval.
        
        Returns:
            True if should update
        """
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            self.last_update = current_time
            return True
        return False


def create_performance_gauge(value: float, max_value: float, label: str, container):
    """
    Create a visual gauge chart for performance metrics.
    
    Args:
        value: Current value
        max_value: Maximum value
        label: Gauge label
        container: Streamlit container
    """
    percentage = (value / max_value) * 100 if max_value > 0 else 0
    
    # Create visual gauge using Unicode blocks
    filled = int(percentage / 10)
    empty = 10 - filled
    
    gauge = "█" * filled + "░" * empty
    
    # Color based on percentage
    if percentage < 50:
        color = "🟢"
    elif percentage < 75:
        color = "🟡"
    else:
        color = "🔴"
    
    container.markdown(f"{label}: {color} {gauge} {percentage:.0f}%")


def create_model_comparison_chart(container):
    """
    Create a comparison chart of different model sizes.
    
    Args:
        container: Streamlit container
    """
    models = {
        "gemma3:latest": 3.3,
        "phi4-mini": 3.2,
        "llama3.2": 5.4,
        "gpt-oss:20b": 13.0
    }
    
    container.markdown("### 🤖 Model Comparison")
    
    for model, size in models.items():
        # Create visual bar
        bar_length = int((size / 16) * 20)  # Scale to 16GB max
        bar = "▓" * bar_length + "░" * (20 - bar_length)
        
        container.markdown(f"**{model}**")
        container.markdown(f"`{bar}` {size:.1f} GB")
        
        # Show if it fits in common RAM sizes
        if size <= 8:
            container.caption("✅ Runs on 8GB RAM")
        elif size <= 16:
            container.caption("⚠️ Needs 16GB RAM")
        else:
            container.caption("❌ Needs 32GB+ RAM")