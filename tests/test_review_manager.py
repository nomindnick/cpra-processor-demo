"""
Unit tests for the review manager and session manager functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path
import tempfile
import json

from processors.review_manager import ReviewManager
from processors.session_manager import SessionManager
from utils.data_structures import (
    Email, CPRARequest, ResponsivenessAnalysis, ExemptionAnalysis,
    DocumentReview, ReviewStatus, ConfidenceLevel, ExemptionType,
    ProcessingSession, ProcessingStats
)


class TestReviewManager:
    """Test cases for ReviewManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.review_manager = ReviewManager()
        
        # Create test session with sample data
        self.session = ProcessingSession(session_id="test_session")
        
        # Add test emails
        self.session.emails = [
            Email(
                from_address="sender1@example.com",
                to_address="receiver@example.com",
                subject="Test Email 1",
                date=datetime(2024, 1, 15, 9, 30),
                body="Test body about roof issues",
                message_id="email_001"
            ),
            Email(
                from_address="sender2@example.com",
                to_address="receiver@example.com",
                subject="Test Email 2",
                date=datetime(2024, 1, 16, 10, 30),
                body="Test body about change orders",
                message_id="email_002"
            )
        ]
        
        # Add test CPRA requests
        self.session.cpra_requests = [
            CPRARequest(text="Documents about roof issues", request_id="req_001"),
            CPRARequest(text="Documents about change orders", request_id="req_002")
        ]
        
        # Add mock analysis results
        self.session.responsiveness_results = {
            "email_001": ResponsivenessAnalysis(
                email_id="email_001",
                cpra_requests=["Documents about roof issues", "Documents about change orders"],
                responsive=[True, False],
                confidence=[ConfidenceLevel.HIGH, ConfidenceLevel.LOW],
                reasoning=["Contains roof issues", "No change order content"]
            ),
            "email_002": ResponsivenessAnalysis(
                email_id="email_002",
                cpra_requests=["Documents about roof issues", "Documents about change orders"],
                responsive=[False, True],
                confidence=[ConfidenceLevel.LOW, ConfidenceLevel.HIGH],
                reasoning=["No roof content", "Contains change order info"]
            )
        }
        
        self.session.exemption_results = {
            "email_001": ExemptionAnalysis(
                email_id="email_001",
                attorney_client={"applies": False, "confidence": ConfidenceLevel.HIGH, "reasoning": "No legal content"},
                personnel={"applies": False, "confidence": ConfidenceLevel.HIGH, "reasoning": "No personnel info"},
                deliberative={"applies": True, "confidence": ConfidenceLevel.MEDIUM, "reasoning": "Contains draft"}
            ),
            "email_002": ExemptionAnalysis(
                email_id="email_002",
                attorney_client={"applies": True, "confidence": ConfidenceLevel.HIGH, "reasoning": "Legal advice"},
                personnel={"applies": False, "confidence": ConfidenceLevel.HIGH, "reasoning": "No personnel info"},
                deliberative={"applies": False, "confidence": ConfidenceLevel.HIGH, "reasoning": "Final document"}
            )
        }
    
    def test_initialize_reviews(self):
        """Test review initialization for all documents."""
        reviews = self.review_manager.initialize_reviews(self.session)
        
        assert len(reviews) == 2
        assert "email_001" in reviews
        assert "email_002" in reviews
        
        for review in reviews.values():
            assert review.review_status == ReviewStatus.PENDING
            assert review.email_id in ["email_001", "email_002"]
    
    def test_start_review(self):
        """Test starting a document review."""
        self.review_manager.initialize_reviews(self.session)
        review = self.session.document_reviews["email_001"]
        
        self.review_manager.start_review(review, "test_reviewer")
        
        assert review.review_status == ReviewStatus.IN_PROGRESS
        assert review.reviewed_by == "test_reviewer"
    
    def test_apply_responsiveness_override(self):
        """Test applying responsiveness override."""
        self.review_manager.initialize_reviews(self.session)
        review = self.session.document_reviews["email_001"]
        
        # Override first request determination (True -> False)
        self.review_manager.apply_responsiveness_override(
            review,
            self.session.responsiveness_results["email_001"],
            request_index=0,
            user_decision=False
        )
        
        assert review.user_responsive_override is not None
        assert review.user_responsive_override[0] == False
    
    def test_apply_exemption_override(self):
        """Test applying exemption override."""
        self.review_manager.initialize_reviews(self.session)
        review = self.session.document_reviews["email_001"]
        
        # Override deliberative exemption (True -> False)
        self.review_manager.apply_exemption_override(
            review,
            self.session.exemption_results["email_001"],
            exemption_type=ExemptionType.DELIBERATIVE,
            user_decision=False
        )
        
        assert review.user_exemption_override is not None
        assert review.user_exemption_override[ExemptionType.DELIBERATIVE] == False
    
    def test_finalize_review(self):
        """Test finalizing a document review."""
        self.review_manager.initialize_reviews(self.session)
        review = self.session.document_reviews["email_001"]
        
        # Start review
        self.review_manager.start_review(review, "test_reviewer")
        
        # Apply overrides
        self.review_manager.apply_responsiveness_override(
            review,
            self.session.responsiveness_results["email_001"],
            request_index=0,
            user_decision=False
        )
        
        self.review_manager.apply_exemption_override(
            review,
            self.session.exemption_results["email_001"],
            exemption_type=ExemptionType.DELIBERATIVE,
            user_decision=False
        )
        
        # Finalize
        self.review_manager.finalize_review(
            review,
            self.session.responsiveness_results["email_001"],
            self.session.exemption_results["email_001"],
            notes="Test review completed"
        )
        
        assert review.review_status == ReviewStatus.COMPLETED
        assert review.review_notes == "Test review completed"
        assert review.review_timestamp is not None
        
        # Check final determinations
        assert review.final_responsive == [False, False]  # First overridden, second original
        assert ExemptionType.DELIBERATIVE not in review.final_exemptions  # Overridden to False
    
    def test_get_review_summary(self):
        """Test generating review summary."""
        self.review_manager.initialize_reviews(self.session)
        
        # Complete one review
        review = self.session.document_reviews["email_001"]
        self.review_manager.start_review(review, "test_reviewer")
        self.review_manager.finalize_review(
            review,
            self.session.responsiveness_results["email_001"],
            self.session.exemption_results["email_001"]
        )
        
        summary = self.review_manager.get_review_summary(self.session)
        
        assert summary["total_documents"] == 2
        assert summary["review_status"]["pending"] == 1
        assert summary["review_status"]["completed"] == 1
        assert summary["completion_percentage"] == 50.0
    
    def test_get_pending_reviews(self):
        """Test getting pending reviews."""
        self.review_manager.initialize_reviews(self.session)
        
        # Complete one review
        review = self.session.document_reviews["email_001"]
        self.review_manager.start_review(review, "test_reviewer")
        self.review_manager.finalize_review(
            review,
            self.session.responsiveness_results["email_001"],
            self.session.exemption_results["email_001"]
        )
        
        pending = self.review_manager.get_pending_reviews(self.session)
        
        assert len(pending) == 1
        assert pending[0].email_id == "email_002"
    
    def test_validate_review_completion(self):
        """Test validation of review completion."""
        self.review_manager.initialize_reviews(self.session)
        
        # Initially not all reviewed
        all_reviewed, unreviewed = self.review_manager.validate_review_completion(self.session)
        assert all_reviewed == False
        assert len(unreviewed) == 2
        
        # Complete all reviews
        for email_id, review in self.session.document_reviews.items():
            self.review_manager.start_review(review)
            self.review_manager.finalize_review(
                review,
                self.session.responsiveness_results.get(email_id),
                self.session.exemption_results.get(email_id)
            )
        
        # Now all should be reviewed
        all_reviewed, unreviewed = self.review_manager.validate_review_completion(self.session)
        assert all_reviewed == True
        assert len(unreviewed) == 0
    
    def test_generate_audit_trail(self):
        """Test audit trail generation."""
        self.review_manager.initialize_reviews(self.session)
        
        # Complete a review with overrides
        review = self.session.document_reviews["email_001"]
        self.review_manager.start_review(review, "test_auditor")
        
        self.review_manager.apply_responsiveness_override(
            review,
            self.session.responsiveness_results["email_001"],
            request_index=0,
            user_decision=False
        )
        
        self.review_manager.apply_exemption_override(
            review,
            self.session.exemption_results["email_001"],
            exemption_type=ExemptionType.DELIBERATIVE,
            user_decision=False
        )
        
        self.review_manager.finalize_review(
            review,
            self.session.responsiveness_results["email_001"],
            self.session.exemption_results["email_001"],
            notes="Audit test"
        )
        
        audit_trail = self.review_manager.generate_audit_trail(self.session)
        
        assert len(audit_trail) == 1
        audit_entry = audit_trail[0]
        
        assert audit_entry["email_id"] == "email_001"
        assert audit_entry["reviewer"] == "test_auditor"
        assert audit_entry["notes"] == "Audit test"
        
        # Check override tracking
        assert "request_0" in audit_entry["overrides"]["responsiveness"]
        assert audit_entry["overrides"]["responsiveness"]["request_0"]["changed"] == True
        
        assert "deliberative" in audit_entry["overrides"]["exemptions"]
        assert audit_entry["overrides"]["exemptions"]["deliberative"]["changed"] == True
    
    def test_batch_approve_ai_determinations(self):
        """Test batch approval of AI determinations."""
        self.review_manager.initialize_reviews(self.session)
        
        approved_count = self.review_manager.batch_approve_ai_determinations(
            self.session,
            reviewer="batch_reviewer"
        )
        
        assert approved_count == 2
        
        # Check all reviews are completed
        for review in self.session.document_reviews.values():
            assert review.review_status == ReviewStatus.COMPLETED
            assert review.reviewed_by == "batch_reviewer"
            assert "Batch approved" in review.review_notes


