from litellm import completion
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import os
from dotenv import load_dotenv

load_dotenv()


class ActionItem(BaseModel):
    """
    Model representing an action item extracted from an email.
    """
    is_action_item: bool
    action_item: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None  # high, medium, low


class EmailSummary(BaseModel):
    """
    Model representing a summary of an email.
    """
    summary: str
    key_points: List[str]
    sentiment: Optional[str] = None  # positive, neutral, negative


class EmailProcessor:
    """
    Helper class to process emails using LLM (Language Model).
    
    This class provides various email processing capabilities:
    - Extract action items from emails
    - Summarize emails
    - Categorize emails
    - Extract key information
    
    Setup:
    - Requires OPENAI_API_KEY or other LLM provider credentials in .env file
    """
    
    # System prompts for different tasks
    ACTION_ITEM_PROMPT = """
You are a helpful assistant that can process emails and create action items.
Descriptions should be actionable, ignore sales emails, ignore UPI transactions, ignore newsletters, ignore promotional emails, ignore social media notifications, ignore notifications, ignore spam, ignore other.
You will be given an email and you will need to create an action item based on the email.

Analyze the email content and determine:
1. If it contains an actionable task or request
2. What the action item is (if any)
3. When it's due (if mentioned)
4. The priority level (high, medium, low) based on urgency keywords

If the email does not have an action item, you should return:
{
    "is_action_item": false,
    "action_item": null,
    "due_date": null,
    "priority": null
}

Keywords indicating urgency:
- High priority: "urgent", "asap", "immediately", "critical", "emergency"
- Medium priority: "soon", "this week", "important"
- Low priority: "when you can", "no rush", "eventually"
"""
    
    SUMMARY_PROMPT = """
You are a helpful assistant that can summarize emails concisely.
Given an email, provide:
1. A brief summary (1-2 sentences)
2. Key points (bullet points of important information)
3. Overall sentiment (positive, neutral, or negative)

Be concise and focus on the most important information.
"""
    
    CATEGORY_PROMPT = """
You are a helpful assistant that can categorize emails.
Given an email, categorize it into one of these categories:
- Work/Business
- Personal
- Promotion/Marketing
- Social
- Notification
- Spam
- Other

Return only the category name.
"""
    
    def __init__(self, model: str = "openai/gpt-4o-mini", api_key: Optional[str] = None):
        """
        Initialize Email Processor with LLM configuration.
        
        Args:
            model: LLM model to use (default: "openai/gpt-4o-mini")
            api_key: API key for the LLM provider (reads from env vars if not provided)
        """
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key and "openai" in model.lower():
            print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
    
    def _format_email(self, email_data: Dict[str, Any]) -> str:
        """
        Format email data into a readable string for LLM processing.
        
        Args:
            email_data: Dictionary containing email fields (subject, from, to, date, body)
            
        Returns:
            Formatted email string
        """
        subject = email_data.get("subject", "No Subject")
        from_addr = email_data.get("from", "Unknown")
        from_name = email_data.get("from_name", "")
        to_addr = email_data.get("to", "")
        date = email_data.get("date", "")
        body = email_data.get("body", "")
        
        from_display = f"{from_name} <{from_addr}>" if from_name else from_addr
        
        formatted = f"""
Subject: {subject}
From: {from_display}
To: {to_addr}
Date: {date}

Body:
{body}
"""
        return formatted.strip()
    
    def extract_action_item(self, email_data: Dict[str, Any]) -> ActionItem:
        """
        Extract action item from an email using LLM.
        
        Args:
            email_data: Dictionary containing email fields (subject, from, to, date, body)
            
        Returns:
            ActionItem model with extracted information
            
        Raises:
            Exception: If LLM processing fails
        """
        try:
            formatted_email = self._format_email(email_data)
            
            messages = [
                {"role": "system", "content": self.ACTION_ITEM_PROMPT},
                {"role": "user", "content": formatted_email}
            ]
            
            response = completion(
                model=self.model,
                messages=messages,
                response_format=ActionItem,
                tools = []
            )
            
            # Parse the response content as JSON and create ActionItem
            import json
            content = response.choices[0].message.content
            action_data = json.loads(content) if isinstance(content, str) else content
            
            return ActionItem(**action_data)
            
        except Exception as e:
            print(f"⚠️  Error extracting action item: {str(e)}")
            # Return empty action item on error
            return ActionItem(is_action_item=False)
    
    def summarize_email(self, email_data: Dict[str, Any]) -> EmailSummary:
        """
        Generate a summary of an email using LLM.
        
        Args:
            email_data: Dictionary containing email fields (subject, from, to, date, body)
            
        Returns:
            EmailSummary model with summary information
            
        Raises:
            Exception: If LLM processing fails
        """
        try:
            formatted_email = self._format_email(email_data)
            
            messages = [
                {"role": "system", "content": self.SUMMARY_PROMPT},
                {"role": "user", "content": formatted_email}
            ]
            
            response = completion(
                model=self.model,
                messages=messages,
                response_format=EmailSummary
            )
            
            # Parse the response content as JSON and create EmailSummary
            import json
            content = response.choices[0].message.content
            summary_data = json.loads(content) if isinstance(content, str) else content
            
            return EmailSummary(**summary_data)
            
        except Exception as e:
            print(f"⚠️  Error summarizing email: {str(e)}")
            # Return basic summary on error
            return EmailSummary(
                summary="Error processing email",
                key_points=["Unable to generate summary"],
                sentiment="neutral"
            )
    
    def categorize_email(self, email_data: Dict[str, Any]) -> str:
        """
        Categorize an email using LLM.
        
        Args:
            email_data: Dictionary containing email fields (subject, from, to, date, body)
            
        Returns:
            Category string (e.g., "Work/Business", "Personal", etc.)
        """
        try:
            formatted_email = self._format_email(email_data)
            
            messages = [
                {"role": "system", "content": self.CATEGORY_PROMPT},
                {"role": "user", "content": formatted_email}
            ]
            
            response = completion(
                model=self.model,
                messages=messages
            )
            
            category = response.choices[0].message.content.strip()
            return category
            
        except Exception as e:
            print(f"⚠️  Error categorizing email: {str(e)}")
            return "Other"
    
    def process_email_batch(
        self, 
        emails: List[Dict[str, Any]], 
        extract_actions: bool = True,
        summarize: bool = False,
        categorize: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Process a batch of emails with various operations.
        
        Args:
            emails: List of email dictionaries
            extract_actions: Whether to extract action items (default: True)
            summarize: Whether to generate summaries (default: False)
            categorize: Whether to categorize emails (default: False)
            
        Returns:
            List of processed email dictionaries with additional fields
        """
        processed_emails = []
        
        for i, email_data in enumerate(emails, 1):
            print(f"📧 Processing email {i}/{len(emails)}: {email_data.get('subject', 'No Subject')[:50]}...")
            
            processed_email = email_data.copy()
            
            try:
                if extract_actions:
                    action_item = self.extract_action_item(email_data)
                    processed_email["action_item"] = action_item.model_dump()
                
                if summarize:
                    summary = self.summarize_email(email_data)
                    processed_email["summary"] = summary.model_dump()
                
                if categorize:
                    category = self.categorize_email(email_data)
                    processed_email["category"] = category
                
                processed_emails.append(processed_email)
                
            except Exception as e:
                print(f"⚠️  Error processing email: {str(e)}")
                processed_emails.append(processed_email)
        
        print(f"✅ Successfully processed {len(processed_emails)} emails")
        return processed_emails
    
    def extract_action_items_from_batch(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract only action items from a batch of emails (filters out non-action emails).
        
        Args:
            emails: List of email dictionaries
            
        Returns:
            List of emails that contain action items with extracted action information
        """
        action_emails = []
        
        for email_data in emails:
            action_item = self.extract_action_item(email_data)
            
            if action_item.is_action_item:
                email_with_action = email_data.copy()
                email_with_action["action_item"] = action_item.model_dump()
                action_emails.append(email_with_action)
        
        print(f"✅ Found {len(action_emails)} emails with action items out of {len(emails)} total")
        return action_emails


# Example usage
if __name__ == "__main__":
    """
    Example usage of EmailProcessor class.
    
    Before running:
    1. Create a .env file in the backend root directory
    2. Add your API key:
       OPENAI_API_KEY=your-api-key
    """
    
    # Example email data
    example_email = {
        "subject": "Urgent: Project Review Meeting Tomorrow",
        "from": "john.doe@example.com",
        "from_name": "John Doe",
        "to": "jane.doe@example.com",
        "date": "2024-01-15 10:30:00",
        "body": """Hi Jane,

I hope this email finds you well. We need to urgently schedule a project review meeting for tomorrow at 2 PM. 

Please prepare the following:
1. Q4 performance metrics
2. Budget analysis report
3. Next quarter roadmap

This is critical for our stakeholder presentation on Friday. Let me know if you can make it.

Best regards,
John"""
    }
    
    try:
        # Initialize email processor
        processor = EmailProcessor()
        
        print("=" * 80)
        print("EMAIL PROCESSOR DEMO")
        print("=" * 80)
        
        # Extract action item
        print("\n📋 Extracting Action Item...\n")
        action_item = processor.extract_action_item(example_email)
        print(f"Is Action Item: {action_item.is_action_item}")
        print(f"Action: {action_item.action_item}")
        print(f"Due Date: {action_item.due_date}")
        print(f"Priority: {action_item.priority}")
        
        # Summarize email
        print("\n📝 Generating Summary...\n")
        summary = processor.summarize_email(example_email)
        print(f"Summary: {summary.summary}")
        print(f"Key Points:")
        for point in summary.key_points:
            print(f"  - {point}")
        print(f"Sentiment: {summary.sentiment}")
        
        # Categorize email
        print("\n🏷️  Categorizing Email...\n")
        category = processor.categorize_email(example_email)
        print(f"Category: {category}")
        
        # Process batch (with single email as example)
        print("\n📦 Processing Batch...\n")
        processed = processor.process_email_batch(
            [example_email],
            extract_actions=True,
            summarize=True,
            categorize=True
        )
        
        print("\n✅ Processing complete!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")