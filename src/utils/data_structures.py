"""
Data structures for CPRA processing application.
Defines core data models for emails, analysis results, and review states.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Union
from enum import Enum


class ConfidenceLevel(Enum):
    """Confidence levels for AI analysis results."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReviewStatus(Enum):
    """Review status for documents."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ExemptionType(Enum):
    """CPRA exemption types."""
    ATTORNEY_CLIENT = "attorney_client"
    PERSONNEL = "personnel"
    DELIBERATIVE = "deliberative"


@dataclass
class Email:
    """Represents a parsed email with metadata."""
    
    # Core email fields
    from_address: str
    to_address: str
    subject: str
    date: datetime
    body: str
    
    # Metadata
    message_id: Optional[str] = None
    cc_addresses: List[str] = field(default_factory=list)
    bcc_addresses: List[str] = field(default_factory=list)
    reply_to: Optional[str] = None
    
    # Processing metadata
    raw_text: str = ""  # Original raw email text
    parsed_successfully: bool = True
    parsing_errors: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        """String representation of email."""
        return f"Email from {self.from_address} to {self.to_address} on {self.date.strftime('%Y-%m-%d %H:%M')} - Subject: {self.subject[:50]}..."
    
    def get_display_text(self) -> str:
        """Get formatted text for display in UI."""
        header = f"From: {self.from_address}\n"
        header += f"To: {self.to_address}\n"
        if self.cc_addresses:
            header += f"CC: {', '.join(self.cc_addresses)}\n"
        header += f"Date: {self.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"Subject: {self.subject}\n"
        header += "-" * 50 + "\n"
        header += self.body
        return header


@dataclass
class ResponsivenessAnalysis:
    """Results of responsiveness analysis for an email against CPRA requests."""
    
    email_id: str  # Identifier for the email being analyzed
    cpra_requests: List[str]  # The CPRA requests analyzed against
    
    # AI analysis results (parallel arrays)
    responsive: List[bool]  # Whether email is responsive to each request
    confidence: List[ConfidenceLevel]  # Confidence level for each determination
    reasoning: List[str]  # AI reasoning for each determination
    
    # Metadata
    model_used: str = ""
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    processing_time_seconds: Optional[float] = None
    
    def get_responsive_requests(self) -> List[int]:
        """Get indices of requests that this email is responsive to."""
        return [i for i, resp in enumerate(self.responsive) if resp]
    
    def is_responsive_to_any(self) -> bool:
        """Check if email is responsive to any request."""
        return any(self.responsive)


@dataclass
class ExemptionAnalysis:
    """Results of exemption analysis for an email."""
    
    email_id: str  # Identifier for the email being analyzed
    
    # Exemption determinations
    attorney_client: Dict[str, Union[bool, ConfidenceLevel, str]] = field(default_factory=lambda: {
        "applies": False, 
        "confidence": ConfidenceLevel.LOW, 
        "reasoning": ""
    })
    personnel: Dict[str, Union[bool, ConfidenceLevel, str]] = field(default_factory=lambda: {
        "applies": False, 
        "confidence": ConfidenceLevel.LOW, 
        "reasoning": ""
    })
    deliberative: Dict[str, Union[bool, ConfidenceLevel, str]] = field(default_factory=lambda: {
        "applies": False, 
        "confidence": ConfidenceLevel.LOW, 
        "reasoning": ""
    })
    
    # Metadata
    model_used: str = ""
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    processing_time_seconds: Optional[float] = None
    
    def get_applicable_exemptions(self) -> List[ExemptionType]:
        """Get list of exemptions that apply to this email."""
        applicable = []
        if self.attorney_client["applies"]:
            applicable.append(ExemptionType.ATTORNEY_CLIENT)
        if self.personnel["applies"]:
            applicable.append(ExemptionType.PERSONNEL)
        if self.deliberative["applies"]:
            applicable.append(ExemptionType.DELIBERATIVE)
        return applicable
    
    def has_any_exemption(self) -> bool:
        """Check if any exemption applies to this email."""
        return len(self.get_applicable_exemptions()) > 0


@dataclass
class DocumentReview:
    """User review and decisions for a document."""
    
    email_id: str
    
    # User review decisions
    user_responsive_override: Optional[Dict[int, bool]] = None  # request_index -> user decision
    user_exemption_override: Optional[Dict[ExemptionType, bool]] = None  # exemption -> user decision
    
    # Review metadata
    review_status: ReviewStatus = ReviewStatus.PENDING
    reviewed_by: Optional[str] = None
    review_timestamp: Optional[datetime] = None
    review_notes: str = ""
    
    # Final determinations (after user review)
    final_responsive: List[bool] = field(default_factory=list)
    final_exemptions: List[ExemptionType] = field(default_factory=list)
    
    def is_reviewable(self) -> bool:
        """Check if document is ready for review."""
        return self.review_status in [ReviewStatus.PENDING, ReviewStatus.IN_PROGRESS]
    
    def mark_reviewed(self, reviewer: str = "user") -> None:
        """Mark document as reviewed."""
        self.review_status = ReviewStatus.COMPLETED
        self.reviewed_by = reviewer
        self.review_timestamp = datetime.now()


@dataclass
class ProcessingStats:
    """Statistics for the processing session."""
    
    total_emails: int = 0
    processed_emails: int = 0
    responsive_emails: int = 0
    exempt_emails: int = 0
    
    # Processing time tracking
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Error tracking
    parsing_errors: int = 0
    analysis_errors: int = 0
    
    def get_processing_time_seconds(self) -> Optional[float]:
        """Get total processing time in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def get_progress_percentage(self) -> float:
        """Get processing progress as percentage."""
        if self.total_emails == 0:
            return 0.0
        return (self.processed_emails / self.total_emails) * 100.0


@dataclass
class CPRARequest:
    """Represents a CPRA request."""
    
    text: str
    request_id: Optional[str] = None
    description: Optional[str] = None
    
    def __str__(self) -> str:
        return self.text[:100] + ("..." if len(self.text) > 100 else "")


@dataclass
class ProcessingSession:
    """Complete processing session data."""
    
    # Input data
    cpra_requests: List[CPRARequest] = field(default_factory=list)
    emails: List[Email] = field(default_factory=list)
    
    # Analysis results
    responsiveness_results: Dict[str, ResponsivenessAnalysis] = field(default_factory=dict)
    exemption_results: Dict[str, ExemptionAnalysis] = field(default_factory=dict)
    
    # Review data
    document_reviews: Dict[str, DocumentReview] = field(default_factory=dict)
    
    # Session metadata
    session_id: str = ""
    model_used: str = ""
    stats: ProcessingStats = field(default_factory=ProcessingStats)
    
    def get_email_by_index(self, index: int) -> Optional[Email]:
        """Get email by index."""
        if 0 <= index < len(self.emails):
            return self.emails[index]
        return None
    
    def get_processing_summary(self) -> Dict:
        """Get summary of processing results."""
        return {
            "total_emails": len(self.emails),
            "responsive_emails": sum(1 for result in self.responsiveness_results.values() 
                                   if result.is_responsive_to_any()),
            "exempt_emails": sum(1 for result in self.exemption_results.values()
                               if result.has_any_exemption()),
            "reviewed_emails": sum(1 for review in self.document_reviews.values()
                                 if review.review_status == ReviewStatus.COMPLETED),
            "processing_time": self.stats.get_processing_time_seconds()
        }