class TestSessionManager:
    """Test cases for SessionManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directory for test sessions
        self.temp_dir = tempfile.mkdtemp()
        self.session_manager = SessionManager(data_dir=self.temp_dir)
        
        # Create test session
        self.session = ProcessingSession(session_id="test_session_003")
        
        # Add test data
        self.session.emails = [
            Email(
                from_address="test@example.com",
                to_address="recipient@example.com",
                subject="Test Subject",
                date=datetime(2024, 1, 15, 9, 30),
                body="Test body"
            )
        ]
        
        self.session.cpra_requests = [
            CPRARequest(text="Test request", request_id="req_001")
        ]
        
        self.session.responsiveness_results["email_0"] = ResponsivenessAnalysis(
            email_id="email_0",
            cpra_requests=["Test request"],
            responsive=[True],
            confidence=[ConfidenceLevel.HIGH],
            reasoning=["Test reasoning"]
        )
        
        self.session.exemption_results["email_0"] = ExemptionAnalysis(
            email_id="email_0"
        )
        
        self.session.document_reviews["email_0"] = DocumentReview(
            email_id="email_0",
            review_status=ReviewStatus.COMPLETED
        )
    
    def teardown_method(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_save_and_load_json(self):
        """Test saving and loading session as JSON."""
        # Save session
        filepath = self.session_manager.save_session(self.session, format="json")
        assert os.path.exists(filepath)
        assert filepath.endswith(".json")
        
        # Load session
        loaded_session = self.session_manager.load_session(filepath)
        assert loaded_session is not None
        assert loaded_session.session_id == "test_session_003"
        assert len(loaded_session.emails) == 1
        assert len(loaded_session.cpra_requests) == 1
        assert "email_0" in loaded_session.responsiveness_results
        assert "email_0" in loaded_session.exemption_results
        assert "email_0" in loaded_session.document_reviews
    
    def test_save_and_load_pickle(self):
        """Test saving and loading session as pickle."""
        # Save session
        filepath = self.session_manager.save_session(self.session, format="pickle")
        assert os.path.exists(filepath)
        assert filepath.endswith(".pkl")
        
        # Load session
        loaded_session = self.session_manager.load_session(filepath)
        assert loaded_session is not None
        assert loaded_session.session_id == "test_session_003"
        assert len(loaded_session.emails) == 1
    
    def test_list_sessions(self):
        """Test listing saved sessions."""
        # Save multiple sessions
        self.session_manager.save_session(self.session, format="json")
        self.session_manager.save_session(self.session, format="pickle")
        
        sessions = self.session_manager.list_sessions()
        assert len(sessions) >= 2
        assert any(".json" in s for s in sessions)
        assert any(".pkl" in s for s in sessions)
    
    def test_delete_session(self):
        """Test deleting a saved session."""
        # Save session
        filepath = self.session_manager.save_session(self.session, format="json")
        assert os.path.exists(filepath)
        
        # Delete session
        deleted = self.session_manager.delete_session(filepath)
        assert deleted == True
        assert not os.path.exists(filepath)
        
        # Try deleting non-existent file
        deleted = self.session_manager.delete_session(filepath)
        assert deleted == False
    
    def test_load_nonexistent_session(self):
        """Test loading a non-existent session file."""
        loaded = self.session_manager.load_session("nonexistent.json")
        assert loaded is None
    
    def test_session_with_overrides(self):
        """Test saving/loading session with review overrides."""
        # Add overrides to review
        review = self.session.document_reviews["email_0"]
        review.user_responsive_override = {0: False}
        review.user_exemption_override = {ExemptionType.ATTORNEY_CLIENT: True}
        review.final_responsive = [False]
        review.final_exemptions = [ExemptionType.ATTORNEY_CLIENT]
        
        # Save and load
        filepath = self.session_manager.save_session(self.session, format="json")
        loaded_session = self.session_manager.load_session(filepath)
        
        # Verify overrides preserved
        loaded_review = loaded_session.document_reviews["email_0"]
        assert loaded_review.user_responsive_override == {0: False}
        assert ExemptionType.ATTORNEY_CLIENT in loaded_review.user_exemption_override
        assert loaded_review.final_responsive == [False]
        assert ExemptionType.ATTORNEY_CLIENT in loaded_review.final_exemptions
    
    def test_session_stats_serialization(self):
        """Test processing stats serialization."""
        # Add stats to session
        self.session.stats = ProcessingStats(
            total_emails=10,
            processed_emails=8,
            responsive_emails=5,
            exempt_emails=2,
            start_time=datetime(2024, 1, 15, 9, 0),
            end_time=datetime(2024, 1, 15, 9, 30),
            parsing_errors=1,
            analysis_errors=0
        )
        
        # Save and load
        filepath = self.session_manager.save_session(self.session, format="json")
        loaded_session = self.session_manager.load_session(filepath)
        
        # Verify stats preserved
        assert loaded_session.stats.total_emails == 10
        assert loaded_session.stats.processed_emails == 8
        assert loaded_session.stats.responsive_emails == 5
        assert loaded_session.stats.exempt_emails == 2
        assert loaded_session.stats.parsing_errors == 1
        assert loaded_session.stats.analysis_errors == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])