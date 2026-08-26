"""
Health check router.
"""

from fastapi import APIRouter
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas import HealthResponse
from app.services.vector_store import get_vector_store

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint - reports status of all system components."""
    db_status = "unknown"
    try:
        from app.core.database import engine
        async with engine.connect() as conn:
            await conn.execute(
                __import__("sqlalchemy").text("SELECT 1")
            )
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"
    
    vs_status = "unknown"
    try:
        vs = get_vector_store()
        count = vs.get_count()
        vs_status = f"connected ({count} chunks)"
    except Exception as e:
        vs_status = f"error: {str(e)[:50]}"
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        database=db_status,
        llm_provider=settings.llm_provider,
        vector_store=vs_status,
    )
