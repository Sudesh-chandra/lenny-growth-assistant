# Product Requirements Document (PRD)
## The Lenny Growth Assistant

**Version:** 1.0.0  
**Date:** August 2026  
**Author:** Forward Deployed Engineer

---

## 1. User & Problem

### Primary User
Product managers, growth leads, and startup founders who consume Lenny's Podcast content and need quick, actionable answers to product and growth questions.

### Core Problem
Lenny's Podcast has hundreds of hours of expert content covering product management, growth strategy, user research, and more. Finding specific insights across this vast library is time-consuming. Users need:
- **Quick answers** to PM/growth questions without re-listening to entire episodes
- **Proper attribution** to original sources and guests
- **Actionable content** they can use immediately in their work
- **Visual artifacts** (dashboards, components) that illustrate concepts

### Pain Points Removed
- Hours spent searching through podcast transcripts
- Forgetting which episode covered a specific topic
- Inability to quickly reference expert insights in team discussions
- No way to visualize product concepts discussed in audio format

## 2. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Answer Grounding Rate** | >90% | % of responses that include valid source citations |
| **User Session Length** | >5 messages | Average messages per session |
| **Artifact Generation** | >20% of sessions | % of sessions that produce at least one artifact |
| **Response Latency** | <3s (first token) | Time from message send to first streamed token |
| **System Uptime** | >99% | Available during business hours |

## 3. Assumptions

1. **Transcript Quality**: Lenny's Podcast transcripts are available in text format and cover sufficient breadth of PM/growth topics.
2. **Local LLM Capability**: Ollama with llama3 or similar model can produce coherent, grounded responses for the demo.
3. **User Technical Level**: Users are comfortable with a web-based chat interface and understand basic AI concepts.
4. **Data Volume**: The transcript corpus fits within ChromaDB's capacity for a single-node deployment.
5. **Network**: Users have reliable internet for cloud LLM fallback (when configured).

## 4. Scope

### Included (v1)
- ✅ Grounded conversational Q&A with citations
- ✅ Ship 30 for 30 content generation skill
- ✅ HTML/CSS and Markdown artifact generation
- ✅ Dual-pane artifact viewer with sandboxed preview
- ✅ Session management with persistence
- ✅ Model toggle (Ollama local / OpenAI / Anthropic cloud)
- ✅ SSE streaming responses
- ✅ Docker Compose deployment
- ✅ Comprehensive documentation

### Intentionally Excluded
- ❌ User authentication (not needed for internal demo)
- ❌ Multi-tenancy (single-user for evaluation)
- ❌ File upload / image analysis
- ❌ Voice input/output
- ❌ Real-time collaboration features
- ❌ Advanced RAG techniques (hybrid search, re-ranking) — can be added later
- ❌ Fine-tuned models

### Rationale for Exclusions
Authentication and multi-tenancy add complexity without value for the demo evaluation. Voice I/O and file uploads are out of scope for an MVP focused on text-based knowledge retrieval. Advanced RAG techniques are deferred to keep the initial implementation clean and understandable.

## 5. User Flows

### Flow 1: Grounded Q&A
1. User opens app → sees "New Chat" welcome screen
2. User types a PM/growth question
3. System retrieves relevant transcript chunks
4. LLM generates answer with inline citations
5. User sees response with citation badges
6. User can hover citations to see source details
7. User can ask follow-up questions (session context maintained)

### Flow 2: Content Generation
1. User requests essay/content ("Write an essay about...")
2. Agent detects Ship 30 skill
3. System retrieves broader context (top 8 chunks)
4. LLM generates ~1,250-word essay with Ship 30 formatting
5. Response appears as Markdown artifact in the side panel
6. User can toggle between Preview and Code views

### Flow 3: Artifact Generation
1. User requests a visual component ("Create a pricing dashboard")
2. Agent detects artifact skill
3. LLM generates self-contained HTML/CSS
4. Artifact renders in sandboxed iframe in side panel
5. User can view Preview or raw Code, copy code

## 6. Acceptance Criteria

- [ ] User can start a new chat session and send messages
- [ ] Responses include citations linking to specific transcript sources
- [ ] System gracefully handles questions outside its knowledge base
- [ ] Ship 30 essays follow the specified formatting principles
- [ ] HTML artifacts render in sandboxed iframes without security risks
- [ ] User can switch between Ollama (local) and cloud models
- [ ] All sessions and messages persist across page reloads
- [ ] Application starts with a single `docker compose up` command
- [ ] Tests pass for API endpoints, retrieval, and agent routing

## 7. Risks & Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Hallucination** | High — users may trust incorrect answers | Strict grounding in retrieved context; explicit "I don't know" fallback |
| **Local model quality** | Medium — Ollama models less capable than cloud | Use best available local model; clear UI indicator of model quality |
| **Latency** | Medium — slow responses frustrate users | SSE streaming for perceived speed; chunked retrieval |
| **Cost** | Low — cloud API costs for evaluation | Default to local Ollama; cloud is opt-in |
| **Data leakage** | Low — transcripts may contain sensitive info | No external data sharing; local-first architecture |
| **Unsafe artifacts** | Medium — generated HTML could be malicious | DOMPurify sanitization + sandboxed iframe without `allow-same-origin` |
| **Empty retrieval** | Medium — no relevant transcripts found | Graceful fallback message; suggest rephrasing |

## 8. Implementation Plan

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| 1. Setup & Docs | Day 1 | Project structure, PRD, architecture docs |
| 2. Data & DB | Day 1-2 | Transcript ingestion, vector store, PostgreSQL models |
| 3. Backend | Day 2-3 | LLM adapters, agent routing, FastAPI endpoints |
| 4. Frontend | Day 3-4 | Dual-pane UI, streaming, artifact viewer |
| 5. Testing & Deploy | Day 4-5 | Tests, Docker, README, final polish |
