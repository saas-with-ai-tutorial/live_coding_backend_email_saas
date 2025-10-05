"""
Unit tests for GmailHelper class.
"""
import pytest
import imaplib
from unittest.mock import Mock, patch, MagicMock, call
from email.message import Message

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.gmail_helper import GmailHelper


class TestGmailHelperInitialization:
    """Tests for GmailHelper initialization."""
    
    def test_initialization_with_credentials(self):
        """Test initialization with provided credentials."""
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        
        assert helper.email_address == "test@gmail.com"
        assert helper.app_password == "test-password"
        assert helper.imap_server == "imap.gmail.com"
        assert helper.imap_port == 993
        assert helper.connection is None
    
    def test_initialization_from_env(self, monkeypatch):
        """Test initialization from environment variables."""
        monkeypatch.setenv("GMAIL_USER", "env@gmail.com")
        monkeypatch.setenv("GMAIL_APP_PASSWORD", "env-password")
        
        helper = GmailHelper()
        
        assert helper.email_address == "env@gmail.com"
        assert helper.app_password == "env-password"
    
    def test_initialization_missing_credentials(self, monkeypatch):
        """Test that initialization raises error without credentials."""
        monkeypatch.delenv("GMAIL_USER", raising=False)
        monkeypatch.delenv("GMAIL_APP_PASSWORD", raising=False)
        
        with pytest.raises(ValueError) as exc_info:
            GmailHelper()
        
        assert "must be provided" in str(exc_info.value)
    
    def test_initialization_partial_credentials(self, monkeypatch):
        """Test that initialization raises error with partial credentials."""
        monkeypatch.setenv("GMAIL_USER", "test@gmail.com")
        monkeypatch.delenv("GMAIL_APP_PASSWORD", raising=False)
        
        with pytest.raises(ValueError):
            GmailHelper()


class TestGmailHelperConnection:
    """Tests for Gmail connection methods."""
    
    @patch('imaplib.IMAP4_SSL')
    def test_connect_success(self, mock_imap):
        """Test successful connection to Gmail."""
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection
        
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        helper.connect()
        
        mock_imap.assert_called_once_with("imap.gmail.com", 993)
        mock_connection.login.assert_called_once_with("test@gmail.com", "test-password")
        assert helper.connection is not None
    
    @patch('imaplib.IMAP4_SSL')
    def test_connect_failure(self, mock_imap):
        """Test connection failure handling."""
        mock_imap.side_effect = imaplib.IMAP4.error("Authentication failed")
        
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="wrong-password"
        )
        
        with pytest.raises(ConnectionError) as exc_info:
            helper.connect()
        
        assert "Failed to connect" in str(exc_info.value)
    
    @patch('imaplib.IMAP4_SSL')
    def test_disconnect(self, mock_imap):
        """Test disconnection from Gmail."""
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection
        
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        helper.connect()
        helper.disconnect()
        
        mock_connection.close.assert_called_once()
        mock_connection.logout.assert_called_once()
    
    def test_disconnect_no_connection(self):
        """Test disconnection when not connected."""
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        
        # Should not raise error
        helper.disconnect()


class TestGmailHelperHeaderDecoding:
    """Tests for header decoding."""
    
    def test_decode_header_ascii(self):
        """Test decoding ASCII header."""
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        
        result = helper._decode_header_value("Simple Subject")
        assert result == "Simple Subject"
    
    def test_decode_header_empty(self):
        """Test decoding empty header."""
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        
        result = helper._decode_header_value("")
        assert result == ""
    
    def test_decode_header_none(self):
        """Test decoding None header."""
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        
        result = helper._decode_header_value(None)
        assert result == ""


class TestGmailHelperExtractBody:
    """Tests for email body extraction."""
    
    def test_extract_body_plain_text(self):
        """Test extracting plain text body."""
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        
        # Create a simple text message
        msg = Message()
        msg.set_payload("This is a plain text email body.")
        
        body = helper._extract_body(msg)
        assert body == "This is a plain text email body."
    
    def test_extract_body_multipart(self):
        """Test extracting body from multipart message."""
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        
        # Create a multipart message
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        
        msg = MIMEMultipart()
        text_part = MIMEText("This is the plain text part.", "plain")
        html_part = MIMEText("<p>This is the HTML part.</p>", "html")
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        body = helper._extract_body(msg)
        assert "plain text part" in body


