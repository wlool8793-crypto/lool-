"""
FastAPI application for LangGraph Deep Web Agent.
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import Optional

from app.core.config import settings
from app.core.database import create_tables
from app.core.redis import redis_manager
from app.api.endpoints import auth, conversations, agents, tools, files
from app.websocket.manager import WebSocketManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting up Deep Agent application...")

    # Create database tables
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

    # Test Redis connection
    try:
        if redis_manager.ping():
            logger.info("Redis connection successful")
        else:
            logger.warning("Redis connection failed")
    except Exception as e:
        logger.warning(f"Redis connection error: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Deep Agent application...")
    redis_manager.close()


# Create FastAPI application
app = FastAPI(
    title="LangGraph Deep Web Agent",
    description="A sophisticated AI agent system with LangGraph orchestration",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize WebSocket manager
websocket_manager = WebSocketManager()

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["conversations"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(tools.router, prefix="/api/v1/tools", tags=["tools"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LangGraph Deep Web Agent API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    redis_status = "connected" if redis_manager.ping() else "disconnected"

    return {
        "status": "healthy",
        "redis": redis_status,
        "environment": settings.environment
    }


@app.get("/api/v1/status")
async def api_status():
    """API status endpoint."""
    return {
        "api_version": "1.0.0",
        "environment": settings.environment,
        "features": {
            "websockets": True,
            "file_upload": True,
            "redis_cache": True,
            "database": True
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level="info"
    )