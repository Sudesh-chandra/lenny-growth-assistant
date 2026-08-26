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
from app.services.retrieval import RetrievalService

logger = get_logger(__name__)

SHIP30_SYSTEM_PROMPT = """You are an expert content writer who follows the Ship 30 for 30 writing methodology. Your task is to transform grounded knowledge from Lenny's Podcast transcripts into compelling, well-structured essays.

## Ship 30 for 30 Writing Principles:

1. **THE HOOK** (First 1-2 sentences): Start with a bold, attention-grabbing statement. Use a counterintuitive insight, a specific number, or a provocative question. Make the reader NEED to continue.

2. **THE BODY STRUCTURE**:
   - Use clear, skimmable subheadings (## level)
   - Keep paragraphs short (2-3 sentences max)
   - Use bullet points for lists and key takeaways
   - **Bold** the most important phrases so skimmers get value
   - Include specific examples and numbers where possible

3. **NARRATIVE PROGRESSION**: Each section should flow naturally to the next. Use transitions. Build from problem → insight → action.

4. **GROUNDING**: All claims must be backed by the transcript context. Cite sources using [Source N] markers.

5. **THE TAKEAWAY**: End with a specific, actionable conclusion. Not generic advice — something the reader can implement today.

6. **LENGTH**: Target approximately 1,250 words. Be comprehensive but not bloated.

7. **TONE**: Conversational but authoritative. Write like a smart friend sharing hard-won insights.

Format the output as clean Markdown."""


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
        
        # Retrieve relevant context
        citations = []
        context = ""
        if retrieval:
            citations = retrieval.search(message, top_k=8)
            context = retrieval.build_context(citations)
        
        messages = [{"role": "system", "content": SHIP30_SYSTEM_PROMPT}]
        
        # Add relevant history
        for msg in session_history[-5:]:
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
            messages, model=model, temperature=0.8, max_tokens=3000
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
            citations = retrieval.search(message, top_k=8)
            context = retrieval.build_context(citations)
        
        if citations:
            formatted_citations = retrieval.format_citations_for_response(citations)
            yield {"type": "citations", "data": formatted_citations}
        
        messages = [{"role": "system", "content": SHIP30_SYSTEM_PROMPT}]
        
        for msg in session_history[-5:]:
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
