"""
Ship 30 for 30 Agent - Generates ~1,250-word essays following Ship 30 for 30 principles.

Ship 30 for 30 writing principles:
- Strong hook that grabs attention
- Skimmable formatting with subheadings
- Bullet points for key ideas
- Selective bolding for emphasis
- Clear narrative progression
- Specific, actionable takeaways
- Grounded in real knowledge/experience
"""

from typing import Dict, Any, Optional, List, AsyncGenerator
from app.core.logging import get_logger
from app.core.config import settings
from app.services.retrieval import RetrievalService

logger = get_logger(__name__)

SHIP30_SYSTEM_PROMPT = """You write Ship 30 for 30 essays: compelling, well-structured content grounded in Lenny's Podcast transcripts.

PRINCIPLES:
1. HOOK: Bold opening (counterintuitive insight, number, or provocative question).
2. BODY: Skimmable subheadings (##), short paragraphs (2-3 sentences), bullet points, **bold** key phrases.
3. NARRATIVE: Problem -> insight -> action flow with transitions.
4. GROUNDING: Back claims with transcript context. Use [Source N] citations.
5. TAKEAWAY: Specific, actionable conclusion.
6. LENGTH: ~1,250 words. Comprehensive but not bloated.
7. TONE: Conversational, authoritative.

Output as clean Markdown."""


class Ship30Agent:
    """Ship 30 for 30 content generation agent."""
    
    async def execute(
        self,
        message: str,
        session_history: List[Dict[str, str]],
        llm_client,
        model: Optional[str] = None,
        retrieval: Optional[RetrievalService] = None,
    ) -> Dict[str, Any]:
        """Generate a Ship 30 for 30 essay."""
        
        # Retrieve relevant context (top 5 for token efficiency)
        citations = []
        context = ""
        if retrieval:
            citations = retrieval.search(message, top_k=5)
            context = retrieval.build_context(citations)
        
        messages = [{"role": "system", "content": SHIP30_SYSTEM_PROMPT}]
        
        # Add relevant history (last 6 messages)
        for msg in session_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        user_content = f"""Write a Ship 30 for 30-style essay about the following topic.

Topic/Question: {message}

{"Transcript context to ground your essay:" + chr(10) + context if context else "Use general product/growth knowledge since no specific transcript context was found."}

Remember:
- Start with a compelling hook
- Use subheadings, bullets, and bold text
- Target ~1,250 words
- Include [Source N] citations where applicable
- End with a specific, actionable takeaway"""
        
        messages.append({"role": "user", "content": user_content})
        
        response = await llm_client.complete(
            messages, model=model, temperature=0.8, max_tokens=settings.max_tokens_essay
        )
        
        formatted_citations = []
        if retrieval:
            formatted_citations = retrieval.format_citations_for_response(citations)
        
        return {
            "content": response,
            "citations": formatted_citations,
            "has_artifact": "markdown",
            "artifact_data": {
                "type": "markdown",
                "title": f"Essay: {message[:60]}",
                "content": response,
            },
        }
    
    async def execute_stream(
        self,
        message: str,
        session_history: List[Dict[str, str]],
        llm_client,
        model: Optional[str] = None,
        retrieval: Optional[RetrievalService] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate Ship 30 essay with streaming."""
        
        citations = []
        context = ""
        if retrieval:
            citations = retrieval.search(message, top_k=5)
            context = retrieval.build_context(citations)
        
        if citations:
            formatted_citations = retrieval.format_citations_for_response(citations)
            yield {"type": "citations", "data": formatted_citations}
        
        messages = [{"role": "system", "content": SHIP30_SYSTEM_PROMPT}]
        
        for msg in session_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        user_content = f"""Write a Ship 30 for 30-style essay about the following topic.

Topic/Question: {message}

{"Transcript context:" + chr(10) + context if context else "Use general product/growth knowledge."}

Remember: compelling hook, subheadings, bullets, bold text, ~1,250 words, [Source N] citations, actionable takeaway."""
        
        messages.append({"role": "user", "content": user_content})
        
        full_content = []
        async for token in llm_client.stream(messages, model=model, temperature=0.8):
            full_content.append(token)
            yield {"type": "token", "data": token}
        
        # Signal artifact creation
        yield {
            "type": "artifact",
            "data": {
                "artifact_type": "markdown",
                "title": f"Essay: {message[:60]}",
                "content": "".join(full_content),
            },
        }
        yield {"type": "done", "data": ""}
