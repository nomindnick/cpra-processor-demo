"""
Review Manager for CPRA document processing.
Handles user review and override of AI analysis results.
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.data_structures import (
    Email, ResponsivenessAnalysis, ExemptionAnalysis, DocumentReview,
    ReviewStatus, ExemptionType, ProcessingSession
)


class ReviewManager:
    """Manages document review and user override functionality."""
    
    def __init__(self):
        """Initialize the review manager."""
        self.logger = logging.getLogger(__name__)
    
    def initialize_reviews(
        self,
        session: ProcessingSession
    ) -> Dict[str, DocumentReview]:
        """
        Initialize review objects for all analyzed documents in a session.
        
        Args:
            session: ProcessingSession containing emails and analysis results
            
        Returns:
            Dictionary of email_id -> DocumentReview objects
        """
        reviews = {}
        
        for i, email in enumerate(session.emails):
            email_id = email.message_id if email.message_id else f"email_{i}"
            
            # Check if review already exists
            if email_id in session.document_reviews:
                reviews[email_id] = session.document_reviews[email_id]
                self.logger.info(f"Existing review found for {email_id}")
            else:
                # Create new review
                review = DocumentReview(
                    email_id=email_id,
                    review_status=ReviewStatus.PENDING
                )
                reviews[email_id] = review
                self.logger.info(f"Created new review for {email_id}")
        
        # Update session with reviews
        session.document_reviews = reviews
        
        self.logger.info(f"Initialized reviews for {len(reviews)} documents")
        return reviews
    
    def start_review(
        self,
        review: DocumentReview,
        reviewer: str = "user"
    ) -> None:
        """
        Mark a document review as in progress.
        
        Args:
            review: DocumentReview object to update
            reviewer: Name/ID of the reviewer
        """
        if review.review_status == ReviewStatus.COMPLETED:
            self.logger.warning(f"Document {review.email_id} already reviewed")
            return
        
        review.review_status = ReviewStatus.IN_PROGRESS
        review.reviewed_by = reviewer
        self.logger.info(f"Started review of {review.email_id} by {reviewer}")
    
    def apply_responsiveness_override(
        self,
        review: DocumentReview,
        responsiveness_analysis: ResponsivenessAnalysis,
        request_index: int,
        user_decision: bool
    ) -> None:
        """
        Apply user override for responsiveness determination.
        
        Args:
            review: DocumentReview object to update
            responsiveness_analysis: Original AI analysis
            request_index: Index of the CPRA request being overridden
            user_decision: User's override decision (True=responsive, False=not responsive)
        """
        # Initialize override dictionary if needed
        if review.user_responsive_override is None:
            review.user_responsive_override = {}
        
        # Store the override
        review.user_responsive_override[request_index] = user_decision
        
        # Log the override
        original_decision = responsiveness_analysis.responsive[request_index]
        if original_decision != user_decision:
            self.logger.info(
                f"Override applied for {review.email_id}, request {request_index}: "
                f"AI={original_decision}, User={user_decision}"
            )
    
    def apply_exemption_override(
        self,
        review: DocumentReview,
        exemption_analysis: ExemptionAnalysis,
        exemption_type: ExemptionType,
        user_decision: bool
    ) -> None:
        """
        Apply user override for exemption determination.
        
        Args:
            review: DocumentReview object to update
            exemption_analysis: Original AI analysis
            exemption_type: Type of exemption being overridden
            user_decision: User's override decision (True=applies, False=does not apply)
        """
        # Initialize override dictionary if needed
        if review.user_exemption_override is None:
            review.user_exemption_override = {}
        
        # Store the override
        review.user_exemption_override[exemption_type] = user_decision
        
        # Log the override
        if exemption_type == ExemptionType.ATTORNEY_CLIENT:
            original_decision = exemption_analysis.attorney_client["applies"]
        elif exemption_type == ExemptionType.PERSONNEL:
            original_decision = exemption_analysis.personnel["applies"]
        elif exemption_type == ExemptionType.DELIBERATIVE:
            original_decision = exemption_analysis.deliberative["applies"]
        else:
            original_decision = False
        
        if original_decision != user_decision:
            self.logger.info(
                f"Exemption override applied for {review.email_id}, {exemption_type.value}: "
                f"AI={original_decision}, User={user_decision}"
            )
    
    def finalize_review(
        self,
        review: DocumentReview,
        responsiveness_analysis: Optional[ResponsivenessAnalysis],
        exemption_analysis: Optional[ExemptionAnalysis],
        notes: str = ""
    ) -> None:
        """
        Finalize a document review with final determinations.
        
        Args:
            review: DocumentReview object to finalize
            responsiveness_analysis: Original responsiveness analysis
            exemption_analysis: Original exemption analysis
            notes: Optional review notes
        """
        # Generate final responsiveness determinations
        if responsiveness_analysis:
            final_responsive = []
            for i, original in enumerate(responsiveness_analysis.responsive):
                if review.user_responsive_override and i in review.user_responsive_override:
                    # Use user override
                    final_responsive.append(review.user_responsive_override[i])
                else:
                    # Use AI determination
                    final_responsive.append(original)
            review.final_responsive = final_responsive
        
        # Generate final exemption determinations
        if exemption_analysis:
            final_exemptions = []
            
            # Check attorney-client privilege
            if review.user_exemption_override and ExemptionType.ATTORNEY_CLIENT in review.user_exemption_override:
                if review.user_exemption_override[ExemptionType.ATTORNEY_CLIENT]:
                    final_exemptions.append(ExemptionType.ATTORNEY_CLIENT)
            elif exemption_analysis.attorney_client["applies"]:
                final_exemptions.append(ExemptionType.ATTORNEY_CLIENT)
            
            # Check personnel records
            if review.user_exemption_override and ExemptionType.PERSONNEL in review.user_exemption_override:
                if review.user_exemption_override[ExemptionType.PERSONNEL]:
                    final_exemptions.append(ExemptionType.PERSONNEL)
            elif exemption_analysis.personnel["applies"]:
                final_exemptions.append(ExemptionType.PERSONNEL)
            
            # Check deliberative process
            if review.user_exemption_override and ExemptionType.DELIBERATIVE in review.user_exemption_override:
                if review.user_exemption_override[ExemptionType.DELIBERATIVE]:
                    final_exemptions.append(ExemptionType.DELIBERATIVE)
            elif exemption_analysis.deliberative["applies"]:
                final_exemptions.append(ExemptionType.DELIBERATIVE)
            
            review.final_exemptions = final_exemptions
        
        # Add review notes
        if notes:
            review.review_notes = notes
        
        # Mark as reviewed
        review.mark_reviewed(review.reviewed_by or "user")
        
        self.logger.info(f"Finalized review for {review.email_id}")
    
    def get_review_summary(self, session: ProcessingSession) -> Dict:
        """
        Generate a summary of all reviews in a session.
        
        Args:
            session: ProcessingSession to summarize
            
        Returns:
            Dictionary containing review statistics and details
        """
        total_documents = len(session.emails)
        reviews = session.document_reviews
        
        # Count review statuses
        pending_count = sum(1 for r in reviews.values() if r.review_status == ReviewStatus.PENDING)
        in_progress_count = sum(1 for r in reviews.values() if r.review_status == ReviewStatus.IN_PROGRESS)
        completed_count = sum(1 for r in reviews.values() if r.review_status == ReviewStatus.COMPLETED)
        
        # Count overrides
        responsiveness_overrides = 0
        exemption_overrides = 0
        
        for review in reviews.values():
            if review.user_responsive_override:
                responsiveness_overrides += len(review.user_responsive_override)
            if review.user_exemption_override:
                exemption_overrides += len(review.user_exemption_override)
        
        # Generate summary
        summary = {
            "total_documents": total_documents,
            "review_status": {
                "pending": pending_count,
                "in_progress": in_progress_count,
                "completed": completed_count
            },
            "overrides": {
                "responsiveness": responsiveness_overrides,
                "exemptions": exemption_overrides,
                "total": responsiveness_overrides + exemption_overrides
            },
            "completion_percentage": (completed_count / total_documents * 100) if total_documents > 0 else 0
        }
        
        # Add reviewer information for completed reviews
        reviewers = {}
        for review in reviews.values():
            if review.review_status == ReviewStatus.COMPLETED and review.reviewed_by:
                if review.reviewed_by not in reviewers:
                    reviewers[review.reviewed_by] = 0
                reviewers[review.reviewed_by] += 1
        summary["reviewers"] = reviewers
        
        return summary
    
    def get_pending_reviews(self, session: ProcessingSession) -> List[DocumentReview]:
        """
        Get all pending reviews from a session.
        
        Args:
            session: ProcessingSession to check
            
        Returns:
            List of DocumentReview objects with PENDING status
        """
        pending = [
            review for review in session.document_reviews.values()
            if review.review_status == ReviewStatus.PENDING
        ]
        return pending
    
    def get_completed_reviews(self, session: ProcessingSession) -> List[DocumentReview]:
        """
        Get all completed reviews from a session.
        
        Args:
            session: ProcessingSession to check
            
        Returns:
            List of DocumentReview objects with COMPLETED status
        """
        completed = [
            review for review in session.document_reviews.values()
            if review.review_status == ReviewStatus.COMPLETED
        ]
        return completed
    
    def validate_review_completion(self, session: ProcessingSession) -> Tuple[bool, List[str]]:
        """
        Validate that all documents have been reviewed.
        
        Args:
            session: ProcessingSession to validate
            
        Returns:
            Tuple of (all_reviewed, list_of_unreviewed_email_ids)
        """
        unreviewed = []
        
        for email_id, review in session.document_reviews.items():
            if review.review_status != ReviewStatus.COMPLETED:
                unreviewed.append(email_id)
        
        all_reviewed = len(unreviewed) == 0
        
        if all_reviewed:
            self.logger.info("All documents have been reviewed")
        else:
            self.logger.warning(f"{len(unreviewed)} documents remain unreviewed")
        
        return all_reviewed, unreviewed
    
    def generate_audit_trail(self, session: ProcessingSession) -> List[Dict]:
        """
        Generate an audit trail of all review actions.
        
        Args:
            session: ProcessingSession to audit
            
        Returns:
            List of audit entries with timestamps and actions
        """
        audit_trail = []
        
        for email_id, review in session.document_reviews.items():
            if review.review_status == ReviewStatus.COMPLETED:
                entry = {
                    "email_id": email_id,
                    "reviewer": review.reviewed_by,
                    "review_timestamp": review.review_timestamp.isoformat() if review.review_timestamp else None,
                    "status": review.review_status.value,
                    "overrides": {
                        "responsiveness": {},
                        "exemptions": {}
                    },
                    "notes": review.review_notes
                }
                
                # Add responsiveness overrides
                if review.user_responsive_override:
                    for req_idx, decision in review.user_responsive_override.items():
                        # Get original decision if available
                        original = None
                        if email_id in session.responsiveness_results:
                            original = session.responsiveness_results[email_id].responsive[req_idx]
                        
                        entry["overrides"]["responsiveness"][f"request_{req_idx}"] = {
                            "original": original,
                            "override": decision,
                            "changed": original != decision if original is not None else None
                        }
                
                # Add exemption overrides
                if review.user_exemption_override:
                    for exemption_type, decision in review.user_exemption_override.items():
                        # Get original decision if available
                        original = None
                        if email_id in session.exemption_results:
                            exemption_result = session.exemption_results[email_id]
                            if exemption_type == ExemptionType.ATTORNEY_CLIENT:
                                original = exemption_result.attorney_client["applies"]
                            elif exemption_type == ExemptionType.PERSONNEL:
                                original = exemption_result.personnel["applies"]
                            elif exemption_type == ExemptionType.DELIBERATIVE:
                                original = exemption_result.deliberative["applies"]
                        
                        entry["overrides"]["exemptions"][exemption_type.value] = {
                            "original": original,
                            "override": decision,
                            "changed": original != decision if original is not None else None
                        }
                
                audit_trail.append(entry)
        
        return audit_trail
    
    def batch_approve_ai_determinations(
        self,
        session: ProcessingSession,
        reviewer: str = "user"
    ) -> int:
        """
        Batch approve all AI determinations without changes.
        Useful for quickly accepting AI analysis results.
        
        Args:
            session: ProcessingSession to process
            reviewer: Name/ID of the reviewer
            
        Returns:
            Number of documents approved
        """
        approved_count = 0
        
        for email_id, review in session.document_reviews.items():
            if review.review_status != ReviewStatus.COMPLETED:
                # Get corresponding analyses
                responsiveness = session.responsiveness_results.get(email_id)
                exemption = session.exemption_results.get(email_id)
                
                # Start and finalize review without overrides
                self.start_review(review, reviewer)
                self.finalize_review(review, responsiveness, exemption, "Batch approved - AI determinations accepted")
                approved_count += 1
        
        self.logger.info(f"Batch approved {approved_count} documents")
        return approved_count


if __name__ == "__main__":
    """Test the review manager with sample data."""
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    from src.parsers.email_parser import EmailParser
    from src.processors.cpra_analyzer import CPRAAnalyzer, create_sample_cpra_requests
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Create a sample session
        session = ProcessingSession(session_id="test_session_001")
        
        # Load sample emails
        email_parser = EmailParser()
        sample_file = "data/sample_emails/test_emails.txt"
        
        if os.path.exists(sample_file):
            with open(sample_file, 'r') as f:
                session.emails = email_parser.parse_email_file(f.read())[:3]  # Use first 3 emails for testing
            
            # Create sample CPRA requests
            session.cpra_requests = create_sample_cpra_requests()
            
            # Simulate some analysis results
            for i, email in enumerate(session.emails):
                email_id = f"email_{i}"
                
                # Create mock responsiveness analysis
                session.responsiveness_results[email_id] = ResponsivenessAnalysis(
                    email_id=email_id,
                    cpra_requests=[req.text for req in session.cpra_requests],
                    responsive=[True, False, True],
                    confidence=[ConfidenceLevel.HIGH, ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM],
                    reasoning=["Test reasoning"] * 3
                )
                
                # Create mock exemption analysis
                session.exemption_results[email_id] = ExemptionAnalysis(
                    email_id=email_id,
                    attorney_client={"applies": False, "confidence": ConfidenceLevel.HIGH, "reasoning": "No legal content"},
                    personnel={"applies": False, "confidence": ConfidenceLevel.HIGH, "reasoning": "No personnel info"},
                    deliberative={"applies": True, "confidence": ConfidenceLevel.MEDIUM, "reasoning": "Contains draft"}
                )
            
            # Test review manager
            review_manager = ReviewManager()
            
            # Initialize reviews
            reviews = review_manager.initialize_reviews(session)
            print(f"Initialized {len(reviews)} reviews")
            
            # Test single review with overrides
            if reviews:
                first_review = list(reviews.values())[0]
                first_email_id = first_review.email_id
                
                # Start review
                review_manager.start_review(first_review, "test_reviewer")
                
                # Apply some overrides
                review_manager.apply_responsiveness_override(
                    first_review,
                    session.responsiveness_results[first_email_id],
                    request_index=0,
                    user_decision=False  # Override TRUE to FALSE
                )
                
                review_manager.apply_exemption_override(
                    first_review,
                    session.exemption_results[first_email_id],
                    exemption_type=ExemptionType.DELIBERATIVE,
                    user_decision=False  # Override TRUE to FALSE
                )
                
                # Finalize review
                review_manager.finalize_review(
                    first_review,
                    session.responsiveness_results[first_email_id],
                    session.exemption_results[first_email_id],
                    notes="Test review with overrides"
                )
                
                print(f"Completed review for {first_email_id}")
            
            # Get review summary
            summary = review_manager.get_review_summary(session)
            print(f"\nReview Summary: {summary}")
            
            # Generate audit trail
            audit_trail = review_manager.generate_audit_trail(session)
            print(f"\nAudit Trail: {len(audit_trail)} entries")
            for entry in audit_trail:
                print(f"  - {entry['email_id']}: {entry['overrides']}")
            
        else:
            print(f"Sample email file not found: {sample_file}")
            
    except Exception as e:
        print(f"Error running test: {e}")
        import traceback
        traceback.print_exc()