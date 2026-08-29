"""
Database models for sessions, messages, and artifacts.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Session(Base):
    """Chat session model - represents a conversation thread."""
    
    __tablename__ = "sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), default="New Chat")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    llm_provider = Column(String(50), default="openrouter")
    model_name = Column(String(100), default="nvidia/nemotron-3-super-120b-a12b:free")
    
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at")
    artifacts = relationship("Artifact", back_populates="session", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "llm_provider": self.llm_provider,
            "model_name": self.model_name,
        }


class Message(Base):
    """Individual message within a session."""
    
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    citations = Column(JSON, nullable=True)  # List of citation objects
    has_artifact = Column(String(20), nullable=True)  # html, markdown, None
    artifact_id = Column(String(36), ForeignKey("artifacts.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    token_count = Column(Integer, nullable=True)
    
    session = relationship("Session", back_populates="messages")
    artifact = relationship("Artifact", back_populates="message", foreign_keys=[artifact_id])
    
    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "citations": self.citations or [],
            "has_artifact": self.has_artifact,
            "artifact_id": self.artifact_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "token_count": self.token_count,
        }


class Artifact(Base):
    """Generated artifact (HTML/CSS or Markdown) from conversations."""
    
    __tablename__ = "artifacts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    artifact_type = Column(String(20), nullable=False)  # html, markdown
    title = Column(String(255), default="Untitled Artifact")
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    session = relationship("Session", back_populates="artifacts")
    message = relationship("Message", back_populates="artifact", foreign_keys="Message.artifact_id", uselist=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "artifact_type": self.artifact_type,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
