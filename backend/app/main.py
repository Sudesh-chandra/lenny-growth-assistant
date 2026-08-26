"""
Lenny Growth Assistant - FastAPI Application
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure the backend directory is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.database import init_db, close_db
from app.routers import chat, models, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - startup and shutdown."""
    # Startup
    setup_logging()
    logger = get_logger("lifespan")
    logger.info("starting_up", app_name=settings.app_name, env=settings.app_env)
    
    try:
        await init_db()
        logger.info("database_initialized")
    except Exception as e:
        logger.error("database_init_failed", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("shutting_down")
    try:
        await close_db()
    except Exception:
        pass


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI-powered conversational assistant for product management and growth, grounded in Lenny's Podcast transcripts.",
    lifespan=lifespan,
)

# CORS middleware - restrict to known frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:80",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(models.router, prefix="/api", tags=["Models"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
