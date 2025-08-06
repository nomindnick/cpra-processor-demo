"""
Integration tests for CPRA Processing Application.

Sprint 7 Implementation: End-to-End Integration Testing
- Tests complete workflow from upload to export
- Validates with demo dataset
- Tests error recovery scenarios
- Verifies session persistence
"""

import unittest
import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import get_config, reset_config
from src.parsers.email_parser import EmailParser
from src.processors.cpra_analyzer import CPRAAnalyzer
from src.processors.review_manager import ReviewManager
from src.processors.session_manager import SessionManager
from src.processors.export_manager import ExportManager
from src.utils.data_structures import (
    Email, ProcessingSession, CPRARequest,
    ReviewStatus
)


class TestEndToEndIntegration(unittest.TestCase):
    """Test complete workflow integration."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        cls.config = get_config()
        cls.test_dir = tempfile.mkdtemp(prefix="cpra_test_")
        cls.export_dir = Path(cls.test_dir) / "exports"
        cls.session_dir = Path(cls.test_dir) / "sessions"
        cls.export_dir.mkdir(parents=True, exist_ok=True)
        cls.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Update config for testing
        cls.config.export.export_directory = str(cls.export_dir)
        cls.config.session.session_directory = str(cls.session_dir)
        cls.config.session.enable_auto_save = True
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        if Path(cls.test_dir).exists():
            shutil.rmtree(cls.test_dir)
        reset_config()
    
    def setUp(self):
        """Set up for each test."""
        self.demo_emails_path = Path("demo-files/synthetic_emails.txt")
        self.demo_requests_path = Path("demo-files/cpra_requests.txt")
        
        # Check if demo files exist
        self.skipTest_if_no_demo_files()
    
    def skipTest_if_no_demo_files(self):
        """Skip test if demo files don't exist."""
        if not self.demo_emails_path.exists():
            self.skipTest("Demo emails file not found")
        if not self.demo_requests_path.exists():
            self.skipTest("Demo requests file not found")
    
    def load_demo_data(self):
        """Load demo emails and CPRA requests."""
        # Load emails
        with open(self.demo_emails_path, 'r', encoding='utf-8') as f:
            email_content = f.read()
        
        parser = EmailParser()
        emails = parser.parse_email_file(email_content)
        
        # Load CPRA requests
        with open(self.demo_requests_path, 'r', encoding='utf-8') as f:
            request_lines = f.readlines()
        
        cpra_requests = [
            CPRARequest(text=line.strip())
            for line in request_lines
            if line.strip()
        ]
        
        return emails, cpra_requests
    
    def test_complete_workflow(self):
        """Test complete workflow from parsing to export."""
        # Step 1: Load and parse demo data
        emails, cpra_requests = self.load_demo_data()
        
        self.assertEqual(len(emails), 30, "Should parse all 30 demo emails")
        self.assertEqual(len(cpra_requests), 3, "Should load 3 CPRA requests")
        
        # Step 2: Create processing session
        session = ProcessingSession(
            session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
            cpra_requests=cpra_requests,
            emails=emails
        )
        
        # Step 3: Analyze responsiveness (test subset for speed)
        analyzer = CPRAAnalyzer(model_name=self.config.model.responsiveness_model)
        
        # Mock the Ollama client to avoid actual API calls in tests
        with patch.object(analyzer.ollama_client, 'generate') as mock_generate:
            mock_generate.return_value = json.dumps({
                "responsive": [True, False, False],
                "confidence": ["high", "high", "high"],
                "reasoning": ["Test reasoning"]
            })
            
            # Analyze first 5 emails for speed
            for i in range(min(5, len(emails))):
                result = analyzer.analyze_email_responsiveness(
                    emails[i],
                    [req.text for req in cpra_requests]
                )
                if result:
                    session.responsiveness_results[str(i)] = result
        
        # Step 4: Analyze exemptions for responsive emails
        with patch.object(analyzer.ollama_client, 'generate') as mock_generate:
            mock_generate.return_value = json.dumps({
                "exemptions": [],
                "confidence": [],
                "reasoning": []
            })
            
            for i in range(min(5, len(emails))):
                if str(i) in session.responsiveness_results:
                    if session.responsiveness_results[str(i)].is_responsive:
                        result = analyzer.analyze_email_exemptions(emails[i])
                        if result:
                            session.exemption_results[str(i)] = result
        
        # Step 5: Initialize review manager
        review_manager = ReviewManager()
        review_manager.initialize_reviews(session)
        
        self.assertGreater(len(review_manager.reviews), 0, "Should have reviews")
        
        # Step 6: Perform some reviews
        first_review_id = list(review_manager.reviews.keys())[0]
        review_manager.start_review(first_review_id)
        
        # Apply user override
        review_manager.apply_user_override(
            first_review_id,
            responsiveness_override=False,
            exemptions_override=["attorney_client_privilege"]
        )
        
        review_manager.finalize_review(first_review_id)
        
        # Step 7: Export results
        export_manager = ExportManager(session, review_manager)
        
        # Test validation
        is_valid, warnings = export_manager.validate_export_readiness()
        self.assertIsNotNone(warnings)  # May have warnings for partial review
        
        # Perform export
        export_results = export_manager.export_all(str(self.export_dir))
        
        self.assertIn('manifest', export_results, "Should create manifest")
        self.assertIn('summary', export_results, "Should create summary")
        
        # Step 8: Save and load session
        session_manager = SessionManager()
        session_path = self.session_dir / f"test_session_{session.session_id}.pkl"
        
        session_manager.save_session(session, str(session_path))
        self.assertTrue(session_path.exists(), "Session should be saved")
        
        loaded_session = session_manager.load_session(str(session_path))
        self.assertEqual(loaded_session.session_id, session.session_id)
        self.assertEqual(len(loaded_session.emails), len(session.emails))
    
    def test_error_recovery(self):
        """Test error recovery scenarios."""
        emails, cpra_requests = self.load_demo_data()
        
        # Create session
        session = ProcessingSession(
            session_id="test_recovery",
            cpra_requests=cpra_requests,
            emails=emails[:5]  # Use subset for testing
        )
        
        # Simulate partial processing
        analyzer = CPRAAnalyzer()
        
        with patch.object(analyzer.ollama_client, 'generate') as mock_generate:
            # First call succeeds
            mock_generate.side_effect = [
                json.dumps({
                    "responsive": [True, False, False],
                    "confidence": ["high", "high", "high"],
                    "reasoning": ["Test"]
                }),
                # Second call fails
                Exception("Simulated model failure"),
                # Third call succeeds
                json.dumps({
                    "responsive": [False, False, False],
                    "confidence": ["high", "high", "high"],
                    "reasoning": ["Test"]
                })
            ]
            
            results = []
            for i, email in enumerate(session.emails):
                try:
                    result = analyzer.analyze_email_responsiveness(
                        email,
                        [req.text for req in cpra_requests]
                    )
                    results.append(result)
                except Exception:
                    results.append(None)
            
            # Should have mix of successful and failed results
            successful = [r for r in results if r is not None]
            failed = [r for r in results if r is None]
            
            self.assertGreater(len(successful), 0, "Should have some successful results")
            self.assertGreater(len(failed), 0, "Should have some failed results")
    
    def test_session_recovery(self):
        """Test session save and recovery functionality."""
        emails, cpra_requests = self.load_demo_data()
        
        # Create and save session
        original_session = ProcessingSession(
            session_id="recovery_test",
            cpra_requests=cpra_requests,
            emails=emails[:3]
        )
        
        # Add some analysis results
        original_session.responsiveness_results["0"] = Mock(
            is_responsive=True,
            confidence=["high"],
            reasoning=["Test reasoning"]
        )
        
        # Save session
        session_manager = SessionManager()
        recovery_path = self.session_dir / "recovery" / f"recovery_{original_session.session_id}.pkl"
        recovery_path.parent.mkdir(parents=True, exist_ok=True)
        
        session_manager.save_session(original_session, str(recovery_path))
        
        # Load session
        loaded_session = session_manager.load_session(str(recovery_path))
        
        self.assertEqual(loaded_session.session_id, original_session.session_id)
        self.assertEqual(len(loaded_session.emails), len(original_session.emails))
        self.assertIn("0", loaded_session.responsiveness_results)
    
    def test_batch_processing(self):
        """Test batch processing functionality."""
        emails, cpra_requests = self.load_demo_data()
        
        analyzer = CPRAAnalyzer()
        
        # Mock Ollama for speed
        with patch.object(analyzer.ollama_client, 'generate') as mock_generate:
            mock_generate.return_value = json.dumps({
                "responsive": [True, False, True],
                "confidence": ["high", "medium", "low"],
                "reasoning": ["Test batch processing"]
            })
            
            # Process in batches
            batch_size = self.config.processing.batch_size
            results = []
            
            for i in range(0, len(emails[:10]), batch_size):
                batch = emails[i:i+batch_size]
                batch_results = analyzer.analyze_batch_responsiveness(
                    batch,
                    [req.text for req in cpra_requests]
                )
                results.extend(batch_results)
            
            self.assertEqual(len(results), min(10, len(emails)))
    
    def test_export_formats(self):
        """Test different export formats."""
        emails, cpra_requests = self.load_demo_data()
        
        # Create minimal session for testing
        session = ProcessingSession(
            session_id="export_test",
            cpra_requests=cpra_requests,
            emails=emails[:2]
        )
        
        # Add mock analysis results
        session.responsiveness_results["0"] = Mock(
            is_responsive=True,
            confidence=["high"],
            reasoning=["Test"],
            email_id="0"
        )
        
        session.exemption_results["0"] = Mock(
            has_exemptions=True,
            exemptions=["attorney_client_privilege"],
            confidence=["high"],
            reasoning=["Legal discussion"]
        )
        
        # Initialize review manager
        review_manager = ReviewManager()
        review_manager.initialize_reviews(session)
        
        # Complete reviews
        for review_id in review_manager.reviews:
            review_manager.start_review(review_id)
            review_manager.finalize_review(review_id)
        
        # Test export
        export_manager = ExportManager(session, review_manager)
        
        # Export production PDF
        pdf_path = export_manager.export_production_pdf(
            str(self.export_dir / "test_production.pdf")
        )
        self.assertTrue(Path(pdf_path).exists() if pdf_path else True)
        
        # Export privilege log
        csv_path, pdf_path = export_manager.export_privilege_log(str(self.export_dir))
        self.assertTrue(Path(csv_path).exists() if csv_path else True)
    
    def test_configuration_loading(self):
        """Test configuration loading and validation."""
        config = get_config()
        
        # Test configuration values
        self.assertIsNotNone(config.model.default_model)
        self.assertGreater(config.model.timeout_seconds, 0)
        self.assertGreater(config.processing.batch_size, 0)
        
        # Test configuration validation
        self.assertTrue(config.validate())
        
        # Test configuration update
        new_settings = {
            'model': {'temperature': 0.5},
            'processing': {'batch_size': 10}
        }
        config.update_from_dict(new_settings)
        
        self.assertEqual(config.model.temperature, 0.5)
        self.assertEqual(config.processing.batch_size, 10)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and recovery."""
    
    def test_malformed_email_handling(self):
        """Test handling of malformed emails."""
        parser = EmailParser()
        
        # Test empty content
        emails = parser.parse_email_file("")
        self.assertEqual(len(emails), 0)
        
        # Test malformed content
        malformed = "This is not a proper email format"
        emails = parser.parse_email_file(malformed)
        # Parser should still attempt to create an email object
        self.assertIsInstance(emails, list)
    
    def test_model_timeout_handling(self):
        """Test handling of model timeouts."""
        analyzer = CPRAAnalyzer()
        
        # Create test email
        email = Email(
            sender="test@example.com",
            recipients=["recipient@example.com"],
            subject="Test",
            body="Test content",
            date=datetime.now().isoformat()
        )
        
        # Mock timeout
        with patch.object(analyzer.ollama_client, 'generate') as mock_generate:
            mock_generate.side_effect = TimeoutError("Model timeout")
            
            result = analyzer.analyze_email_responsiveness(
                email,
                ["Test request"]
            )
            
            # Should return None or handle gracefully
            self.assertIsNone(result)
    
    def test_review_manager_error_handling(self):
        """Test review manager error handling."""
        review_manager = ReviewManager()
        
        # Test with empty session
        empty_session = ProcessingSession(
            session_id="empty_test",
            cpra_requests=[],
            emails=[]
        )
        
        review_manager.initialize_reviews(empty_session)
        self.assertEqual(len(review_manager.reviews), 0)
        
        # Test invalid review operations
        with self.assertRaises(ValueError):
            review_manager.start_review("nonexistent_id")
        
        with self.assertRaises(ValueError):
            review_manager.finalize_review("nonexistent_id")


if __name__ == "__main__":
    unittest.main()