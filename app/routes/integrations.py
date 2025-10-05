from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.storage.memory_store import store

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.get("", response_model=List[Dict[str, Any]])
async def get_integrations():
    """Get all available integrations."""
    return store.get_all_integrations()


@router.get("/{name}", response_model=Dict[str, Any])
async def get_integration(name: str):
    """Get a specific integration by name."""
    integration = store.get_integration(name)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.post("/{name}/toggle", response_model=Dict[str, Any])
async def toggle_integration(name: str):
    """Toggle an integration's enabled status."""
    integration = store.toggle_integration(name)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration
