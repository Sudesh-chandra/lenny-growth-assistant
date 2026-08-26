"""
Logging configuration using structlog for structured, JSON-formatted logs.
"""

import structlog
import logging
from app.core.config import settings


def setup_logging():
    """Configure structured logging for the application."""
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.log_level),
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
            if settings.app_env == "development"
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__):
    """Get a structured logger instance."""
    return structlog.get_logger(name)
