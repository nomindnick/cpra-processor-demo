#!/usr/bin/env python3
"""
Test Sprint 5 Streamlit Interface Implementation
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pathlib import Path
from datetime import datetime

# Test imports
def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from src.parsers.email_parser import EmailParser
        from src.processors.cpra_analyzer import CPRAAnalyzer
        from src.processors.review_manager import ReviewManager
        from src.processors.session_manager import SessionManager
        from src.processors.export_manager import ExportManager
        from src.utils.data_structures import (
            Email, ProcessingSession, ResponsivenessAnalysis,
            ExemptionAnalysis, DocumentReview, ReviewDecision,
            ReviewStatus
        )
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_sample_data():
    """Test that sample data can be loaded and parsed."""
    print("\nTesting sample data loading...")
    
    sample_file_path = Path("data/sample_emails/test_emails.txt")
    if not sample_file_path.exists():
        print(f"❌ Sample data file not found: {sample_file_path}")
        return False
    
    try:
        from src.parsers.email_parser import EmailParser
        
        with open(sample_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parser = EmailParser()
        emails = parser.parse_email_file(content)
        
        print(f"✅ Parsed {len(emails)} emails from sample data")
        
        # Show first few email subjects
        for i, email in enumerate(emails[:3], 1):
            print(f"  {i}. {email.subject or '(No subject)'}")
        
        return True
    except Exception as e:
        print(f"❌ Error loading sample data: {e}")
        return False


def test_session_initialization():
    """Test that a processing session can be initialized."""
    print("\nTesting session initialization...")
    
    try:
        from src.utils.data_structures import ProcessingSession, CPRARequest
        
        cpra_requests = [CPRARequest(text="Test request 1"), CPRARequest(text="Test request 2")]
        session = ProcessingSession(
            session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
            cpra_requests=cpra_requests
        )
        
        print(f"✅ Session created with ID: {session.session_id}")
        return True
    except Exception as e:
        print(f"❌ Error creating session: {e}")
        return False


def test_review_manager():
    """Test that review manager can be initialized."""
    print("\nTesting review manager...")
    
    try:
        from src.processors.review_manager import ReviewManager
        from src.parsers.email_parser import EmailParser
        from pathlib import Path
        
        # Load sample emails
        sample_file_path = Path("data/sample_emails/test_emails.txt")
        with open(sample_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parser = EmailParser()
        emails = parser.parse_email_file(content)
        
        # Create review manager and session
        from src.utils.data_structures import ProcessingSession, CPRARequest
        
        session = ProcessingSession(
            session_id="test_session",
            cpra_requests=[CPRARequest(text="Test request")],
            emails=emails
        )
        
        review_manager = ReviewManager()
        review_manager.initialize_reviews(session)
        
        summary = review_manager.get_review_summary(session)
        print(f"✅ Review manager initialized with {summary['total_documents']} documents")
        return True
    except Exception as e:
        print(f"❌ Error with review manager: {e}")
        return False


def test_export_manager():
    """Test that export manager can be initialized."""
    print("\nTesting export manager...")
    
    try:
        from src.processors.export_manager import ExportManager
        from src.processors.review_manager import ReviewManager
        from src.utils.data_structures import ProcessingSession
        from src.parsers.email_parser import EmailParser
        from pathlib import Path
        from datetime import datetime
        
        # Create test session
        from src.utils.data_structures import CPRARequest
        cpra_requests = [CPRARequest(text="Test request")]
        session = ProcessingSession(
            session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
            cpra_requests=cpra_requests
        )
        
        # Load sample emails
        sample_file_path = Path("data/sample_emails/test_emails.txt")
        with open(sample_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parser = EmailParser()
        emails = parser.parse_email_file(content)[:1]  # Just test with first email
        
        # Create review manager and session
        from src.utils.data_structures import ProcessingSession, CPRARequest
        
        session = ProcessingSession(
            session_id="test_session",
            cpra_requests=[CPRARequest(text="Test request")],
            emails=emails
        )
        
        review_manager = ReviewManager()
        review_manager.initialize_reviews(session)
        
        # Create export manager
        export_manager = ExportManager(output_dir="data/test_exports")
        
        print("✅ Export manager initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error with export manager: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Sprint 5: Streamlit Interface Testing")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_sample_data,
        test_session_initialization,
        test_review_manager,
        test_export_manager
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✅ All tests passed! Sprint 5 interface is ready.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)