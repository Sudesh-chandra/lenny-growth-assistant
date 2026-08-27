"""
Agent Router - determines which skill/agent to use based on the user's request.
Includes provider fallback: if the primary provider fails, tries the next available one.
"""

from typing import Dict, Any, Optional, List, AsyncGenerator
from app.core.logging import get_logger
from app.services import get_llm_client
from app.services.provider_errors import ProviderError, ProviderErrorCode, PROVIDER_PRIORITY
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
    
    async def _execute_with_fallback(
        self,
        selected_skill: str,
        message: str,
        session_history: List[Dict[str, str]],
        primary_provider: str,
        model: Optional[str],
        is_stream: bool = False,
    ):
        """
        Execute the agent with automatic provider fallback.
        If the primary provider fails with a retryable error, tries the next available provider.
        """
        # Build fallback order: primary first, then others by priority
        fallback_order = [primary_provider] + [p for p in PROVIDER_PRIORITY if p != primary_provider]
        last_error = None
        
        for provider in fallback_order:
            try:
                llm_client = get_llm_client(provider)
                
                if selected_skill == "ship30":
                    if is_stream:
                        return self.ship30_agent.execute_stream(
                            message=message,
                            session_history=session_history,
                            llm_client=llm_client,
                            model=model,
                            retrieval=self.retrieval,
                        )
                    return await self.ship30_agent.execute(
                        message=message,
                        session_history=session_history,
                        llm_client=llm_client,
                        model=model,
                        retrieval=self.retrieval,
                    )
                elif selected_skill == "artifact":
                    if is_stream:
                        return self.artifact_agent.execute_stream(
                            message=message,
                            session_history=session_history,
                            llm_client=llm_client,
                            model=model,
                        )
                    return await self.artifact_agent.execute(
                        message=message,
                        session_history=session_history,
                        llm_client=llm_client,
                        model=model,
                    )
                else:
                    if is_stream:
                        return self.rag_agent.execute_stream(
                            message=message,
                            session_history=session_history,
                            llm_client=llm_client,
                            model=model,
                            retrieval=self.retrieval,
                        )
                    return await self.rag_agent.execute(
                        message=message,
                        session_history=session_history,
                        llm_client=llm_client,
                        model=model,
                        retrieval=self.retrieval,
                    )
            except ProviderError as e:
                last_error = e
                # Allow fallback for insufficient credits (402) errors
                if not e.retryable and e.code != ProviderErrorCode.INSUFFICIENT_CREDITS:
                    # Non-retryable errors (auth, etc) - don't fallback
                    logger.warning(
                        "provider_non_retryable_error",
                        provider=provider,
                        code=e.code.value,
                    )
                    raise
                logger.warning(
                    "provider_failed_trying_next",
                    provider=provider,
                    code=e.code.value,
                )
                continue
            except Exception as e:
                last_error = e
                logger.warning(
                    "provider_unexpected_error_trying_next",
                    provider=provider,
                    error=str(e),
                )
                continue
        
        # All providers failed
        if isinstance(last_error, ProviderError):
            raise last_error
        raise last_error or RuntimeError("All providers failed")
    
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
        selected_skill = skill or self.detect_skill(message)
        logger.info("routing_request", skill=selected_skill, provider=provider)
        
        try:
            return await self._execute_with_fallback(
                selected_skill=selected_skill,
                message=message,
                session_history=session_history,
                primary_provider=provider,
                model=model,
                is_stream=False,
            )
        except ProviderError as e:
            logger.error("agent_routing_failed", error=e.user_message(), skill=selected_skill, provider=e.provider)
            return {
                "content": e.user_message(),
                "citations": [],
                "has_artifact": None,
                "artifact_data": None,
            }
        except Exception as e:
            logger.error("agent_routing_failed", error=str(e), skill=selected_skill)
            return {
                "content": "I encountered an error processing your request. Please try again. If the issue persists, start a new chat.",
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
        Includes provider fallback for retryable errors.
        
        Yields dicts with: type (token/citations/artifact/done/error), data
        """
        selected_skill = skill or self.detect_skill(message)
        logger.info("routing_stream", skill=selected_skill, provider=provider)
        
        try:
            stream_gen = await self._execute_with_fallback(
                selected_skill=selected_skill,
                message=message,
                session_history=session_history,
                primary_provider=provider,
                model=model,
                is_stream=True,
            )
            async for chunk in stream_gen:
                yield chunk
        except ProviderError as e:
            logger.error("stream_routing_failed", error=e.user_message(), skill=selected_skill, provider=e.provider)
            yield {
                "type": "error",
                "data": e.user_message(),
            }
        except Exception as e:
            logger.error("stream_routing_failed", error=str(e), skill=selected_skill)
            yield {
                "type": "error",
                "data": "An internal error occurred. Please try again or start a new chat.",
            }
