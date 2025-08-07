#!/usr/bin/env python3
"""
Test script to verify UI streaming functionality is working.
This simulates what happens in the main app during processing.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.models.ollama_client import OllamaClient
from src.parsers.email_parser import EmailParser
from src.processors.cpra_analyzer import CPRAAnalyzer
from src.utils.data_structures import CPRARequest
import time
from datetime import datetime


def test_ui_streaming():
    """Test UI streaming with session state simulation."""
    
    print("Testing UI Streaming Functionality")
    print("=" * 50)
    
    # Simulate session state
    class SessionState:
        def __init__(self):
            self.stream_events = []
    
    session_state = SessionState()
    
    # Create streaming callback that stores events like the UI does
    def stream_callback(event_type, content, metadata):
        """Callback that mimics UI behavior."""
        event = {
            'type': event_type,
            'content': content,
            'metadata': metadata if metadata else {},
            'timestamp': datetime.now()
        }
        session_state.stream_events.append(event)
        
        # Show progress
        if event_type == 'response_chunk':
            print(".", end="", flush=True)
        else:
            print(f"\n[{event_type.upper()}] captured")
    
    # Initialize components
    print("\n1. Initializing components...")
    analyzer = CPRAAnalyzer(model_name="gemma3:latest")
    
    # Create test email
    print("\n2. Creating test email...")
    test_email_content = """From: john.smith@agency.gov
To: team@agency.gov
Subject: Roof Leak Update - Community Center
Date: Fri, 15 Mar 2024 10:30:00 -0800

Team,

I wanted to update everyone on the roof leak situation at the Community Center. 
The contractor has identified the source of the water intrusion and will begin 
repairs tomorrow. This should resolve the ongoing water damage issues we've been 
experiencing in the north wing.

Best regards,
John Smith"""
    
    parser = EmailParser()
    emails = parser.parse_email_file(test_email_content)
    
    if not emails:
        print("Error: Failed to parse test email")
        return False
    
    test_email = emails[0]
    print(f"   Email parsed: {test_email.subject}")
    
    # Create test CPRA request
    print("\n3. Creating CPRA request...")
    cpra_requests = [
        CPRARequest(
            text="All documents regarding roof leaks or water damage at the Community Center",
            request_id="test_001"
        )
    ]
    print(f"   Request: {cpra_requests[0].text}")
    
    # Test analysis with streaming
    print("\n4. Running analysis with streaming (simulating UI behavior)...")
    print("-" * 50)
    
    result = analyzer.analyze_email_responsiveness(
        email=test_email,
        cpra_requests=cpra_requests,
        email_index=0,
        stream_callback=stream_callback
    )
    
    print("\n")
    
    if result:
        print(f"✅ Analysis completed successfully")
        print(f"   Result: {'Responsive' if result.is_responsive_to_any() else 'Not Responsive'}")
    else:
        print("❌ Analysis failed")
        return False
    
    # Check session state (simulating what UI would see)
    print("\n5. Checking captured events (simulating UI display)...")
    print("-" * 50)
    
    events_count = len(session_state.stream_events)
    print(f"Total events captured: {events_count}")
    
    if events_count > 0:
        print("\n✅ Stream events successfully captured!")
        print("\nEvent breakdown:")
        
        event_types = {}
        for event in session_state.stream_events:
            event_type = event['type']
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        for event_type, count in event_types.items():
            print(f"  - {event_type}: {count}")
        
        # Show sample events
        print("\nFirst 3 events:")
        for i, event in enumerate(session_state.stream_events[:3]):
            content = event.get('content', '')
            content_preview = (content[:50] + '...') if content and len(content) > 50 else content
            print(f"  {i+1}. {event['type']}: {content_preview if content else '(no content)'}")
        
        print("\nLast event:")
        last_event = session_state.stream_events[-1]
        content = last_event.get('content', '')
        content_preview = (content[:50] + '...') if content and len(content) > 50 else content
        print(f"  {last_event['type']}: {content_preview if content else '(no content)'}")
        
        return True
    else:
        print("\n❌ No stream events captured")
        return False


if __name__ == "__main__":
    # Check if Ollama is running
    client = OllamaClient()
    if not client.test_connectivity():
        print("Error: Cannot connect to Ollama. Please ensure Ollama is running.")
        print("Start Ollama with: ollama serve")
        sys.exit(1)
    
    # Check if required model is available
    models = client.list_models()
    if "gemma3:latest" not in models:
        print("Error: gemma3:latest model not found.")
        print("Please pull the model with: ollama pull gemma3:latest")
        sys.exit(1)
    
    # Run the test
    success = test_ui_streaming()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ UI STREAMING TEST PASSED")
        print("\nThe streaming functionality is working correctly.")
        print("Events are being captured and would be displayed in the UI.")
    else:
        print("❌ UI STREAMING TEST FAILED")
    
    sys.exit(0 if success else 1)