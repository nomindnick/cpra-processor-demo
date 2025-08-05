"""
Test the generate_structured_response method directly.
"""

import sys
import os
import logging
sys.path.append('src')

from models.ollama_client import OllamaClient

def test_generate_response():
    """Test generate_structured_response directly."""
    logging.basicConfig(level=logging.DEBUG)
    
    client = OllamaClient()
    
    system_prompt = "You are a helpful assistant. Respond with valid JSON only."
    prompt = "Provide a simple JSON response: {\"test\": \"success\"}"
    
    print("Testing generate_structured_response...")
    
    response = client.generate_structured_response(
        model_name="gemma3:latest",
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.2,
        max_tokens=100
    )
    
    print(f"Response: {repr(response)}")
    print(f"Response type: {type(response)}")
    
    if response:
        print(f"Response length: {len(response)}")
        print(f"First 100 chars: {response[:100]}")

if __name__ == "__main__":
    test_generate_response()