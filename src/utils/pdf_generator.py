"""
PDF Generator for CPRA document exports.
Handles PDF creation for production documents and summary reports.
"""

import logging
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from .data_structures import Email, ProcessingSession, ReviewStatus


class PDFGenerator:
    """Generates professional PDF documents for CPRA exports."""
    
    def __init__(self):
        """Initialize the PDF generator."""
        self.logger = logging.getLogger(__name__)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles for the PDF."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Header style
        self.styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Email header style
        self.styles.add(ParagraphStyle(
            name='EmailHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#34495e'),
            leftIndent=20
        ))
        
        # Email body style
        self.styles.add(ParagraphStyle(
            name='EmailBody',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            leftIndent=20,
            rightIndent=20,
            spaceBefore=6,
            spaceAfter=6
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))
    
    def generate_production_pdf(
        self,
        emails: List[Email],
        output_path: str,
        cpra_requests: List[str],
        session_id: str = ""
    ):
        """
        Generate production PDF with responsive documents.
        
        Args:
            emails: List of Email objects to include
            output_path: Path for output PDF file
            cpra_requests: List of CPRA request texts
            session_id: Session identifier
        """
        # Create document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build content
        story = []
        
        # Add title page
        story.extend(self._create_title_page(
            "CPRA Document Production",
            cpra_requests,
            session_id,
            len(emails)
        ))
        
        # Add page break after title
        story.append(PageBreak())
        
        # Add each email as a separate section
        for i, email in enumerate(emails, 1):
            story.extend(self._create_email_section(email, i, len(emails)))
            
            # Add page break between emails (except for last one)
            if i < len(emails):
                story.append(PageBreak())
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, 
                 onLaterPages=self._add_header_footer)
        
        self.logger.info(f"Generated production PDF with {len(emails)} documents: {output_path}")
    
    def generate_summary_report(
        self,
        session: ProcessingSession,
        output_path: str
    ):
        """
        Generate summary report PDF.
        
        Args:
            session: ProcessingSession to summarize
            output_path: Path for output PDF file
        """
        # Create document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build content
        story = []
        
        # Add title
        story.append(Paragraph(
            "CPRA Processing Summary Report",
            self.styles['CustomTitle']
        ))
        story.append(Spacer(1, 0.5*inch))
        
        # Add session information
        story.extend(self._create_session_summary(session))
        
        # Add statistics
        story.append(PageBreak())
        story.extend(self._create_statistics_section(session))
        
        # Add CPRA requests
        story.append(PageBreak())
        story.extend(self._create_requests_section(session))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer,
                 onLaterPages=self._add_header_footer)
        
        self.logger.info(f"Generated summary report: {output_path}")
    
    def _create_title_page(
        self,
        title: str,
        cpra_requests: List[str],
        session_id: str,
        document_count: int
    ) -> List:
        """Create title page elements."""
        elements = []
        
        # Title
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Production date
        elements.append(Paragraph(
            f"Production Date: {datetime.now().strftime('%B %d, %Y')}",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Session ID
        if session_id:
            elements.append(Paragraph(
                f"Session ID: {session_id}",
                self.styles['Normal']
            ))
            elements.append(Spacer(1, 0.2*inch))
        
        # Document count
        elements.append(Paragraph(
            f"Total Documents: {document_count}",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.5*inch))
        
        # CPRA Requests
        elements.append(Paragraph(
            "CPRA Requests:",
            self.styles['CustomHeader']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        for i, request in enumerate(cpra_requests, 1):
            elements.append(Paragraph(
                f"{i}. {request}",
                self.styles['Normal']
            ))
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_email_section(
        self,
        email: Email,
        index: int,
        total: int
    ) -> List:
        """Create PDF elements for an email."""
        elements = []
        
        # Document header
        elements.append(Paragraph(
            f"Document {index} of {total}",
            self.styles['CustomHeader']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Email metadata table
        metadata = [
            ["From:", email.from_address],
            ["To:", email.to_address],
            ["Date:", email.date.strftime('%Y-%m-%d %H:%M:%S')],
            ["Subject:", email.subject]
        ]
        
        if email.cc_addresses:
            metadata.insert(2, ["CC:", ", ".join(email.cc_addresses)])
        
        table = Table(metadata, colWidths=[1.5*inch, 5*inch])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#34495e')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Email body
        elements.append(Paragraph(
            "Message:",
            self.styles['EmailHeader']
        ))
        elements.append(Spacer(1, 0.1*inch))
        
        # Process body text to handle special characters
        body_text = self._sanitize_text(email.body)
        
        # Split body into paragraphs
        for paragraph in body_text.split('\n\n'):
            if paragraph.strip():
                elements.append(Paragraph(
                    paragraph.strip(),
                    self.styles['EmailBody']
                ))
                elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_session_summary(self, session: ProcessingSession) -> List:
        """Create session summary elements."""
        elements = []
        
        elements.append(Paragraph(
            "Session Information",
            self.styles['CustomHeader']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Get summary data
        summary = session.get_processing_summary()
        
        # Create summary table
        data = [
            ["Session ID:", session.session_id or "N/A"],
            ["Processing Date:", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ["Model Used:", session.model_used or "N/A"],
            ["Total Emails:", str(summary['total_emails'])],
            ["Responsive Emails:", str(summary['responsive_emails'])],
            ["Exempt Emails:", str(summary['exempt_emails'])],
            ["Reviewed Emails:", str(summary['reviewed_emails'])],
        ]
        
        if summary['processing_time']:
            data.append([
                "Processing Time:",
                f"{summary['processing_time']:.2f} seconds"
            ])
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#34495e')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _create_statistics_section(self, session: ProcessingSession) -> List:
        """Create statistics section."""
        elements = []
        
        elements.append(Paragraph(
            "Processing Statistics",
            self.styles['CustomHeader']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Count review statuses
        pending = sum(1 for r in session.document_reviews.values() 
                     if r.review_status == ReviewStatus.PENDING)
        in_progress = sum(1 for r in session.document_reviews.values()
                         if r.review_status == ReviewStatus.IN_PROGRESS)
        completed = sum(1 for r in session.document_reviews.values()
                       if r.review_status == ReviewStatus.COMPLETED)
        
        # Create pie chart data (would need additional library for actual chart)
        review_data = [
            ["Review Status", "Count", "Percentage"],
            ["Pending", str(pending), f"{pending/len(session.emails)*100:.1f}%"],
            ["In Progress", str(in_progress), f"{in_progress/len(session.emails)*100:.1f}%"],
            ["Completed", str(completed), f"{completed/len(session.emails)*100:.1f}%"],
        ]
        
        table = Table(review_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 11),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _create_requests_section(self, session: ProcessingSession) -> List:
        """Create CPRA requests section."""
        elements = []
        
        elements.append(Paragraph(
            "CPRA Requests Processed",
            self.styles['CustomHeader']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        for i, request in enumerate(session.cpra_requests, 1):
            elements.append(Paragraph(
                f"Request {i}:",
                self.styles['Heading3']
            ))
            elements.append(Paragraph(
                request.text,
                self.styles['Normal']
            ))
            elements.append(Spacer(1, 0.2*inch))
            
            # Count responsive documents for this request
            responsive_count = 0
            for result in session.responsiveness_results.values():
                if i-1 < len(result.responsive) and result.responsive[i-1]:
                    responsive_count += 1
            
            elements.append(Paragraph(
                f"Documents responsive to this request: {responsive_count}",
                self.styles['Normal']
            ))
            elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _sanitize_text(self, text: str) -> str:
        """
        Sanitize text for PDF generation.
        
        Args:
            text: Raw text to sanitize
            
        Returns:
            Sanitized text safe for PDF
        """
        # Replace special characters that might break PDF generation
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&apos;'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _add_header_footer(self, canvas, doc):
        """Add header and footer to each page."""
        canvas.saveState()
        
        # Footer
        footer_text = f"Page {doc.page} - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(
            doc.pagesize[0] / 2,
            0.5 * inch,
            footer_text
        )
        
        # Header line
        canvas.setStrokeColor(colors.grey)
        canvas.setLineWidth(0.5)
        canvas.line(doc.leftMargin, doc.height + 0.75*inch, 
                   doc.width + doc.leftMargin, doc.height + 0.75*inch)
        
        canvas.restoreState()