"""
Reranking service - uses cross-encoder models to improve retrieval quality.

Reranking is critical for RAG quality:
- Vector search (bi-encoder) is fast but only captures semantic similarity
- Cross-encoder reranking evaluates query-document pairs for actual relevance
- Two-stage approach: retrieve top-20 fast, then rerank to top-5 accurately
- Expected improvement: +25% retrieval precision, +50% citation click-through
"""

from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class Reranker:
    """
    Cross-encoder reranker for improving vector search results.
    
    Uses sentence-transformers cross-encoder model to score (query, document) pairs.
    Falls back to original vector similarity scores if reranking fails.
    """
    
    def __init__(self):
        self.model = None
        self.enabled = getattr(settings, 'rerank_enabled', True)
        self.model_name = getattr(settings, 'rerank_model', 'cross-encoder/ms-marco-MiniLM-L-6-v2')
        self.top_k = getattr(settings, 'rerank_top_k', 5)
        
        if self.enabled:
            logger.info("reranker_initialized", model=self.model_name, enabled=True)
    
    def _load_model(self):
        """Lazy-load the cross-encoder model on first use."""
        if self.model is not None:
            return
        
        try:
            from sentence_transformers import CrossEncoder
            logger.info("loading_reranker_model", model=self.model_name)
            self.model = CrossEncoder(self.model_name)
            logger.info("reranker_model_loaded")
        except Exception as e:
            logger.error("reranker_model_load_failed", error=str(e))
            self.enabled = False  # Disable reranking if model fails to load
    
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents using cross-encoder model.
        
        Args:
            query: The search query
            documents: List of documents from vector search (with 'text' field)
            top_k: Number of top documents to return (default: settings.rerank_top_k)
        
        Returns:
            Reranked list of documents with updated 'score' field
        """
        if not self.enabled or not documents:
            return documents[:top_k or self.top_k]
        
        # Lazy-load model on first use
        self._load_model()
        
        if self.model is None:
            logger.warning("reranker_model_unavailable, falling back to vector scores")
            return documents[:top_k or self.top_k]
        
        k = top_k or self.top_k
        
        try:
            # Prepare (query, document) pairs for cross-encoder
            pairs = [(query, doc['text']) for doc in documents]
            
            # Score all pairs with cross-encoder
            scores = self.model.predict(pairs)
            
            # Add reranker scores to documents
            for i, doc in enumerate(documents):
                doc['rerank_score'] = float(scores[i])
                # Blend original vector score with reranker score (70% reranker, 30% vector)
                # This prevents edge cases where reranker gives low scores to all documents
                original_score = doc.get('score', 0.0)
                doc['score'] = 0.7 * doc['rerank_score'] + 0.3 * original_score
            
            # Sort by blended score (descending)
            documents.sort(key=lambda x: x['score'], reverse=True)
            
            # Return top-k
            reranked = documents[:k]
            
            logger.info("reranking_complete",
                       query=query[:50],
                       candidates=len(documents),
                       returned=len(reranked),
                       top_score=reranked[0]['score'] if reranked else 0.0)
            
            return reranked
        
        except Exception as e:
            logger.error("reranking_failed", error=str(e), fallback="vector_scores")
            # Fall back to original vector similarity scores
            return documents[:k]


# Singleton instance
_reranker: Optional[Reranker] = None


def get_reranker() -> Reranker:
    """Get or create the reranker singleton."""
    global _reranker
    if _reranker is None:
        _reranker = Reranker()
    return _reranker
