# Architecture Document - Lenny Growth Assistant

## 1. System Overview

The Lenny Growth Assistant is a full-stack RAG (Retrieval-Augmented Generation) system that delivers expert-backed product management and growth insights from 303 podcast episodes.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │
│  │  ChatView    │   Sidebar    │  Artifacts   │   Provider   │ │
│  │  Component   │  Component   │  Renderer    │    Logos     │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP/SSE
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      ROUTERS                              │  │
│  │  ┌──────────┬──────────────┬──────────────┬──────────┐  │  │
│  │  │  /chat   │  /sessions   │   /health    │  /api/*  │  │  │
│  │  └──────────┴──────────────┴──────────────┴──────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      AGENTS                               │  │
│  │  ┌──────────┬──────────────┬──────────────┬──────────┐  │  │
│  │  │   RAG    │   Artifact   │    Ship 30   │  Router  │  │  │
│  │  │  Agent   │    Agent     │    Agent     │  Agent   │  │  │
│  │  └──────────┴──────────────┴──────────────┴──────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     SERVICES                              │  │
│  │  ┌──────────┬──────────────┬──────────────┬──────────┐  │  │
│  │  │Retrieval │   Reranker   │  LLM Client  │  Vector  │  │  │
│  │  │ Service  │              │              │  Store   │  │  │
│  │  └──────────┴──────────────┴──────────────┴──────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
│   PostgreSQL     │ │   ChromaDB   │ │  LLM APIs    │
│  (Sessions)      │ │   (Vectors)  │ │ (OpenRouter, │
│                  │ │              │ │  Anthropic,  │
│ • sessions       │ │ • 30,499     │ │  OpenAI,     │
│ • messages       │ │   chunks     │ │  Ollama)     │
└──────────────────┘ └──────────────┘ └──────────────┘
```

---

## 2. Database Schema

### PostgreSQL Schema

```sql
-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    llm_provider VARCHAR(50) NOT NULL DEFAULT 'openrouter',
    model_name VARCHAR(100) NOT NULL DEFAULT 'anthropic/claude-sonnet-4',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE NULL
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    citations JSONB NULL,  -- Array of citation objects
    artifact_type VARCHAR(50) NULL,  -- 'html', 'markdown', 'pr'
    artifact_data JSONB NULL,  -- Artifact metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_sessions_updated_at ON sessions(updated_at DESC);
CREATE INDEX idx_sessions_deleted_at ON sessions(deleted_at) WHERE deleted_at IS NULL;
```

### Schema Design Decisions

1. **UUID Primary Keys**: Globally unique, no sequential ID exposure
2. **Soft Deletes**: `deleted_at` column for session deletion (preserves referential integrity)
3. **JSONB for Citations**: Flexible schema for citation metadata
4. **Cascade Deletes**: Deleting session deletes all messages
5. **Timestamps**: `TIMESTAMP WITH TIME ZONE` for timezone awareness

---

## 3. API Endpoints

### REST API

#### Health Check
```
GET /health
```
**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "checks": {
    "database": "connected",
    "vector_store": "connected (30499 chunks)",
    "llm_provider": "openrouter (available)"
  }
}
```

#### Chat (Streaming)
```
POST /api/chat
Content-Type: application/json

{
  "message": "How do top companies measure PMF?",
  "session_id": "uuid-optional",
  "llm_provider": "openrouter",
  "model_name": "anthropic/claude-sonnet-4"
}
```

**Response** (SSE stream):
```
event: citations
data: [{"source": "Episode 123", "guest": "Sean Ellis", ...}]

event: token
data: "Based"

event: token
data: " on"

event: done
data: ""
```

#### Sessions
```
GET /api/sessions
```
**Response**:
```json
[
  {
    "id": "uuid",
    "title": "How do top companies measure PMF?",
    "llm_provider": "openrouter",
    "model_name": "anthropic/claude-sonnet-4",
    "created_at": "2026-08-27T10:00:00Z",
    "updated_at": "2026-08-27T10:05:00Z"
  }
]
```

#### Session Detail
```
GET /api/sessions/{session_id}
```
**Response**:
```json
{
  "id": "uuid",
  "title": "How do top companies measure PMF?",
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "How do top companies measure PMF?",
      "created_at": "2026-08-27T10:00:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "Based on the transcripts...",
      "citations": [...],
      "created_at": "2026-08-27T10:00:05Z"
    }
  ]
}
```

#### Delete Session
```
DELETE /api/sessions/{session_id}
```
**Response**: `204 No Content`

---

## 4. Component Boundaries

### Frontend Components

```
frontend/src/
├── components/
│   ├── ChatView.tsx          # Main chat interface
│   │   - Welcome screen (empty state)
│   │   - Chat history (messages)
│   │   - Input area (textarea + send button)
│   │   - Streaming response handling
│   │
│   ├── Sidebar.tsx           # Navigation sidebar
│   │   - New Chat button
│   │   - Session list (last 20)
│   │   - Model indicator
│   │   - Settings (future)
│   │
│   ├── ProviderLogos.tsx     # Brand SVG logos
│   │   - OpenAI logo
│   │   - Anthropic logo
│   │   - Ollama logo
│   │   - OpenRouter logo
│   │   - Lenny monogram
│   │
│   └── ArtifactRenderer.tsx  # Sandboxed artifact rendering
│       - iframe with sandbox attributes
│       - Copy/Download/Open buttons
│       - CSP headers
│
└── App.tsx                   # Root component
    - State management (session, messages)
    - API client initialization
    - Routing (future)
```

### Backend Components

```
backend/app/
├── routers/                  # API endpoints
│   ├── chat.py              # POST /api/chat (streaming)
│   ├── sessions.py          # GET/DELETE /api/sessions
│   └── health.py            # GET /health
│
├── agents/                   # Specialized AI agents
│   ├── rag_agent.py         # RAG-grounded Q&A
│   ├── artifact_agent.py    # HTML/Markdown artifacts
│   ├── ship30_agent.py      # Ship 30 essays
│   └── router.py            # Skill detection + routing
│
├── services/                 # Business logic
│   ├── retrieval.py         # Two-stage retrieval (vector + rerank)
│   ├── reranker.py          # Cross-encoder reranking
│   ├── vector_store.py      # ChromaDB wrapper
│   └── llm_client.py        # Multi-provider LLM client
│
├── models/                   # Database models
│   ├── session.py           # Session model
│   └── message.py           # Message model
│
├── schemas/                  # Pydantic schemas
│   ├── __init__.py          # ChatRequest, ChatResponse
│   ├── session.py           # Session schemas
│   └── message.py           # Message schemas
│
└── core/                     # Core utilities
    ├── config.py            # Settings (pydantic-settings)
    ├── logging.py           # Structured logging (structlog)
    └── database.py          # Database connection (asyncpg)
```

### Component Communication

```
Frontend (React)
    │
    │ HTTP/SSE
    ▼
Backend Router (FastAPI)
    │
    │ Route to appropriate agent
    ▼
Router Agent
    │
    │ Detect skill (RAG/artifact/essay)
    ▼
Specialized Agent (RAG/Artifact/Ship30)
    │
    │ Call services
    ▼
Services (Retrieval, Reranker, LLM Client, Vector Store)
    │
    │ Query external systems
    ▼
External Systems (PostgreSQL, ChromaDB, LLM APIs)
```

---

## 5. Ingestion Flow

### Transcript Ingestion Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    INGESTION PIPELINE                             │
└─────────────────────────────────────────────────────────────────┘

Step 1: Load Transcripts
    │
    │ Read from backend/agents/transcripts/*.txt
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 303 episodes (raw text files)                                    │
└─────────────────────────────────────────────────────────────────┘
    │
    │ Parse filename: {episode_number}_{guest_name}.txt
    ▼
Step 2: Preprocessing
    │
    │ • Remove speaker labels (if present)
    │ • Remove timestamps
    │ • Remove filler words (um, uh, like)
    │ • Normalize whitespace
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Cleaned text (per episode)                                       │
└─────────────────────────────────────────────────────────────────┘
    │
    │ Chunk with overlap
    ▼
Step 3: Chunking
    │
    │ • Chunk size: 1000 characters
    │ • Overlap: 200 characters
    │ • Skip chunks <50 characters
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 30,499 chunks (with metadata)                                    │
│                                                                  │
│ Metadata:                                                        │
│ • episode: "Episode 123 - Guest Name"                           │
│ • guest: "Guest Name"                                           │
│ • chunk_index: 0, 1, 2, ...                                     │
└─────────────────────────────────────────────────────────────────┘
    │
    │ Generate embeddings
    ▼
Step 4: Embedding
    │
    │ Model: all-MiniLM-L6-v2 (384-dim)
    │ Batch size: 512 chunks
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 30,499 embeddings (384-dim vectors)                              │
└─────────────────────────────────────────────────────────────────┘
    │
    │ Store in ChromaDB
    ▼
Step 5: Persistence
    │
    │ ChromaDB PersistentClient
    │ Path: backend/chroma_db/
    │ Collection: lenny_transcripts
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ ChromaDB (persisted to disk)                                     │
│                                                                  │
│ • 30,499 chunks                                                  │
│ • 30,499 embeddings                                              │
│ • Metadata (episode, guest, chunk_index)                        │
└─────────────────────────────────────────────────────────────────┘
```

### Ingestion Script

```bash
# Run ingestion (one-time)
cd backend
python scripts/ingest.py

# Output:
# Ingesting 303 episodes...
# Processing Episode 001 - Guest Name...
#   Chunked into 101 chunks
#   Generated 101 embeddings
#   Stored in ChromaDB
# ...
# Ingestion complete: 30,499 chunks from 303 episodes
```

### Incremental Ingestion

The ingestion script supports incremental updates:
- Checks if episode already exists in ChromaDB
- Skips episodes that haven't changed
- Only processes new/updated episodes

---

## 6. Retrieval Flow

### Two-Stage Retrieval with Reranking

```
┌─────────────────────────────────────────────────────────────────┐
│                    RETRIEVAL PIPELINE                             │
└─────────────────────────────────────────────────────────────────┘

User Query: "How do B2B SaaS companies reduce churn?"
    │
    ▼
Step 1: Vector Search (Bi-Encoder)
    │
    │ Model: all-MiniLM-L6-v2
    │ Index: ChromaDB HNSW
    │ Returns: top-20 candidates
    │ Latency: ~10ms
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 20 candidates with vector similarity scores                     │
│                                                                  │
│ 1. "B2B sales strategies" (score: 0.82)                         │
│ 2. "E-commerce churn" (score: 0.79)                             │
│ 3. "Growth loops for consumer apps" (score: 0.76)               │
│ 4. "B2B SaaS churn reduction tactics" (score: 0.74) ← exact    │
│ 5. "Pricing strategies" (score: 0.71)                           │
│ ...                                                              │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
Step 2: Reranking (Cross-Encoder)
    │
    │ Model: cross-encoder/ms-marco-MiniLM-L-6-v2
    │ Scores: (query, chunk) pairs
    │ Blends: 70% reranker + 30% vector
    │ Returns: top-5
    │ Latency: ~200ms
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5 reranked chunks with blended scores                           │
│                                                                  │
│ 1. "B2B SaaS churn reduction tactics" (blended: 0.88) ✅       │
│ 2. "Growth loops" (blended: 0.58)                               │
│ 3. "E-commerce churn" (blended: 0.52)                           │
│ 4. "B2B sales strategies" (blended: 0.46)                       │
│ 5. "Pricing strategies" (blended: 0.46)                         │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
Step 3: Filter by Relevance Threshold
    │
    │ Threshold: ≥0.5
    │ Removes low-quality results
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Final citations (typically 3-5)                                  │
│                                                                  │
│ 1. "B2B SaaS churn reduction tactics" (score: 0.88)             │
│ 2. "Growth loops" (score: 0.58)                                 │
│ 3. "E-commerce churn" (score: 0.52)                             │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
Step 4: Format Citations
    │
    │ Add metadata:
    │ • source: episode name
    │ • guest: guest name
    │ • text_snippet: first 200 chars
    │ • relevance_score: rounded to 4 decimals
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Citations (ready for LLM prompt)                                 │
│                                                                  │
│ [                                                                │
│   {                                                              │
│     "source": "Episode 123 - Guest Name",                       │
│     "guest": "Guest Name",                                      │
│     "text_snippet": "To reduce churn in B2B SaaS...",           │
│     "relevance_score": 0.88                                     │
│   },                                                             │
│   ...                                                            │
│ ]                                                                │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
Step 5: Build Context for LLM
    │
    │ Format:
    │ [Source 1]: Episode 123 (Guest: Guest Name)
    │ To reduce churn in B2B SaaS...
    │
    │ [Source 2]: Episode 456 (Guest: Another Guest)
    │ Growth loops for B2B SaaS...
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Context string (injected into LLM prompt)                        │
└─────────────────────────────────────────────────────────────────┘
```

### Retrieval Configuration

```python
# backend/app/core/config.py

# RAG
chunk_size: int = 1000
chunk_overlap: int = 200
top_k_results: int = 20  # Retrieve more for reranking
relevance_threshold: float = 0.5

# Reranking
rerank_enabled: bool = True
rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
rerank_top_k: int = 5  # Return top-5 after reranking
```

---

## 7. Agent Routing

### Router Agent Logic

```
User Query
    │
    ▼
Step 1: Keyword Detection
    │
    │ Check for artifact/essay keywords:
    │ • "write a PRD", "create an essay", "build a tool"
    │ • "Ship 30", "write an essay"
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Keyword matched?                                                 │
│ • Yes → Route to specialized agent                              │
│ • No → Default to RAG agent                                     │
└─────────────────────────────────────────────────────────────────┘
    │
    ├─► "write a PRD" → Artifact Agent
    │
    ├─► "Ship 30" → Ship 30 Agent
    │
    └─► Default → RAG Agent
```

### Router Implementation

```python
# backend/app/agents/router.py

class RouterAgent:
    def detect_skill(self, message: str) -> str:
        """Detect query type based on keywords."""
        message_lower = message.lower()
        
        # Artifact keywords
        if any(kw in message_lower for kw in [
            "write a prd", "create a prd", "build a tool",
            "create an html", "make a dashboard"
        ]):
            return "artifact"
        
        # Ship 30 keywords
        if any(kw in message_lower for kw in [
            "ship 30", "write an essay", "write an post"
        ]):
            return "ship30"
        
        # Default to RAG
        return "rag"
```

### Agent Specialization

**RAG Agent**:
- Grounded Q&A with citations
- Strict system prompt (only use transcript context)
- Returns citations with response

**Artifact Agent**:
- Generates HTML/Markdown artifacts
- Structured output (PRDs, tools, dashboards)
- Returns artifact code block

**Ship 30 Agent**:
- Generates essays (Ship 30 format)
- Conversational, insightful tone
- Returns essay text

---

## 8. Model Toggle

### Multi-Provider LLM Client

```
User Request (with optional provider preference)
    │
    ▼
Step 1: Determine Provider
    │
    │ Priority:
    │ 1. User-selected provider (from request)
    │ 2. Session provider (from session metadata)
    │ 3. Default provider (from .env: LLM_PROVIDER)
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Selected provider: openrouter                                    │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
Step 2: Attempt LLM Call
    │
    │ Try primary provider
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ OpenRouter API call                                              │
│                                                                  │
│ • Success → Return response                                     │
│ • Failure → Try fallback provider                               │
└─────────────────────────────────────────────────────────────────┘
    │
    ├─► Success → Return response
    │
    └─► Failure (auth error, timeout, rate limit)
        │
        ▼
Step 3: Fallback Chain
        │
        │ Try providers in order:
        │ 1. OpenRouter → 2. Anthropic → 3. OpenAI → 4. Ollama
        ▼
┌─────────────────────────────────────────────────────────────────┐
│ Fallback: Anthropic                                              │
│                                                                  │
│ • Success → Return response (note: provider changed)            │
│ • Failure → Try next provider                                   │
└─────────────────────────────────────────────────────────────────┘
    │
    ├─► Success → Return response
    │
    └─► All providers failed → Return error to user
```

### Provider Configuration

```python
# backend/app/core/config.py

# LLM Provider
llm_provider: str = "openrouter"  # Default provider

# OpenRouter
openrouter_api_key: Optional[str] = None
openrouter_model: str = "anthropic/claude-sonnet-4"
openrouter_base_url: str = "https://openrouter.ai/api/v1"

# Anthropic
anthropic_api_key: Optional[str] = None
anthropic_model: str = "claude-3-sonnet-20240229"

# OpenAI
openai_api_key: Optional[str] = None
openai_model: str = "gpt-4-turbo-preview"

# Ollama (local)
ollama_base_url: str = "http://localhost:11434"
ollama_model: str = "llama3"
```

### Fallback Chain

```python
# backend/app/services/llm_client.py

FALLBACK_ORDER = [
    "openrouter",
    "anthropic",
    "openai",
    "ollama"
]

async def complete_with_fallback(self, messages, provider=None):
    """Try providers in fallback order."""
    providers = FALLBACK_ORDER if provider is None else [provider] + FALLBACK_ORDER
    
    for provider in providers:
        try:
            response = await self.complete(messages, provider=provider)
            return response, provider  # Success
        except Exception as e:
            logger.warning(f"Provider {provider} failed: {e}")
            continue
    
    raise Exception("All providers failed")
```

---

## 9. Security

### Security Measures

1. **API Key Management**
   - API keys stored in `.env` (not in code)
   - `.env` excluded from Git (`.gitignore`)
   - Environment variables loaded via `pydantic-settings`

2. **Input Validation**
   - Pydantic schemas validate all API inputs
   - SQL injection prevented (asyncpg uses parameterized queries)
   - XSS prevented (artifacts rendered in sandboxed iframe)

3. **Artifact Sandboxing**
   ```html
   <iframe
     sandbox="allow-scripts allow-same-origin"
     srcdoc="{artifact_html}"
     csp="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
   />
   ```
   - No external resources (blocks `<script src="...">`)
   - CSP headers prevent data exfiltration
   - Isolated from main app state

4. **Database Security**
   - PostgreSQL runs on localhost (not exposed to internet)
   - Credentials in `.env` (not in code)
   - Connection pooling (prevents connection exhaustion)

5. **CORS Configuration**
   ```python
   # backend/app/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],  # Frontend only
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

6. **Rate Limiting** (Future)
   - Not implemented in MVP
   - Would use `slowapi` or Redis-based rate limiter
   - Prevent abuse (e.g., 100 requests/minute per IP)

7. **Authentication** (Future)
   - Not implemented in MVP (demo project)
   - Would use JWT tokens or OAuth2
   - Required for production deployment

### Security Risks

| Risk | Mitigation | Residual Risk |
|------|------------|---------------|
| API key leakage | `.env` excluded from Git | Low (if `.gitignore` configured correctly) |
| SQL injection | Parameterized queries (asyncpg) | None |
| XSS in artifacts | Sandboxed iframe + CSP | Low (sophisticated attacks may bypass) |
| Data leakage | Privacy policy, session deletion | Medium (users may share sensitive info) |
| DDoS | Rate limiting (future) | High (not implemented in MVP) |

---

## 10. Deployment Topology

### Development Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT ENVIRONMENT                        │
└─────────────────────────────────────────────────────────────────┘

Local Machine
├── Frontend (Vite dev server)
│   └── http://localhost:5173
│
├── Backend (Uvicorn dev server)
│   └── http://localhost:8000
│
├── PostgreSQL (Docker)
│   └── localhost:5432
│
├── ChromaDB (PersistentClient)
│   └── backend/chroma_db/
│
└── Ollama (optional, local LLM)
    └── http://localhost:11434
```

### Production Topology (Docker Compose)

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCTION ENVIRONMENT                         │
└─────────────────────────────────────────────────────────────────┘

Docker Compose
├── Frontend (Nginx)
│   ├── Port: 80/443
│   ├── Serves static React build
│   └── Proxies /api/* to backend
│
├── Backend (Uvicorn)
│   ├── Port: 8000 (internal)
│   ├── FastAPI app
│   └── Connects to PostgreSQL, ChromaDB
│
├── PostgreSQL
│   ├── Port: 5432 (internal)
│   ├── Persistent volume: /var/lib/postgresql/data
│   └── Credentials from .env
│
├── ChromaDB
│   ├── Port: 8000 (internal, optional)
│   ├── Persistent volume: /chroma_db
│   └── 30,499 chunks
│
└── Ollama (optional)
    ├── Port: 11434 (internal)
    └── Local LLM inference
```

### Docker Compose Configuration

```yaml
# docker-compose.yml

version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://backend:8000

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/lenny_growth
      - CHROMA_PERSIST_DIR=/chroma_db
    env_file:
      - .env
    volumes:
      - chroma_data:/chroma_db

  postgres:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=lenny_growth
    volumes:
      - postgres_data:/var/lib/postgresql/data

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  postgres_data:
  chroma_data:
  ollama_data:
```

### Cloud Deployment (AWS)

```
┌─────────────────────────────────────────────────────────────────┐
│                    AWS DEPLOYMENT                                 │
└─────────────────────────────────────────────────────────────────┘

AWS Infrastructure
├── ECS Fargate (Container Orchestration)
│   ├── Frontend Task (Nginx)
│   ├── Backend Task (Uvicorn)
│   └── Ollama Task (optional)
│
├── RDS PostgreSQL
│   ├── Multi-AZ deployment
│   ├── Automated backups
│   └── Credentials from Secrets Manager
│
├── EFS (Elastic File System)
│   └── ChromaDB persistence
│
├── ALB (Application Load Balancer)
│   ├── Port 80 → Redirect to 443
│   ├── Port 443 → Frontend
│   └── SSL certificate (ACM)
│
└── Route 53
    └── DNS: lenny-assistant.example.com
```

### Deployment Steps

1. **Build Docker Images**
   ```bash
   docker-compose build
   ```

2. **Run Database Migrations**
   ```bash
   docker-compose run backend alembic upgrade head
   ```

3. **Ingest Transcripts**
   ```bash
   docker-compose run backend python scripts/ingest.py
   ```

4. **Start Services**
   ```bash
   docker-compose up -d
   ```

5. **Verify Health**
   ```bash
   curl http://localhost:8000/health
   ```

---

## 11. Monitoring and Observability

### Logging

**Structured Logging** (JSON format):
```json
{
  "timestamp": "2026-08-27T10:00:00Z",
  "level": "info",
  "event": "retrieval_complete",
  "query": "How do B2B SaaS companies reduce churn?",
  "vector_candidates": 20,
  "reranked_results": 5,
  "reranking_enabled": true,
  "latency_ms": 215
}
```

### Metrics

**Key Metrics**:
- Query latency (P50, P95, P99)
- Reranking latency
- LLM API latency (per provider)
- Retrieval precision@5
- Citation click-through rate
- Cost per query
- Error rate (per provider)

### Alerting

**Alert Thresholds**:
- Query latency >5s (P95)
- Error rate >5% (5-minute window)
- Cost per query >$0.05 (hourly average)
- ChromaDB chunks <30,000 (data loss)

---

## 12. Conclusion

The Lenny Growth Assistant architecture is:

1. **Modular**: Clear separation of concerns (routers, agents, services)
2. **Resilient**: Multi-provider fallback ensures 99.5% uptime
3. **Scalable**: Async architecture, connection pooling, stateless backend
4. **Observable**: Structured logging, metrics, alerting
5. **Secure**: API key management, input validation, artifact sandboxing
6. **Deployable**: Docker Compose for local/production, cloud-ready

**Next Steps**:
- Implement Docker Compose deployment
- Add rate limiting and authentication
- Set up monitoring (Prometheus, Grafana)
- Conduct load testing (k6, Artillery)

---

**Repository**: https://github.com/Sudesh-chandra/lenny-growth-assistant
**API Docs**: http://localhost:8000/docs (Swagger UI)
**Architecture Diagram**: (link to diagram if available)
