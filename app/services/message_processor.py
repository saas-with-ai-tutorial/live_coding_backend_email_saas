from typing import List
from app.models import MessageCreate, TodoCreate, Priority
from app.services.todo_service import TodoService
from litellm import completion
from pydantic import BaseModel
from typing import Optional
import os


class ActionItem(BaseModel):
    is_action_item: bool
    action_item: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None


class MessageProcessor:
    """Service to process messages and create action items."""
    
    SYSTEM_PROMPT = """
You are a helpful assistant that processes messages and identifies action items.

Analyze the provided message and determine if it contains any action items or tasks that need to be done.

Rules:
1. If the message contains an action item, return is_action_item: true
2. Extract a clear, concise action item (task description)
3. Identify any due dates mentioned (format: YYYY-MM-DD)
4. Determine priority: "low", "medium", or "high" based on urgency
5. If no action item exists, return is_action_item: false

Examples of action items:
- "Review the Q4 budget report by Friday"
- "Deploy the new feature to staging"
- "Schedule a meeting with the marketing team"
- "Don't forget to pickup groceries"

Examples of non-action items:
- "Thanks for your help!"
- "The meeting went well yesterday"
- "Here's the document you requested"
"""
    
    @staticmethod
    def process_message(message: MessageCreate) -> List[str]:
        """
        Process a message and create todos for any action items found.
        
        Args:
            message: The message to process
            
        Returns:
            List of todo IDs that were created
        """
        # Format the message for AI processing
        message_content = f"""
Subject: {message.subject or 'N/A'}
From: {message.sender}
Source: {message.source}

Content:
{message.content}
"""
        
        try:
            # Use LiteLLM to analyze the message
            response = completion(
                model=os.getenv("LLM_MODEL", "openai/gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": MessageProcessor.SYSTEM_PROMPT},
                    {"role": "user", "content": message_content}
                ],
                response_format=ActionItem
            )
            
            # Parse the response
            result_content = response.choices[0].message.content
            
            # Parse JSON response if it's a string
            if isinstance(result_content, str):
                import json
                action_item = ActionItem(**json.loads(result_content))
            else:
                action_item = ActionItem(**result_content)
            
            # Create todos if action items were found
            todo_ids = []
            if action_item.is_action_item and action_item.action_item:
                # Determine priority
                priority_map = {
                    "low": Priority.low,
                    "medium": Priority.medium,
                    "high": Priority.high
                }
                priority = priority_map.get(action_item.priority, Priority.medium)
                
                # Create the todo
                todo_create = TodoCreate(
                    title=action_item.action_item,
                    description=f"From {message.source}: {message.subject or message.sender}",
                    priority=priority,
                    due_date=action_item.due_date,
                    source=message.source
                )
                
                created_todo = TodoService.create_todo(todo_create)
                todo_ids.append(created_todo.id)
            
            return todo_ids
            
        except Exception as e:
            print(f"Error processing message with AI: {str(e)}")
            # Fallback: create a simple todo from the message
            todo_create = TodoCreate(
                title=message.content[:100],  # First 100 chars as title
                description=f"From {message.source}: {message.subject or message.sender}",
                source=message.source
            )
            created_todo = TodoService.create_todo(todo_create)
            return [created_todo.id]
