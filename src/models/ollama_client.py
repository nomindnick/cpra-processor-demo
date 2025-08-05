"""
Ollama client for local AI model integration.
Handles communication with local Ollama service for CPRA document processing.
"""

import json
import time
import logging
from typing import Dict, List, Optional, Tuple
import ollama
from ollama import ChatResponse


class OllamaClient:
    """Client for interacting with local Ollama models."""
    
    def __init__(self, host: str = "http://localhost:11434", timeout: int = 120):
        """
        Initialize the Ollama client.
        
        Args:
            host: Ollama service host URL
            timeout: Request timeout in seconds
        """
        self.host = host
        self.timeout = timeout
        self.client = ollama.Client(host=host, timeout=timeout)
        self.logger = logging.getLogger(__name__)
        
    def test_connectivity(self) -> bool:
        """
        Test connection to Ollama service.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Test basic connectivity by listing models
            models = self.client.list()
            self.logger.info(f"Connected to Ollama. Found {len(models['models'])} models.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Ollama: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """
        Get list of available models.
        
        Returns:
            List of model names
        """
        try:
            models = self.client.list()
            # Handle different response structures
            if 'models' in models:
                return [model.get('name', model.get('model', '')) for model in models['models']]
            else:
                # Fallback for different API response structure
                return [model.get('name', model.get('model', '')) for model in models]
        except Exception as e:
            self.logger.error(f"Failed to list models: {e}")
            return []
    
    def test_model(self, model_name: str, test_prompt: str = "Hello, how are you?") -> Tuple[bool, Optional[str], Optional[float]]:
        """
        Test a specific model with a simple prompt.
        
        Args:
            model_name: Name of the model to test
            test_prompt: Simple test prompt
            
        Returns:
            Tuple of (success, response_text, response_time_seconds)
        """
        try:
            start_time = time.time()
            
            response = self.client.generate(
                model=model_name,
                prompt=test_prompt,
                options={
                    'temperature': 0.7,
                    'num_predict': 50  # Limit tokens for test
                }
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            response_text = response['response'].strip()
            self.logger.info(f"Model {model_name} test successful. Response time: {response_time:.2f}s")
            
            return True, response_text, response_time
            
        except Exception as e:
            self.logger.error(f"Model {model_name} test failed: {e}")
            return False, None, None
    
    def generate_structured_response(
        self, 
        model_name: str, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None
    ) -> Optional[str]:
        """
        Generate a response using the specified model with structured prompting.
        
        Args:
            model_name: Name of the model to use
            prompt: The main prompt
            system_prompt: Optional system prompt for context
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response text or None if failed
        """
        try:
            options = {
                'temperature': temperature,
            }
            
            if max_tokens:
                options['num_predict'] = max_tokens
            
            # Build messages for chat format
            messages = []
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            messages.append({
                'role': 'user', 
                'content': prompt
            })
            
            response = self.client.chat(
                model=model_name,
                messages=messages,
                options=options
            )
            
            return response['message']['content'].strip()
            
        except Exception as e:
            self.logger.error(f"Failed to generate response with model {model_name}: {e}")
            return None
    
    def analyze_responsiveness(
        self, 
        model_name: str, 
        email_content: str, 
        cpra_requests: List[str],
        retry_attempts: int = 3
    ) -> Optional[Dict]:
        """
        Analyze if an email is responsive to CPRA requests with enhanced prompting.
        
        Args:
            model_name: Model to use for analysis
            email_content: The email content to analyze
            cpra_requests: List of CPRA request strings
            retry_attempts: Number of retry attempts for failed requests
            
        Returns:
            Dictionary with analysis results or None if failed
        """
        system_prompt = f"""You are an expert legal assistant specializing in California Public Records Act (CPRA) requests. 
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
{{
    "responsive": [true/false for each request],
    "confidence": ["high"/"medium"/"low" for each request],
    "reasoning": ["brief explanation for each request"]
}}

CRITICAL: Your response must be valid JSON with exactly {len(cpra_requests)} elements in each array."""
        
        # Format the requests with clear numbering
        requests_text = "\n".join([f"Request {i+1}: {req}" for i, req in enumerate(cpra_requests)])
        
        prompt = f"""Analyze this email for responsiveness to the following CPRA requests:

CPRA REQUESTS TO ANALYZE:
{requests_text}

EMAIL DOCUMENT TO ANALYZE:
{email_content}

