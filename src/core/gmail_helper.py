import imaplib
import email
from email import message_from_bytes
from email.header import decode_header
from email.message import Message
from typing import List, Dict, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class GmailHelper:
    """
    Helper class to read emails from Gmail using IMAP with App Password authentication.
    
    Setup:
    1. Enable 2-factor authentication on your Google account
    2. Generate an App Password: https://myaccount.google.com/apppasswords
    3. Set GMAIL_USER and GMAIL_APP_PASSWORD in your .env file
    """
    
    def __init__(self, email_address: Optional[str] = None, app_password: Optional[str] = None):
        """
        Initialize Gmail helper with credentials.
        
        Args:
            email_address: Gmail email address (reads from GMAIL_USER env var if not provided)
            app_password: Gmail app password (reads from GMAIL_APP_PASSWORD env var if not provided)
        """
        self.email_address = email_address or os.getenv("GMAIL_USER")
        self.app_password = app_password or os.getenv("GMAIL_APP_PASSWORD")
        
        if not self.email_address or not self.app_password:
            raise ValueError("Email address and app password must be provided either as arguments or environment variables")
        
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        self.connection = None
    
    def connect(self) -> None:
        """Establish connection to Gmail IMAP server."""
        try:
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.connection.login(self.email_address, self.app_password)
            print(f"✅ Successfully connected to Gmail as {self.email_address}")
        except imaplib.IMAP4.error as e:
            raise ConnectionError(f"Failed to connect to Gmail: {str(e)}")
    
    def disconnect(self) -> None:
        """Close connection to Gmail IMAP server."""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                print("✅ Disconnected from Gmail")
            except:
                pass
    
    def _decode_header_value(self, value: str) -> str:
        """
        Decode email header value handling different encodings.
        
        Args:
            value: Raw header value
            
        Returns:
            Decoded string
        """
        if not value:
            return ""
        
        decoded_parts = decode_header(value)
        decoded_string = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    decoded_string += part.decode(encoding or 'utf-8', errors='ignore')
                except:
                    decoded_string += part.decode('utf-8', errors='ignore')
            else:
                decoded_string += part
        
        return decoded_string
    
    def _extract_body(self, msg: Message) -> str:
        """
        Extract email body from message.
        
        Args:
            msg: Email message object
            
        Returns:
            Email body text
        """
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Get text/plain or text/html parts
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
                elif content_type == "text/html" and not body and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(msg.get_payload())
        
        return body.strip()
    
    def read_latest_emails(
        self, 
        n: int = 10, 
        folder: str = "INBOX",
        unread_only: bool = False
    ) -> List[Dict[str, any]]:
        """
        Read the latest n emails from Gmail.
        
        Args:
            n: Number of latest emails to retrieve (default: 10)
            folder: Email folder to read from (default: "INBOX")
            unread_only: If True, only fetch unread emails (default: False)
            
        Returns:
            List of email dictionaries containing:
                - id: Email unique ID
                - subject: Email subject
                - from: Sender email address
                - from_name: Sender name
                - to: Recipient email address
                - date: Email date
                - body: Email body text
                - snippet: First 200 characters of body
                - is_unread: Boolean indicating if email is unread
        """
        if not self.connection:
            self.connect()
        
        try:
            # Select the mailbox
            status, messages = self.connection.select(folder)
            
            if status != "OK":
                raise Exception(f"Failed to select folder: {folder}")
            
            # Search for emails
            search_criteria = "UNSEEN" if unread_only else "ALL"
            status, message_ids = self.connection.search(None, search_criteria)
            
            if status != "OK":
                raise Exception("Failed to search emails")
            
            # Get list of email IDs
            email_id_list = message_ids[0].split()
            
            if not email_id_list:
                print(f"ℹ️  No {'unread' if unread_only else ''} emails found in {folder}")
                return []
            
            # Get the latest n emails (emails are in chronological order, so we want the last n)
            latest_email_ids = email_id_list[-n:] if len(email_id_list) >= n else email_id_list
            latest_email_ids = list(reversed(latest_email_ids))  # Reverse to get newest first
            
            emails = []
            
            for email_id in latest_email_ids:
                try:
                    # Fetch the email
                    status, msg_data = self.connection.fetch(email_id, "(RFC822)")
                    
                    if status != "OK":
                        continue
                    
                    # Parse the email
                    raw_email = msg_data[0][1]
                    msg = message_from_bytes(raw_email)
                    
                    # Extract email details
                    subject = self._decode_header_value(msg.get("Subject", ""))
                    from_header = self._decode_header_value(msg.get("From", ""))
                    to_header = self._decode_header_value(msg.get("To", ""))
                    date_header = msg.get("Date", "")
                    
                    # Extract sender email and name
                    from_name = from_header
                    from_email = from_header
                    if "<" in from_header and ">" in from_header:
                        from_name = from_header.split("<")[0].strip().strip('"')
                        from_email = from_header.split("<")[1].split(">")[0].strip()
                    
                    # Get email body
                    body = self._extract_body(msg)
                    snippet = body[:200] + "..." if len(body) > 200 else body
                    
                    # Check if email is unread
                    status, flag_data = self.connection.fetch(email_id, "(FLAGS)")
                    is_unread = b'\\Seen' not in flag_data[0]
                    
                    email_dict = {
                        "id": email_id.decode(),
                        "subject": subject,
                        "from": from_email,
                        "from_name": from_name,
                        "to": to_header,
                        "date": date_header,
                        "body": body,
                        "snippet": snippet,
                        "is_unread": is_unread
                    }
                    
                    emails.append(email_dict)
                    
                except Exception as e:
                    print(f"⚠️  Error processing email {email_id}: {str(e)}")
                    continue
            
            print(f"✅ Successfully retrieved {len(emails)} emails from {folder}")
            return emails
            
        except Exception as e:
            raise Exception(f"Error reading emails: {str(e)}")
    
    def mark_as_read(self, email_id: str) -> bool:
        """
        Mark an email as read.
        
        Args:
            email_id: Email ID to mark as read
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            self.connect()
        
        try:
            self.connection.store(email_id, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            print(f"⚠️  Error marking email as read: {str(e)}")
            return False
    
    def mark_as_unread(self, email_id: str) -> bool:
        """
        Mark an email as unread.
        
        Args:
            email_id: Email ID to mark as unread
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            self.connect()
        
        try:
            self.connection.store(email_id, '-FLAGS', '\\Seen')
            return True
        except Exception as e:
            print(f"⚠️  Error marking email as unread: {str(e)}")
            return False
    
    def get_folders(self) -> List[str]:
        """
        Get list of all available folders/labels.
        
        Returns:
            List of folder names
        """
        if not self.connection:
            self.connect()
        
        try:
            status, folders = self.connection.list()
            if status != "OK":
                return []
            
            folder_list = []
            for folder in folders:
                folder_name = folder.decode().split('"/"')[-1].strip().strip('"')
                folder_list.append(folder_name)
            
            return folder_list
        except Exception as e:
            print(f"⚠️  Error getting folders: {str(e)}")
            return []
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


