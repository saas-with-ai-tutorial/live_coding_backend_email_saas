from fastapi import APIRouter, HTTPException
from typing import List
from app.models import Todo, TodoCreate, TodoUpdate
from app.services.todo_service import TodoService

router = APIRouter(prefix="/api/todos", tags=["todos"])


@router.get("", response_model=List[Todo])
async def get_todos():
    """Get all todos."""
    return TodoService.get_all_todos()


@router.post("", response_model=Todo)
async def create_todo(todo: TodoCreate):
    """Create a new todo."""
    return TodoService.create_todo(todo)


@router.get("/{todo_id}", response_model=Todo)
async def get_todo(todo_id: str):
    """Get a specific todo by ID."""
    todo = TodoService.get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.put("/{todo_id}", response_model=Todo)
async def update_todo(todo_id: str, todo_update: TodoUpdate):
    """Update a todo."""
    updated_todo = TodoService.update_todo(todo_id, todo_update)
    if not updated_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated_todo


@router.delete("/{todo_id}")
async def delete_todo(todo_id: str):
    """Delete a todo."""
    success = TodoService.delete_todo(todo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}


@router.patch("/{todo_id}/toggle", response_model=Todo)
async def toggle_todo(todo_id: str):
    """Toggle todo completion status."""
    toggled_todo = TodoService.toggle_todo(todo_id)
    if not toggled_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return toggled_todo