Provide your analysis in the required JSON format with exactly {len(cpra_requests)} elements in each array."""
        
        # Retry logic for better reliability
        for attempt in range(retry_attempts):
            json_content = ""
            response = ""
            try:
                response = self.generate_structured_response(
                    model_name=model_name,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.2,
                    max_tokens=800
                )
                
                if not response:
                    if attempt < retry_attempts - 1:
                        self.logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                        continue
                    return None
                
                # Try to parse JSON response, handling markdown code blocks
                json_content = self._extract_json_from_response(response)
                
                # Additional check for empty JSON content
                if not json_content or json_content.strip() == "":
                    if attempt < retry_attempts - 1:
                        self.logger.warning(f"Empty JSON content on attempt {attempt + 1}, retrying...")
                        continue
                    return None
                
                result = json.loads(json_content)
                
                # Validate the response structure
                if self._validate_responsiveness_result(result, len(cpra_requests)):
                    return result
                else:
                    if attempt < retry_attempts - 1:
                        self.logger.warning(f"Invalid response structure on attempt {attempt + 1}, retrying...")
                        continue
                    return None
                    
            except json.JSONDecodeError as e:
                if attempt < retry_attempts - 1:
                    self.logger.warning(f"JSON parse error on attempt {attempt + 1}: {e}, retrying...")
                    self.logger.debug(f"Raw response: {response}")
                    self.logger.debug(f"Extracted JSON: {json_content}")
                    continue
                else:
                    self.logger.error(f"Failed to parse JSON response after {retry_attempts} attempts: {e}")
                    self.logger.debug(f"Raw response: {response}")
                    self.logger.debug(f"Extracted JSON: {json_content}")
                    return None
            except Exception as e:
                self.logger.error(f"Unexpected error in responsiveness analysis: {e}")
                self.logger.debug(f"Raw response: {response}")
                self.logger.debug(f"Extracted JSON: {json_content}")
                return None
        
        return None
    
    def _validate_responsiveness_result(self, result: Dict, expected_length: int) -> bool:
        """
        Validate the structure of a responsiveness analysis result.
        
        Args:
            result: The parsed JSON result
            expected_length: Expected number of elements in each array
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required keys
            required_keys = ['responsive', 'confidence', 'reasoning']
            if not all(key in result for key in required_keys):
                self.logger.error(f"Missing required keys in result: {result.keys()}")
                return False
            
            # Check array lengths
            responsive = result['responsive']
            confidence = result['confidence']
            reasoning = result['reasoning']
            
            if not (len(responsive) == len(confidence) == len(reasoning) == expected_length):
                self.logger.error(f"Array length mismatch. Expected: {expected_length}, "
                                f"Got - responsive: {len(responsive)}, confidence: {len(confidence)}, reasoning: {len(reasoning)}")
                return False
            
            # Check data types and values
            if not all(isinstance(r, bool) for r in responsive):
                self.logger.error("Invalid responsive values - must be boolean")
                return False
                
            valid_confidence = ['high', 'medium', 'low']
            if not all(c.lower() in valid_confidence for c in confidence):
                self.logger.error(f"Invalid confidence values. Must be one of: {valid_confidence}")
                return False
                
            if not all(isinstance(r, str) for r in reasoning):
                self.logger.error("Invalid reasoning values - must be strings")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating responsiveness result: {e}")
            return False
    
    def _extract_json_from_response(self, response: str) -> str:
        """
        Extract JSON content from response, handling markdown code blocks.
        
        Args:
            response: Raw response from model
            
        Returns:
            Clean JSON string
        """
        if not response:
            return response
        
        # Check if wrapped in markdown code blocks
        if response.strip().startswith('```'):
            # Find the JSON content within code blocks
            lines = response.strip().split('\n')
            json_lines = []
            in_json = False
            
            for line in lines:
                if line.strip().startswith('```'):
                    if in_json:
                        break
                    else:
                        in_json = True
                        continue
                if in_json:
                    json_lines.append(line)
            
            return '\n'.join(json_lines)
        
        # Check if we can find JSON by braces
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            return response[start:end]
        
        # Return as-is if no special formatting detected
        return response
    
    def analyze_exemptions(
        self, 
        model_name: str, 
        email_content: str
    ) -> Optional[Dict]:
        """
        Analyze an email for CPRA exemptions.
        
        Args:
            model_name: Model to use for analysis
            email_content: The email content to analyze
            
        Returns:
            Dictionary with exemption analysis results or None if failed
        """
        system_prompt = """You are a legal assistant specializing in California Public Records Act (CPRA) exemptions.
Your task is to identify potential exemptions that may apply to email content.

Focus on these exemption types:
1. Attorney-Client Privilege: Communications between attorney and client
2. Personnel Records: Information relating to employee performance, discipline, or personal matters
3. Deliberative Process: Pre-decisional discussions, recommendations, or draft documents

You must respond with valid JSON only, using this exact format:
{
    "exemptions": {
        "attorney_client": {"applies": true/false, "confidence": "high/medium/low", "reasoning": "explanation"},
        "personnel": {"applies": true/false, "confidence": "high/medium/low", "reasoning": "explanation"},
        "deliberative": {"applies": true/false, "confidence": "high/medium/low", "reasoning": "explanation"}
    }
}"""
        
        prompt = f"""Analyze this email for potential CPRA exemptions:

EMAIL TO ANALYZE:
{email_content}

Respond with JSON only."""
        
        response = self.generate_structured_response(
            model_name=model_name,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=600
        )
        
        if not response:
            return None
            
        try:
            # Try to parse JSON response
            return json.loads(response)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            self.logger.debug(f"Raw response: {response}")
            return None


def test_all_models() -> Dict[str, Dict]:
    """
    Test connectivity and basic functionality of all target models.
    
    Returns:
        Dictionary with test results for each model
    """
    client = OllamaClient()
    target_models = ['gpt-oss:20b', 'gemma3:latest', 'phi4-mini-reasoning:3.8b']
    results = {}
    
    # Test connectivity first
    if not client.test_connectivity():
        return {"error": "Could not connect to Ollama service"}
    
    # Test each target model
    for model in target_models:
        print(f"Testing model: {model}")
        
        success, response, response_time = client.test_model(model)
        
        if success:
            results[model] = {
                "status": "success",
                "response_time": response_time,
                "sample_response": response[:100] + "..." if len(response) > 100 else response
            }
        else:
            results[model] = {
                "status": "failed",
                "error": "Model test failed"
            }
    
    return results


if __name__ == "__main__":
    # Run tests when script is executed directly
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Ollama connectivity and target models...")
    results = test_all_models()
    
    print("\nTest Results:")
    print(json.dumps(results, indent=2))