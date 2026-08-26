"""
OpenAI LLM client - supports GPT-4 and other OpenAI models.
"""

from typing import AsyncGenerator, Optional, List, Dict, Any
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    """Client for OpenAI cloud LLM inference."""
    
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.provider_name = "openai"
        
        if not self.api_key:
            logger.warning("openai_api_key_missing")
    
    async def is_available(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(self.api_key)
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available OpenAI models."""
        return [
            {
                "model_id": "gpt-4-turbo-preview",
                "display_name": "GPT-4 Turbo",
                "provider": "openai",
                "is_local": False,
            },
            {
                "model_id": "gpt-4",
                "display_name": "GPT-4",
                "provider": "openai",
                "is_local": False,
            },
            {
                "model_id": "gpt-3.5-turbo",
                "display_name": "GPT-3.5 Turbo",
                "provider": "openai",
                "is_local": False,
            },
        ]
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Generate a completion from OpenAI."""
        if not self.api_key:
            raise RuntimeError("OpenAI API key not configured. Set OPENAI_API_KEY in your .env file.")
        
        model = model or self.model
        
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("openai_completion_failed", error=str(e), model=model)
            raise RuntimeError(f"OpenAI completion failed: {str(e)}")
    
    async def stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        """Stream a completion from OpenAI token by token."""
        if not self.api_key:
            raise RuntimeError("OpenAI API key not configured. Set OPENAI_API_KEY in your .env file.")
        
        model = model or self.model
        
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error("openai_stream_failed", error=str(e), model=model)
            raise RuntimeError(f"OpenAI stream failed: {str(e)}")
