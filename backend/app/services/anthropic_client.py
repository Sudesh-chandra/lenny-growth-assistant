"""
Anthropic LLM client - supports Claude models.
"""

from typing import AsyncGenerator, Optional, List, Dict, Any
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AnthropicClient:
    """Client for Anthropic Claude cloud LLM inference."""
    
    def __init__(self):
        self.api_key = settings.anthropic_api_key
        self.model = settings.anthropic_model
        self.provider_name = "anthropic"
        
        if not self.api_key:
            logger.warning("anthropic_api_key_missing")
    
    async def is_available(self) -> bool:
        """Check if Anthropic API key is configured."""
        return bool(self.api_key)
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available Anthropic models."""
        return [
            {
                "model_id": "claude-3-sonnet-20240229",
                "display_name": "Claude 3 Sonnet",
                "provider": "anthropic",
                "is_local": False,
            },
            {
                "model_id": "claude-3-haiku-20240307",
                "display_name": "Claude 3 Haiku",
                "provider": "anthropic",
                "is_local": False,
            },
            {
                "model_id": "claude-3-opus-20240229",
                "display_name": "Claude 3 Opus",
                "provider": "anthropic",
                "is_local": False,
            },
        ]
    
    def _convert_messages(self, messages: List[Dict[str, str]]) -> tuple:
        """Convert OpenAI-style messages to Anthropic format."""
        system_msg = ""
        anthropic_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            elif msg["role"] == "user":
                anthropic_messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                anthropic_messages.append({"role": "assistant", "content": msg["content"]})
        
        return system_msg, anthropic_messages
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Generate a completion from Anthropic."""
        if not self.api_key:
            raise RuntimeError("Anthropic API key not configured")
        
        model = model or self.model
        system_msg, anthropic_messages = self._convert_messages(messages)
        
        try:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=self.api_key)
            
            kwargs = {
                "model": model,
                "messages": anthropic_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            if system_msg:
                kwargs["system"] = system_msg
            
            response = await client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            logger.error("anthropic_completion_failed", error=str(e), model=model)
            raise RuntimeError(f"Anthropic completion failed: {str(e)}")
    
    async def stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        """Stream a completion from Anthropic token by token."""
        if not self.api_key:
            raise RuntimeError("Anthropic API key not configured")
        
        model = model or self.model
        system_msg, anthropic_messages = self._convert_messages(messages)
        
        try:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=self.api_key)
            
            kwargs = {
                "model": model,
                "messages": anthropic_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            if system_msg:
                kwargs["system"] = system_msg
            
            async with client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error("anthropic_stream_failed", error=str(e), model=model)
            raise RuntimeError(f"Anthropic stream failed: {str(e)}")
