from pydantic import BaseModel
from typing import Optional, List


class MessageBase(BaseModel):
    content: str
    sender: str
    source: str  # 'gmail', 'slack', 'whatsapp', 'outlook', 'telegram'
    subject: Optional[str] = None


class MessageCreate(MessageBase):
    pass


class ProcessedMessage(BaseModel):
    message: MessageBase
    todos_created: List[str]  # List of todo IDs created
