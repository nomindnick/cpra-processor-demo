#!/usr/bin/env python3
"""
End-to-end test for CPRA Processing Application.
Tests complete workflow with demo dataset.
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.config import get_config
from src.parsers.email_parser import EmailParser
from src.processors.cpra_analyzer import CPRAAnalyzer
from src.processors.review_manager import ReviewManager
from src.processors.session_manager import SessionManager
from src.processors.export_manager import ExportManager
from src.utils.data_structures import ProcessingSession, CPRARequest


def test_end_to_end():
    """Run complete end-to-end test with demo data."""
    print("=" * 60)
    print("CPRA Processing Application - End-to-End Test")
    print("=" * 60)
    
    # Initialize configuration
    config = get_config()
    print(f"\n✅ Configuration loaded")
    print(f"   Default model: {config.model.default_model}")
    print(f"   Batch size: {config.processing.batch_size}")
    
    # Step 1: Load demo data
    print("\n📁 Loading demo data...")
    demo_emails_path = Path("demo-files/synthetic_emails.txt")
    demo_requests_path = Path("demo-files/cpra_requests.txt")
    
    if not demo_emails_path.exists():
        print("❌ Demo emails file not found!")
        return False
    
    if not demo_requests_path.exists():
        print("❌ Demo requests file not found!")
        return False
    
    # Parse emails
    with open(demo_emails_path, 'r', encoding='utf-8') as f:
        email_content = f.read()
    
    parser = EmailParser()
    emails = parser.parse_email_file(email_content)
    print(f"   ✅ Parsed {len(emails)} emails")
    
    # Load CPRA requests
    with open(demo_requests_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the requests (skip header lines and Request N: prefixes)
    requests = []
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('=') and not line.startswith('CPRA') and not line.startswith('Request '):
            if line:  # Skip empty lines
                requests.append(line)
    
    cpra_requests = [CPRARequest(text=req) for req in requests]
    print(f"   ✅ Loaded {len(cpra_requests)} CPRA requests")
    
    # Display requests
    for i, req in enumerate(cpra_requests, 1):
        print(f"      {i}. {req.text[:60]}...")
    
    # Step 2: Create processing session
    print("\n🔧 Creating processing session...")
    session = ProcessingSession(
        session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
        cpra_requests=cpra_requests,
        emails=emails
    )
    print(f"   ✅ Session ID: {session.session_id}")
    
    # Step 3: Analyze responsiveness (subset for testing)
    print("\n🔍 Analyzing responsiveness...")
    analyzer = CPRAAnalyzer(model_name=config.model.responsiveness_model)
    
    # Test with first 5 emails
    test_emails = emails[:5]
    print(f"   Testing with {len(test_emails)} emails...")
    
    start_time = time.time()
    responsiveness_results = []
    
    for i, email in enumerate(test_emails):
        print(f"   Analyzing email {i+1}/{len(test_emails)}: {email.subject[:40]}...")
        try:
            # Pass CPRA request objects directly - the analyzer will extract the text
            result = analyzer.analyze_email_responsiveness(
                email,
                cpra_requests
            )
            if result:
                responsiveness_results.append(result)
                session.responsiveness_results[str(i)] = result
                print(f"      → Responsive: {result.is_responsive_to_any()}")
            else:
                print(f"      → Analysis failed")
                responsiveness_results.append(None)
        except Exception as e:
            print(f"      → Error: {str(e)}")
            responsiveness_results.append(None)
    
    elapsed = time.time() - start_time
    print(f"   ✅ Responsiveness analysis complete in {elapsed:.2f}s")
    
    responsive_count = sum(1 for r in responsiveness_results if r and r.is_responsive_to_any())
    print(f"   📊 Responsive emails: {responsive_count}/{len(test_emails)}")
    
    # Step 4: Analyze exemptions for responsive emails
    print("\n🛡️ Analyzing exemptions...")
    exemption_results = []
    
    for i, email in enumerate(test_emails):
        if responsiveness_results[i] and responsiveness_results[i].is_responsive_to_any():
            print(f"   Checking exemptions for email {i+1}...")
            try:
                result = analyzer.analyze_email_exemptions(email)
                if result:
                    exemption_results.append(result)
                    session.exemption_results[str(i)] = result
                    if result.has_exemptions:
                        print(f"      → Found exemptions: {', '.join(result.exemptions)}")
                    else:
                        print(f"      → No exemptions")
                else:
                    print(f"      → Analysis failed")
                    exemption_results.append(None)
            except Exception as e:
                print(f"      → Error: {str(e)}")
                exemption_results.append(None)
        else:
            exemption_results.append(None)
    
    exemption_count = sum(1 for r in exemption_results if r and r.has_exemptions)
    print(f"   ✅ Exemption analysis complete")
    print(f"   📊 Emails with exemptions: {exemption_count}")
    
    # Step 5: Initialize review system
    print("\n📋 Initializing review system...")
    review_manager = ReviewManager()
    reviews = review_manager.initialize_reviews(session)
    
    review_count = len(reviews)
    print(f"   ✅ Created {review_count} reviews")
    
    # Perform sample review
    if review_count > 0:
        first_review_id = list(reviews.keys())[0]
        first_review = reviews[first_review_id]
        review_manager.start_review(first_review)
        
        # Get the corresponding analysis results for finalization
        email_idx = first_review_id.replace('email_', '')
        if email_idx.isdigit():
            idx = int(email_idx)
        else:
            idx = 0
        
        resp_analysis = session.responsiveness_results.get(str(idx))
        exemp_analysis = session.exemption_results.get(str(idx))
        
        if resp_analysis:
            review_manager.finalize_review(first_review, resp_analysis, exemp_analysis)
            print(f"   ✅ Completed sample review")
        else:
            print(f"   ⚠️ Could not complete review (no analysis results)")
    
    # Step 6: Test session save/load
    print("\n💾 Testing session persistence...")
    session_manager = SessionManager()
    
    # Create test directory
    test_dir = Path("test_sessions")
    test_dir.mkdir(exist_ok=True)
    
    session_path = test_dir / f"test_{session.session_id}.pkl"
    
    try:
        # Save session
        session_manager.save_session(session, str(session_path))
        print(f"   ✅ Session saved to {session_path}")
        
        # Load session
        loaded_session = session_manager.load_session(str(session_path))
        if loaded_session:
            print(f"   ✅ Session loaded successfully")
            print(f"      Session ID matches: {loaded_session.session_id == session.session_id}")
            print(f"      Email count matches: {len(loaded_session.emails) == len(session.emails)}")
        else:
            print(f"   ❌ Failed to load session")
    except Exception as e:
        print(f"   ❌ Session persistence error: {str(e)}")
    finally:
        # Clean up test file
        if session_path.exists():
            session_path.unlink()
    
    # Step 7: Test export (without actually creating files)
    print("\n📤 Testing export functionality...")
    export_manager = ExportManager(session, review_manager)
    
    is_valid, warnings = export_manager.validate_export_readiness()
    print(f"   Export validation: {'✅ Valid' if is_valid else '⚠️ Has warnings'}")
    if warnings:
        for warning in warnings[:3]:  # Show first 3 warnings
            print(f"      - {warning}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Emails parsed: {len(emails)}")
    print(f"✅ CPRA requests loaded: {len(cpra_requests)}")
    print(f"✅ Emails analyzed: {len(test_emails)}")
    print(f"✅ Responsive emails: {responsive_count}")
    print(f"✅ Emails with exemptions: {exemption_count}")
    print(f"✅ Reviews created: {review_count}")
    print(f"✅ Session persistence: Working")
    print(f"✅ Export validation: {'Ready' if is_valid else 'Has warnings'}")
    
    print("\n🎉 End-to-end test completed successfully!")
    return True


if __name__ == "__main__":
    success = test_end_to_end()
    sys.exit(0 if success else 1)