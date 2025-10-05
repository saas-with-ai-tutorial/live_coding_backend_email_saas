from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import asyncio
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Import routers
from app.routes import todos, messages, integrations, gmail
from app.services.gmail_poller import gmail_poller


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to start and stop background tasks."""
    # Start the Gmail poller
    polling_task = asyncio.create_task(gmail_poller.start_polling())
    print("✅ Started Gmail background poller")
    
    yield
    
    # Stop the Gmail poller
    gmail_poller.stop_polling()
    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        pass
    print("✅ Stopped Gmail background poller")


# Create FastAPI app
app = FastAPI(
    title="Email SaaS API",
    description="Message aggregator and todo manager API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3004"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(todos.router)
app.include_router(messages.router)
app.include_router(integrations.router)
app.include_router(gmail.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Email SaaS API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "email-saas-api"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
