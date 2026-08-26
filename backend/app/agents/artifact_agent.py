"""
Artifact Agent - Generates HTML/CSS or Markdown artifacts based on user requests.
Detects code blocks and triggers artifact rendering in the frontend.
"""

import re
from typing import Dict, Any, Optional, List, AsyncGenerator
from app.core.logging import get_logger

logger = get_logger(__name__)

ARTIFACT_SYSTEM_PROMPT = """You are an expert frontend developer and designer. When asked to create a component, page, or visual artifact, you generate clean, modern, self-contained HTML/CSS code.

## Artifact Generation Rules:

1. **Self-contained**: All CSS must be inline in a <style> tag. No external dependencies except CDN links for fonts/icons if needed.

2. **Modern design**: Use clean typography, good spacing, subtle shadows, rounded corners, and a professional color palette.

3. **Responsive**: The artifact should look good on different screen sizes.

4. **Interactive**: Include hover states, transitions, and any relevant JavaScript for interactivity.

5. **Format**: When generating an artifact, wrap the COMPLETE HTML document in a code block marked with triple backticks and "html" language tag:

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        /* All styles here */
    </style>
</head>
<body>
    <!-- Content here -->
    <script>
        // Any JavaScript here
    </script>
</body>
</html>
```

6. **For Markdown artifacts**: Wrap in triple backticks with "markdown" tag.

7. **Quality**: Pay attention to details - proper alignment, consistent spacing, accessible colors, and smooth animations.

If the user asks for something that doesn't require an artifact (like a general question), just answer normally without generating code."""


class ArtifactAgent:
    """Agent for generating HTML/CSS and Markdown artifacts."""
    
    def _extract_artifact(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract artifact from the LLM response."""
        # Look for HTML code blocks
        html_pattern = r'```html\s*\n(.*?)```'
        html_match = re.search(html_pattern, content, re.DOTALL)
        
        if html_match:
            return {
                "artifact_type": "html",
                "content": html_match.group(1).strip(),
                "title": "HTML Artifact",
            }
        
        # Look for Markdown code blocks
        md_pattern = r'```markdown\s*\n(.*?)```'
        md_match = re.search(md_pattern, content, re.DOTALL)
        
        if md_match:
            return {
                "artifact_type": "markdown",
                "content": md_match.group(1).strip(),
                "title": "Markdown Document",
            }
        
        return None
    
    async def execute(
        self,
        message: str,
        session_history: List[Dict[str, str]],
        llm_client,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate an artifact."""
        
        messages = [{"role": "system", "content": ARTIFACT_SYSTEM_PROMPT}]
        
        for msg in session_history[-5:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": message})
        
        response = await llm_client.complete(
            messages, model=model, temperature=0.7, max_tokens=4096
        )
        
        # Extract artifact from response
        artifact_data = self._extract_artifact(response)
        
        has_artifact = None
        if artifact_data:
            has_artifact = artifact_data["artifact_type"]
        
        return {
            "content": response,
            "citations": [],
            "has_artifact": has_artifact,
            "artifact_data": artifact_data,
        }
    
    async def execute_stream(
        self,
        message: str,
        session_history: List[Dict[str, str]],
        llm_client,
        model: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate artifact with streaming."""
        
        messages = [{"role": "system", "content": ARTIFACT_SYSTEM_PROMPT}]
        
        for msg in session_history[-5:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": message})
        
        full_content = []
        async for token in llm_client.stream(messages, model=model, temperature=0.7):
            full_content.append(token)
            yield {"type": "token", "data": token}
        
        # Check for artifact in complete response
        complete_response = "".join(full_content)
        artifact_data = self._extract_artifact(complete_response)
        
        if artifact_data:
            yield {"type": "artifact", "data": artifact_data}
        
        yield {"type": "done", "data": ""}