# Example usage
if __name__ == "__main__":
    """
    Example usage of GmailHelper class.
    
    Before running:
    1. Create a .env file in the backend root directory
    2. Add your Gmail credentials:
       GMAIL_USER=your-email@gmail.com
       GMAIL_APP_PASSWORD=your-app-password
    """
    
    try:
        # Using context manager (recommended)
        with GmailHelper() as gmail:
            # Read latest 5 emails
            emails = gmail.read_latest_emails(n=5)
            
            print(f"\n📧 Found {len(emails)} emails:\n")
            
            for i, email_data in enumerate(emails, 1):
                print(f"{i}. {email_data['subject']}")
                print(f"   From: {email_data['from_name']} <{email_data['from']}>")
                print(f"   Date: {email_data['date']}")
                print(f"   Unread: {'Yes' if email_data['is_unread'] else 'No'}")
                print(f"   Snippet: {email_data['snippet']}")
                print()
            
            # Read only unread emails
            print("\n📬 Unread emails:")
            unread_emails = gmail.read_latest_emails(n=10, unread_only=True)
            print(f"Found {len(unread_emails)} unread emails")
            
            # Get all folders
            print("\n📁 Available folders:")
            folders = gmail.get_folders()
            for folder in folders:
                print(f"  - {folder}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
