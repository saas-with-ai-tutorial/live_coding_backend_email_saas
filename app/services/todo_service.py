from typing import List, Optional
from app.models import Todo, TodoCreate, TodoUpdate
from app.storage.memory_store import store


class TodoService:
    """Service layer for todo operations."""
    
    @staticmethod
    def create_todo(todo_create: TodoCreate) -> Todo:
        """Create a new todo."""
        todo_data = todo_create.model_dump()
        created_todo = store.create_todo(todo_data)
        return Todo(**created_todo)
    
    @staticmethod
    def get_todo(todo_id: str) -> Optional[Todo]:
        """Get a todo by ID."""
        todo_data = store.get_todo(todo_id)
        if todo_data:
            return Todo(**todo_data)
        return None
    
    @staticmethod
    def get_all_todos() -> List[Todo]:
        """Get all todos."""
        todos_data = store.get_all_todos()
        return [Todo(**todo) for todo in todos_data]
    
    @staticmethod
    def update_todo(todo_id: str, todo_update: TodoUpdate) -> Optional[Todo]:
        """Update a todo."""
        update_data = todo_update.model_dump(exclude_unset=True)
        updated_todo = store.update_todo(todo_id, update_data)
        if updated_todo:
            return Todo(**updated_todo)
        return None
    
    @staticmethod
    def delete_todo(todo_id: str) -> bool:
        """Delete a todo."""
        return store.delete_todo(todo_id)
    
    @staticmethod
    def toggle_todo(todo_id: str) -> Optional[Todo]:
        """Toggle todo completion status."""
        toggled_todo = store.toggle_todo(todo_id)
        if toggled_todo:
            return Todo(**toggled_todo)
        return None
