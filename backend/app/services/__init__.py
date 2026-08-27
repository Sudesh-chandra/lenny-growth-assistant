"""
LLM Provider Services - Unified interface for Ollama, OpenAI, Anthropic, and OpenRouter.
"""

from app.services.ollama_client import OllamaClient
from app.services.openai_client import OpenAIClient
from app.services.anthropic_client import AnthropicClient
from app.services.openrouter_client import OpenRouterClient
from app.services.provider_errors import ProviderError, ProviderErrorCode, PROVIDER_PRIORITY

__all__ = [
    "OllamaClient", "OpenAIClient", "AnthropicClient", "OpenRouterClient",
    "get_llm_client", "ProviderError", "ProviderErrorCode", "PROVIDER_PRIORITY",
    "get_available_providers",
]


def get_llm_client(provider: str = "openrouter"):
    """Factory function to get the appropriate LLM client."""
    clients = {
        "ollama": OllamaClient,
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
        "openrouter": OpenRouterClient,
    }
    client_class = clients.get(provider, OpenRouterClient)
    return client_class()


async def get_available_providers() -> list:
    """Check which providers are currently available."""
    available = []
    for provider_name in PROVIDER_PRIORITY:
        client = get_llm_client(provider_name)
        if await client.is_available():
            available.append(provider_name)
    return available
