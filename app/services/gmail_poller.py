import asyncio
from datetime import datetime
import sys
import os

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.gmail_helper import GmailHelper
from src.core.email_processor import EmailProcessor
from app.services.todo_service import TodoService
from app.models import TodoCreate, Priority


class GmailPoller:
    """Background service to poll Gmail periodically and create todos."""
    
    def __init__(self, poll_interval_seconds: int = 60):
        self.poll_interval_seconds = poll_interval_seconds
        self.is_running = False
        self.last_poll_time = None
        self.last_poll_status = None
        self.total_emails_processed = 0
        self.total_todos_created = 0
        self.email_processor = EmailProcessor()
        self.processed_email_ids = set()  # Track processed emails to avoid duplicates
        
    async def start_polling(self):
        """Start the background polling loop."""
        self.is_running = True
        print(f"🚀 Gmail poller started - polling every {self.poll_interval_seconds} seconds")
        
        while self.is_running:
            try:
                await self.poll_gmail()
            except Exception as e:
                print(f"⚠️  Error in polling loop: {e}")
                self.last_poll_status = f"error: {str(e)}"
            
            # Wait for the next poll
            await asyncio.sleep(self.poll_interval_seconds)
    
    async def poll_gmail(self):
        """Poll Gmail once and process emails."""
        try:
            # Check if credentials are configured
            gmail_user = os.getenv("GMAIL_USER")
            gmail_password = os.getenv("GMAIL_APP_PASSWORD")
            
            if not gmail_user or not gmail_password:
                self.last_poll_status = "credentials_not_configured"
                print("⚠️  Gmail credentials not configured. Skipping poll.")
                return
            
            print(f"📧 Polling Gmail at {datetime.now().isoformat()}")
            
            # Fetch unread emails
            with GmailHelper() as gmail:
                emails = gmail.read_latest_emails(n=10, unread_only=True)
            
            if not emails:
                print("✅ No new emails to process")
                self.last_poll_time = datetime.now().isoformat()
                self.last_poll_status = "success"
                return
            
            # Filter out already processed emails
            new_emails = [e for e in emails if e['id'] not in self.processed_email_ids]
            
            if not new_emails:
                print("✅ All emails already processed")
                self.last_poll_time = datetime.now().isoformat()
                self.last_poll_status = "success"
                return
            
            print(f"📨 Found {len(new_emails)} new emails to process")
            
            # Process each email using the email_processor
            todos_created = 0
            for email_data in new_emails:
                try:
                    # Extract action item using email_processor
                    action_item = self.email_processor.extract_action_item(email_data)
                    
                    if action_item.is_action_item and action_item.action_item:
                        # Map priority
                        priority_map = {
                            "low": Priority.low,
                            "medium": Priority.medium,
                            "high": Priority.high
                        }
                        priority = priority_map.get(action_item.priority, Priority.medium)
                        
                        # Create todo
                        todo_create = TodoCreate(
                            title=action_item.action_item,
                            description=f"From: {email_data['from_name']} <{email_data['from']}>\nSubject: {email_data['subject']}",
                            priority=priority,
                            due_date=action_item.due_date,
                            source="gmail"
                        )
                        
                        TodoService.create_todo(todo_create)
                        todos_created += 1
                        print(f"✅ Created todo: {action_item.action_item[:50]}...")
                    
                    # Mark as processed
                    self.processed_email_ids.add(email_data['id'])
                    
                except Exception as e:
                    print(f"⚠️  Error processing email {email_data.get('subject', 'unknown')}: {e}")
            
            # Update stats
            self.total_emails_processed += len(new_emails)
            self.total_todos_created += todos_created
            self.last_poll_time = datetime.now().isoformat()
            self.last_poll_status = "success"
            
            print(f"✅ Poll complete - processed {len(new_emails)} emails, created {todos_created} todos")
            
        except Exception as e:
            print(f"❌ Error polling Gmail: {e}")
            self.last_poll_status = f"error: {str(e)}"
            raise
    
    def stop_polling(self):
        """Stop the background polling loop."""
        self.is_running = False
        print("🛑 Gmail poller stopped")
    
    def get_status(self):
        """Get the current status of the poller."""
        return {
            "is_running": self.is_running,
            "poll_interval_seconds": self.poll_interval_seconds,
            "last_poll_time": self.last_poll_time,
            "last_poll_status": self.last_poll_status,
            "total_emails_processed": self.total_emails_processed,
            "total_todos_created": self.total_todos_created,
            "processed_email_count": len(self.processed_email_ids)
        }


# Global instance
gmail_poller = GmailPoller(poll_interval_seconds=60)
