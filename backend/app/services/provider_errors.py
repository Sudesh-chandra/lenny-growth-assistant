"""
Provider error handling - structured exceptions for LLM provider failures.
Separated from __init__.py to avoid circular imports.
"""

from enum import Enum


class ProviderErrorCode(str, Enum):
    """Structured error codes for provider failures."""
    NOT_CONFIGURED = "not_configured"       # API key missing
    AUTH_FAILED = "auth_failed"             # Invalid API key (401)
    INSUFFICIENT_CREDITS = "insufficient_credits"  # No credits (402)
    RATE_LIMITED = "rate_limited"           # Rate limited (429)
    SERVICE_UNAVAILABLE = "service_unavailable"  # Service down (503)
    CONNECTION_FAILED = "connection_failed"  # Can't reach service
    UNKNOWN = "unknown"                     # Other errors


class ProviderError(Exception):
    """Structured exception for LLM provider failures."""
    
    def __init__(
        self,
        message: str,
        code: ProviderErrorCode = ProviderErrorCode.UNKNOWN,
        provider: str = "",
        retryable: bool = False,
    ):
        self.code = code
        self.provider = provider
        self.retryable = retryable
        super().__init__(message)
    
    def user_message(self) -> str:
        """Return a user-friendly error message."""
        if self.code == ProviderErrorCode.NOT_CONFIGURED:
            return (
                f"{self.provider.capitalize()} is not configured. "
                f"Please add your API key in Settings or switch to another provider."
            )
        elif self.code == ProviderErrorCode.AUTH_FAILED:
            return (
                f"{self.provider.capitalize()} authentication failed. "
                f"Please check your API key in Settings."
            )
        elif self.code == ProviderErrorCode.INSUFFICIENT_CREDITS:
            return (
                f"{self.provider.capitalize()} has insufficient credits. "
                f"Please add credits or switch to another provider."
            )
        elif self.code == ProviderErrorCode.RATE_LIMITED:
            return (
                f"{self.provider.capitalize()} rate limit reached. "
                f"Please wait a moment and try again."
            )
        elif self.code == ProviderErrorCode.SERVICE_UNAVAILABLE:
            return (
                f"{self.provider.capitalize()} is temporarily unavailable. "
                f"Please try again shortly."
            )
        elif self.code == ProviderErrorCode.CONNECTION_FAILED:
            return (
                f"Cannot connect to {self.provider.capitalize()}. "
                f"Please check your connection and try again."
            )
        else:
            return (
                f"An error occurred with {self.provider.capitalize()}. "
                f"Please try again or switch to another provider."
            )


# Provider priority order for fallback
PROVIDER_PRIORITY = ["openrouter", "anthropic", "openai", "ollama"]
