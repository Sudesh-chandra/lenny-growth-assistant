"""
Chat router - handles streaming chat, sessions, and messages.
"""

import json
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, async_session_maker
from app.core.logging import get_logger
from app.models import Session, Message, Artifact
from app.schemas import (
    ChatRequest, ChatResponse, SessionCreate, SessionResponse,
    MessageResponse, ArtifactResponse,
)
from app.agents.router import AgentRouter

logger = get_logger(__name__)
router = APIRouter()

# Agent router singleton
agent_router = AgentRouter()


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    body: SessionCreate = SessionCreate(),
    db: AsyncSession = Depends(get_db),
):
    """Create a new chat session."""
    session = Session(
        title=body.title or "New Chat",
        llm_provider=body.llm_provider.value if body.llm_provider else "openrouter",
        model_name=body.model_name or "anthropic/claude-sonnet-4",
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)
    logger.info("session_created", session_id=session.id)
    return SessionResponse(**session.to_dict())


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    """List all chat sessions, ordered by most recent."""
    result = await db.execute(
        select(Session).order_by(Session.updated_at.desc())
    )
    sessions = result.scalars().all()
    return [SessionResponse(**s.to_dict()) for s in sessions]


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific session by ID."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(**session.to_dict())


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a session and all its messages."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.delete(session)
    logger.info("session_deleted", session_id=session_id)
    return {"status": "deleted", "session_id": session_id}


@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
async def get_messages(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get all messages for a session."""
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()
    return [MessageResponse(**m.to_dict()) for m in messages]


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Non-streaming chat endpoint.
    Processes user message and returns complete response.
    """
    # Get or create session
    session = None
    if body.session_id:
        result = await db.execute(select(Session).where(Session.id == body.session_id))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = Session(
            title=body.message[:50] + "..." if len(body.message) > 50 else body.message,
            llm_provider=body.llm_provider.value if body.llm_provider else "openrouter",
            model_name=body.model_name or "anthropic/claude-sonnet-4",
        )
        db.add(session)
        await db.flush()
    
    # Save user message
    user_msg = Message(
        session_id=session.id,
        role="user",
        content=body.message,
    )
    db.add(user_msg)
    await db.flush()
    
    # Get session history
    history_result = await db.execute(
        select(Message)
        .where(Message.session_id == session.id)
        .order_by(Message.created_at.asc())
    )
    history = [
        {"role": m.role, "content": m.content}
        for m in history_result.scalars().all()
        if m.role in ("user", "assistant")
    ]
    
    # Route to agent
    provider = body.llm_provider.value if body.llm_provider else session.llm_provider
    result = await agent_router.route(
        message=body.message,
        session_history=history,
        provider=provider,
        model=body.model_name or session.model_name,
        skill=body.skill,
    )
    
    # Save artifact if present
    artifact_id = None
    if result.get("artifact_data"):
        artifact = Artifact(
            session_id=session.id,
            artifact_type=result["artifact_data"]["artifact_type"],
            title=result["artifact_data"].get("title", "Untitled"),
            content=result["artifact_data"]["content"],
        )
        db.add(artifact)
        await db.flush()
        artifact_id = artifact.id
    
    # Save assistant message
    assistant_msg = Message(
        session_id=session.id,
        role="assistant",
        content=result["content"],
        citations=result.get("citations", []),
        has_artifact=result.get("has_artifact"),
        artifact_id=artifact_id,
    )
    db.add(assistant_msg)
    await db.flush()
    
    # Update session timestamp
    session.updated_at = None  # Will trigger onupdate
    
    await db.commit()
    
    return ChatResponse(
        session_id=session.id,
        message_id=assistant_msg.id,
        content=result["content"],
        citations=result.get("citations", []),
        has_artifact=result.get("has_artifact"),
        artifact_id=artifact_id,
        artifact_title=result.get("artifact_data", {}).get("title") if result.get("artifact_data") else None,
    )


@router.post("/chat/stream")
async def chat_stream(body: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    SSE streaming chat endpoint.
    Streams response token by token using Server-Sent Events.
    """
    # Get or create session
    session = None
    if body.session_id:
        result = await db.execute(select(Session).where(Session.id == body.session_id))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = Session(
            title=body.message[:50] + "..." if len(body.message) > 50 else body.message,
            llm_provider=body.llm_provider.value if body.llm_provider else "openrouter",
            model_name=body.model_name or "anthropic/claude-sonnet-4",
        )
        db.add(session)
        await db.flush()
        await db.commit()
    
    # Save user message
    user_msg = Message(
        session_id=session.id,
        role="user",
        content=body.message,
    )
    db.add(user_msg)
    await db.flush()
    await db.commit()
    
    # Get session history
    history_result = await db.execute(
        select(Message)
        .where(Message.session_id == session.id)
        .order_by(Message.created_at.asc())
    )
    history = [
        {"role": m.role, "content": m.content}
        for m in history_result.scalars().all()
        if m.role in ("user", "assistant")
    ]
    
    provider = body.llm_provider.value if body.llm_provider else session.llm_provider
    
    async def event_generator():
        """Generate SSE events from agent stream."""
        full_content = []
        citations_data = []
        artifact_data = None
        
        # Send session ID first
        yield f"data: {json.dumps({'type': 'session', 'data': {'session_id': session.id}})}\n\n"
        
        try:
            async for chunk in agent_router.route_stream(
                message=body.message,
                session_history=history,
                provider=provider,
                model=body.model_name or session.model_name,
                skill=body.skill,
            ):
                chunk_type = chunk.get("type", "token")
                
                if chunk_type == "token":
                    full_content.append(chunk["data"])
                    yield f"data: {json.dumps({'type': 'token', 'data': chunk['data']})}\n\n"
                elif chunk_type == "citations":
                    citations_data = chunk["data"]
                    yield f"data: {json.dumps({'type': 'citations', 'data': chunk['data']})}\n\n"
                elif chunk_type == "artifact":
                    artifact_data = chunk["data"]
                    yield f"data: {json.dumps({'type': 'artifact', 'data': chunk['data']})}\n\n"
                elif chunk_type == "error":
                    yield f"data: {json.dumps({'type': 'error', 'data': chunk['data']})}\n\n"
                elif chunk_type == "done":
                    break
        except Exception as e:
            logger.error("stream_error", error=str(e))
            yield f"data: {json.dumps({'type': 'error', 'data': 'An internal error occurred. Please try again.'})}\n\n"
        
        # Save assistant message to DB using a fresh session
        async with async_session_maker() as save_session:
            content = "".join(full_content)
            
            artifact_id = None
            if artifact_data:
                artifact = Artifact(
                    session_id=session.id,
                    artifact_type=artifact_data["artifact_type"],
                    title=artifact_data.get("title", "Untitled"),
                    content=artifact_data["content"],
                )
                save_session.add(artifact)
                await save_session.flush()
                artifact_id = artifact.id
            
            assistant_msg = Message(
                session_id=session.id,
                role="assistant",
                content=content,
                citations=citations_data,
                has_artifact=artifact_data["artifact_type"] if artifact_data else None,
                artifact_id=artifact_id,
            )
            save_session.add(assistant_msg)
            await save_session.commit()
        
        # Send done event
        yield f"data: {json.dumps({'type': 'done', 'data': ''})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/artifacts/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(artifact_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific artifact by ID."""
    result = await db.execute(select(Artifact).where(Artifact.id == artifact_id))
    artifact = result.scalar_one_or_none()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return ArtifactResponse(**artifact.to_dict())
