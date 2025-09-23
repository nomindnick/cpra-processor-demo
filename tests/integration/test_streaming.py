#!/usr/bin/env python3
"""
Test script for LLM streaming visualization functionality.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.models.ollama_client import OllamaClient
from src.parsers.email_parser import EmailParser
from src.processors.cpra_analyzer import CPRAAnalyzer
from src.utils.data_structures import CPRARequest
import time


def test_streaming_callback():
    """Test the streaming callback functionality."""
    
    print("Testing LLM Streaming Visualization\n" + "="*50)
    
    # Track events
    events = []
    
    def stream_callback(event_type, content, metadata):
        """Callback to capture streaming events."""
        events.append({
            'type': event_type,
            'content': content[:100] if content and len(content) > 100 else content,
            'metadata': metadata,
            'timestamp': time.time()
        })
        
        # Print events in real-time
        if event_type == 'system_prompt':
            print(f"\n[SYSTEM PROMPT] Model: {metadata.get('model', 'unknown')}")
            print(f"Content preview: {content[:200]}...")
        elif event_type == 'user_prompt':
            print(f"\n[USER PROMPT] Requests: {metadata.get('requests_count', 0)}")
            print(f"Content preview: {content[:200]}...")
        elif event_type == 'processing_start':
            print(f"\n[PROCESSING START] Attempt: {metadata.get('attempt', 1)}")
        elif event_type == 'response_chunk':
            print(".", end="", flush=True)  # Show progress dots
        elif event_type == 'response_complete':
            print(f"\n[RESPONSE COMPLETE] Model: {metadata.get('model', 'unknown')}")
            print(f"Response preview: {content[:200]}...")
    
    try:
        # Initialize components
        print("\n1. Initializing components...")
        analyzer = CPRAAnalyzer(model_name="gemma3:latest")
        
        # Create test email - use exact format from demo files
        print("\n2. Creating test email...")
        # Note: EmailParser expects emails to start with "From:" at beginning of content
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
John Smith

From: jane.doe@agency.gov
To: legal@agency.gov
Subject: Non-responsive test email
Date: Fri, 15 Mar 2024 11:00:00 -0800

This is a test email about something completely unrelated to the CPRA request.
It's about scheduling a meeting for next week's budget review.

Thanks,
Jane"""
        
        parser = EmailParser()
        emails = parser.parse_email_file(test_email_content)
        
        if not emails:
            print("Error: Failed to parse test email")
            return False
        
        test_email = emails[0]
        print(f"   Email parsed: {test_email.subject}")
        
        # Create test CPRA request
        print("\n3. Creating test CPRA request...")
        cpra_requests = [
            CPRARequest(
                text="All documents regarding roof leaks or water damage at the Community Center",
                request_id="test_001"
            )
        ]
        print(f"   Request: {cpra_requests[0].text}")
        
        # Test responsiveness analysis with streaming
        print("\n4. Testing responsiveness analysis with streaming...")
        print("-" * 50)
        
        result = analyzer.analyze_email_responsiveness(
            email=test_email,
            cpra_requests=cpra_requests,
            email_index=0,
            stream_callback=stream_callback
        )
        
        if result:
            print(f"\n   Result: {'Responsive' if result.is_responsive_to_any() else 'Not Responsive'}")
            print(f"   Confidence: {result.confidence}")
            print(f"   Reasoning: {result.reasoning}")
        else:
            print("\n   Error: Analysis failed")
            return False
        
        # Test exemption analysis with streaming
        print("\n5. Testing exemption analysis with streaming...")
        print("-" * 50)
        
        # Clear events for second test
        events.clear()
        
        exemption_result = analyzer.analyze_email_exemptions(
            email=test_email,
            email_index=0,
            stream_callback=stream_callback
        )
        
        if exemption_result:
            print(f"\n   Exemptions found: {exemption_result.has_any_exemption()}")
            if exemption_result.has_any_exemption():
                for exemption in exemption_result.get_applicable_exemptions():
                    print(f"   - {exemption.value}")
        else:
            print("\n   Error: Exemption analysis failed")
            return False
        
        # Summary
        print("\n" + "="*50)
        print("STREAMING TEST SUMMARY")
        print("="*50)
        print(f"Total events captured: {len(events)}")
        
        event_types = {}
        for event in events:
            event_type = event['type']
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        print("\nEvent breakdown:")
        for event_type, count in event_types.items():
            print(f"  - {event_type}: {count}")
        
        print("\n✅ Streaming test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
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
    success = test_streaming_callback()
    sys.exit(0 if success else 1)