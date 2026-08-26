"""
Models router - provides information about available LLM models.
"""

from fastapi import APIRouter
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas import ModelInfo, ModelsResponse
from app.services import get_llm_client

logger = get_logger(__name__)
router = APIRouter()


@router.get("/models", response_model=ModelsResponse)
async def list_models():
    """
    Get all available models across providers.
    Checks availability of each provider.
    """
    all_models = []
    
    # Check Ollama models
    try:
        ollama = get_llm_client("ollama")
        if await ollama.is_available():
            ollama_models = await ollama.get_available_models()
            for m in ollama_models:
                all_models.append(ModelInfo(
                    provider="ollama",
                    model_id=m["model_id"],
                    display_name=m["display_name"],
                    is_local=True,
                    is_available=True,
                ))
        else:
            # Add default Ollama model as unavailable
            all_models.append(ModelInfo(
                provider="ollama",
                model_id=settings.ollama_model,
                display_name=f"{settings.ollama_model} (Ollama offline)",
                is_local=True,
                is_available=False,
            ))
    except Exception as e:
        logger.warning("ollama_check_failed", error=str(e))
        all_models.append(ModelInfo(
            provider="ollama",
            model_id=settings.ollama_model,
            display_name=f"{settings.ollama_model} (Ollama offline)",
            is_local=True,
            is_available=False,
        ))
    
    # Add OpenAI models
    try:
        openai_client = get_llm_client("openai")
        is_available = await openai_client.is_available()
        openai_models = await openai_client.get_available_models()
        for m in openai_models:
            all_models.append(ModelInfo(
                provider="openai",
                model_id=m["model_id"],
                display_name=m["display_name"],
                is_local=False,
                is_available=is_available,
            ))
    except Exception as e:
        logger.warning("openai_check_failed", error=str(e))
    
    # Add Anthropic models
    try:
        anthropic_client = get_llm_client("anthropic")
        is_available = await anthropic_client.is_available()
        anthropic_models = await anthropic_client.get_available_models()
        for m in anthropic_models:
            all_models.append(ModelInfo(
                provider="anthropic",
                model_id=m["model_id"],
                display_name=m["display_name"],
                is_local=False,
                is_available=is_available,
            ))
    except Exception as e:
        logger.warning("anthropic_check_failed", error=str(e))
    
    # Add OpenRouter models
    try:
        openrouter_client = get_llm_client("openrouter")
        is_available = await openrouter_client.is_available()
        openrouter_models = await openrouter_client.get_available_models()
        for m in openrouter_models:
            all_models.append(ModelInfo(
                provider="openrouter",
                model_id=m["model_id"],
                display_name=m["display_name"],
                is_local=False,
                is_available=is_available,
            ))
    except Exception as e:
        logger.warning("openrouter_check_failed", error=str(e))
    
    # Determine active model
    active_model_map = {
        "ollama": settings.ollama_model,
        "openai": settings.openai_model,
        "anthropic": settings.anthropic_model,
        "openrouter": settings.openrouter_model,
    }
    active_model = active_model_map.get(settings.llm_provider, settings.openrouter_model)
    
    return ModelsResponse(
        models=all_models,
        active_provider=settings.llm_provider,
        active_model=active_model,
    )
