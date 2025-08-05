"""
Email parser for processing Outlook export format emails.
Handles parsing of bulk email exports into individual Email objects.
"""

import re
import logging
from datetime import datetime
from typing import List, Optional, Tuple
from email.utils import parsedate_to_datetime, parseaddr
from dateutil import parser as date_parser

from src.utils.data_structures import Email


class EmailParser:
    """Parser for Outlook export format emails."""
    
    def __init__(self):
        """Initialize the email parser."""
        self.logger = logging.getLogger(__name__)
        
        # Common Outlook export patterns
        self.header_patterns = {
            'from': re.compile(r'^From:\s*(.+?)$', re.MULTILINE | re.IGNORECASE),
            'to': re.compile(r'^To:\s*(.+?)$', re.MULTILINE | re.IGNORECASE),
            'cc': re.compile(r'^CC:\s*(.+?)$', re.MULTILINE | re.IGNORECASE),
            'bcc': re.compile(r'^BCC:\s*(.+?)$', re.MULTILINE | re.IGNORECASE),
            'subject': re.compile(r'^Subject:\s*(.+?)$', re.MULTILINE | re.IGNORECASE),
            'date': re.compile(r'^(?:Date|Sent):\s*(.+?)$', re.MULTILINE | re.IGNORECASE),
            'message_id': re.compile(r'^Message-ID:\s*(.+?)$', re.MULTILINE | re.IGNORECASE),
        }
        
        # Email separation patterns
        self.email_separator_patterns = [
            re.compile(r'^From:\s+', re.MULTILINE),  # Standard From: line
            re.compile(r'^_{10,}', re.MULTILINE),    # Underline separator
            re.compile(r'^-{10,}', re.MULTILINE),    # Dash separator
            re.compile(r'^\s*(?:From|TO|Subject):\s+', re.MULTILINE | re.IGNORECASE),  # Header restart
        ]
    
    def parse_email_file(self, file_content: str) -> List[Email]:
        """
        Parse a file containing multiple emails in Outlook export format.
        
        Args:
            file_content: Raw text content of the email export file
            
        Returns:
            List of parsed Email objects
        """
        try:
            # Split into individual emails
            raw_emails = self._split_emails(file_content)
            
            parsed_emails = []
            for i, raw_email in enumerate(raw_emails):
                try:
                    email = self._parse_single_email(raw_email, email_index=i)
                    if email:
                        parsed_emails.append(email)
                    else:
                        # Create a failed email object for tracking
                        failed_email = Email(
                            from_address="PARSE_ERROR",
                            to_address="PARSE_ERROR", 
                            subject="PARSE_ERROR",
                            date=datetime.now(),
                            body="Failed to parse this email",
                            raw_text=raw_email[:500],  # Keep first 500 chars for debugging
                            parsed_successfully=False,
                            parsing_errors=["Failed to parse email - missing required fields"]
                        )
                        parsed_emails.append(failed_email)
                except Exception as e:
                    self.logger.error(f"Failed to parse email {i}: {e}")
                    # Create a failed email object for tracking
                    failed_email = Email(
                        from_address="PARSE_ERROR",
                        to_address="PARSE_ERROR", 
                        subject="PARSE_ERROR",
                        date=datetime.now(),
                        body="Failed to parse this email",
                        raw_text=raw_email[:500],  # Keep first 500 chars for debugging
                        parsed_successfully=False,
                        parsing_errors=[str(e)]
                    )
                    parsed_emails.append(failed_email)
            
            self.logger.info(f"Successfully parsed {len([e for e in parsed_emails if e.parsed_successfully])} of {len(raw_emails)} emails")
            return parsed_emails
            
        except Exception as e:
            self.logger.error(f"Failed to parse email file: {e}")
            return []
    
    def _split_emails(self, content: str) -> List[str]:
        """
        Split file content into individual email strings.
        
        Args:
            content: Raw file content
            
        Returns:
            List of individual email text blocks
        """
        # Try different splitting strategies
        
        # Strategy 1: Split by "From:" lines that start new emails
        from_pattern = re.compile(r'^From:\s+', re.MULTILINE)
        matches = list(from_pattern.finditer(content))
        
        if len(matches) > 1:
            emails = []
            for i in range(len(matches)):
                start = matches[i].start()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
                email_text = content[start:end].strip()
                if email_text:
                    emails.append(email_text)
            return emails
        
        # Strategy 2: Split by separator lines
        for pattern in self.email_separator_patterns[1:]:  # Skip From: pattern already tried
            if pattern.search(content):
                parts = pattern.split(content)
                if len(parts) > 1:
                    return [part.strip() for part in parts if part.strip()]
        
        # Strategy 3: If no clear separators found, treat as single email
        return [content.strip()] if content.strip() else []
    
    def _parse_single_email(self, raw_email: str, email_index: int = 0) -> Optional[Email]:
        """
        Parse a single email from raw text.
        
        Args:
            raw_email: Raw text of a single email
            email_index: Index of email for ID generation
            
        Returns:
            Parsed Email object or None if parsing fails
        """
        try:
            # Extract headers
            headers = self._extract_headers(raw_email)
            
            # Extract body (everything after headers)
            body = self._extract_body(raw_email, headers)
            
            # Parse required fields
            from_addr = self._parse_address(headers.get('from', ''))
            to_addr = self._parse_address(headers.get('to', ''))
            subject = headers.get('subject', '').strip()
            date = self._parse_date(headers.get('date', ''))
            
            # Validate required fields
            if not from_addr or not to_addr:
                raise ValueError(f"Missing required fields: from='{from_addr}', to='{to_addr}'")
            
            # Parse optional fields
            cc_addrs = self._parse_address_list(headers.get('cc', ''))
            bcc_addrs = self._parse_address_list(headers.get('bcc', ''))
            message_id = headers.get('message_id', '').strip()
            
            # Create email object
            email = Email(
                from_address=from_addr,
                to_address=to_addr,
                subject=subject,
                date=date,
                body=body,
                message_id=message_id if message_id else f"parsed_email_{email_index}",
                cc_addresses=cc_addrs,
                bcc_addresses=bcc_addrs,
                raw_text=raw_email,
                parsed_successfully=True
            )
            
            return email
            
        except Exception as e:
            self.logger.error(f"Failed to parse single email: {e}")
            return None
    
    def _extract_headers(self, raw_email: str) -> dict:
        """Extract email headers from raw text."""
        headers = {}
        
        for header_name, pattern in self.header_patterns.items():
            match = pattern.search(raw_email)
            if match:
                headers[header_name] = match.group(1).strip()
        
        return headers
    
    def _extract_body(self, raw_email: str, headers: dict) -> str:
        """Extract email body by removing header section."""
        # Find the end of headers (first blank line after headers)
        lines = raw_email.split('\n')
        body_start = 0
        
        # Look for the first blank line after we've seen some headers
        found_headers = False
        for i, line in enumerate(lines):
            if any(pattern.match(line) for pattern in self.header_patterns.values()):
                found_headers = True
            elif found_headers and line.strip() == '':
                body_start = i + 1
                break
            elif found_headers and not any(pattern.match(line) for pattern in self.header_patterns.values()):
                # If we found headers but this line doesn't match any pattern and isn't blank,
                # assume body starts here
                body_start = i
                break
        
        # If no clear separation found, try to find body after subject line
        if body_start == 0 and 'subject' in headers:
            subject_pattern = re.compile(rf'^Subject:\s*{re.escape(headers["subject"])}\s*$', re.MULTILINE | re.IGNORECASE)
            match = subject_pattern.search(raw_email)
            if match:
                body_start_pos = match.end()
                remaining_text = raw_email[body_start_pos:].lstrip('\n\r')
                return remaining_text
        
        # Extract body from determined start point
        body_lines = lines[body_start:]
        body = '\n'.join(body_lines).strip()
        
        return body
    
    def _parse_address(self, addr_string: str) -> str:
        """Parse a single email address, extracting just the email part."""
        if not addr_string:
            return ""
        
        # Use email.utils.parseaddr to handle "Name <email@domain.com>" format
        name, email = parseaddr(addr_string.strip())
        return email if email else addr_string.strip()
    
    def _parse_address_list(self, addr_string: str) -> List[str]:
        """Parse a list of email addresses separated by commas or semicolons."""
        if not addr_string:
            return []
        
        # Split by comma or semicolon
        addresses = re.split(r'[,;]', addr_string)
        return [self._parse_address(addr.strip()) for addr in addresses if addr.strip()]
    
    def _parse_date(self, date_string: str) -> datetime:
        """Parse email date string into datetime object."""
        if not date_string:
            return datetime.now()
        
        try:
            # Try standard email date format first
            return parsedate_to_datetime(date_string)
        except (TypeError, ValueError):
            pass
        
        try:
            # Try dateutil parser as fallback
            return date_parser.parse(date_string)
        except (ValueError, TypeError):
            pass
        
        # If all parsing fails, return current time
        self.logger.warning(f"Could not parse date '{date_string}', using current time")
        return datetime.now()


