"""
Debug script to test responsiveness analysis with raw output.
"""

import sys
import os
sys.path.append('src')

from models.ollama_client import OllamaClient
from parsers.email_parser import EmailParser
from processors.cpra_analyzer import create_sample_cpra_requests

def debug_analysis():
    """Debug the responsiveness analysis."""
    # Initialize client
    client = OllamaClient()
    
    # Load sample email
    email_parser = EmailParser()
    with open("data/sample_emails/test_emails.txt", 'r') as f:
        emails = email_parser.parse_email_file(f.read())
    
    if not emails:
        print("No emails parsed!")
        return
    
    # Get first email
    test_email = emails[0]
    print(f"Testing email: {test_email.subject}")
    print(f"Email content preview: {test_email.get_display_text()[:200]}...")
    
    # Create CPRA requests
    cpra_requests = create_sample_cpra_requests()
    request_texts = [req.text for req in cpra_requests]
    
    print(f"\nCPRA Requests:")
    for i, req in enumerate(request_texts):
        print(f"{i+1}. {req}")
    
    # Test raw response
    email_content = test_email.get_display_text()
    
    print(f"\nTesting raw response...")
    response = client.generate_structured_response(
        model_name="gemma3:latest",
        prompt=f"""Analyze this email for responsiveness to the following CPRA requests:

CPRA REQUESTS TO ANALYZE:
{chr(10).join([f"Request {i+1}: {req}" for i, req in enumerate(request_texts)])}

EMAIL DOCUMENT TO ANALYZE:
{email_content}

Provide your analysis in the required JSON format with exactly {len(request_texts)} elements in each array.""",
        system_prompt="""You are an expert legal assistant specializing in California Public Records Act (CPRA) requests. 
Your task is to determine if an email document is responsive to specific CPRA requests.

RESPONSIVENESS CRITERIA:
- A document is "responsive" if it contains information that relates to, discusses, or provides evidence about the subject matter of the CPRA request
- Consider both direct mentions and indirect relevance
- Even partial relevance should be considered responsive
- When in doubt, err on the side of finding documents responsive

CONFIDENCE LEVELS:
- "high": Clear, direct relevance to the request
- "medium": Indirect or partial relevance to the request  
- "low": Minimal or questionable relevance to the request

You must respond with valid JSON only, using this exact format:
{
    "responsive": [true/false for each request],
    "confidence": ["high"/"medium"/"low" for each request],
    "reasoning": ["brief explanation for each request"]
}

CRITICAL: Your response must be valid JSON with exactly 3 elements in each array.""",
        temperature=0.2,
        max_tokens=800
    )
    
    print(f"\nRaw response:")
    print(repr(response))
    print(f"\nFormatted response:")
    print(response)
    
    # Try to parse
    import json
    try:
        parsed = json.loads(response)
        print(f"\nSuccessfully parsed JSON:")
        print(json.dumps(parsed, indent=2))
    except json.JSONDecodeError as e:
        print(f"\nJSON parse error: {e}")
        # Try to clean the response
        if response:
            # Look for JSON content
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_part = response[start:end]
                print(f"\nExtracted JSON part:")
                print(repr(json_part))
                try:
                    parsed = json.loads(json_part)
                    print(f"Successfully parsed extracted JSON:")
                    print(json.dumps(parsed, indent=2))
                except json.JSONDecodeError as e2:
                    print(f"Still failed to parse: {e2}")

if __name__ == "__main__":
    debug_analysis()