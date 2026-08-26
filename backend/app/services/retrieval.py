"""
Retrieval service - handles RAG search with citation generation.
"""

from typing import List, Dict, Any, Optional
from app.services.vector_store import get_vector_store
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RetrievalService:
    """Service for retrieving relevant transcript chunks with citations."""
    
    def __init__(self):
        self.vector_store = get_vector_store()
        self.top_k = settings.top_k_results
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        episode_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant transcript chunks.
        
        Returns list of chunks with citation metadata.
        """
        k = top_k or self.top_k
        
        where_filter = None
        if episode_filter:
            where_filter = {"episode": episode_filter}
        
        results = self.vector_store.search(
            query=query,
            top_k=k,
            where=where_filter,
        )
        
        # Format results with citation information
        citations = []
        for chunk in results:
            metadata = chunk.get("metadata", {})
            citation = {
                "source": metadata.get("episode", "Unknown Episode"),
                "guest": metadata.get("guest", None),
                "text_snippet": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
                "chunk_id": chunk["id"],
                "relevance_score": round(chunk["score"], 4),
                "timestamp": metadata.get("timestamp", None),
            }
            citations.append(citation)
        
        logger.info("retrieval_complete", 
                     query=query[:50], 
                     results_found=len(citations))
        
        return citations
    
    def build_context(self, citations: List[Dict[str, Any]]) -> str:
        """Build a context string from citations for LLM prompting."""
        if not citations:
            return ""
        
        context_parts = []
        for i, c in enumerate(citations, 1):
            source = c.get("source", "Unknown")
            guest = c.get("guest", "")
            text = c.get("text_snippet", "")
            
            header = f"[Source {i}]: {source}"
            if guest:
                header += f" (Guest: {guest})"
            
            context_parts.append(f"{header}\n{text}\n")
        
        return "\n---\n".join(context_parts)
    
    def format_citations_for_response(self, citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format citations for inclusion in API response."""
        return [
            {
                "source": c["source"],
                "guest": c.get("guest"),
                "text_snippet": c.get("text_snippet", ""),
                "chunk_id": c.get("chunk_id"),
                "relevance_score": c.get("relevance_score"),
            }
            for c in citations
        ]


# Singleton
_retrieval_service: Optional[RetrievalService] = None


def get_retrieval_service() -> RetrievalService:
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
    return _retrieval_service
