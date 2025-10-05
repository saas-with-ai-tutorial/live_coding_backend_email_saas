from fastapi import APIRouter
from app.models import MessageCreate, ProcessedMessage
from app.services.message_processor import MessageProcessor

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.post("/process", response_model=ProcessedMessage)
async def process_message(message: MessageCreate):
    """
    Process a message and create action items.
    Works for any message source.
    """
    todo_ids = MessageProcessor.process_message(message)
    
    return ProcessedMessage(
        message=message,
        todos_created=todo_ids
    )


@router.post("/gmail")
async def receive_gmail_message(message: MessageCreate):
    """Endpoint specifically for Gmail messages."""
    message.source = "gmail"
    todo_ids = MessageProcessor.process_message(message)
    
    return {
        "message": "Gmail message processed",
        "todos_created": todo_ids
    }


@router.post("/slack")
async def receive_slack_message(message: MessageCreate):
    """Endpoint specifically for Slack messages."""
    message.source = "slack"
    todo_ids = MessageProcessor.process_message(message)
    
    return {
        "message": "Slack message processed",
        "todos_created": todo_ids
    }


@router.post("/whatsapp")
async def receive_whatsapp_message(message: MessageCreate):
    """Endpoint specifically for WhatsApp messages."""
    message.source = "whatsapp"
    todo_ids = MessageProcessor.process_message(message)
    
    return {
        "message": "WhatsApp message processed",
        "todos_created": todo_ids
    }


@router.post("/outlook")
async def receive_outlook_message(message: MessageCreate):
    """Endpoint specifically for Outlook messages."""
    message.source = "outlook"
    todo_ids = MessageProcessor.process_message(message)
    
    return {
        "message": "Outlook message processed",
        "todos_created": todo_ids
    }


@router.post("/telegram")
async def receive_telegram_message(message: MessageCreate):
    """Endpoint specifically for Telegram messages."""
    message.source = "telegram"
    todo_ids = MessageProcessor.process_message(message)
    
    return {
        "message": "Telegram message processed",
        "todos_created": todo_ids
    }
