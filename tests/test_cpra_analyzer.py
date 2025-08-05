"""
Unit tests for CPRA analyzer functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from processors.cpra_analyzer import CPRAAnalyzer, create_sample_cpra_requests
from utils.data_structures import Email, CPRARequest, ResponsivenessAnalysis, ExemptionAnalysis, ConfidenceLevel, ExemptionType
from models.ollama_client import OllamaClient


class TestCPRAAnalyzer:
    """Test cases for CPRAAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock the Ollama client to avoid actual API calls during testing
        with patch('processors.cpra_analyzer.OllamaClient') as mock_client_class:
            mock_client = Mock()
            mock_client.test_connectivity.return_value = True
            mock_client.list_models.return_value = ['gemma3:latest', 'phi4-mini-reasoning:3.8b']
            mock_client_class.return_value = mock_client
            
            self.analyzer = CPRAAnalyzer()
            self.mock_client = mock_client
    
    def create_test_email(self, subject="Test Subject", body="Test body content") -> Email:
        """Create a test email for testing."""
        return Email(
            from_address="test@example.com",
            to_address="recipient@example.com", 
            subject=subject,
            date=datetime(2024, 1, 15, 9, 30),
            body=body,
            message_id="test_email_001"
        )
    
    def create_test_cpra_requests(self) -> list[CPRARequest]:
        """Create test CPRA requests."""
        return [
            CPRARequest(
                text="All documents regarding roof leak issues",
                request_id="req_001"
            ),
            CPRARequest(
                text="All documents regarding change orders",
                request_id="req_002"
            )
        ]
    
    def test_analyzer_initialization_success(self):
        """Test successful analyzer initialization."""
        with patch('processors.cpra_analyzer.OllamaClient') as mock_client_class:
            mock_client = Mock()
            mock_client.test_connectivity.return_value = True
            mock_client.list_models.return_value = ['gemma3:latest']
            mock_client_class.return_value = mock_client
            
            analyzer = CPRAAnalyzer(model_name="gemma3:latest")
            assert analyzer.model_name == "gemma3:latest"
            assert analyzer.ollama_client == mock_client
    
    def test_analyzer_initialization_connection_failure(self):
        """Test analyzer initialization with connection failure."""
        with patch('processors.cpra_analyzer.OllamaClient') as mock_client_class:
            mock_client = Mock()
            mock_client.test_connectivity.return_value = False
            mock_client_class.return_value = mock_client
            
            with pytest.raises(ConnectionError):
                CPRAAnalyzer()
    
    def test_analyzer_initialization_invalid_model(self):
        """Test analyzer initialization with invalid model."""
        with patch('processors.cpra_analyzer.OllamaClient') as mock_client_class:
            mock_client = Mock()
            mock_client.test_connectivity.return_value = True
            mock_client.list_models.return_value = ['gemma3:latest']
            mock_client_class.return_value = mock_client
            
            with pytest.raises(ValueError):
                CPRAAnalyzer(model_name="nonexistent_model")
    
    def test_single_email_analysis_success(self):
        """Test successful single email analysis."""
        # Mock successful AI response
        mock_response = {
            "responsive": [True, False],
            "confidence": ["high", "low"],
            "reasoning": ["Email discusses roof leaks", "No mention of change orders"]
        }
        self.mock_client.analyze_responsiveness.return_value = mock_response
        
        email = self.create_test_email("Roof Leak Issues", "We have serious roof leak problems")
        cpra_requests = self.create_test_cpra_requests()
        
        result = self.analyzer.analyze_email_responsiveness(email, cpra_requests, 0)
        
        assert result is not None
        assert isinstance(result, ResponsivenessAnalysis)
        assert result.email_id == "test_email_001"
        assert result.responsive == [True, False]
        assert result.confidence == [ConfidenceLevel.HIGH, ConfidenceLevel.LOW]
        assert len(result.reasoning) == 2
        assert result.model_used == "gemma3:latest"
        assert result.processing_time_seconds is not None
    
    def test_single_email_analysis_failure(self):
        """Test single email analysis with AI failure."""
        # Mock AI failure
        self.mock_client.analyze_responsiveness.return_value = None
        
        email = self.create_test_email()
        cpra_requests = self.create_test_cpra_requests()
        
        result = self.analyzer.analyze_email_responsiveness(email, cpra_requests, 0)
        
        assert result is None
    
    def test_batch_analysis_success(self):
        """Test successful batch email analysis."""
        # Mock successful AI responses
        mock_response_1 = {
            "responsive": [True, False],
            "confidence": ["high", "low"],
            "reasoning": ["Discusses roof issues", "No change orders mentioned"]
        }
        mock_response_2 = {
            "responsive": [False, True],
            "confidence": ["low", "medium"],
            "reasoning": ["No roof content", "Mentions change order process"]
        }
        
        self.mock_client.analyze_responsiveness.side_effect = [mock_response_1, mock_response_2]
        
        email1 = self.create_test_email("Roof Issues", "Roof leak problems")
        email1.message_id = "test_email_001"
        
        email2 = self.create_test_email("Change Orders", "Processing change order #3")
        email2.message_id = "test_email_002"
        
        emails = [email1, email2]
        cpra_requests = self.create_test_cpra_requests()
        
        # Track progress callback calls
        progress_calls = []
        def progress_callback(current, total, email):
            progress_calls.append((current, total, email.subject))
        
        results, stats = self.analyzer.analyze_batch_responsiveness(
            emails, cpra_requests, progress_callback
        )
        
        # Verify results
        assert len(results) == 2
        assert stats.total_emails == 2
        assert stats.processed_emails == 2
        assert stats.responsive_emails == 2  # Both emails are responsive to at least one request
        assert stats.analysis_errors == 0
        
        # Verify progress callback was called
        assert len(progress_calls) == 2
        assert progress_calls[0] == (0, 2, "Roof Issues")
        assert progress_calls[1] == (1, 2, "Change Orders")
    
    def test_batch_analysis_with_failures(self):
        """Test batch analysis with some failures."""
        # Mock mixed success/failure responses
        mock_response = {
            "responsive": [True, False],
            "confidence": ["high", "low"],
            "reasoning": ["Valid analysis", "No relevance"]
        }
        
        self.mock_client.analyze_responsiveness.side_effect = [mock_response, None]
        
        emails = [
            self.create_test_email("Success Email"),
            self.create_test_email("Failure Email")
        ]
        cpra_requests = self.create_test_cpra_requests()
        
        results, stats = self.analyzer.analyze_batch_responsiveness(emails, cpra_requests)
        
        # Verify results
        assert len(results) == 1  # Only successful analysis included
        assert stats.total_emails == 2
        assert stats.processed_emails == 2
        assert stats.analysis_errors == 1
        assert stats.responsive_emails == 1
    
    def test_parse_responsiveness_result_success(self):
        """Test successful parsing of responsiveness result.""" 
        analysis_result = {
            "responsive": [True, False, True],
            "confidence": ["high", "low", "medium"],
            "reasoning": ["Clear match", "No relevance", "Partial match"]
        }
        
        result = self.analyzer._parse_responsiveness_result(
            email_id="test_001",
            cpra_requests=["Request 1", "Request 2", "Request 3"],
            analysis_result=analysis_result,
            processing_time=1.5
        )
        
        assert result is not None
        assert result.email_id == "test_001"
        assert result.responsive == [True, False, True]
        assert result.confidence == [ConfidenceLevel.HIGH, ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM]
        assert result.reasoning == ["Clear match", "No relevance", "Partial match"]
        assert result.processing_time_seconds == 1.5
    
    def test_parse_responsiveness_result_missing_fields(self):
        """Test parsing with missing required fields."""
        analysis_result = {
            "responsive": [True, False],
            # Missing confidence and reasoning
        }
        
        result = self.analyzer._parse_responsiveness_result(
            email_id="test_001",
            cpra_requests=["Request 1", "Request 2"], 
            analysis_result=analysis_result,
            processing_time=1.0
        )
        
        assert result is None
    
    def test_parse_responsiveness_result_length_mismatch(self):
        """Test parsing with array length mismatch."""
        analysis_result = {
            "responsive": [True, False, True],  # 3 elements
            "confidence": ["high", "low"],      # 2 elements - mismatch
            "reasoning": ["Match", "No match", "Partial"]  # 3 elements
        }
        
        result = self.analyzer._parse_responsiveness_result(
            email_id="test_001",
            cpra_requests=["Request 1", "Request 2", "Request 3"],
            analysis_result=analysis_result,
            processing_time=1.0
        )
        
        assert result is None
    
    def test_parse_responsiveness_result_invalid_confidence(self):
        """Test parsing with invalid confidence values."""
        analysis_result = {
            "responsive": [True, False],
            "confidence": ["high", "invalid"],  # Invalid confidence level
            "reasoning": ["Match", "No match"]
        }
        
        result = self.analyzer._parse_responsiveness_result(
            email_id="test_001",
            cpra_requests=["Request 1", "Request 2"],
            analysis_result=analysis_result,
            processing_time=1.0
        )
        
        # Should still work but with invalid confidence converted to LOW
        assert result is not None
        assert result.confidence == [ConfidenceLevel.HIGH, ConfidenceLevel.LOW]
    
    def test_model_connectivity_test(self):
        """Test model connectivity testing."""
        # Mock successful connectivity test
        self.mock_client.test_model.return_value = (True, "Test response", 2.5)
        
        result = self.analyzer.test_model_connectivity()
        
        assert result is True
        self.mock_client.test_model.assert_called_once_with("gemma3:latest")
    
    def test_model_connectivity_test_failure(self):
        """Test model connectivity test failure."""
        # Mock failed connectivity test
        self.mock_client.test_model.return_value = (False, None, None)
        
        result = self.analyzer.test_model_connectivity()
        
        assert result is False
    
    def test_get_model_info(self):
        """Test getting model information."""
        self.mock_client.list_models.return_value = ["model1", "model2"]
        self.mock_client.test_connectivity.return_value = True
        
        info = self.analyzer.get_model_info()
        
        assert info["model_name"] == "gemma3:latest"
        assert info["available_models"] == ["model1", "model2"]
        assert info["connectivity"] is True


