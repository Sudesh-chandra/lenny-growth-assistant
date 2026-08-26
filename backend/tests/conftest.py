"""
Pytest configuration and shared fixtures.
Pre-mocks heavy dependencies (chromadb, sentence_transformers) so tests
can run without installing them.
"""

import pytest
import sys
import os
import types
from unittest.mock import MagicMock

# Add backend root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# Pre-mock heavy native dependencies BEFORE any app module is imported.
# This allows the test suite to run with only pip install pytest pytest-asyncio
# (no chromadb, sentence-transformers, etc. required).
# ---------------------------------------------------------------------------


def _install_mock_module(name: str):
    """Install a MagicMock module, including in submodules."""
    mock = MagicMock()
    mock.__path__ = []  # Make it look like a package
    sys.modules[name] = mock
    return mock


# Mock chromadb and its submodules
_chroma_mock = _install_mock_module("chromadb")
_install_mock_module("chromadb.config")
_install_mock_module("chromadb.api")
_install_mock_module("chromadb.api.types")

# Mock sentence_transformers
_install_mock_module("sentence_transformers")

# Mock tiktoken
_install_mock_module("tiktoken")

# Mock structlog if not available
try:
    import structlog  # noqa: F401
except ImportError:
    _sl = _install_mock_module("structlog")
    _sl.get_logger.return_value = MagicMock()
    _sl.make_filtering_bound_logger.return_value = MagicMock()
    _sl.configure = MagicMock()
    _sl.contextvars = MagicMock()
    _sl.processors = MagicMock()
    _sl.dev = MagicMock()
    _sl.PrintLoggerFactory = MagicMock()
    _sl.wrapper_class = MagicMock()
