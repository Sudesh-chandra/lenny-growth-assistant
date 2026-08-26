"""
RAG Agent - Grounded conversational Q&A using Lenny's transcripts.
Provides inline citations and gracefully handles insufficient context.
"""

from typing import Dict, Any, Optional, List, AsyncGenerator
from app.core.logging import get_logger
from app.core.config import settings
from app.services.retrieval import RetrievalService

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are the Lenny Growth Assistant, an expert AI helper specialized in product management and growth strategies. Answer using only the provided transcript context.

RULES:
1. ONLY use information from the transcript context.
2. If context is insufficient, state: "I don't have enough information from the available transcripts to answer this question thoroughly."
3. Cite sources with [Source N] notation.
4. Be conversational, precise, and attribute claims to guests.
5. Redirect off-topic questions to your PM/growth expertise."""


class RAGAgent:
    """Grounded Q&A agent with citation support."""
    
    async def execute(
        self,
        message: str,
        session_history: List[Dict[str, str]],
        llm_client,
        model: Optional[str] = None,
        retrieval: Optional[RetrievalService] = None,
    ) -> Dict[str, Any]:
        """Execute RAG-grounded Q&A."""
        
        # Retrieve relevant context
        citations = []
        context = ""
        if retrieval:
            citations = retrieval.search(message)
            context = retrieval.build_context(citations)
        
        # Build messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history (last 6 messages for balanced context/token ratio)
        for msg in session_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Build user message with context
        user_content = message
        if context:
            user_content = f"""Question: {message}

Relevant transcript context:
{context}

Please answer the question using the transcript context above. Include [Source N] citations."""
        else:
            user_content = f"""Question: {message}

Note: No relevant transcript context was found. If you cannot answer from general product/growth knowledge, let the user know that the available transcripts don't cover this topic."""
        
        messages.append({"role": "user", "content": user_content})
        
        # Generate response (1024 tokens sufficient for most Q&A)
        response = await llm_client.complete(messages, model=model, temperature=0.7, max_tokens=settings.max_tokens_qa)
        
        formatted_citations = []
        if retrieval:
            formatted_citations = retrieval.format_citations_for_response(citations)
        
        return {
            "content": response,
            "citations": formatted_citations,
            "has_artifact": None,
            "artifact_data": None,
        }
    
    async def execute_stream(
        self,
        message: str,
        session_history: List[Dict[str, str]],
        llm_client,
        model: Optional[str] = None,
        retrieval: Optional[RetrievalService] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute RAG Q&A with streaming response."""
        
        # Retrieve relevant context
        citations = []
        context = ""
        if retrieval:
            citations = retrieval.search(message)
            context = retrieval.build_context(citations)
        
        # Yield citations first
        if citations:
            formatted_citations = retrieval.format_citations_for_response(citations)
            yield {"type": "citations", "data": formatted_citations}
        
        # Build messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        for msg in session_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        user_content = message
        if context:
            user_content = f"""Question: {message}

Relevant transcript context:
{context}

Please answer the question using the transcript context above. Include [Source N] citations."""
        else:
            user_content = f"""Question: {message}

Note: No relevant transcript context was found. Let the user know if the available transcripts don't cover this topic."""
        
        messages.append({"role": "user", "content": user_content})
        
        # Stream response
        async for token in llm_client.stream(messages, model=model, temperature=0.7):
            yield {"type": "token", "data": token}
        
        yield {"type": "done", "data": ""}