class TestSampleCPRARequests:
    """Test cases for sample CPRA request creation."""
    
    def test_create_sample_cpra_requests(self):
        """Test creation of sample CPRA requests."""
        requests = create_sample_cpra_requests()
        
        assert len(requests) == 3
        assert all(isinstance(req, CPRARequest) for req in requests)
        
        # Check specific content
        request_texts = [req.text for req in requests]
        assert any("roof leak" in text.lower() for text in request_texts)
        assert any("change order" in text.lower() for text in request_texts)
        assert any("project delays" in text.lower() for text in request_texts)
        
        # Check that all requests have IDs
        assert all(req.request_id for req in requests)
        assert all(req.description for req in requests)


class TestOllamaClientEnhancements:
    """Test cases for enhanced Ollama client methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = OllamaClient()
    
    def test_validate_responsiveness_result_valid(self):
        """Test validation of valid responsiveness result."""
        result = {
            "responsive": [True, False, True],
            "confidence": ["high", "medium", "low"],
            "reasoning": ["Match found", "No relevance", "Partial match"]
        }
        
        is_valid = self.client._validate_responsiveness_result(result, 3)
        assert is_valid is True
    
    def test_validate_responsiveness_result_missing_keys(self):
        """Test validation with missing required keys."""
        result = {
            "responsive": [True, False],
            # Missing confidence and reasoning
        }
        
        is_valid = self.client._validate_responsiveness_result(result, 2)
        assert is_valid is False
    
    def test_validate_responsiveness_result_length_mismatch(self):
        """Test validation with array length mismatch."""
        result = {
            "responsive": [True, False],
            "confidence": ["high"],  # Wrong length
            "reasoning": ["Match", "No match"]
        }
        
        is_valid = self.client._validate_responsiveness_result(result, 2)
        assert is_valid is False
    
    def test_validate_responsiveness_result_invalid_types(self):
        """Test validation with invalid data types."""
        result = {
            "responsive": ["true", "false"],  # Should be boolean
            "confidence": ["high", "low"],
            "reasoning": ["Match", "No match"]
        }
        
        is_valid = self.client._validate_responsiveness_result(result, 2)
        assert is_valid is False
    
    def test_validate_responsiveness_result_invalid_confidence(self):
        """Test validation with invalid confidence values."""
        result = {
            "responsive": [True, False],
            "confidence": ["high", "invalid"],  # Invalid confidence level
            "reasoning": ["Match", "No match"]
        }
        
        is_valid = self.client._validate_responsiveness_result(result, 2)
        assert is_valid is False


class TestExemptionAnalysis:
    """Test cases for exemption analysis functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock the Ollama client to avoid actual API calls during testing
        with patch('processors.cpra_analyzer.OllamaClient') as mock_client_class:
            mock_client = Mock()
            mock_client.test_connectivity.return_value = True
            mock_client.list_models.return_value = ['gemma3:latest', 'phi4-mini-reasoning:3.8b']
            mock_client_class.return_value = mock_client
            
            self.analyzer = CPRAAnalyzer()
            self.mock_client = mock_client
    
    def create_test_email(self, subject="Test Subject", body="Test body content") -> Email:
        """Create a test email for testing."""
        return Email(
            from_address="test@example.com",
            to_address="recipient@example.com", 
            subject=subject,
            date=datetime(2024, 1, 15, 9, 30),
            body=body,
            message_id="test_email_001"
        )
    
    def test_single_email_exemption_analysis_success(self):
        """Test successful single email exemption analysis."""
        # Mock successful AI response
        mock_response = {
            "exemptions": {
                "attorney_client": {
                    "applies": True,
                    "confidence": "high",
                    "reasoning": "Contains legal advice from attorney"
                },
                "personnel": {
                    "applies": False,
                    "confidence": "low",
                    "reasoning": "No personnel information discussed"
                },
                "deliberative": {
                    "applies": True,
                    "confidence": "medium",
                    "reasoning": "Contains draft recommendation"
                }
            }
        }
        self.mock_client.analyze_exemptions.return_value = mock_response
        
        email = self.create_test_email("Legal Advice", "Attorney recommends we proceed with litigation")
        
        result = self.analyzer.analyze_email_exemptions(email, 0)
        
        assert result is not None
        assert isinstance(result, ExemptionAnalysis)
        assert result.email_id == "test_email_001"
        assert result.attorney_client["applies"] is True
        assert result.attorney_client["confidence"] == ConfidenceLevel.HIGH
        assert result.personnel["applies"] is False
        assert result.deliberative["applies"] is True
        assert result.model_used == "gemma3:latest"
        assert result.processing_time_seconds is not None
    
    def test_single_email_exemption_analysis_failure(self):
        """Test single email exemption analysis with AI failure."""
        # Mock AI failure
        self.mock_client.analyze_exemptions.return_value = None
        
        email = self.create_test_email()
        
        result = self.analyzer.analyze_email_exemptions(email, 0)
        
        assert result is None
    
    def test_batch_exemption_analysis_success(self):
        """Test successful batch exemption analysis."""
        # Mock successful AI responses
        mock_response_1 = {
            "exemptions": {
                "attorney_client": {"applies": True, "confidence": "high", "reasoning": "Legal advice present"},
                "personnel": {"applies": False, "confidence": "low", "reasoning": "No personnel content"},
                "deliberative": {"applies": False, "confidence": "low", "reasoning": "Final decision communication"}
            }
        }
        mock_response_2 = {
            "exemptions": {
                "attorney_client": {"applies": False, "confidence": "low", "reasoning": "No legal advice"},
                "personnel": {"applies": True, "confidence": "medium", "reasoning": "Employee performance discussion"},
                "deliberative": {"applies": False, "confidence": "low", "reasoning": "Administrative communication"}
            }
        }
        
        self.mock_client.analyze_exemptions.side_effect = [mock_response_1, mock_response_2]
        
        email1 = self.create_test_email("Legal Matter", "Attorney client privilege applies here")
        email1.message_id = "test_email_001"
        
        email2 = self.create_test_email("HR Discussion", "Employee performance needs improvement")
        email2.message_id = "test_email_002"
        
        emails = [email1, email2]
        
        # Track progress callback calls
        progress_calls = []
        def progress_callback(current, total, email):
            progress_calls.append((current, total, email.subject))
        
        results, stats = self.analyzer.analyze_batch_exemptions(emails, progress_callback)
        
        # Verify results
        assert len(results) == 2
        assert stats.total_emails == 2
        assert stats.processed_emails == 2
        assert stats.exempt_emails == 2  # Both emails have at least one exemption
        assert stats.analysis_errors == 0
        
        # Verify progress callback was called
        assert len(progress_calls) == 2
        assert progress_calls[0] == (0, 2, "Legal Matter")
        assert progress_calls[1] == (1, 2, "HR Discussion")
    
    def test_batch_exemption_analysis_with_failures(self):
        """Test batch exemption analysis with some failures."""
        # Mock mixed success/failure responses
        mock_response = {
            "exemptions": {
                "attorney_client": {"applies": False, "confidence": "low", "reasoning": "No legal content"},
                "personnel": {"applies": False, "confidence": "low", "reasoning": "No personnel content"},
                "deliberative": {"applies": False, "confidence": "low", "reasoning": "Final communication"}
            }
        }
        
        self.mock_client.analyze_exemptions.side_effect = [mock_response, None]
        
        emails = [
            self.create_test_email("Success Email"),
            self.create_test_email("Failure Email")
        ]
        
        results, stats = self.analyzer.analyze_batch_exemptions(emails)
        
        # Verify results
        assert len(results) == 1  # Only successful analysis included
        assert stats.total_emails == 2
        assert stats.processed_emails == 2
        assert stats.analysis_errors == 1
        assert stats.exempt_emails == 0  # No exemptions in successful email
    
    def test_parse_exemption_result_success(self):
        """Test successful parsing of exemption result."""
        analysis_result = {
            "exemptions": {
                "attorney_client": {
                    "applies": True,
                    "confidence": "high",
                    "reasoning": "Clear attorney-client communication"
                },
                "personnel": {
                    "applies": False,
                    "confidence": "low", 
                    "reasoning": "No personnel information"
                },
                "deliberative": {
                    "applies": True,
                    "confidence": "medium",
                    "reasoning": "Draft policy discussion"
                }
            }
        }
        
        result = self.analyzer._parse_exemption_result(
            email_id="test_001",
            analysis_result=analysis_result,
            processing_time=2.5
        )
        
        assert result is not None
        assert result.email_id == "test_001"
        assert result.attorney_client["applies"] is True
        assert result.attorney_client["confidence"] == ConfidenceLevel.HIGH
        assert result.personnel["applies"] is False
        assert result.deliberative["applies"] is True
        assert result.deliberative["confidence"] == ConfidenceLevel.MEDIUM
        assert result.processing_time_seconds == 2.5
    
    def test_parse_exemption_result_missing_exemptions_key(self):
        """Test parsing with missing exemptions key."""
        analysis_result = {
            "wrong_key": {}
        }
        
        result = self.analyzer._parse_exemption_result(
            email_id="test_001",
            analysis_result=analysis_result,
            processing_time=1.0
        )
        
        assert result is None
    
    def test_parse_exemption_result_missing_exemption_types(self):
        """Test parsing with missing exemption types."""
        analysis_result = {
            "exemptions": {
                "attorney_client": {"applies": True, "confidence": "high", "reasoning": "Legal advice"},
                # Missing personnel and deliberative
            }
        }
        
        result = self.analyzer._parse_exemption_result(
            email_id="test_001",
            analysis_result=analysis_result,
            processing_time=1.0
        )
        
        assert result is None
    
    def test_parse_single_exemption_success(self):
        """Test successful parsing of single exemption."""
        exemption_data = {
            "applies": True,
            "confidence": "medium",
            "reasoning": "Contains sensitive information"
        }
        
        result = self.analyzer._parse_single_exemption(exemption_data)
        
        assert result is not None
        assert result["applies"] is True
        assert result["confidence"] == ConfidenceLevel.MEDIUM
        assert result["reasoning"] == "Contains sensitive information"
    
    def test_parse_single_exemption_missing_fields(self):
        """Test parsing single exemption with missing fields."""
        exemption_data = {
            "applies": True,
            # Missing confidence and reasoning
        }
        
        result = self.analyzer._parse_single_exemption(exemption_data)
        
        assert result is None
    
    def test_parse_single_exemption_invalid_types(self):
        """Test parsing single exemption with invalid data types."""
        exemption_data = {
            "applies": "true",  # Should be boolean
            "confidence": "high",
            "reasoning": "Valid reasoning"
        }
        
        result = self.analyzer._parse_single_exemption(exemption_data)
        
        assert result is None
    
    def test_parse_single_exemption_invalid_confidence(self):
        """Test parsing single exemption with invalid confidence level."""
        exemption_data = {
            "applies": True,
            "confidence": "invalid_level",
            "reasoning": "Valid reasoning"
        }
        
        result = self.analyzer._parse_single_exemption(exemption_data)
        
        # Should still work but with confidence converted to LOW
        assert result is not None
        assert result["confidence"] == ConfidenceLevel.LOW
    
    def test_exemption_analysis_object_methods(self):
        """Test ExemptionAnalysis object helper methods."""
        # Create ExemptionAnalysis with mixed exemptions
        analysis = ExemptionAnalysis(
            email_id="test_001",
            attorney_client={"applies": True, "confidence": ConfidenceLevel.HIGH, "reasoning": "Legal advice"},
            personnel={"applies": False, "confidence": ConfidenceLevel.LOW, "reasoning": "No personnel info"},
            deliberative={"applies": True, "confidence": ConfidenceLevel.MEDIUM, "reasoning": "Draft document"}
        )
        
        # Test get_applicable_exemptions
        applicable = analysis.get_applicable_exemptions()
        assert len(applicable) == 2
        assert ExemptionType.ATTORNEY_CLIENT in applicable
        assert ExemptionType.DELIBERATIVE in applicable
        assert ExemptionType.PERSONNEL not in applicable
        
        # Test has_any_exemption
        assert analysis.has_any_exemption() is True
        
        # Test with no exemptions
        analysis_no_exemptions = ExemptionAnalysis(
            email_id="test_002",
            attorney_client={"applies": False, "confidence": ConfidenceLevel.LOW, "reasoning": "No legal content"},
            personnel={"applies": False, "confidence": ConfidenceLevel.LOW, "reasoning": "No personnel info"},
            deliberative={"applies": False, "confidence": ConfidenceLevel.LOW, "reasoning": "Final document"}
        )
        
        assert analysis_no_exemptions.has_any_exemption() is False
        assert len(analysis_no_exemptions.get_applicable_exemptions()) == 0


