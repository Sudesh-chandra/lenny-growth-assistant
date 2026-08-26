"""
OpenRouter LLM client - provides access to 200+ models via a unified OpenAI-compatible API.
Supports Claude, GPT-4, Llama, Mistral, and many more through a single endpoint.
"""

from typing import AsyncGenerator, Optional, List, Dict, Any
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenRouterClient:
    """Client for OpenRouter unified LLM API (OpenAI-compatible)."""
    
    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        self.base_url = settings.openrouter_base_url
        self.provider_name = "openrouter"
        
        if not self.api_key:
            logger.warning("openrouter_api_key_missing")
    
    async def is_available(self) -> bool:
        """Check if OpenRouter API key is configured."""
        return bool(self.api_key)
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get curated list of popular models available via OpenRouter."""
        return [
            {
                "model_id": "anthropic/claude-sonnet-4",
                "display_name": "Claude Sonnet 4",
                "provider": "openrouter",
                "is_local": False,
            },
            {
                "model_id": "anthropic/claude-3.5-sonnet",
                "display_name": "Claude 3.5 Sonnet",
                "provider": "openrouter",
                "is_local": False,
            },
            {
                "model_id": "openai/gpt-4o",
                "display_name": "GPT-4o",
                "provider": "openrouter",
                "is_local": False,
            },
            {
                "model_id": "openai/gpt-4o-mini",
                "display_name": "GPT-4o Mini",
                "provider": "openrouter",
                "is_local": False,
            },
            {
                "model_id": "google/gemini-2.0-flash-001",
                "display_name": "Gemini 2.0 Flash",
                "provider": "openrouter",
                "is_local": False,
            },
            {
                "model_id": "meta-llama/llama-3.1-70b-instruct",
                "display_name": "Llama 3.1 70B",
                "provider": "openrouter",
                "is_local": False,
            },
            {
                "model_id": "deepseek/deepseek-chat",
                "display_name": "DeepSeek Chat",
                "provider": "openrouter",
                "is_local": False,
            },
        ]
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers for OpenRouter API."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "Lenny Growth Assistant",
        }
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Generate a completion via OpenRouter."""
        if not self.api_key:
            raise RuntimeError("OpenRouter API key not configured")
        
        model = model or self.model
        
        try:
            import httpx
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            logger.error("openrouter_http_error", status=e.response.status_code, body=e.response.text[:200])
            raise RuntimeError(f"OpenRouter API error ({e.response.status_code}): {e.response.text[:200]}")
        except Exception as e:
            logger.error("openrouter_completion_failed", error=str(e), model=model)
            raise RuntimeError(f"OpenRouter completion failed: {str(e)}")
    
    async def stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        """Stream a completion via OpenRouter token by token."""
        if not self.api_key:
            raise RuntimeError("OpenRouter API key not configured")
        
        model = model or self.model
        
        try:
            import httpx
            import json
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": True,
                    },
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        
                        data_str = line[6:]  # Remove "data: " prefix
                        if data_str.strip() == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            choices = data.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
        except httpx.HTTPStatusError as e:
            logger.error("openrouter_stream_http_error", status=e.response.status_code)
            raise RuntimeError(f"OpenRouter stream error ({e.response.status_code})")
        except Exception as e:
            logger.error("openrouter_stream_failed", error=str(e), model=model)
            raise RuntimeError(f"OpenRouter stream failed: {str(e)}")
