"""
Privilege Log Generator for CPRA document exports.
Handles creation of privilege logs in CSV and PDF formats.
"""

import csv
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, LongTable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from .data_structures import Email, ExemptionType


class PrivilegeLogGenerator:
    """Generates privilege logs for withheld documents."""
    
    def __init__(self):
        """Initialize the privilege log generator."""
        self.logger = logging.getLogger(__name__)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='LogTitle',
            parent=self.styles['Title'],
            fontSize=20,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Header style
        self.styles.add(ParagraphStyle(
            name='LogHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12
        ))
        
        # Table header style
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
    
    def generate_csv_log(
        self,
        withheld_documents: List[Dict],
        output_path: str,
        session_id: str = ""
    ):
        """
        Generate CSV privilege log.
        
        Args:
            withheld_documents: List of withheld document information
            output_path: Path for output CSV file
            session_id: Session identifier
        """
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Document_ID',
                'Date',
                'From',
                'To',
                'Subject',
                'Responsive',
                'Exemptions_Applied',
                'Justification',
                'Review_Notes'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for doc_info in withheld_documents:
                email = doc_info['email']
                
                # Format exemptions
                exemptions_str = self._format_exemptions_csv(doc_info['exemptions'])
                
                # Format justification
                justification = self._format_justification_csv(doc_info['reasoning'])
                
                row = {
                    'Document_ID': doc_info['email_id'],
                    'Date': email.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'From': email.from_address,
                    'To': email.to_address,
                    'Subject': email.subject,
                    'Responsive': 'Yes' if doc_info['responsive'] else 'No',
                    'Exemptions_Applied': exemptions_str,
                    'Justification': justification,
                    'Review_Notes': ''  # Can be populated from review notes if available
                }
                
                writer.writerow(row)
        
        self.logger.info(f"Generated CSV privilege log with {len(withheld_documents)} entries: {output_path}")
    
    def generate_pdf_log(
        self,
        withheld_documents: List[Dict],
        output_path: str,
        session_id: str = ""
    ):
        """
        Generate PDF privilege log.
        
        Args:
            withheld_documents: List of withheld document information
            output_path: Path for output PDF file
            session_id: Session identifier
        """
        # Create document in landscape for wider table
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(letter),
            rightMargin=36,
            leftMargin=36,
            topMargin=72,
            bottomMargin=36
        )
        
        # Build content
        story = []
        
        # Add title
        story.append(Paragraph(
            "CPRA Privilege Log",
            self.styles['LogTitle']
        ))
        
        # Add metadata
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
            self.styles['Normal']
        ))
        
        if session_id:
            story.append(Paragraph(
                f"Session ID: {session_id}",
                self.styles['Normal']
            ))
        
        story.append(Paragraph(
            f"Total Withheld Documents: {len(withheld_documents)}",
            self.styles['Normal']
        ))
        
        story.append(Spacer(1, 0.5*inch))
        
        # Create privilege log table
        if withheld_documents:
            table_data = self._create_log_table_data(withheld_documents)
            table = self._create_styled_table(table_data)
            story.append(table)
        else:
            story.append(Paragraph(
                "No documents withheld.",
                self.styles['Normal']
            ))
        
        # Add summary statistics
        story.append(PageBreak())
        story.extend(self._create_summary_section(withheld_documents))
        
        # Build PDF
        doc.build(story)
        
        self.logger.info(f"Generated PDF privilege log with {len(withheld_documents)} entries: {output_path}")
    
    def _create_log_table_data(self, withheld_documents: List[Dict]) -> List[List]:
        """
        Create table data for privilege log.
        
        Args:
            withheld_documents: List of withheld document information
            
        Returns:
            Table data as list of lists
        """
        # Header row
        data = [[
            Paragraph('Doc ID', self.styles['TableHeader']),
            Paragraph('Date', self.styles['TableHeader']),
            Paragraph('From', self.styles['TableHeader']),
            Paragraph('To', self.styles['TableHeader']),
            Paragraph('Subject', self.styles['TableHeader']),
            Paragraph('Responsive', self.styles['TableHeader']),
            Paragraph('Exemptions', self.styles['TableHeader']),
            Paragraph('Justification', self.styles['TableHeader'])
        ]]
        
        # Data rows
        for doc_info in withheld_documents:
            email = doc_info['email']
            
            # Format exemptions for display
            exemptions_display = self._format_exemptions_display(doc_info['exemptions'])
            
            # Format justification for display
            justification_display = self._format_justification_display(doc_info['reasoning'])
            
            # Truncate long text fields
            subject_display = self._truncate_text(email.subject, 40)
            from_display = self._truncate_text(email.from_address, 25)
            to_display = self._truncate_text(email.to_address, 25)
            
            row = [
                Paragraph(doc_info['email_id'][:15], self.styles['BodyText']),
                Paragraph(email.date.strftime('%m/%d/%Y'), self.styles['BodyText']),
                Paragraph(from_display, self.styles['BodyText']),
                Paragraph(to_display, self.styles['BodyText']),
                Paragraph(subject_display, self.styles['BodyText']),
                Paragraph('Yes' if doc_info['responsive'] else 'No', self.styles['BodyText']),
                Paragraph(exemptions_display, self.styles['BodyText']),
                Paragraph(justification_display, self.styles['BodyText'])
            ]
            
            data.append(row)
        
        return data
    
    def _create_styled_table(self, data: List[List]) -> LongTable:
        """
        Create styled table for privilege log.
        
        Args:
            data: Table data
            
        Returns:
            Styled LongTable object
        """
        # Define column widths
        col_widths = [
            0.8*inch,  # Doc ID
            0.7*inch,  # Date
            1.2*inch,  # From
            1.2*inch,  # To
            1.8*inch,  # Subject
            0.7*inch,  # Responsive
            1.2*inch,  # Exemptions
            2.4*inch   # Justification
        ]
        
        table = LongTable(data, colWidths=col_widths, repeatRows=1)
        
        # Apply table style
        table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            
            # Padding
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        return table
    
    def _create_summary_section(self, withheld_documents: List[Dict]) -> List:
        """Create summary statistics section."""
        elements = []
        
        elements.append(Paragraph(
            "Privilege Log Summary",
            self.styles['LogHeader']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Count exemption types
        exemption_counts = {
            ExemptionType.ATTORNEY_CLIENT: 0,
            ExemptionType.PERSONNEL: 0,
            ExemptionType.DELIBERATIVE: 0
        }
        
        non_responsive_count = 0
        
        for doc_info in withheld_documents:
            if not doc_info['responsive']:
                non_responsive_count += 1
            
            for exemption in doc_info['exemptions']:
                if exemption in exemption_counts:
                    exemption_counts[exemption] += 1
        
        # Create summary table
        summary_data = [
            ['Category', 'Count'],
            ['Non-Responsive Documents', str(non_responsive_count)],
            ['Attorney-Client Privilege', str(exemption_counts[ExemptionType.ATTORNEY_CLIENT])],
            ['Personnel Records', str(exemption_counts[ExemptionType.PERSONNEL])],
            ['Deliberative Process', str(exemption_counts[ExemptionType.DELIBERATIVE])],
            ['', ''],
            ['Total Withheld', str(len(withheld_documents))]
        ]
        
        table = Table(summary_data, colWidths=[3*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 11),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
            ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 11),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _format_exemptions_csv(self, exemptions: List[ExemptionType]) -> str:
        """Format exemptions for CSV output."""
        exemption_names = {
            ExemptionType.ATTORNEY_CLIENT: "Attorney-Client Privilege",
            ExemptionType.PERSONNEL: "Personnel Records",
            ExemptionType.DELIBERATIVE: "Deliberative Process"
        }
        
        if not exemptions:
            return "None"
        
        return "; ".join(exemption_names.get(e, str(e)) for e in exemptions)
    
    def _format_exemptions_display(self, exemptions: List[ExemptionType]) -> str:
        """Format exemptions for PDF display."""
        exemption_abbrev = {
            ExemptionType.ATTORNEY_CLIENT: "A-C Priv",
            ExemptionType.PERSONNEL: "Personnel",
            ExemptionType.DELIBERATIVE: "Delib Proc"
        }
        
        if not exemptions:
            return "None"
        
        return ", ".join(exemption_abbrev.get(e, str(e)) for e in exemptions)
    
    def _format_justification_csv(self, reasoning: Dict[str, str]) -> str:
        """Format justification for CSV output."""
        if not reasoning:
            return "Document withheld"
        
        justifications = []
        
        if 'non_responsive' in reasoning:
            justifications.append(reasoning['non_responsive'])
        
        if 'attorney_client' in reasoning:
            justifications.append(f"Attorney-Client: {reasoning['attorney_client']}")
        
        if 'personnel' in reasoning:
            justifications.append(f"Personnel: {reasoning['personnel']}")
        
        if 'deliberative' in reasoning:
            justifications.append(f"Deliberative: {reasoning['deliberative']}")
        
        return " | ".join(justifications) if justifications else "Document withheld"
    
    def _format_justification_display(self, reasoning: Dict[str, str]) -> str:
        """Format justification for PDF display."""
        if not reasoning:
            return "Withheld"
        
        # Take first reasoning found, truncated
        for key in ['non_responsive', 'attorney_client', 'personnel', 'deliberative']:
            if key in reasoning:
                return self._truncate_text(reasoning[key], 60)
        
        return "Withheld"
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """
        Truncate text to maximum length.
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            
        Returns:
            Truncated text with ellipsis if needed
        """
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."