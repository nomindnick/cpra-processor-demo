"""
Unit tests for Export Manager functionality.
Tests PDF generation, privilege log creation, and export validation.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from processors.export_manager import ExportManager
from utils.data_structures import (
    ProcessingSession, Email, DocumentReview, ReviewStatus,
    ExemptionType, ResponsivenessAnalysis, ExemptionAnalysis,
    ConfidenceLevel, CPRARequest
)


class TestExportManager(unittest.TestCase):
    """Test suite for ExportManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test exports
        self.temp_dir = tempfile.mkdtemp()
        self.export_manager = ExportManager(output_dir=self.temp_dir)
        
        # Create test session with sample data
        self.session = self._create_test_session()
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_test_session(self) -> ProcessingSession:
        """Create a test processing session with sample data."""
        session = ProcessingSession()
        session.session_id = "test_session_001"
        session.model_used = "test_model"
        
        # Add CPRA requests
        session.cpra_requests = [
            CPRARequest(text="All documents regarding roof leaks"),
            CPRARequest(text="All documents regarding change orders")
        ]
        
        # Create test emails
        emails = [
            Email(
                from_address="john@example.com",
                to_address="jane@example.com",
                subject="Roof Leak Report",
                date=datetime(2024, 1, 15, 10, 30),
                body="We found significant water damage in the roof.",
                message_id="email_0"
            ),
            Email(
                from_address="attorney@law.com",
                to_address="client@example.com",
                subject="Legal Analysis - Privileged",
                date=datetime(2024, 1, 16, 14, 0),
                body="This is attorney-client privileged communication.",
                message_id="email_1"
            ),
            Email(
                from_address="hr@example.com",
                to_address="manager@example.com",
                subject="Employee Performance Review",
                date=datetime(2024, 1, 17, 9, 0),
                body="Confidential personnel record.",
                message_id="email_2"
            )
        ]
        
        session.emails = emails
        
        # Create responsiveness analysis results
        session.responsiveness_results = {
            "email_0": ResponsivenessAnalysis(
                email_id="email_0",
                cpra_requests=[req.text for req in session.cpra_requests],
                responsive=[True, False],  # Responsive to first request only
                confidence=[ConfidenceLevel.HIGH, ConfidenceLevel.HIGH],
                reasoning=["Directly about roof leaks", "Not about change orders"]
            ),
            "email_1": ResponsivenessAnalysis(
                email_id="email_1",
                cpra_requests=[req.text for req in session.cpra_requests],
                responsive=[False, False],
                confidence=[ConfidenceLevel.HIGH, ConfidenceLevel.HIGH],
                reasoning=["Not about roof leaks", "Not about change orders"]
            ),
            "email_2": ResponsivenessAnalysis(
                email_id="email_2",
                cpra_requests=[req.text for req in session.cpra_requests],
                responsive=[False, False],
                confidence=[ConfidenceLevel.HIGH, ConfidenceLevel.HIGH],
                reasoning=["Not about roof leaks", "Not about change orders"]
            )
        }
        
        # Create exemption analysis results
        session.exemption_results = {
            "email_0": ExemptionAnalysis(
                email_id="email_0",
                attorney_client={"applies": False, "confidence": ConfidenceLevel.HIGH, "reasoning": ""},
                personnel={"applies": False, "confidence": ConfidenceLevel.HIGH, "reasoning": ""},
                deliberative={"applies": False, "confidence": ConfidenceLevel.HIGH, "reasoning": ""}
            ),
            "email_1": ExemptionAnalysis(
                email_id="email_1",
                attorney_client={"applies": True, "confidence": ConfidenceLevel.HIGH, 
                               "reasoning": "Communication between attorney and client"},
                personnel={"applies": False, "confidence": ConfidenceLevel.HIGH, "reasoning": ""},
                deliberative={"applies": False, "confidence": ConfidenceLevel.HIGH, "reasoning": ""}
            ),
            "email_2": ExemptionAnalysis(
                email_id="email_2",
                attorney_client={"applies": False, "confidence": ConfidenceLevel.HIGH, "reasoning": ""},
                personnel={"applies": True, "confidence": ConfidenceLevel.HIGH,
                          "reasoning": "Contains employee performance information"},
                deliberative={"applies": False, "confidence": ConfidenceLevel.HIGH, "reasoning": ""}
            )
        }
        
        # Create document reviews
        session.document_reviews = {
            "email_0": DocumentReview(
                email_id="email_0",
                review_status=ReviewStatus.COMPLETED,
                final_responsive=[True, False],
                final_exemptions=[],
                reviewed_by="test_user"
            ),
            "email_1": DocumentReview(
                email_id="email_1",
                review_status=ReviewStatus.COMPLETED,
                final_responsive=[False, False],
                final_exemptions=[ExemptionType.ATTORNEY_CLIENT],
                reviewed_by="test_user"
            ),
            "email_2": DocumentReview(
                email_id="email_2",
                review_status=ReviewStatus.COMPLETED,
                final_responsive=[False, False],
                final_exemptions=[ExemptionType.PERSONNEL],
                reviewed_by="test_user"
            )
        }
        
        return session
    
    def test_validate_export_readiness_success(self):
        """Test validation of export-ready session."""
        result = self.export_manager.validate_export_readiness(self.session)
        
        self.assertTrue(result["ready"])
        self.assertEqual(len(result["warnings"]), 0)
        self.assertEqual(len(result["errors"]), 0)
    
    def test_validate_export_readiness_no_documents(self):
        """Test validation with no documents."""
        empty_session = ProcessingSession()
        result = self.export_manager.validate_export_readiness(empty_session)
        
        self.assertFalse(result["ready"])
        self.assertIn("No documents in session", result["errors"])
    
    def test_validate_export_readiness_incomplete_reviews(self):
        """Test validation with incomplete reviews."""
        # Mark one review as pending
        self.session.document_reviews["email_2"].review_status = ReviewStatus.PENDING
        
        result = self.export_manager.validate_export_readiness(self.session)
        
        # Should still be ready but with warning
        self.assertTrue(result["ready"])
        self.assertTrue(result["allow_partial"])
        self.assertIn("2/3", result["reason"])  # 2 of 3 reviewed
    
    def test_get_producible_documents(self):
        """Test getting producible documents (responsive, non-exempt)."""
        producible = self.export_manager._get_producible_documents(self.session)
        
        # Only email_0 should be producible (responsive and no exemptions)
        self.assertEqual(len(producible), 1)
        self.assertEqual(producible[0].message_id, "email_0")
    
    def test_get_withheld_documents(self):
        """Test getting withheld documents."""
        withheld = self.export_manager._get_withheld_documents(self.session)
        
        # email_1 and email_2 should be withheld
        self.assertEqual(len(withheld), 2)
        
        # Check exemption types
        withheld_ids = [doc["email_id"] for doc in withheld]
        self.assertIn("email_1", withheld_ids)
        self.assertIn("email_2", withheld_ids)
        
        # Verify exemptions
        for doc in withheld:
            if doc["email_id"] == "email_1":
                self.assertIn(ExemptionType.ATTORNEY_CLIENT, doc["exemptions"])
            elif doc["email_id"] == "email_2":
                self.assertIn(ExemptionType.PERSONNEL, doc["exemptions"])
    
    def test_generate_filename(self):
        """Test filename generation."""
        filename = self.export_manager._generate_filename(
            "Production", "pdf", "session123"
        )
        
        self.assertTrue(filename.startswith("CPRA_Production_session123_"))
        self.assertTrue(filename.endswith(".pdf"))
    
    @patch('processors.export_manager.PDFGenerator')
    @patch('processors.export_manager.PrivilegeLogGenerator')
    def test_generate_production_pdf(self, mock_privilege_gen, mock_pdf_gen):
        """Test production PDF generation."""
        # Mock PDF generator
        mock_pdf_instance = MagicMock()
        mock_pdf_gen.return_value = mock_pdf_instance
        
        # Reinitialize export manager with mocked dependencies
        self.export_manager = ExportManager(output_dir=self.temp_dir)
        self.export_manager.pdf_generator = mock_pdf_instance
        
        # Generate production PDF
        pdf_path = self.export_manager.generate_production_pdf(self.session)
        
        # Verify PDF generator was called
        mock_pdf_instance.generate_production_pdf.assert_called_once()
        
        # Check arguments
        call_args = mock_pdf_instance.generate_production_pdf.call_args
        self.assertEqual(len(call_args[1]['emails']), 1)  # Only 1 producible document
        self.assertEqual(call_args[1]['emails'][0].message_id, "email_0")
        self.assertTrue(pdf_path.endswith(".pdf"))
    
    @patch('src.processors.export_manager.PrivilegeLogGenerator')
    def test_generate_privilege_log(self, mock_privilege_gen):
        """Test privilege log generation."""
        # Mock privilege log generator
        mock_log_instance = MagicMock()
        mock_privilege_gen.return_value = mock_log_instance
        
        # Reinitialize export manager with mocked dependency
        self.export_manager = ExportManager(output_dir=self.temp_dir)
        self.export_manager.privilege_log_generator = mock_log_instance
        
        # Generate privilege log
        log_path = self.export_manager.generate_privilege_log(self.session)
        
        # Verify both CSV and PDF generation were called
        mock_log_instance.generate_csv_log.assert_called_once()
        mock_log_instance.generate_pdf_log.assert_called_once()
        
        # Check arguments
        call_args = mock_log_instance.generate_csv_log.call_args
        withheld_docs = call_args[1]['withheld_documents']
        self.assertEqual(len(withheld_docs), 2)  # 2 withheld documents
        self.assertTrue(log_path.endswith(".csv"))
    
    def test_create_export_manifest(self):
        """Test export manifest creation."""
        export_files = {
            "production_pdf": "/path/to/production.pdf",
            "privilege_log": "/path/to/privilege.csv"
        }
        
        manifest_path = self.export_manager.create_export_manifest(
            self.session, export_files
        )
        
        # Verify manifest was created
        self.assertTrue(os.path.exists(manifest_path))
        
        # Read and verify content
        with open(manifest_path, 'r') as f:
            content = f.read()
        
        self.assertIn("CPRA EXPORT MANIFEST", content)
        self.assertIn("Session ID: test_session_001", content)
        self.assertIn("Total Documents: 3", content)
        self.assertIn("Produced Documents: 1", content)
        self.assertIn("Withheld Documents: 2", content)
    
    @patch('processors.export_manager.PDFGenerator')
    @patch('processors.export_manager.PrivilegeLogGenerator')
    def test_generate_exports_complete(self, mock_privilege_gen, mock_pdf_gen):
        """Test complete export generation."""
        # Mock generators
        mock_pdf_instance = MagicMock()
        mock_pdf_gen.return_value = mock_pdf_instance
        mock_log_instance = MagicMock()
        mock_privilege_gen.return_value = mock_log_instance
        
        # Reinitialize export manager
        self.export_manager = ExportManager(output_dir=self.temp_dir)
        self.export_manager.pdf_generator = mock_pdf_instance
        self.export_manager.privilege_log_generator = mock_log_instance
        
        # Generate all exports
        export_files = self.export_manager.generate_exports(
            self.session, include_summary=True
        )
        
        # Verify all export types were generated
        self.assertIn("production_pdf", export_files)
        self.assertIn("privilege_log", export_files)
        self.assertIn("summary_report", export_files)
        self.assertIn("manifest", export_files)
        
        # Verify methods were called
        mock_pdf_instance.generate_production_pdf.assert_called_once()
        mock_pdf_instance.generate_summary_report.assert_called_once()
        mock_log_instance.generate_csv_log.assert_called_once()
        mock_log_instance.generate_pdf_log.assert_called_once()
    
    def test_exemption_reasoning_extraction(self):
        """Test extraction of exemption reasoning."""
        exemptions = [ExemptionType.ATTORNEY_CLIENT]
        analysis = self.session.exemption_results["email_1"]
        
        reasoning = self.export_manager._get_exemption_reasoning(
            exemptions, analysis
        )
        
        self.assertIn("attorney_client", reasoning)
        self.assertEqual(
            reasoning["attorney_client"],
            "Communication between attorney and client"
        )
    
    def test_export_with_unreviewed_documents(self):
        """Test export behavior with unreviewed documents."""
        # Mark one document as pending
        self.session.document_reviews["email_2"].review_status = ReviewStatus.PENDING
        
        # Should still be able to export with partial results
        producible = self.export_manager._get_producible_documents(self.session)
        withheld = self.export_manager._get_withheld_documents(self.session)
        
        # email_2 should be excluded from both lists
        self.assertEqual(len(producible), 1)  # Only email_0
        self.assertEqual(len(withheld), 1)    # Only email_1
        
        withheld_ids = [doc["email_id"] for doc in withheld]
        self.assertNotIn("email_2", withheld_ids)


class TestExportIntegration(unittest.TestCase):
    """Integration tests for export functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_export_empty_session(self):
        """Test export with empty session."""
        export_manager = ExportManager(output_dir=self.temp_dir)
        empty_session = ProcessingSession()
        empty_session.session_id = "empty_test"
        
        # Should raise error for empty session
        with self.assertRaises(ValueError) as context:
            export_manager.generate_exports(empty_session)
        
        self.assertIn("No documents", str(context.exception))
    
    def test_export_file_creation(self):
        """Test that export files are actually created."""
        # This test would require actual file creation
        # For now, we'll skip actual PDF generation testing
        # as it requires reportlab to be properly configured
        pass


if __name__ == '__main__':
    unittest.main()