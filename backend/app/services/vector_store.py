"""
Vector store service using ChromaDB for transcript embeddings and retrieval.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional, Tuple
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class VectorStore:
    """ChromaDB-based vector store for transcript chunks."""
    
    def __init__(self):
        self.client = chromadb.Client(ChromaSettings(
            persist_directory=settings.chroma_persist_dir,
            anonymized_telemetry=False,
        ))
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("vector_store_initialized", 
                     collection=settings.chroma_collection_name,
                     count=self.collection.count())
    
    def add_chunks(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        embeddings: Optional[List[List[float]]] = None,
    ):
        """Add document chunks to the vector store."""
        # ChromaDB has a batch limit, process in chunks of 100
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            batch_end = min(i + batch_size, len(ids))
            self.collection.add(
                ids=ids[i:batch_end],
                documents=documents[i:batch_end],
                metadatas=metadatas[i:batch_end],
                embeddings=embeddings[i:batch_end] if embeddings else None,
            )
        logger.info("chunks_added", count=len(ids))
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for relevant chunks using the query."""
        kwargs = {
            "query_texts": [query],
            "n_results": min(top_k, self.collection.count() or 1),
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where
        
        if self.collection.count() == 0:
            logger.warning("vector_store_empty")
            return []
        
        results = self.collection.query(**kwargs)
        
        chunks = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0.0
                chunk_id = results["ids"][0][i] if results["ids"] else f"chunk_{i}"
                
                chunks.append({
                    "id": chunk_id,
                    "text": doc,
                    "metadata": metadata,
                    "score": 1.0 - distance,  # Convert cosine distance to similarity
                })
        
        return chunks
    
    def get_count(self) -> int:
        """Get total number of chunks in the store."""
        return self.collection.count()
    
    def delete_collection(self):
        """Delete and recreate the collection."""
        self.client.delete_collection(settings.chroma_collection_name)
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("collection_reset")


# Singleton instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get or create the vector store singleton."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
