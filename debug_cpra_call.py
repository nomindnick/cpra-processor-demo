"""
Debug the exact CPRA analysis call.
"""

import sys
import os
import logging
sys.path.append('src')

from models.ollama_client import OllamaClient
from parsers.email_parser import EmailParser
from processors.cpra_analyzer import create_sample_cpra_requests

def debug_cpra_call():
    """Debug the exact CPRA analysis call."""
    logging.basicConfig(level=logging.DEBUG)
    
    client = OllamaClient()
    
    # Load sample email
    email_parser = EmailParser()
    with open("data/sample_emails/test_emails.txt", 'r') as f:
        emails = email_parser.parse_email_file(f.read())
    
    test_email = emails[0]
    cpra_requests = create_sample_cpra_requests()
    request_texts = [req.text for req in cpra_requests]
    
    print("Testing exact CPRA analysis call...")
    print(f"Email: {test_email.subject}")
    print(f"Requests: {len(request_texts)}")
    
    try:
        result = client.analyze_responsiveness(
            model_name="gemma3:latest",
            email_content=test_email.get_display_text(),
            cpra_requests=request_texts,
            retry_attempts=1
        )
        
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_cpra_call()