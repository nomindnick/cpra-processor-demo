#!/usr/bin/env python3
"""
Test the improved prompt display functionality.
Verifies that structured output instructions are properly shown.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.processors.cpra_analyzer import CPRAAnalyzer
from src.parsers.email_parser import EmailParser
from src.utils.data_structures import CPRARequest
from datetime import datetime


def test_improved_display():
    """Test that prompts are captured with full structured output instructions."""
    
    print("Testing Improved Prompt Display")
    print("=" * 50)
    
    # Track events
    captured_prompts = []
    
    def capture_callback(event_type, content, metadata):
        """Capture prompts for analysis."""
        if event_type in ['system_prompt', 'user_prompt']:
            captured_prompts.append({
                'type': event_type,
                'content': content,
                'metadata': metadata
            })
            print(f"✓ Captured {event_type}")
    
    # Create test data
    analyzer = CPRAAnalyzer(model_name="gemma3:latest")
    
    test_email_content = """From: test@agency.gov
To: team@agency.gov
Subject: Roof Leak Update
Date: Fri, 15 Mar 2024 10:30:00 -0800

Update on the roof leak situation at the Community Center."""
    
    parser = EmailParser()
    emails = parser.parse_email_file(test_email_content)
    
    if not emails:
        print("Failed to parse test email")
        return False
    
    cpra_requests = [
        CPRARequest(
            text="All documents regarding roof leaks",
            request_id="test_001"
        )
    ]
    
    print("\nRunning analysis to capture prompts...")
    print("-" * 50)
    
    # Run analysis
    result = analyzer.analyze_email_responsiveness(
        email=emails[0],
        cpra_requests=cpra_requests,
        email_index=0,
        stream_callback=capture_callback
    )
    
    if not result:
        print("Analysis failed")
        return False
    
    print(f"\n✅ Analysis complete")
    print(f"Captured {len(captured_prompts)} prompts")
    
    # Check system prompt for structured output instructions
    print("\nVerifying structured output instructions...")
    print("-" * 50)
    
    system_prompt = None
    for prompt in captured_prompts:
        if prompt['type'] == 'system_prompt':
            system_prompt = prompt['content']
            break
    
    if not system_prompt:
        print("❌ No system prompt captured")
        return False
    
    # Check for key instructions
    checks = [
        ("JSON format instructions", "You must respond with valid JSON"),
        ("Response format example", '"responsive": [true/false'),
        ("Confidence levels", '"confidence": ["high"/"medium"/"low"'),
        ("Reasoning field", '"reasoning": ["brief explanation'),
        ("Array length instruction", "EXACTLY")
    ]
    
    all_passed = True
    for check_name, check_text in checks:
        if check_text in system_prompt:
            print(f"✅ {check_name}: Found")
        else:
            print(f"❌ {check_name}: Missing")
            all_passed = False
    
    # Check display length
    json_start = system_prompt.find("You must respond with valid JSON")
    if json_start > 0:
        # Simulate what would be displayed
        display_start = max(0, json_start - 200)
        display_end = min(len(system_prompt), json_start + 800)
        display_length = display_end - display_start
        
        print(f"\nDisplay metrics:")
        print(f"  - Total prompt length: {len(system_prompt)} chars")
        print(f"  - JSON instruction position: {json_start}")
        print(f"  - Display window: {display_length} chars")
        print(f"  - Shows structured output: {'Yes' if display_length >= 600 else 'Partial'}")
        
        # Show what would be displayed
        print("\nSample of what audience would see:")
        print("=" * 50)
        display_content = system_prompt[display_start:display_end]
        if display_start > 0:
            display_content = "..." + display_content
        if display_end < len(system_prompt):
            display_content = display_content + "..."
        
        # Show first 500 chars of the display
        print(display_content[:500] + "..." if len(display_content) > 500 else display_content)
        print("=" * 50)
    
    return all_passed


if __name__ == "__main__":
    success = test_improved_display()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ IMPROVED DISPLAY TEST PASSED")
        print("\nThe structured output instructions are properly captured")
        print("and would be visible to the demonstration audience.")
    else:
        print("❌ IMPROVED DISPLAY TEST FAILED")
    
    sys.exit(0 if success else 1)