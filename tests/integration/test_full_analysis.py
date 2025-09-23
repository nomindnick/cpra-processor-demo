"""
Test full analysis with debug logging.
"""

import sys
import os
import logging
sys.path.append('src')

from processors.cpra_analyzer import CPRAAnalyzer, create_sample_cpra_requests
from parsers.email_parser import EmailParser

def test_full_analysis():
    """Test the full analysis with detailed logging."""
    # Set up debug logging
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        # Initialize analyzer
        analyzer = CPRAAnalyzer("gemma3:latest")
        
        # Load sample emails
        email_parser = EmailParser()
        with open("data/sample_emails/test_emails.txt", 'r') as f:
            emails = email_parser.parse_email_file(f.read())
        
        # Create sample CPRA requests
        cpra_requests = create_sample_cpra_requests()
        
        print(f"Testing with {len(emails)} emails and {len(cpra_requests)} CPRA requests")
        
        # Test single email analysis
        if emails:
            test_email = emails[0]
            print(f"\nTesting single email: {test_email.subject}")
            
            analysis = analyzer.analyze_email_responsiveness(test_email, cpra_requests, 0)
            
            if analysis:
                print(f"Analysis successful!")
                print(f"Email ID: {analysis.email_id}")
                print(f"Responsive to: {analysis.get_responsive_requests()}")
                print(f"Processing time: {analysis.processing_time_seconds:.2f}s")
                print(f"Responsive results: {analysis.responsive}")
                print(f"Confidence levels: {[c.value for c in analysis.confidence]}")
                print(f"Reasoning: {analysis.reasoning}")
            else:
                print("Analysis failed!")
                
    except Exception as e:
        print(f"Error running test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_analysis()