class TestGmailHelperReadEmails:
    """Tests for reading emails."""
    
    @patch('imaplib.IMAP4_SSL')
    def test_read_latest_emails_success(self, mock_imap):
        """Test successfully reading latest emails."""
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection
        
        # Mock select mailbox
        mock_connection.select.return_value = ("OK", [b"10"])
        
        # Mock search
        mock_connection.search.return_value = ("OK", [b"1 2 3 4 5"])
        
        # Mock fetch for each email
        email_data = b"""From: sender@example.com
To: recipient@example.com
Subject: Test Email
Date: Mon, 1 Jan 2024 12:00:00 +0000

This is a test email body."""
        
        mock_connection.fetch.return_value = ("OK", [(b"1 (RFC822 {123}", email_data)])
        
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        helper.connect()
        
        emails = helper.read_latest_emails(n=3)
        
        # Should fetch 3 latest emails
        assert len(emails) <= 3
        mock_connection.select.assert_called_with("INBOX")
    
    @patch('imaplib.IMAP4_SSL')
    def test_read_latest_emails_unread_only(self, mock_imap):
        """Test reading only unread emails."""
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection
        
        mock_connection.select.return_value = ("OK", [b"10"])
        mock_connection.search.return_value = ("OK", [b"1 2 3"])
        
        email_data = b"""From: sender@example.com
To: recipient@example.com
Subject: Unread Email
Date: Mon, 1 Jan 2024 12:00:00 +0000

Unread email body."""
        
        mock_connection.fetch.return_value = ("OK", [(b"1 (RFC822 {123}", email_data)])
        
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        helper.connect()
        
        emails = helper.read_latest_emails(n=10, unread_only=True)
        
        # Should search for unread emails
        mock_connection.search.assert_called_with(None, "UNSEEN")
    
    @patch('imaplib.IMAP4_SSL')
    def test_read_latest_emails_no_emails(self, mock_imap):
        """Test reading when no emails exist."""
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection
        
        mock_connection.select.return_value = ("OK", [b"0"])
        mock_connection.search.return_value = ("OK", [b""])
        
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        helper.connect()
        
        emails = helper.read_latest_emails(n=10)
        
        assert emails == []
    
    @patch('imaplib.IMAP4_SSL')
    def test_read_latest_emails_auto_connect(self, mock_imap):
        """Test that read_latest_emails connects if not already connected."""
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection
        
        mock_connection.select.return_value = ("OK", [b"0"])
        mock_connection.search.return_value = ("OK", [b""])
        
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        
        # Don't call connect() manually
        emails = helper.read_latest_emails(n=10)
        
        # Should auto-connect
        mock_connection.login.assert_called_once()


class TestGmailHelperMarkEmails:
    """Tests for marking emails as read/unread."""
    
    @patch('imaplib.IMAP4_SSL')
    def test_mark_as_read(self, mock_imap):
        """Test marking email as read."""
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection
        
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        helper.connect()
        
        result = helper.mark_as_read("123")
        
        assert result is True
        mock_connection.store.assert_called_once_with("123", '+FLAGS', '\\Seen')
    
    @patch('imaplib.IMAP4_SSL')
    def test_mark_as_unread(self, mock_imap):
        """Test marking email as unread."""
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection
        
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        helper.connect()
        
        result = helper.mark_as_unread("123")
        
        assert result is True
        mock_connection.store.assert_called_once_with("123", '-FLAGS', '\\Seen')
    
    @patch('imaplib.IMAP4_SSL')
    def test_mark_as_read_error(self, mock_imap):
        """Test error handling when marking email fails."""
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection
        mock_connection.store.side_effect = Exception("Store failed")
        
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        helper.connect()
        
        result = helper.mark_as_read("123")
        
        assert result is False


class TestGmailHelperGetFolders:
    """Tests for getting folder list."""
    
    @patch('imaplib.IMAP4_SSL')
    def test_get_folders_success(self, mock_imap):
        """Test successfully getting folder list."""
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection
        
        mock_connection.list.return_value = ("OK", [
            b'(\\HasNoChildren) "/" "INBOX"',
            b'(\\HasNoChildren) "/" "Sent"',
            b'(\\HasNoChildren) "/" "Drafts"'
        ])
        
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        helper.connect()
        
        folders = helper.get_folders()
        
        assert len(folders) == 3
        assert "INBOX" in folders
    
    @patch('imaplib.IMAP4_SSL')
    def test_get_folders_error(self, mock_imap):
        """Test error handling when getting folders fails."""
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection
        
        mock_connection.list.return_value = ("NO", [])
        
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        helper.connect()
        
        folders = helper.get_folders()
        
        assert folders == []


class TestGmailHelperContextManager:
    """Tests for context manager functionality."""
    
    @patch('imaplib.IMAP4_SSL')
    def test_context_manager(self, mock_imap):
        """Test using GmailHelper as context manager."""
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection
        
        with GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        ) as helper:
            assert helper.connection is not None
            mock_connection.login.assert_called_once()
        
        # After exiting context, should disconnect
        mock_connection.close.assert_called_once()
        mock_connection.logout.assert_called_once()


class TestGmailHelperIntegration:
    """Integration tests for GmailHelper."""
    
    @patch('imaplib.IMAP4_SSL')
    def test_full_workflow(self, mock_imap):
        """Test complete workflow of connecting, reading, and disconnecting."""
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection
        
        # Setup mocks
        mock_connection.select.return_value = ("OK", [b"0"])
        mock_connection.search.return_value = ("OK", [b""])
        mock_connection.list.return_value = ("OK", [b'(\\HasNoChildren) "/" "INBOX"'])
        
        helper = GmailHelper(
            email_address="test@gmail.com",
            app_password="test-password"
        )
        
        # Connect
        helper.connect()
        assert helper.connection is not None
        
        # Read emails
        emails = helper.read_latest_emails(n=5)
        assert isinstance(emails, list)
        
        # Get folders
        folders = helper.get_folders()
        assert isinstance(folders, list)
        
        # Disconnect
        helper.disconnect()
        mock_connection.close.assert_called_once()


# Run tests with coverage if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.core.gmail_helper", "--cov-report=term-missing"])
