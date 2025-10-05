from fastapi import APIRouter, HTTPException
from typing import List
import sys
import os

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.gmail_helper import GmailHelper
from app.services.message_processor import MessageProcessor
from app.services.gmail_poller import gmail_poller
from app.models import MessageCreate

router = APIRouter(prefix="/api/gmail", tags=["gmail"])


@router.post("/sync")
async def sync_gmail_emails(count: int = 10, unread_only: bool = True):
    """
    Sync emails from Gmail and create action items.
    
    Args:
        count: Number of emails to fetch (default: 10)
        unread_only: Only fetch unread emails (default: True)
    """
    try:
        # Check if Gmail credentials are configured
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        
        if not gmail_user or not gmail_password:
            raise HTTPException(
                status_code=400, 
                detail="Gmail credentials not configured. Please set GMAIL_USER and GMAIL_APP_PASSWORD in .env file"
            )
        
        # Fetch emails from Gmail
        with GmailHelper() as gmail:
            emails = gmail.read_latest_emails(n=count, unread_only=unread_only)
        
        # Process each email and create todos
        all_todo_ids = []
        processed_count = 0
        
        for email_data in emails:
            # Create a message object from email
            message = MessageCreate(
                content=email_data["body"],
                sender=email_data["from"],
                source="gmail",
                subject=email_data["subject"]
            )
            
            # Process the message
            todo_ids = MessageProcessor.process_message(message)
            all_todo_ids.extend(todo_ids)
            
            if todo_ids:
                processed_count += 1
        
        return {
            "message": "Gmail sync completed",
            "emails_fetched": len(emails),
            "action_items_created": len(all_todo_ids),
            "emails_with_action_items": processed_count,
            "todo_ids": all_todo_ids
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to Gmail: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing Gmail: {str(e)}")


@router.get("/test-connection")
async def test_gmail_connection():
    """Test Gmail connection and credentials."""
    try:
        with GmailHelper() as gmail:
            folders = gmail.get_folders()
            return {
                "status": "connected",
                "message": "Successfully connected to Gmail",
                "folders_count": len(folders)
            }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing Gmail connection: {str(e)}")


@router.get("/polling-status")
async def get_polling_status():
    """Get the status of the Gmail background polling service."""
    return gmail_poller.get_status()


@router.post("/trigger-poll")
async def trigger_manual_poll():
    """Manually trigger a Gmail poll (in addition to automatic polling)."""
    try:
        await gmail_poller.poll_gmail()
        return {
            "message": "Manual poll completed",
            "status": gmail_poller.get_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering poll: {str(e)}")
