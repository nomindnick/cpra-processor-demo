"""
CPRA Analysis Engine for responsiveness determination.
Orchestrates AI-driven analysis of emails against CPRA requests.
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.ollama_client import OllamaClient
from utils.data_structures import (
    Email, CPRARequest, ResponsivenessAnalysis, 
    ConfidenceLevel, ProcessingStats
)


class CPRAAnalyzer:
    """Main analyzer for CPRA document responsiveness determination."""
    
    def __init__(self, model_name: str = "gemma3:latest", ollama_host: str = "http://localhost:11434"):
        """
        Initialize the CPRA analyzer.
        
        Args:
            model_name: Ollama model to use for analysis
            ollama_host: Ollama service host URL
        """
        self.model_name = model_name
        self.ollama_client = OllamaClient(host=ollama_host)
        self.logger = logging.getLogger(__name__)
        
        # Verify model connectivity on initialization
        if not self.ollama_client.test_connectivity():
            raise ConnectionError("Cannot connect to Ollama service")
            
        available_models = self.ollama_client.list_models()
        if model_name not in available_models:
            raise ValueError(f"Model {model_name} not available. Available models: {available_models}")
    
    def analyze_email_responsiveness(
        self, 
        email: Email, 
        cpra_requests: List[CPRARequest],
        email_index: Optional[int] = None
    ) -> Optional[ResponsivenessAnalysis]:
        """
        Analyze a single email's responsiveness to CPRA requests.
        
        Args:
            email: Email object to analyze
            cpra_requests: List of CPRA request objects
            email_index: Optional index for tracking (used as email_id if message_id not available)
            
        Returns:
            ResponsivenessAnalysis object or None if analysis failed
        """
        try:
            start_time = time.time()
            
            # Create email identifier
            email_id = email.message_id if email.message_id else f"email_{email_index or 0}"
            
            # Extract request texts
            request_texts = [req.text for req in cpra_requests]
            
            # Prepare email content for analysis
            email_content = email.get_display_text()
            
            self.logger.info(f"Analyzing email {email_id} against {len(request_texts)} CPRA requests")
            
            # Call AI model for analysis
            analysis_result = self.ollama_client.analyze_responsiveness(
                model_name=self.model_name,
                email_content=email_content,
                cpra_requests=request_texts
            )
            
            if not analysis_result:
                self.logger.error(f"Failed to get analysis result for email {email_id}")
                return None
            
            # Parse and validate the analysis result
            return self._parse_responsiveness_result(
                email_id=email_id,
                cpra_requests=request_texts,
                analysis_result=analysis_result,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing email responsiveness: {e}")
            return None
    
    def analyze_batch_responsiveness(
        self,
        emails: List[Email],
        cpra_requests: List[CPRARequest],
        progress_callback: Optional[callable] = None
    ) -> Tuple[Dict[str, ResponsivenessAnalysis], ProcessingStats]:
        """
        Analyze multiple emails for responsiveness in batch.
        
        Args:
            emails: List of Email objects to analyze
            cpra_requests: List of CPRA request objects
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Tuple of (analysis_results_dict, processing_stats)
        """
        results = {}
        stats = ProcessingStats(
            total_emails=len(emails),
            start_time=datetime.now()
        )
        
        self.logger.info(f"Starting batch analysis of {len(emails)} emails against {len(cpra_requests)} CPRA requests")
        
        for i, email in enumerate(emails):
            try:
                # Progress callback
                if progress_callback:
                    progress_callback(i, len(emails), email)
                
                # Analyze individual email
                analysis = self.analyze_email_responsiveness(email, cpra_requests, i)
                
                if analysis:
                    email_id = email.message_id if email.message_id else f"email_{i}"
                    results[email_id] = analysis
                    
                    # Update stats
                    if analysis.is_responsive_to_any():
                        stats.responsive_emails += 1
                else:
                    stats.analysis_errors += 1
                    self.logger.warning(f"Failed to analyze email {i}")
                
                stats.processed_emails += 1
                
            except Exception as e:
                self.logger.error(f"Error processing email {i}: {e}")
                stats.analysis_errors += 1
        
        stats.end_time = datetime.now()
        
        self.logger.info(f"Batch analysis complete. Processed: {stats.processed_emails}/{stats.total_emails}, "
                        f"Responsive: {stats.responsive_emails}, Errors: {stats.analysis_errors}")
        
        return results, stats
    
    def _parse_responsiveness_result(
        self,
        email_id: str,
        cpra_requests: List[str],
        analysis_result: Dict,
        processing_time: float
    ) -> Optional[ResponsivenessAnalysis]:
        """
        Parse and validate AI analysis result into ResponsivenessAnalysis object.
        
        Args:
            email_id: Identifier for the email
            cpra_requests: List of CPRA request texts
            analysis_result: Raw analysis result from AI model
            processing_time: Time taken for analysis in seconds
            
        Returns:
            ResponsivenessAnalysis object or None if parsing failed
        """
        try:
            # Validate required fields
            if not all(key in analysis_result for key in ['responsive', 'confidence', 'reasoning']):
                self.logger.error(f"Missing required fields in analysis result: {analysis_result}")
                return None
            
            responsive = analysis_result['responsive']
            confidence_raw = analysis_result['confidence']
            reasoning = analysis_result['reasoning']
            
            # Validate array lengths match number of requests
            if not (len(responsive) == len(confidence_raw) == len(reasoning) == len(cpra_requests)):
                self.logger.error(f"Array length mismatch in analysis result. "
                                f"Requests: {len(cpra_requests)}, "
                                f"Responsive: {len(responsive)}, "
                                f"Confidence: {len(confidence_raw)}, "
                                f"Reasoning: {len(reasoning)}")
                return None
            
            # Parse confidence levels
            confidence_levels = []
            for conf in confidence_raw:
                try:
                    confidence_levels.append(ConfidenceLevel(conf.lower()))
                except ValueError:
                    self.logger.warning(f"Invalid confidence level '{conf}', defaulting to LOW")
                    confidence_levels.append(ConfidenceLevel.LOW)
            
            # Create ResponsivenessAnalysis object
            return ResponsivenessAnalysis(
                email_id=email_id,
                cpra_requests=cpra_requests,
                responsive=responsive,
                confidence=confidence_levels,
                reasoning=reasoning,
                model_used=self.model_name,
                analysis_timestamp=datetime.now(),
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing responsiveness result: {e}")
            return None
    
    def test_model_connectivity(self) -> bool:
        """
        Test connectivity and basic functionality of the current model.
        
        Returns:
            True if model is working properly, False otherwise
        """
        try:
            success, response, response_time = self.ollama_client.test_model(self.model_name)
            if success:
                self.logger.info(f"Model {self.model_name} test successful. Response time: {response_time:.2f}s")
                return True
            else:
                self.logger.error(f"Model {self.model_name} test failed")
                return False
        except Exception as e:
            self.logger.error(f"Error testing model connectivity: {e}")
            return False
    
    def get_model_info(self) -> Dict:
        """
        Get information about the current model and its performance.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "available_models": self.ollama_client.list_models(),
            "connectivity": self.ollama_client.test_connectivity()
        }


