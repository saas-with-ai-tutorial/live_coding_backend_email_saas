from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.medium
    due_date: Optional[str] = None


class TodoCreate(TodoBase):
    source: str = "manual"


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    due_date: Optional[str] = None
    completed: Optional[bool] = None


class Todo(TodoBase):
    id: str
    completed: bool = False
    source: str
    created_at: str

    class Config:
        from_attributes = True
