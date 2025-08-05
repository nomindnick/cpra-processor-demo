"""
Export Manager for CPRA document processing.
Handles PDF production, privilege log generation, and export validation.
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import csv

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.data_structures import (
    ProcessingSession, Email, DocumentReview, ReviewStatus, 
    ExemptionType, ResponsivenessAnalysis, ExemptionAnalysis
)
from utils.pdf_generator import PDFGenerator
from utils.privilege_log import PrivilegeLogGenerator


class ExportManager:
    """Manages document export functionality for CPRA processing."""
    
    def __init__(self, output_dir: str = "data/exports"):
        """
        Initialize the export manager.
        
        Args:
            output_dir: Directory for storing exported files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.pdf_generator = PDFGenerator()
        self.privilege_log_generator = PrivilegeLogGenerator()
    
    def generate_exports(
        self,
        session: ProcessingSession,
        include_summary: bool = True
    ) -> Dict[str, str]:
        """
        Generate all export files for a processing session.
        
        Args:
            session: ProcessingSession with completed reviews
            include_summary: Whether to generate a summary report
            
        Returns:
            Dictionary of export_type -> file_path
        """
        # Validate session is ready for export
        validation_result = self.validate_export_readiness(session)
        if not validation_result["ready"]:
            self.logger.warning(f"Session not ready for export: {validation_result['reason']}")
            if not validation_result.get("allow_partial", False):
                raise ValueError(f"Export validation failed: {validation_result['reason']}")
        
        export_files = {}
        
        # Generate production PDF
        try:
            production_pdf = self.generate_production_pdf(session)
            export_files["production_pdf"] = production_pdf
            self.logger.info(f"Generated production PDF: {production_pdf}")
        except Exception as e:
            self.logger.error(f"Failed to generate production PDF: {e}")
            raise
        
        # Generate privilege log
        try:
            privilege_log = self.generate_privilege_log(session)
            export_files["privilege_log"] = privilege_log
            self.logger.info(f"Generated privilege log: {privilege_log}")
        except Exception as e:
            self.logger.error(f"Failed to generate privilege log: {e}")
            raise
        
        # Generate summary report if requested
        if include_summary:
            try:
                summary_report = self.generate_processing_summary(session)
                export_files["summary_report"] = summary_report
                self.logger.info(f"Generated summary report: {summary_report}")
            except Exception as e:
                self.logger.error(f"Failed to generate summary report: {e}")
                # Don't fail entire export if summary fails
        
        # Create export manifest
        manifest = self.create_export_manifest(session, export_files)
        export_files["manifest"] = manifest
        
        return export_files
    
    def generate_production_pdf(self, session: ProcessingSession) -> str:
        """
        Generate PDF with responsive, non-exempt documents.
        
        Args:
            session: ProcessingSession with completed reviews
            
        Returns:
            Path to generated PDF file
        """
        # Get responsive, non-exempt documents
        documents_to_produce = self._get_producible_documents(session)
        
        if not documents_to_produce:
            self.logger.warning("No documents to produce in PDF")
        
        # Generate filename
        filename = self._generate_filename("Production", "pdf", session.session_id)
        filepath = self.output_dir / filename
        
        # Prepare CPRA request texts for header
        cpra_requests = [req.text for req in session.cpra_requests]
        
        # Generate PDF
        self.pdf_generator.generate_production_pdf(
            emails=documents_to_produce,
            output_path=str(filepath),
            cpra_requests=cpra_requests,
            session_id=session.session_id
        )
        
        return str(filepath)
    
    def generate_privilege_log(self, session: ProcessingSession) -> str:
        """
        Generate privilege log for withheld documents.
        
        Args:
            session: ProcessingSession with completed reviews
            
        Returns:
            Path to generated privilege log file
        """
        # Get withheld documents with exemptions
        withheld_documents = self._get_withheld_documents(session)
        
        # Generate filename
        filename = self._generate_filename("PrivilegeLog", "csv", session.session_id)
        filepath = self.output_dir / filename
        
        # Generate privilege log
        self.privilege_log_generator.generate_csv_log(
            withheld_documents=withheld_documents,
            output_path=str(filepath),
            session_id=session.session_id
        )
        
        # Also generate PDF version
        pdf_filename = self._generate_filename("PrivilegeLog", "pdf", session.session_id)
        pdf_filepath = self.output_dir / pdf_filename
        
        self.privilege_log_generator.generate_pdf_log(
            withheld_documents=withheld_documents,
            output_path=str(pdf_filepath),
            session_id=session.session_id
        )
        
        return str(filepath)
    
    def generate_processing_summary(self, session: ProcessingSession) -> str:
        """
        Generate summary report of processing session.
        
        Args:
            session: ProcessingSession to summarize
            
        Returns:
            Path to generated summary report
        """
        # Generate filename
        filename = self._generate_filename("Summary", "pdf", session.session_id)
        filepath = self.output_dir / filename
        
        # Generate summary report
        self.pdf_generator.generate_summary_report(
            session=session,
            output_path=str(filepath)
        )
        
        return str(filepath)
    
    def validate_export_readiness(self, session: ProcessingSession) -> Dict:
        """
        Validate that session is ready for export.
        
        Args:
            session: ProcessingSession to validate
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            "ready": True,
            "warnings": [],
            "errors": []
        }
        
        # Check if any documents exist
        if not session.emails:
            validation["ready"] = False
            validation["errors"].append("No documents in session")
            validation["reason"] = "No documents to export"
            return validation
        
        # Check if reviews exist
        if not session.document_reviews:
            validation["ready"] = False
            validation["errors"].append("No reviews found")
            validation["reason"] = "Documents have not been reviewed"
            return validation
        
        # Count review statuses
        total_docs = len(session.emails)
        completed_reviews = sum(
            1 for review in session.document_reviews.values()
            if review.review_status == ReviewStatus.COMPLETED
        )
        
        # Check if all documents are reviewed
        if completed_reviews < total_docs:
            validation["warnings"].append(
                f"Only {completed_reviews}/{total_docs} documents reviewed"
            )
            validation["allow_partial"] = True
            validation["reason"] = f"Incomplete reviews ({completed_reviews}/{total_docs})"
        
        # Check for analysis results
        if not session.responsiveness_results:
            validation["warnings"].append("No responsiveness analysis results found")
        
        if not session.exemption_results:
            validation["warnings"].append("No exemption analysis results found")
        
        return validation
    
    def _get_producible_documents(self, session: ProcessingSession) -> List[Email]:
        """
        Get list of documents that should be produced (responsive, non-exempt).
        
        Args:
            session: ProcessingSession with reviews
            
        Returns:
            List of Email objects to produce
        """
        producible = []
        
        for i, email in enumerate(session.emails):
            email_id = email.message_id if email.message_id else f"email_{i}"
            
            # Get review if exists
            review = session.document_reviews.get(email_id)
            if not review or review.review_status != ReviewStatus.COMPLETED:
                self.logger.debug(f"Skipping unreviewed document: {email_id}")
                continue
            
            # Check if responsive to any request
            is_responsive = False
            if review.final_responsive:
                # Handle both list and dict format
                if isinstance(review.final_responsive, list):
                    is_responsive = any(review.final_responsive)
                
            # Check if fully exempt
            is_fully_exempt = len(review.final_exemptions) > 0 if review.final_exemptions else False
            
            # Document is producible if responsive and not fully exempt
            if is_responsive and not is_fully_exempt:
                producible.append(email)
                self.logger.debug(f"Including document in production: {email_id}")
        
        return producible
    
    def _get_withheld_documents(self, session: ProcessingSession) -> List[Dict]:
        """
        Get list of withheld documents with exemption information.
        
        Args:
            session: ProcessingSession with reviews
            
        Returns:
            List of dictionaries with withheld document information
        """
        withheld = []
        
        for i, email in enumerate(session.emails):
            email_id = email.message_id if email.message_id else f"email_{i}"
            
            # Get review if exists
            review = session.document_reviews.get(email_id)
            if not review or review.review_status != ReviewStatus.COMPLETED:
                continue
            
            # Check if document is withheld (has exemptions or not responsive)
            is_responsive = False
            if review.final_responsive:
                if isinstance(review.final_responsive, list):
                    is_responsive = any(review.final_responsive)
            
            has_exemptions = len(review.final_exemptions) > 0 if review.final_exemptions else False
            
            if has_exemptions or not is_responsive:
                # Get exemption analysis for reasoning
                exemption_analysis = session.exemption_results.get(email_id)
                
                # Build withheld document entry
                doc_info = {
                    "email": email,
                    "email_id": email_id,
                    "responsive": is_responsive,
                    "exemptions": review.final_exemptions,
                    "reasoning": self._get_exemption_reasoning(
                        review.final_exemptions,
                        exemption_analysis
                    )
                }
                
                if not is_responsive:
                    doc_info["reasoning"]["non_responsive"] = "Document not responsive to CPRA request"
                
                withheld.append(doc_info)
                self.logger.debug(f"Including document in privilege log: {email_id}")
        
        return withheld
    
    def _get_exemption_reasoning(
        self,
        exemptions: List[ExemptionType],
        analysis: Optional[ExemptionAnalysis]
    ) -> Dict[str, str]:
        """
        Get exemption reasoning from analysis.
        
        Args:
            exemptions: List of applicable exemptions
            analysis: ExemptionAnalysis with reasoning
            
        Returns:
            Dictionary of exemption type -> reasoning
        """
        reasoning = {}
        
        if not analysis:
            return reasoning
        
        for exemption in exemptions:
            if exemption == ExemptionType.ATTORNEY_CLIENT:
                # Handle both dict and object attribute access
                if isinstance(analysis.attorney_client, dict):
                    reasoning["attorney_client"] = analysis.attorney_client.get("reasoning", "Attorney-client privilege applies")
                else:
                    reasoning["attorney_client"] = "Attorney-client privilege applies"
            elif exemption == ExemptionType.PERSONNEL:
                if isinstance(analysis.personnel, dict):
                    reasoning["personnel"] = analysis.personnel.get("reasoning", "Personnel records exemption applies")
                else:
                    reasoning["personnel"] = "Personnel records exemption applies"
            elif exemption == ExemptionType.DELIBERATIVE:
                if isinstance(analysis.deliberative, dict):
                    reasoning["deliberative"] = analysis.deliberative.get("reasoning", "Deliberative process exemption applies")
                else:
                    reasoning["deliberative"] = "Deliberative process exemption applies"
        
        return reasoning
    
    def _generate_filename(
        self,
        file_type: str,
        extension: str,
        session_id: str = ""
    ) -> str:
        """
        Generate standardized filename.
        
        Args:
            file_type: Type of file (Production, PrivilegeLog, Summary)
            extension: File extension (pdf, csv)
            session_id: Optional session ID to include
            
        Returns:
            Generated filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if session_id:
            filename = f"CPRA_{file_type}_{session_id}_{timestamp}.{extension}"
        else:
            filename = f"CPRA_{file_type}_{timestamp}.{extension}"
        
        return filename
    
    def create_export_manifest(
        self,
        session: ProcessingSession,
        export_files: Dict[str, str]
    ) -> str:
        """
        Create manifest file documenting the export.
        
        Args:
            session: ProcessingSession that was exported
            export_files: Dictionary of generated export files
            
        Returns:
            Path to manifest file
        """
        manifest_filename = self._generate_filename("Manifest", "txt", session.session_id)
        manifest_path = self.output_dir / manifest_filename
        
        with open(manifest_path, 'w') as f:
            f.write("CPRA EXPORT MANIFEST\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Session ID: {session.session_id}\n")
            f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Documents: {len(session.emails)}\n")
            
            # Count document categories
            producible = len(self._get_producible_documents(session))
            withheld = len(self._get_withheld_documents(session))
            
            f.write(f"Produced Documents: {producible}\n")
            f.write(f"Withheld Documents: {withheld}\n\n")
            
            f.write("EXPORTED FILES:\n")
            f.write("-" * 30 + "\n")
            
            for export_type, filepath in export_files.items():
                if export_type != "manifest":
                    f.write(f"{export_type}: {Path(filepath).name}\n")
            
            f.write("\nCPRA REQUESTS:\n")
            f.write("-" * 30 + "\n")
            for i, request in enumerate(session.cpra_requests, 1):
                f.write(f"{i}. {request.text}\n")
            
            f.write("\nEND OF MANIFEST\n")
        
        self.logger.info(f"Created export manifest: {manifest_path}")
        return str(manifest_path)