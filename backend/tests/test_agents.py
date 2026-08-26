"""
Tests for agent routing and skill detection.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAgentRouter:
    """Tests for the agent router skill detection."""
    
    def _get_router(self):
        """Create router without initialization."""
        from app.agents.router import AgentRouter
        router = AgentRouter.__new__(AgentRouter)
        return router
    
    def test_detect_rag_default(self):
        """Default routing should be RAG for general questions."""
        router = self._get_router()
        assert router.detect_skill("What is product-led growth?") == "rag"
        assert router.detect_skill("How do I improve retention?") == "rag"
        assert router.detect_skill("Tell me about activation metrics") == "rag"
    
    def test_detect_ship30(self):
        """Ship 30 should be detected for writing requests."""
        router = self._get_router()
        assert router.detect_skill("Write an essay about growth loops") == "ship30"
        assert router.detect_skill("Write a post about user onboarding") == "ship30"
        assert router.detect_skill("Ship 30 content about pricing") == "ship30"
        assert router.detect_skill("Create content about retention") == "ship30"
        assert router.detect_skill("Draft a post about PLG") == "ship30"
    
    def test_detect_artifact(self):
        """Artifact should be detected for component/UI requests."""
        router = self._get_router()
        assert router.detect_skill("Create a pricing dashboard component") == "artifact"
        assert router.detect_skill("Build a landing page for my product") == "artifact"
        assert router.detect_skill("Generate html for a signup form") == "artifact"
        assert router.detect_skill("Create a widget showing metrics") == "artifact"
        assert router.detect_skill("Design a card component") == "artifact"
    
    def test_detect_artifact_over_rag(self):
        """Artifact keywords should take priority over RAG."""
        router = self._get_router()
        assert router.detect_skill("Create a component that shows growth metrics") == "artifact"
    
    def test_detect_ship30_over_rag(self):
        """Ship30 keywords should take priority over RAG."""
        router = self._get_router()
        assert router.detect_skill("Write an essay about how growth loops work") == "ship30"


class TestArtifactAgent:
    """Tests for the artifact agent."""
    
    def test_extract_html_artifact(self):
        """Should extract HTML from code blocks."""
        from app.agents.artifact_agent import ArtifactAgent
        agent = ArtifactAgent()
        
        content = """Here's the component:

```html
<!DOCTYPE html>
<html>
<body><h1>Hello</h1></body>
</html>
```

Hope you like it!"""
        
        result = agent._extract_artifact(content)
        assert result is not None
        assert result["artifact_type"] == "html"
        assert "<h1>Hello</h1>" in result["content"]
    
    def test_extract_markdown_artifact(self):
        """Should extract Markdown from code blocks."""
        from app.agents.artifact_agent import ArtifactAgent
        agent = ArtifactAgent()
        
        content = """Here's the essay:

```markdown
# My Essay

This is the content.
```"""
        
        result = agent._extract_artifact(content)
        assert result is not None
        assert result["artifact_type"] == "markdown"
        assert "# My Essay" in result["content"]
    
    def test_no_artifact(self):
        """Should return None when no code blocks present."""
        from app.agents.artifact_agent import ArtifactAgent
        agent = ArtifactAgent()
        
        content = "This is a regular response without any code blocks."
        result = agent._extract_artifact(content)
        assert result is None


class TestLLMClientFactory:
    """Tests for the LLM client factory."""
    
    def test_get_ollama_client(self):
        """Should return OllamaClient for 'ollama' provider."""
        from app.services import get_llm_client
        from app.services.ollama_client import OllamaClient
        client = get_llm_client("ollama")
        assert isinstance(client, OllamaClient)
    
    def test_get_openai_client(self):
        """Should return OpenAIClient for 'openai' provider."""
        from app.services import get_llm_client
        from app.services.openai_client import OpenAIClient
        client = get_llm_client("openai")
        assert isinstance(client, OpenAIClient)
    
    def test_get_anthropic_client(self):
        """Should return AnthropicClient for 'anthropic' provider."""
        from app.services import get_llm_client
        from app.services.anthropic_client import AnthropicClient
        client = get_llm_client("anthropic")
        assert isinstance(client, AnthropicClient)
    
    def test_default_to_ollama(self):
        """Should default to OllamaClient for unknown provider."""
        from app.services import get_llm_client
        from app.services.ollama_client import OllamaClient
        client = get_llm_client("unknown")
        assert isinstance(client, OllamaClient)
