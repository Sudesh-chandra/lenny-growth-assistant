"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class LLMProvider(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"


class ArtifactType(str, Enum):
    HTML = "html"
    MARKDOWN = "markdown"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# ============================================================================
# Citation Schema
# ============================================================================

class Citation(BaseModel):
    """Source citation for grounded answers."""
    source: str = Field(..., description="Episode or transcript name")
    guest: Optional[str] = Field(None, description="Guest name if applicable")
    text_snippet: Optional[str] = Field(None, description="Relevant text snippet")
    chunk_id: Optional[str] = Field(None, description="ID of the source chunk")
    relevance_score: Optional[float] = Field(None, description="Retrieval relevance score")


# ============================================================================
# Session Schemas
# ============================================================================

class SessionCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    title: Optional[str] = "New Chat"
    llm_provider: Optional[LLMProvider] = LLMProvider.OPENROUTER
    model_name: Optional[str] = "anthropic/claude-sonnet-4"


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    id: str
    title: str
    created_at: Optional[str]
    updated_at: Optional[str]
    llm_provider: str
    model_name: str


# ============================================================================
# Message Schemas
# ============================================================================

class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    model_config = ConfigDict(protected_namespaces=())
    session_id: Optional[str] = Field(None, description="Existing session ID, or None for new session")
    message: str = Field(..., min_length=1, max_length=10000)
    llm_provider: Optional[LLMProvider] = None
    model_name: Optional[str] = None
    skill: Optional[str] = Field(None, description="Skill to use: 'rag', 'ship30', 'artifact'")


class ChatResponse(BaseModel):
    """Response from chat endpoint (non-streaming)."""
    session_id: str
    message_id: str
    content: str
    citations: List[Citation] = []
    has_artifact: Optional[str] = None
    artifact_id: Optional[str] = None
    artifact_title: Optional[str] = None


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    id: str
    session_id: str
    role: str
    content: str
    citations: List[Dict[str, Any]] = []
    has_artifact: Optional[str] = None
    artifact_id: Optional[str] = None
    created_at: Optional[str]
    token_count: Optional[int]


# ============================================================================
# Artifact Schemas
# ============================================================================

class ArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    session_id: str
    artifact_type: str
    title: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str]


# ============================================================================
# Model Info Schemas
# ============================================================================

class ModelInfo(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    provider: str
    model_id: str
    display_name: str
    is_local: bool
    is_available: bool


class ModelsResponse(BaseModel):
    models: List[ModelInfo]
    active_provider: str
    active_model: str


# ============================================================================
# Health Schema
# ============================================================================

class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    llm_provider: str
    vector_store: str
