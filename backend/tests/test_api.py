"""
Tests for API endpoints - health, sessions, models.
"""

import pytest
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_db():
    """Mock database session."""
    db = AsyncMock()
    return db


@pytest.fixture
def mock_vector_store():
    """Mock vector store."""
    with patch("app.services.vector_store.get_vector_store") as mock:
        store = MagicMock()
        store.get_count.return_value = 100
        store.search.return_value = []
        mock.return_value = store
        yield store


class TestHealthEndpoint:
    """Tests for the /health endpoint."""
    
    def test_health_response_structure(self):
        """Health endpoint should return expected fields."""
        from app.schemas import HealthResponse
        response = HealthResponse(
            status="healthy",
            version="1.0.0",
            database="connected",
            llm_provider="ollama",
            vector_store="connected (100 chunks)",
        )
        assert response.status == "healthy"
        assert response.version == "1.0.0"
        assert response.llm_provider == "ollama"


class TestSessionSchemas:
    """Tests for session-related schemas."""
    
    def test_session_create_defaults(self):
        """SessionCreate should have sensible defaults."""
        from app.schemas import SessionCreate
        session = SessionCreate()
        assert session.title == "New Chat"
        assert session.llm_provider.value == "openrouter"
    
    def test_session_create_custom(self):
        """SessionCreate should accept custom values."""
        from app.schemas import SessionCreate, LLMProvider
        session = SessionCreate(
            title="Test Session",
            llm_provider=LLMProvider.OPENAI,
            model_name="gpt-4",
        )
        assert session.title == "Test Session"
        assert session.llm_provider.value == "openai"
        assert session.model_name == "gpt-4"


class TestChatSchemas:
    """Tests for chat-related schemas."""
    
    def test_chat_request_validation(self):
        """ChatRequest should validate message length."""
        from app.schemas import ChatRequest
        
        # Valid request
        req = ChatRequest(message="Hello")
        assert req.message == "Hello"
        
        # Empty message should fail
        with pytest.raises(Exception):
            ChatRequest(message="")
    
    def test_chat_request_with_skill(self):
        """ChatRequest should accept skill parameter."""
        from app.schemas import ChatRequest
        req = ChatRequest(message="Write an essay", skill="ship30")
        assert req.skill == "ship30"


class TestCitationSchema:
    """Tests for citation schema."""
    
    def test_citation_creation(self):
        """Citation should store source information."""
        from app.schemas import Citation
        citation = Citation(
            source="Test Episode",
            guest="John Doe",
            text_snippet="This is a test snippet",
            relevance_score=0.95,
        )
        assert citation.source == "Test Episode"
        assert citation.guest == "John Doe"
        assert citation.relevance_score == 0.95


class TestModelSchemas:
    """Tests for model info schemas."""
    
    def test_model_info(self):
        """ModelInfo should capture model metadata."""
        from app.schemas import ModelInfo
        model = ModelInfo(
            provider="ollama",
            model_id="llama3",
            display_name="Llama 3",
            is_local=True,
            is_available=True,
        )
        assert model.provider == "ollama"
        assert model.is_local is True
        assert model.is_available is True