class TestOllamaClientExemptions:
    """Test cases for Ollama client exemption analysis methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = OllamaClient()
    
    def test_validate_exemption_result_valid(self):
        """Test validation of valid exemption result."""
        result = {
            "exemptions": {
                "attorney_client": {"applies": True, "confidence": "high", "reasoning": "Legal advice"},
                "personnel": {"applies": False, "confidence": "low", "reasoning": "No personnel info"},
                "deliberative": {"applies": True, "confidence": "medium", "reasoning": "Draft document"}
            }
        }
        
        is_valid = self.client._validate_exemption_result(result)
        assert is_valid is True
    
    def test_validate_exemption_result_missing_exemptions_key(self):
        """Test validation with missing exemptions key."""
        result = {
            "wrong_key": {}
        }
        
        is_valid = self.client._validate_exemption_result(result)
        assert is_valid is False
    
    def test_validate_exemption_result_missing_exemption_types(self):
        """Test validation with missing exemption types."""
        result = {
            "exemptions": {
                "attorney_client": {"applies": True, "confidence": "high", "reasoning": "Legal"},
                # Missing personnel and deliberative
            }
        }
        
        is_valid = self.client._validate_exemption_result(result)
        assert is_valid is False
    
    def test_validate_exemption_result_invalid_fields(self):
        """Test validation with invalid field types."""
        result = {
            "exemptions": {
                "attorney_client": {
                    "applies": "true",  # Should be boolean
                    "confidence": "high",
                    "reasoning": "Legal advice"
                },
                "personnel": {"applies": False, "confidence": "low", "reasoning": "No personnel"},
                "deliberative": {"applies": False, "confidence": "low", "reasoning": "No deliberative"}
            }
        }
        
        is_valid = self.client._validate_exemption_result(result)
        assert is_valid is False
    
    def test_validate_exemption_result_invalid_confidence(self):
        """Test validation with invalid confidence values."""
        result = {
            "exemptions": {
                "attorney_client": {"applies": True, "confidence": "invalid", "reasoning": "Legal"},
                "personnel": {"applies": False, "confidence": "low", "reasoning": "No personnel"},
                "deliberative": {"applies": False, "confidence": "low", "reasoning": "No deliberative"}
            }
        }
        
        is_valid = self.client._validate_exemption_result(result)
        assert is_valid is False


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])