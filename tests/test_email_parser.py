"""
Unit tests for email parser functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from datetime import datetime
from parsers.email_parser import EmailParser, create_sample_outlook_export
from utils.data_structures import Email


class TestEmailParser:
    """Test cases for EmailParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EmailParser()
    
    def test_parse_single_email_basic(self):
        """Test parsing a basic single email."""
        raw_email = """From: test@example.com
To: recipient@example.com
Subject: Test Subject
Date: Mon, 1 Jan 2024 12:00:00 -0800

This is a test email body."""
        
        email = self.parser._parse_single_email(raw_email)
        
        assert email is not None
        assert email.from_address == "test@example.com"
        assert email.to_address == "recipient@example.com"
        assert email.subject == "Test Subject"
        assert email.body == "This is a test email body."
        assert email.parsed_successfully == True
    
    def test_parse_email_with_cc(self):
        """Test parsing email with CC field."""
        raw_email = """From: sender@example.com
To: primary@example.com
CC: cc1@example.com, cc2@example.com
Subject: Test with CC
Date: Mon, 1 Jan 2024 12:00:00 -0800

Email with CC recipients."""
        
        email = self.parser._parse_single_email(raw_email)
        
        assert email is not None
        assert len(email.cc_addresses) == 2
        assert "cc1@example.com" in email.cc_addresses
        assert "cc2@example.com" in email.cc_addresses
    
    def test_parse_email_with_name_format(self):
        """Test parsing email with 'Name <email>' format."""
        raw_email = """From: John Smith <john.smith@example.com>
To: Jane Doe <jane.doe@example.com>
Subject: Name Format Test
Date: Mon, 1 Jan 2024 12:00:00 -0800

Email with name format addresses."""
        
        email = self.parser._parse_single_email(raw_email)
        
        assert email is not None
        assert email.from_address == "john.smith@example.com"
        assert email.to_address == "jane.doe@example.com"
    
    def test_parse_multiple_emails(self):
        """Test parsing multiple emails from sample data."""
        sample_content = create_sample_outlook_export()
        emails = self.parser.parse_email_file(sample_content)
        
        assert len(emails) == 3
        
        # Check first email
        assert emails[0].from_address == "john.smith@cityengineering.gov"
        assert emails[0].to_address == "sarah.johnson@contractor.com"
        assert "Community Center Roof Issues" in emails[0].subject
        
        # Check second email
        assert emails[1].from_address == "sarah.johnson@contractor.com"
        assert emails[1].to_address == "john.smith@cityengineering.gov"
        assert "Material Delivery Schedule" in emails[1].subject
        
        # Check third email
        assert emails[2].from_address == "mike.attorney@citylegal.gov"
        assert emails[2].to_address == "john.smith@cityengineering.gov"
        assert "CONFIDENTIAL" in emails[2].subject
    
    def test_parse_date_formats(self):
        """Test parsing different date formats."""
        test_cases = [
            ("Mon, 15 Jan 2024 09:30:00 -0800", 2024),
            ("January 15, 2024 9:30 AM", 2024),
            ("2024-01-15 09:30:00", 2024),
            ("invalid date", datetime.now().year)  # Should fallback to current time
        ]
        
        for date_string, expected_year in test_cases:
            parsed_date = self.parser._parse_date(date_string)
            assert parsed_date.year == expected_year
    
    def test_parse_address_formats(self):
        """Test parsing different address formats."""
        test_cases = [
            ("simple@example.com", "simple@example.com"),
            ("Name <email@example.com>", "email@example.com"),
            ('"Full Name" <email@example.com>', "email@example.com"),
            ("", ""),
        ]
        
        for input_addr, expected in test_cases:
            result = self.parser._parse_address(input_addr)
            assert result == expected
    
    def test_parse_address_list(self):
        """Test parsing address lists with different separators."""
        test_cases = [
            ("a@example.com, b@example.com", ["a@example.com", "b@example.com"]),
            ("a@example.com; b@example.com", ["a@example.com", "b@example.com"]),
            ("Name <a@example.com>, b@example.com", ["a@example.com", "b@example.com"]),
            ("", []),
        ]
        
        for input_list, expected in test_cases:
            result = self.parser._parse_address_list(input_list)
            assert result == expected
    
    def test_empty_content(self):
        """Test parsing empty content."""
        emails = self.parser.parse_email_file("")
        assert len(emails) == 0
    
    def test_malformed_email(self):
        """Test parsing malformed email content."""
        malformed_content = "This is not a proper email format"
        emails = self.parser.parse_email_file(malformed_content)
        
        # Should return one failed email object
        assert len(emails) == 1
        assert emails[0].parsed_successfully == False
        assert len(emails[0].parsing_errors) > 0
    
    def test_missing_required_fields(self):
        """Test parsing email missing required fields."""
        incomplete_email = """Subject: Missing From and To
Date: Mon, 1 Jan 2024 12:00:00 -0800

This email is missing from and to fields."""
        
        email = self.parser._parse_single_email(incomplete_email)
        assert email is None  # Should fail to parse
    
    def test_extract_body_with_headers(self):
        """Test body extraction when headers are present."""
        raw_email = """From: test@example.com
To: recipient@example.com
Subject: Test Subject
Date: Mon, 1 Jan 2024 12:00:00 -0800

Line 1 of body
Line 2 of body
Line 3 of body"""
        
        headers = self.parser._extract_headers(raw_email)
        body = self.parser._extract_body(raw_email, headers)
        
        expected_body = "Line 1 of body\nLine 2 of body\nLine 3 of body"
        assert body == expected_body
    
    def test_sample_data_file(self):
        """Test parsing the actual sample data file."""
        sample_file_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "data", 
            "sample_emails", 
            "test_emails.txt"
        )
        
        if os.path.exists(sample_file_path):
            with open(sample_file_path, 'r') as f:
                content = f.read()
            
            emails = self.parser.parse_email_file(content)
            
            # Should parse all 10 sample emails successfully
            assert len(emails) == 10
            successful_parses = sum(1 for email in emails if email.parsed_successfully)
            assert successful_parses >= 8  # Allow for some parsing challenges
            
            # Check specific emails we know should be there
            subjects = [email.subject for email in emails]
            assert any("Roof Issues" in subject for subject in subjects)
            assert any("Change Order" in subject for subject in subjects)
            assert any("PERSONNEL CONFIDENTIAL" in subject for subject in subjects)


