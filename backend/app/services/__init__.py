"""
LLM Provider Services - Unified interface for Ollama, OpenAI, Anthropic, and OpenRouter.
"""

from app.services.ollama_client import OllamaClient
from app.services.openai_client import OpenAIClient
from app.services.anthropic_client import AnthropicClient
from app.services.openrouter_client import OpenRouterClient

__all__ = ["OllamaClient", "OpenAIClient", "AnthropicClient", "OpenRouterClient", "get_llm_client"]


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
