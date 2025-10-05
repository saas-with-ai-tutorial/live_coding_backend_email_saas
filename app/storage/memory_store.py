from typing import Dict, List, Optional
from datetime import datetime
import uuid
import json
import os
from pathlib import Path


class MemoryStore:
    """In-memory storage with JSON persistence."""
    
    def __init__(self):
        self.storage_dir = Path(__file__).parent.parent.parent / "data"
        self.storage_dir.mkdir(exist_ok=True)
        
        self.todos_file = self.storage_dir / "todos.json"
        self.messages_file = self.storage_dir / "messages.json"
        
        # Load data from files if they exist
        self.todos: Dict[str, dict] = self._load_json(self.todos_file, {})
        self.messages: Dict[str, dict] = self._load_json(self.messages_file, {})
        self.integrations: Dict[str, dict] = {
            "gmail": {
                "id": "gmail",
                "name": "gmail",
                "display_name": "Gmail",
                "description": "Connect your Gmail account to automatically extract action items from emails",
                "logo": "/logos/gmail.svg",
                "enabled": True,
                "status": "connected",
                "category": "Email"
            },
            "slack": {
                "id": "slack",
                "name": "slack",
                "display_name": "Slack",
                "description": "Integrate with Slack to turn team messages into actionable tasks",
                "logo": "/logos/slack.svg",
                "enabled": False,
                "status": "disconnected",
                "category": "Team Chat"
            },
            "whatsapp": {
                "id": "whatsapp",
                "name": "whatsapp",
                "display_name": "WhatsApp",
                "description": "Connect WhatsApp to create todos from important messages",
                "logo": "/logos/whatsapp.svg",
                "enabled": False,
                "status": "disconnected",
                "category": "Messaging"
            },
            "outlook": {
                "id": "outlook",
                "name": "outlook",
                "display_name": "Outlook",
                "description": "Sync your Outlook emails and automatically create action items",
                "logo": "/logos/outlook.svg",
                "enabled": False,
                "status": "disconnected",
                "category": "Email"
            },
            "telegram": {
                "id": "telegram",
                "name": "telegram",
                "display_name": "Telegram",
                "description": "Monitor Telegram messages and convert them into todos",
                "logo": "/logos/telegram.svg",
                "enabled": False,
                "status": "disconnected",
                "category": "Messaging"
            },
            "discord": {
                "id": "discord",
                "name": "discord",
                "display_name": "Discord",
                "description": "Connect Discord servers to track community tasks and discussions",
                "logo": "/logos/discord.svg",
                "enabled": False,
                "status": "disconnected",
                "category": "Community"
            },
            "teams": {
                "id": "teams",
                "name": "teams",
                "display_name": "Microsoft Teams",
                "description": "Integrate Microsoft Teams for seamless collaboration and task management",
                "logo": "/logos/teams.svg",
                "enabled": False,
                "status": "disconnected",
                "category": "Collaboration"
            },
            "linkedin": {
                "id": "linkedin",
                "name": "linkedin",
                "display_name": "LinkedIn",
                "description": "Track professional messages and networking opportunities",
                "logo": "/logos/linkedin.svg",
                "enabled": False,
                "status": "disconnected",
                "category": "Professional"
            }
        }
    
    def _load_json(self, filepath: Path, default: dict) -> dict:
        """Load data from JSON file."""
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading {filepath}: {e}")
                return default
        return default
    
    def _save_json(self, filepath: Path, data: dict):
        """Save data to JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving {filepath}: {e}")
    
    def _save_todos(self):
        """Persist todos to JSON file."""
        self._save_json(self.todos_file, self.todos)
    
    def _save_messages(self):
        """Persist messages to JSON file."""
        self._save_json(self.messages_file, self.messages)
    
    # Todo operations
    def create_todo(self, todo_data: dict) -> dict:
        """Create a new todo."""
        todo_id = str(uuid.uuid4())
        todo = {
            "id": todo_id,
            "created_at": datetime.now().isoformat(),
            "completed": False,
            **todo_data
        }
        self.todos[todo_id] = todo
        self._save_todos()
        return todo
    
    def get_todo(self, todo_id: str) -> Optional[dict]:
        """Get a todo by ID."""
        return self.todos.get(todo_id)
    
    def get_all_todos(self) -> List[dict]:
        """Get all todos."""
        return list(self.todos.values())
    
    def update_todo(self, todo_id: str, todo_data: dict) -> Optional[dict]:
        """Update a todo."""
        if todo_id not in self.todos:
            return None
        
        # Update only provided fields
        for key, value in todo_data.items():
            if value is not None:
                self.todos[todo_id][key] = value
        
        self._save_todos()
        return self.todos[todo_id]
    
    def delete_todo(self, todo_id: str) -> bool:
        """Delete a todo."""
        if todo_id in self.todos:
            del self.todos[todo_id]
            self._save_todos()
            return True
        return False
    
    def toggle_todo(self, todo_id: str) -> Optional[dict]:
        """Toggle todo completion status."""
        if todo_id not in self.todos:
            return None
        
        self.todos[todo_id]["completed"] = not self.todos[todo_id]["completed"]
        self._save_todos()
        return self.todos[todo_id]
    
    # Integration operations
    def get_all_integrations(self) -> List[dict]:
        """Get all integrations."""
        return list(self.integrations.values())
    
    def get_integration(self, name: str) -> Optional[dict]:
        """Get an integration by name."""
        return self.integrations.get(name)
    
    def toggle_integration(self, name: str) -> Optional[dict]:
        """Toggle integration enabled status."""
        if name not in self.integrations:
            return None
        
        self.integrations[name]["enabled"] = not self.integrations[name]["enabled"]
        if self.integrations[name]["enabled"]:
            self.integrations[name]["status"] = "connected"
        else:
            self.integrations[name]["status"] = "disconnected"
        
        return self.integrations[name]


# Global instance
store = MemoryStore()
