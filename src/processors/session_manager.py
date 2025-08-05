"""
Session Manager for CPRA document processing.
Handles session persistence, recovery, and state management.
"""

import json
import pickle
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.data_structures import (
    ProcessingSession, Email, CPRARequest, ResponsivenessAnalysis,
    ExemptionAnalysis, DocumentReview, ReviewStatus, ConfidenceLevel,
    ExemptionType, ProcessingStats
)


class SessionManager:
    """Manages processing session persistence and recovery."""
    
    def __init__(self, data_dir: str = "data/sessions"):
        """
        Initialize the session manager.
        
        Args:
            data_dir: Directory for storing session data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def save_session(self, session: ProcessingSession, format: str = "json") -> str:
        """
        Save a processing session to disk.
        
        Args:
            session: ProcessingSession to save
            format: Save format ('json' or 'pickle')
            
        Returns:
            Path to saved session file
        """
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = session.session_id or f"session_{timestamp}"
        
        if format == "json":
            filepath = self.data_dir / f"{session_id}.json"
            self._save_session_json(session, filepath)
        elif format == "pickle":
            filepath = self.data_dir / f"{session_id}.pkl"
            self._save_session_pickle(session, filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        self.logger.info(f"Session saved to {filepath}")
        return str(filepath)
    
    def load_session(self, filepath: str) -> Optional[ProcessingSession]:
        """
        Load a processing session from disk.
        
        Args:
            filepath: Path to session file
            
        Returns:
            ProcessingSession object or None if loading failed
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            self.logger.error(f"Session file not found: {filepath}")
            return None
        
        try:
            if filepath.suffix == ".json":
                return self._load_session_json(filepath)
            elif filepath.suffix == ".pkl":
                return self._load_session_pickle(filepath)
            else:
                self.logger.error(f"Unsupported file format: {filepath.suffix}")
                return None
        except Exception as e:
            self.logger.error(f"Error loading session: {e}")
            return None
    
    def _save_session_json(self, session: ProcessingSession, filepath: Path) -> None:
        """
        Save session as JSON (human-readable format).
        
        Args:
            session: ProcessingSession to save
            filepath: Path to save file
        """
        data = {
            "session_id": session.session_id,
            "model_used": session.model_used,
            "timestamp": datetime.now().isoformat(),
            "cpra_requests": self._serialize_cpra_requests(session.cpra_requests),
            "emails": self._serialize_emails(session.emails),
            "responsiveness_results": self._serialize_responsiveness_results(session.responsiveness_results),
            "exemption_results": self._serialize_exemption_results(session.exemption_results),
            "document_reviews": self._serialize_document_reviews(session.document_reviews),
            "stats": self._serialize_stats(session.stats)
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load_session_json(self, filepath: Path) -> ProcessingSession:
        """
        Load session from JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            ProcessingSession object
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        session = ProcessingSession(
            session_id=data.get("session_id", ""),
            model_used=data.get("model_used", "")
        )
        
        # Deserialize components
        session.cpra_requests = self._deserialize_cpra_requests(data.get("cpra_requests", []))
        session.emails = self._deserialize_emails(data.get("emails", []))
        session.responsiveness_results = self._deserialize_responsiveness_results(data.get("responsiveness_results", {}))
        session.exemption_results = self._deserialize_exemption_results(data.get("exemption_results", {}))
        session.document_reviews = self._deserialize_document_reviews(data.get("document_reviews", {}))
        session.stats = self._deserialize_stats(data.get("stats", {}))
        
        return session
    
    def _save_session_pickle(self, session: ProcessingSession, filepath: Path) -> None:
        """
        Save session as pickle (binary format, preserves all object types).
        
        Args:
            session: ProcessingSession to save
            filepath: Path to save file
        """
        with open(filepath, 'wb') as f:
            pickle.dump(session, f)
    
    def _load_session_pickle(self, filepath: Path) -> ProcessingSession:
        """
        Load session from pickle file.
        
        Args:
            filepath: Path to pickle file
            
        Returns:
            ProcessingSession object
        """
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    
    def _serialize_cpra_requests(self, requests: list) -> list:
        """Serialize CPRA requests for JSON storage."""
        return [
            {
                "text": req.text,
                "request_id": req.request_id,
                "description": req.description
            }
            for req in requests
        ]
    
    def _deserialize_cpra_requests(self, data: list) -> list:
        """Deserialize CPRA requests from JSON."""
        return [
            CPRARequest(
                text=req["text"],
                request_id=req.get("request_id"),
                description=req.get("description")
            )
            for req in data
        ]
    
    def _serialize_emails(self, emails: list) -> list:
        """Serialize emails for JSON storage."""
        return [
            {
                "from_address": email.from_address,
                "to_address": email.to_address,
                "subject": email.subject,
                "date": email.date.isoformat() if email.date else None,
                "body": email.body,
                "message_id": email.message_id,
                "cc_addresses": email.cc_addresses,
                "bcc_addresses": email.bcc_addresses,
                "reply_to": email.reply_to,
                "raw_text": email.raw_text,
                "parsed_successfully": email.parsed_successfully,
                "parsing_errors": email.parsing_errors
            }
            for email in emails
        ]
    
    def _deserialize_emails(self, data: list) -> list:
        """Deserialize emails from JSON."""
        emails = []
        for email_data in data:
            email = Email(
                from_address=email_data["from_address"],
                to_address=email_data["to_address"],
                subject=email_data["subject"],
                date=datetime.fromisoformat(email_data["date"]) if email_data["date"] else datetime.now(),
                body=email_data["body"]
            )
            email.message_id = email_data.get("message_id")
            email.cc_addresses = email_data.get("cc_addresses", [])
            email.bcc_addresses = email_data.get("bcc_addresses", [])
            email.reply_to = email_data.get("reply_to")
            email.raw_text = email_data.get("raw_text", "")
            email.parsed_successfully = email_data.get("parsed_successfully", True)
            email.parsing_errors = email_data.get("parsing_errors", [])
            emails.append(email)
        return emails
    
    def _serialize_responsiveness_results(self, results: Dict[str, ResponsivenessAnalysis]) -> Dict:
        """Serialize responsiveness results for JSON storage."""
        serialized = {}
        for email_id, analysis in results.items():
            serialized[email_id] = {
                "email_id": analysis.email_id,
                "cpra_requests": analysis.cpra_requests,
                "responsive": analysis.responsive,
                "confidence": [c.value for c in analysis.confidence],
                "reasoning": analysis.reasoning,
                "model_used": analysis.model_used,
                "analysis_timestamp": analysis.analysis_timestamp.isoformat() if analysis.analysis_timestamp else None,
                "processing_time_seconds": analysis.processing_time_seconds
            }
        return serialized
    
    def _deserialize_responsiveness_results(self, data: Dict) -> Dict[str, ResponsivenessAnalysis]:
        """Deserialize responsiveness results from JSON."""
        results = {}
        for email_id, analysis_data in data.items():
            analysis = ResponsivenessAnalysis(
                email_id=analysis_data["email_id"],
                cpra_requests=analysis_data["cpra_requests"],
                responsive=analysis_data["responsive"],
                confidence=[ConfidenceLevel(c) for c in analysis_data["confidence"]],
                reasoning=analysis_data["reasoning"]
            )
            analysis.model_used = analysis_data.get("model_used", "")
            if analysis_data.get("analysis_timestamp"):
                analysis.analysis_timestamp = datetime.fromisoformat(analysis_data["analysis_timestamp"])
            analysis.processing_time_seconds = analysis_data.get("processing_time_seconds")
            results[email_id] = analysis
        return results
    
    def _serialize_exemption_results(self, results: Dict[str, ExemptionAnalysis]) -> Dict:
        """Serialize exemption results for JSON storage."""
        serialized = {}
        for email_id, analysis in results.items():
            serialized[email_id] = {
                "email_id": analysis.email_id,
                "attorney_client": {
                    "applies": analysis.attorney_client["applies"],
                    "confidence": analysis.attorney_client["confidence"].value if isinstance(analysis.attorney_client["confidence"], ConfidenceLevel) else analysis.attorney_client["confidence"],
                    "reasoning": analysis.attorney_client["reasoning"]
                },
                "personnel": {
                    "applies": analysis.personnel["applies"],
                    "confidence": analysis.personnel["confidence"].value if isinstance(analysis.personnel["confidence"], ConfidenceLevel) else analysis.personnel["confidence"],
                    "reasoning": analysis.personnel["reasoning"]
                },
                "deliberative": {
                    "applies": analysis.deliberative["applies"],
                    "confidence": analysis.deliberative["confidence"].value if isinstance(analysis.deliberative["confidence"], ConfidenceLevel) else analysis.deliberative["confidence"],
                    "reasoning": analysis.deliberative["reasoning"]
                },
                "model_used": analysis.model_used,
                "analysis_timestamp": analysis.analysis_timestamp.isoformat() if analysis.analysis_timestamp else None,
                "processing_time_seconds": analysis.processing_time_seconds
            }
        return serialized
    
    def _deserialize_exemption_results(self, data: Dict) -> Dict[str, ExemptionAnalysis]:
        """Deserialize exemption results from JSON."""
        results = {}
        for email_id, analysis_data in data.items():
            analysis = ExemptionAnalysis(email_id=analysis_data["email_id"])
            
            # Deserialize each exemption type
            for exemption_type in ["attorney_client", "personnel", "deliberative"]:
                exemption_data = analysis_data[exemption_type]
                deserialized = {
                    "applies": exemption_data["applies"],
                    "confidence": ConfidenceLevel(exemption_data["confidence"]),
                    "reasoning": exemption_data["reasoning"]
                }
                setattr(analysis, exemption_type, deserialized)
            
            analysis.model_used = analysis_data.get("model_used", "")
            if analysis_data.get("analysis_timestamp"):
                analysis.analysis_timestamp = datetime.fromisoformat(analysis_data["analysis_timestamp"])
            analysis.processing_time_seconds = analysis_data.get("processing_time_seconds")
            results[email_id] = analysis
        return results
    
    def _serialize_document_reviews(self, reviews: Dict[str, DocumentReview]) -> Dict:
        """Serialize document reviews for JSON storage."""
        serialized = {}
        for email_id, review in reviews.items():
            serialized[email_id] = {
                "email_id": review.email_id,
                "user_responsive_override": {
                    str(k): v for k, v in review.user_responsive_override.items()
                } if review.user_responsive_override else None,
                "user_exemption_override": {
                    exemption_type.value: decision
                    for exemption_type, decision in review.user_exemption_override.items()
                } if review.user_exemption_override else None,
                "review_status": review.review_status.value,
                "reviewed_by": review.reviewed_by,
                "review_timestamp": review.review_timestamp.isoformat() if review.review_timestamp else None,
                "review_notes": review.review_notes,
                "final_responsive": review.final_responsive,
                "final_exemptions": [e.value for e in review.final_exemptions]
            }
        return serialized
    
    def _deserialize_document_reviews(self, data: Dict) -> Dict[str, DocumentReview]:
        """Deserialize document reviews from JSON."""
        reviews = {}
        for email_id, review_data in data.items():
            review = DocumentReview(email_id=review_data["email_id"])
            
            # Deserialize responsiveness overrides (convert string keys back to int)
            if review_data.get("user_responsive_override"):
                review.user_responsive_override = {
                    int(k): v for k, v in review_data["user_responsive_override"].items()
                }
            else:
                review.user_responsive_override = review_data.get("user_responsive_override")
            
            # Deserialize exemption overrides
            if review_data.get("user_exemption_override"):
                review.user_exemption_override = {
                    ExemptionType(exemption_str): decision
                    for exemption_str, decision in review_data["user_exemption_override"].items()
                }
            
            review.review_status = ReviewStatus(review_data["review_status"])
            review.reviewed_by = review_data.get("reviewed_by")
            if review_data.get("review_timestamp"):
                review.review_timestamp = datetime.fromisoformat(review_data["review_timestamp"])
            review.review_notes = review_data.get("review_notes", "")
            review.final_responsive = review_data.get("final_responsive", [])
            review.final_exemptions = [ExemptionType(e) for e in review_data.get("final_exemptions", [])]
            reviews[email_id] = review
        return reviews
    
    def _serialize_stats(self, stats: ProcessingStats) -> Dict:
        """Serialize processing stats for JSON storage."""
        return {
            "total_emails": stats.total_emails,
            "processed_emails": stats.processed_emails,
            "responsive_emails": stats.responsive_emails,
            "exempt_emails": stats.exempt_emails,
            "start_time": stats.start_time.isoformat() if stats.start_time else None,
            "end_time": stats.end_time.isoformat() if stats.end_time else None,
            "parsing_errors": stats.parsing_errors,
            "analysis_errors": stats.analysis_errors
        }
    
    def _deserialize_stats(self, data: Dict) -> ProcessingStats:
        """Deserialize processing stats from JSON."""
        stats = ProcessingStats()
        stats.total_emails = data.get("total_emails", 0)
        stats.processed_emails = data.get("processed_emails", 0)
        stats.responsive_emails = data.get("responsive_emails", 0)
        stats.exempt_emails = data.get("exempt_emails", 0)
        if data.get("start_time"):
            stats.start_time = datetime.fromisoformat(data["start_time"])
        if data.get("end_time"):
            stats.end_time = datetime.fromisoformat(data["end_time"])
        stats.parsing_errors = data.get("parsing_errors", 0)
        stats.analysis_errors = data.get("analysis_errors", 0)
        return stats
    
    def list_sessions(self) -> list:
        """
        List all saved sessions.
        
        Returns:
            List of session file paths
        """
        sessions = []
        for filepath in self.data_dir.glob("*.json"):
            sessions.append(str(filepath))
        for filepath in self.data_dir.glob("*.pkl"):
            sessions.append(str(filepath))
        return sorted(sessions)
    
    def delete_session(self, filepath: str) -> bool:
        """
        Delete a saved session file.
        
        Args:
            filepath: Path to session file
            
        Returns:
            True if deleted successfully, False otherwise
        """
        filepath = Path(filepath)
        if filepath.exists():
            filepath.unlink()
            self.logger.info(f"Deleted session: {filepath}")
            return True
        else:
            self.logger.warning(f"Session file not found: {filepath}")
            return False
    
    def auto_save_session(
        self,
        session: ProcessingSession,
        interval_seconds: int = 300
    ) -> None:
        """
        Auto-save session at regular intervals (for future implementation).
        
        Args:
            session: ProcessingSession to auto-save
            interval_seconds: Save interval in seconds
        """
        # This would be implemented with threading or async for real-time auto-save
        # For now, it's a placeholder for future enhancement
        self.logger.info(f"Auto-save configured for {interval_seconds}s intervals (not yet implemented)")


if __name__ == "__main__":
    """Test the session manager with sample data."""
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    from src.processors.review_manager import ReviewManager
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Create a test session
        session = ProcessingSession(session_id="test_session_002")
        
        # Add some test data
        session.cpra_requests = [
            CPRARequest(text="Test request 1", request_id="req_001"),
            CPRARequest(text="Test request 2", request_id="req_002")
        ]
        
        session.emails = [
            Email(
                from_address="sender@example.com",
                to_address="receiver@example.com",
                subject="Test Email 1",
                date=datetime.now(),
                body="This is a test email body."
            ),
            Email(
                from_address="another@example.com",
                to_address="recipient@example.com",
                subject="Test Email 2",
                date=datetime.now(),
                body="Another test email."
            )
        ]
        
        # Add some mock analysis results
        session.responsiveness_results["email_0"] = ResponsivenessAnalysis(
            email_id="email_0",
            cpra_requests=["Test request 1", "Test request 2"],
            responsive=[True, False],
            confidence=[ConfidenceLevel.HIGH, ConfidenceLevel.LOW],
            reasoning=["Relevant content", "Not relevant"]
        )
        
        session.exemption_results["email_0"] = ExemptionAnalysis(
            email_id="email_0",
            attorney_client={"applies": False, "confidence": ConfidenceLevel.HIGH, "reasoning": "No legal content"},
            personnel={"applies": False, "confidence": ConfidenceLevel.HIGH, "reasoning": "No personnel info"},
            deliberative={"applies": True, "confidence": ConfidenceLevel.MEDIUM, "reasoning": "Contains draft"}
        )
        
        # Initialize reviews
        review_manager = ReviewManager()
        review_manager.initialize_reviews(session)
        
        # Create session manager
        session_manager = SessionManager()
        
        # Test JSON save/load
        print("Testing JSON save/load...")
        json_path = session_manager.save_session(session, format="json")
        print(f"Saved session to: {json_path}")
        
        loaded_session = session_manager.load_session(json_path)
        if loaded_session:
            print(f"Loaded session: {loaded_session.session_id}")
            print(f"  - Emails: {len(loaded_session.emails)}")
            print(f"  - CPRA Requests: {len(loaded_session.cpra_requests)}")
            print(f"  - Reviews: {len(loaded_session.document_reviews)}")
        
        # Test pickle save/load
        print("\nTesting pickle save/load...")
        pickle_path = session_manager.save_session(session, format="pickle")
        print(f"Saved session to: {pickle_path}")
        
        loaded_session_pkl = session_manager.load_session(pickle_path)
        if loaded_session_pkl:
            print(f"Loaded session: {loaded_session_pkl.session_id}")
            print(f"  - Emails: {len(loaded_session_pkl.emails)}")
            print(f"  - CPRA Requests: {len(loaded_session_pkl.cpra_requests)}")
            print(f"  - Reviews: {len(loaded_session_pkl.document_reviews)}")
        
        # List all sessions
        print("\nAll saved sessions:")
        sessions = session_manager.list_sessions()
        for session_path in sessions:
            print(f"  - {session_path}")
        
    except Exception as e:
        print(f"Error running test: {e}")
        import traceback
        traceback.print_exc()