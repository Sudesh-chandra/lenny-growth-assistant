"""
Tests for the retrieval service and vector store.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRetrievalService:
    """Tests for the retrieval service."""
    
    def test_build_context_empty(self):
        """build_context should return empty string for no citations."""
        from app.services.retrieval import RetrievalService
        service = RetrievalService.__new__(RetrievalService)
        result = service.build_context([])
        assert result == ""
    
    def test_build_context_with_citations(self):
        """build_context should format citations correctly."""
        from app.services.retrieval import RetrievalService
        service = RetrievalService.__new__(RetrievalService)
        
        citations = [
            {
                "source": "Episode 1",
                "guest": "Guest A",
                "text_snippet": "This is relevant content",
            },
            {
                "source": "Episode 2",
                "guest": None,
                "text_snippet": "More relevant content",
            },
        ]
        
        result = service.build_context(citations)
        assert "[Source 1]" in result
        assert "Episode 1" in result
        assert "Guest A" in result
        assert "[Source 2]" in result
        assert "Episode 2" in result
    
    def test_format_citations_for_response(self):
        """format_citations should return clean citation dicts."""
        from app.services.retrieval import RetrievalService
        service = RetrievalService.__new__(RetrievalService)
        
        citations = [
            {
                "source": "Test Episode",
                "guest": "John",
                "text_snippet": "snippet",
                "chunk_id": "abc123",
                "relevance_score": 0.9,
                "extra_field": "should be removed",
            }
        ]
        
        result = service.format_citations_for_response(citations)
        assert len(result) == 1
        assert result[0]["source"] == "Test Episode"
        assert result[0]["guest"] == "John"
        assert "extra_field" not in result[0]


class TestVectorStore:
    """Tests for the vector store."""
    
    @patch("app.services.vector_store.chromadb")
    def test_search_empty_store(self, mock_chroma):
        """Search should return empty list when store is empty."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma.Client.return_value = mock_client
        
        from app.services.vector_store import VectorStore
        store = VectorStore()
        
        results = store.search("test query")
        assert results == []
    
    @patch("app.services.vector_store.chromadb")
    def test_search_with_results(self, mock_chroma):
        """Search should return formatted results."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_collection.query.return_value = {
            "ids": [["chunk1", "chunk2"]],
            "documents": [["Text about growth", "Text about product"]],
            "metadatas": [
                [{"episode": "Ep 1", "guest": "Alice"}, {"episode": "Ep 2", "guest": "Bob"}],
            ],
            "distances": [[0.1, 0.3]],
        }
        
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma.Client.return_value = mock_client
        
        from app.services.vector_store import VectorStore
        store = VectorStore()
        
        results = store.search("growth strategies", top_k=2)
        assert len(results) == 2
        assert results[0]["text"] == "Text about growth"
        assert results[0]["metadata"]["episode"] == "Ep 1"
        assert results[0]["score"] == 0.9  # 1 - 0.1


class TestIngestion:
    """Tests for the transcript ingestion script."""
    
    def test_chunk_text_basic(self):
        """chunk_text should split text into overlapping chunks."""
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
        from scripts.ingest import chunk_text
        
        text = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
        chunks = chunk_text(text, chunk_size=50, overlap=10)
        
        assert len(chunks) >= 1
        for chunk in chunks:
            assert len(chunk) > 0
    
    def test_chunk_text_empty(self):
        """chunk_text should return empty list for empty text."""
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
        from scripts.ingest import chunk_text
        
        chunks = chunk_text("", chunk_size=100, overlap=20)
        assert chunks == []
    
    def test_extract_guest_from_path(self):
        """extract_guest_from_path should parse guest name from file path."""
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
        from scripts.ingest import extract_guest_from_path
        
        # Test with transcripts/<slug>/transcript.md structure
        assert extract_guest_from_path("data/transcripts/sarah-chen-growth/transcript.md") == "Sarah Chen Growth"
        assert extract_guest_from_path("data/transcripts/john-doe/transcript.md") == "John Doe"
        # Test with episodes/<slug>/transcript.md structure
        assert extract_guest_from_path("data/transcripts/episodes/jane-smith/transcript.md") == "Jane Smith"