def create_sample_cpra_requests() -> List[CPRARequest]:
    """
    Create sample CPRA requests for testing based on the synthetic email dataset.
    
    Returns:
        List of CPRARequest objects
    """
    requests = [
        CPRARequest(
            text="All documents regarding the roof leak issues on the Community Center construction project",
            request_id="req_001",
            description="Documents related to roof leak problems and remediation"
        ),
        CPRARequest(
            text="All documents regarding Change Order #3 and the agency's decision to approve or deny it",
            request_id="req_002", 
            description="Change order approval process and decisions"
        ),
        CPRARequest(
            text="All internal communications about project delays between January and March 2024",
            request_id="req_003",
            description="Internal discussions about construction project timeline delays"
        )
    ]
    
    return requests


if __name__ == "__main__":
    """Test the CPRA analyzer with sample data."""
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    from src.parsers.email_parser import EmailParser
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Initialize analyzer
        analyzer = CPRAAnalyzer()
        
        # Test model connectivity
        if not analyzer.test_model_connectivity():
            print("Model connectivity test failed!")
            sys.exit(1)
        
        # Load sample emails
        email_parser = EmailParser()
        sample_file = "data/sample_emails/test_emails.txt"
        
        if os.path.exists(sample_file):
            with open(sample_file, 'r') as f:
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
                    print(f"Responsive to: {analysis.get_responsive_requests()}")
                    print(f"Processing time: {analysis.processing_time_seconds:.2f}s")
                else:
                    print("Analysis failed!")
            
        else:
            print(f"Sample email file not found: {sample_file}")
            
    except Exception as e:
        print(f"Error running test: {e}")