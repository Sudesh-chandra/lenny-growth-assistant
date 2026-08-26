"""
Agent Router - determines which skill/agent to use based on the user's request.
"""

from typing import Dict, Any, Optional, List, AsyncGenerator
from app.core.logging import get_logger
from app.services import get_llm_client
from app.services.retrieval import get_retrieval_service
from app.agents.rag_agent import RAGAgent
from app.agents.ship30_agent import Ship30Agent
from app.agents.artifact_agent import ArtifactAgent

logger = get_logger(__name__)


class AgentRouter:
    """
    Routes user requests to the appropriate agent skill:
    - 'rag': Grounded Q&A using Lenny's transcripts (default)
    - 'ship30': Ship 30 for 30 content generation
    - 'artifact': HTML/CSS or Markdown artifact generation
    """
    
    def __init__(self):
        self.retrieval = get_retrieval_service()
        self.rag_agent = RAGAgent()
        self.ship30_agent = Ship30Agent()
        self.artifact_agent = ArtifactAgent()
    
    def detect_skill(self, message: str) -> str:
        """
        Detect which skill to use based on the user's message.
        
        Returns: 'rag', 'ship30', or 'artifact'
        """
        message_lower = message.lower()
        
        # Artifact detection - user wants HTML/CSS or visual components
        artifact_keywords = [
            "create a component", "build a landing page", "generate html",
            "create an artifact", "make a widget", "build a dashboard",
            "create a form", "design a card", "generate css",
            "create a chart", "build a table", "make a ui",
            "artifact", "render this", "create a visual",
            "dashboard component", "pricing dashboard", "create a dashboard",
            "landing page", "signup form", "widget",
        ]
        if any(kw in message_lower for kw in artifact_keywords):
            return "artifact"
        
        # Ship 30 for 30 detection - user wants essay/content writing
        ship30_keywords = [
            "write an essay", "write a post", "ship 30", "content skill",
            "write about", "create content", "blog post", "writeup",
            "write a guide", "draft a post", "write an article",
        ]
        if any(kw in message_lower for kw in ship30_keywords):
            return "ship30"
        
        # Default to RAG grounded Q&A
        return "rag"
    
    async def route(
        self,
        message: str,
        session_history: List[Dict[str, str]],
        provider: str = "openrouter",
        model: Optional[str] = None,
        skill: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Route the request to the appropriate agent and return the response.
        
        Returns dict with: content, citations, has_artifact, artifact_data
        """
        # Determine which skill to use
        selected_skill = skill or self.detect_skill(message)
        logger.info("routing_request", skill=selected_skill, provider=provider)
        
        llm_client = get_llm_client(provider)
        
        try:
            if selected_skill == "ship30":
                return await self.ship30_agent.execute(
                    message=message,
                    session_history=session_history,
                    llm_client=llm_client,
                    model=model,
                    retrieval=self.retrieval,
                )
            elif selected_skill == "artifact":
                return await self.artifact_agent.execute(
                    message=message,
                    session_history=session_history,
                    llm_client=llm_client,
                    model=model,
                )
            else:
                return await self.rag_agent.execute(
                    message=message,
                    session_history=session_history,
                    llm_client=llm_client,
                    model=model,
                    retrieval=self.retrieval,
                )
        except Exception as e:
            logger.error("agent_routing_failed", error=str(e), skill=selected_skill)
            return {
                "content": f"I encountered an error processing your request. Please try again.\n\nError: {str(e)}",
                "citations": [],
                "has_artifact": None,
                "artifact_data": None,
            }
    
    async def route_stream(
        self,
        message: str,
        session_history: List[Dict[str, str]],
        provider: str = "openrouter",
        model: Optional[str] = None,
        skill: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Route the request and stream the response token by token.
        
        Yields dicts with: type (token/citations/artifact/done), data
        """
        selected_skill = skill or self.detect_skill(message)
        logger.info("routing_stream", skill=selected_skill, provider=provider)
        
        llm_client = get_llm_client(provider)
        
        try:
            if selected_skill == "ship30":
                async for chunk in self.ship30_agent.execute_stream(
                    message=message,
                    session_history=session_history,
                    llm_client=llm_client,
                    model=model,
                    retrieval=self.retrieval,
                ):
                    yield chunk
            elif selected_skill == "artifact":
                async for chunk in self.artifact_agent.execute_stream(
                    message=message,
                    session_history=session_history,
                    llm_client=llm_client,
                    model=model,
                ):
                    yield chunk
            else:
                async for chunk in self.rag_agent.execute_stream(
                    message=message,
                    session_history=session_history,
                    llm_client=llm_client,
                    model=model,
                    retrieval=self.retrieval,
                ):
                    yield chunk
        except Exception as e:
            logger.error("stream_routing_failed", error=str(e), skill=selected_skill)
            yield {
                "type": "error",
                "data": f"Error: {str(e)}",
            }
