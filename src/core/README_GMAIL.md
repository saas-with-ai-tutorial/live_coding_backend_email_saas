# Gmail Helper - Setup Guide

## 🎯 Overview

The `GmailHelper` class provides easy access to read emails from Gmail using IMAP with App Password authentication.

## 🔐 Setup Gmail App Password

### Step 1: Enable 2-Factor Authentication
1. Go to your [Google Account Security Settings](https://myaccount.google.com/security)
2. Enable **2-Step Verification** if not already enabled

### Step 2: Generate App Password
1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
2. Select **Mail** as the app
3. Select **Other (Custom name)** as the device, enter "Email SaaS Backend"
4. Click **Generate**
5. Copy the 16-character password (remove spaces)

### Step 3: Configure Environment Variables
Create a `.env` file in the backend root directory:

```bash
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
```

**Security Note**: Never commit the `.env` file to version control. Add it to `.gitignore`.

## 📦 Installation

Install required dependencies:

```bash
pip install python-dotenv
```

The `imaplib` and `email` modules are part of Python's standard library.

## 🚀 Usage Examples

### Basic Usage - Read Latest Emails

```python
from src.core.gmail_helper import GmailHelper

# Using context manager (recommended - auto connects and disconnects)
with GmailHelper() as gmail:
    emails = gmail.read_latest_emails(n=10)
    
    for email_data in emails:
        print(f"Subject: {email_data['subject']}")
        print(f"From: {email_data['from_name']} <{email_data['from']}>")
        print(f"Date: {email_data['date']}")
        print(f"Body: {email_data['body'][:100]}...")
        print()
```

### Read Only Unread Emails

```python
with GmailHelper() as gmail:
    unread_emails = gmail.read_latest_emails(n=20, unread_only=True)
    
    print(f"Found {len(unread_emails)} unread emails")
    
    for email_data in unread_emails:
        print(f"✉️ {email_data['subject']}")
        print(f"   Snippet: {email_data['snippet']}")
```

### Read from Specific Folder

```python
with GmailHelper() as gmail:
    # Get all available folders
    folders = gmail.get_folders()
    print("Available folders:", folders)
    
    # Read from specific folder
    emails = gmail.read_latest_emails(n=5, folder="INBOX")
```

### Mark Emails as Read/Unread

```python
with GmailHelper() as gmail:
    emails = gmail.read_latest_emails(n=5, unread_only=True)
    
    for email_data in emails:
        print(f"Processing: {email_data['subject']}")
        
        # Mark as read after processing
        gmail.mark_as_read(email_data['id'])
```

### Manual Connection Management

```python
# If you need more control over the connection
gmail = GmailHelper()

try:
    gmail.connect()
    emails = gmail.read_latest_emails(n=10)
    
    # Process emails...
    
finally:
    gmail.disconnect()
```

### Using Custom Credentials

```python
# Override environment variables
gmail = GmailHelper(
    email_address="custom@gmail.com",
    app_password="custom-app-password"
)

with gmail:
    emails = gmail.read_latest_emails(n=5)
```

## 📊 Email Data Structure

Each email returned is a dictionary with the following structure:

```python
{
    "id": "12345",                          # Email unique ID
    "subject": "Meeting Tomorrow",          # Email subject
    "from": "sender@example.com",           # Sender email
    "from_name": "John Doe",                # Sender name
    "to": "recipient@gmail.com",            # Recipient email
    "date": "Mon, 1 Jan 2024 10:00:00",    # Email date
    "body": "Full email body text...",      # Complete email body
    "snippet": "First 200 chars...",        # Body preview
    "is_unread": True                       # Unread status
}
```

## 🔧 Methods Reference

### `__init__(email_address, app_password)`
Initialize the Gmail helper with credentials.

- **Parameters**:
  - `email_address` (optional): Gmail address (defaults to `GMAIL_USER` env var)
  - `app_password` (optional): App password (defaults to `GMAIL_APP_PASSWORD` env var)

### `connect()`
Establish connection to Gmail IMAP server.

### `disconnect()`
Close connection to Gmail IMAP server.

### `read_latest_emails(n, folder, unread_only)`
Read the latest n emails from Gmail.

- **Parameters**:
  - `n` (int, default=10): Number of emails to retrieve
  - `folder` (str, default="INBOX"): Folder to read from
  - `unread_only` (bool, default=False): Only fetch unread emails
- **Returns**: List of email dictionaries

### `mark_as_read(email_id)`
Mark an email as read.

- **Parameters**: `email_id` (str): Email ID
- **Returns**: `bool` - Success status

### `mark_as_unread(email_id)`
Mark an email as unread.

- **Parameters**: `email_id` (str): Email ID
- **Returns**: `bool` - Success status

### `get_folders()`
Get list of all available folders/labels.

- **Returns**: List of folder names

## 🧪 Testing

Run the example code directly:

```bash
cd /Users/rakeshbhugra/code/instructor_notes/live_coding_saas/live_coding_backend_email_saas

# Make sure you have your .env file configured
python -m src.core.gmail_helper
```

## 🔒 Security Best Practices

1. **Never commit credentials**: Always use environment variables
2. **Use App Passwords**: Don't use your main Gmail password
3. **Rotate passwords**: Periodically generate new app passwords
4. **Limit scope**: App passwords are specific to the app, not your entire account
5. **Revoke unused**: Remove app passwords you're no longer using

## ⚠️ Common Issues

### Authentication Failed
- Verify 2-factor authentication is enabled
- Check that the app password is correct (no spaces)
- Ensure you're using an app password, not your regular password

### Connection Timeout
- Check your internet connection
- Verify firewall isn't blocking port 993
- Try connecting from a different network

### No Emails Found
- Check the folder name is correct
- Verify there are emails in the specified folder
- Try with `unread_only=False` to see all emails

## 🔗 Integration with FastAPI

Example FastAPI endpoint to fetch emails:

```python
from fastapi import APIRouter, HTTPException
from src.core.gmail_helper import GmailHelper

router = APIRouter()

@router.get("/api/emails/latest")
async def get_latest_emails(n: int = 10, unread_only: bool = False):
    """Fetch latest emails from Gmail."""
    try:
        with GmailHelper() as gmail:
            emails = gmail.read_latest_emails(n=n, unread_only=unread_only)
            return {"success": True, "emails": emails, "count": len(emails)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 📚 Resources

- [Gmail IMAP Settings](https://support.google.com/mail/answer/7126229)
- [Google App Passwords](https://support.google.com/accounts/answer/185833)
- [Python imaplib Documentation](https://docs.python.org/3/library/imaplib.html)
- [Python email Documentation](https://docs.python.org/3/library/email.html)

---

**Last Updated**: October 5, 2025
**Python Version**: 3.11+