class TestEmail:
    """Test cases for Email data structure."""
    
    def test_email_creation(self):
        """Test creating an Email object."""
        email = Email(
            from_address="test@example.com",
            to_address="recipient@example.com",
            subject="Test Subject",
            date=datetime.now(),
            body="Test body"
        )
        
        assert email.from_address == "test@example.com"
        assert email.to_address == "recipient@example.com"
        assert email.subject == "Test Subject"
        assert email.body == "Test body"
        assert email.parsed_successfully == True
        assert len(email.parsing_errors) == 0
    
    def test_email_string_representation(self):
        """Test string representation of Email."""
        test_date = datetime(2024, 1, 15, 9, 30)
        email = Email(
            from_address="test@example.com",
            to_address="recipient@example.com",
            subject="Test Subject",
            date=test_date,
            body="Test body"
        )
        
        str_repr = str(email)
        assert "test@example.com" in str_repr
        assert "recipient@example.com" in str_repr
        assert "2024-01-15 09:30" in str_repr
        assert "Test Subject" in str_repr
    
    def test_get_display_text(self):
        """Test getting display text for Email."""
        test_date = datetime(2024, 1, 15, 9, 30)
        email = Email(
            from_address="test@example.com",
            to_address="recipient@example.com",
            subject="Test Subject",
            date=test_date,
            body="Test body",
            cc_addresses=["cc@example.com"]
        )
        
        display_text = email.get_display_text()
        assert "From: test@example.com" in display_text
        assert "To: recipient@example.com" in display_text
        assert "CC: cc@example.com" in display_text
        assert "Subject: Test Subject" in display_text
        assert "Test body" in display_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])