def create_sample_outlook_export() -> str:
    """
    Create a sample Outlook export format string for testing.
    
    Returns:
        Sample email export content
    """
    return """From: john.smith@cityengineering.gov
To: sarah.johnson@contractor.com
CC: legal@cityengineering.gov
Subject: RE: Community Center Roof Issues - Urgent Response Needed
Date: Mon, 15 Jan 2024 09:30:00 -0800

Sarah,

I've reviewed the inspection report you sent regarding the roof leak issues in the Community Center construction project. The situation is more serious than initially thought.

The leak in the southwest corner has caused water damage to the electrical systems below. We need to halt construction in that area immediately until we can assess the full extent of the damage.

Please coordinate with your team to:
1. Secure the affected area
2. Document all damage with photos
3. Provide a timeline for repairs

We'll need to discuss potential change orders for this remediation work.

Best regards,
John Smith
Senior Project Manager
City Engineering Department

From: sarah.johnson@contractor.com
To: john.smith@cityengineering.gov
Subject: Community Center - Material Delivery Schedule
Date: Wed, 17 Jan 2024 14:20:00 -0800

John,

Quick update on the material deliveries for next week:

- Steel beams: Tuesday 1/23
- Electrical components: Thursday 1/25
- Roofing materials: Friday 1/26

The roofing materials include the upgraded membrane we discussed for the problem areas. This should prevent future leak issues.

Let me know if this schedule works for your team.

Sarah Johnson
Project Coordinator
ABC Construction Company

From: mike.attorney@citylegal.gov
To: john.smith@cityengineering.gov
CC: city.manager@cityengineering.gov
Subject: CONFIDENTIAL: Legal Analysis - Community Center Change Order #3
Date: Thu, 18 Jan 2024 16:45:00 -0800

ATTORNEY-CLIENT PRIVILEGED COMMUNICATION

John,

I've completed my review of the proposed Change Order #3 for the Community Center project. Based on the contract terms and applicable law, here's my confidential legal analysis:

The contractor's claim for additional compensation due to the roof leak remediation appears to have merit under Section 4.3 of the construction contract. However, we should negotiate the amount as their initial request seems excessive.

My recommendation is to authorize the change order but counter with 75% of their requested amount. This protects the city's interests while avoiding potential litigation delays.

Please do not share this analysis outside of our privileged attorney-client relationship without my explicit approval.

Mike Rodriguez
City Attorney
City Legal Department"""


if __name__ == "__main__":
    # Test the parser with sample data
    logging.basicConfig(level=logging.INFO)
    
    parser = EmailParser()
    sample_content = create_sample_outlook_export()
    
    print("Testing email parser with sample data...")
    emails = parser.parse_email_file(sample_content)
    
    print(f"\nParsed {len(emails)} emails:")
    for i, email in enumerate(emails):
        print(f"\nEmail {i+1}:")
        print(f"  From: {email.from_address}")
        print(f"  To: {email.to_address}")
        print(f"  Subject: {email.subject}")
        print(f"  Date: {email.date}")
        print(f"  Body length: {len(email.body)} characters")
        print(f"  Parsed successfully: {email.parsed_successfully}")
        
        if email.parsing_errors:
            print(f"  Errors: {email.parsing_errors}")
    
    print("\nTesting completed successfully!")