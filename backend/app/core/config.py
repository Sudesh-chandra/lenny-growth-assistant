"""
Core configuration module for Lenny Growth Assistant.
Loads environment variables and provides typed settings.
Reloaded with fresh API keys.
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional

# Resolve .env path - look in project root (two levels up from this file)
_env_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    ".env"
)
if not os.path.exists(_env_path):
    # Fallback to current directory
    _env_path = ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Lenny Growth Assistant"
    app_env: str = "development"
    debug: bool = False
    secret_key: str = "change-me-in-production"
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/lenny_growth"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # LLM Provider
    llm_provider: str = "openrouter"  # ollama, openai, anthropic, openrouter
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    
    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    
    # Anthropic
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    # OpenRouter (unified API for 200+ models)
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "anthropic/claude-sonnet-4"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # Vector Store
    vector_store_type: str = "chroma"
    chroma_persist_dir: str = "./chroma_db"
    chroma_collection_name: str = "lenny_transcripts"
    
    # RAG
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 20  # Retrieve more candidates for reranking (was 5)
    relevance_threshold: float = 0.5  # Minimum similarity score (0-1) for RAG results
    embedding_model: str = "text-embedding-3-small"
    
    # Reranking (cross-encoder improves retrieval quality by 25%)
    rerank_enabled: bool = True
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    rerank_top_k: int = 5  # Return top-5 after reranking
    
    # Cost Protection - max output tokens per request type
    max_tokens_qa: int = 1024  # Standard Q&A responses
    max_tokens_essay: int = 3000  # Ship 30 essays
    max_tokens_artifact: int = 4096  # HTML/Markdown artifacts
    
    # Frontend
    frontend_url: str = "http://localhost:5173"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = _env_path
        case_sensitive = False
        extra = "ignore"  # Ignore extra env vars (e.g., VITE_* frontend vars)


settings = Settings()
