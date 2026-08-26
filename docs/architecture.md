# Architecture Document
## The Lenny Growth Assistant

---

## 1. System Overview

```
┌──────────────────────────────────────────────────────────────┐
│                        Client (Browser)                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ React SPA (Vite + Tailwind CSS)                         │ │
│  │ ┌──────────┐ ┌──────────────┐ ┌──────────────────────┐ │ │
│  │ │ Sidebar  │ │ Chat View    │ │ Artifact Viewer      │ │ │
│  │ │ Sessions │ │ Streaming    │ │ Sandboxed iframe     │ │ │
│  │ │ Models   │ │ Citations    │ │ DOMPurify            │ │ │
│  │ └──────────┘ └──────────────┘ └──────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTP / SSE
┌──────────────────────────┴───────────────────────────────────┐
│                    FastAPI Backend                             │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Routers: health | models | chat                          ││
│  ├──────────────────────────────────────────────────────────┤│
│  │ Agent Layer                                              ││
│  │ ┌────────────┐ ┌────────────┐ ┌────────────────────┐   ││
│  │ │ Agent      │ │ RAG Agent  │ │ Ship30 Agent       │   ││
│  │ │ Router     │ │ (citations)│ │ (essay generation) │   ││
│  │ └────────────┘ └────────────┘ └────────────────────┘   ││
│  │ ┌────────────────┐                                       ││
│  │ │ Artifact Agent │                                       ││
│  │ │ (HTML/MD gen)  │                                       ││
│  │ └────────────────┘                                       ││
│  ├──────────────────────────────────────────────────────────┤│
│  │ LLM Provider Layer                                       ││
│  │ ┌──────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────┐ ││
│  │ │ Ollama   │ │ OpenAI   │ │ Anthropic    │ │OpenRouter│ ││
│  │ │ Client   │ │ Client   │ │ Client       │ │ Client   │ ││
│  │ └──────────┘ └──────────┘ └──────────────┘ └──────────┘ ││
│  ├──────────────────────────────────────────────────────────┤│
│  │ Services: Retrieval | Vector Store                       ││
│  └──────────────────────────────────────────────────────────┘│
└──────┬──────────────────┬────────────────────────────────────┘
       │                  │
┌──────┴──────┐  ┌───────┴────────┐
│ PostgreSQL  │  │ ChromaDB       │
│ Sessions    │  │ Vector Store   │
│ Messages    │  │ Embeddings     │
│ Artifacts   │  │ Transcript     │
│             │  │ Chunks         │
└─────────────┘  └────────────────┘
```

## 2. Database Schema

### Sessions Table
| Column | Type | Description |
|--------|------|-------------|
| `id` | VARCHAR(36) PK | UUID |
| `title` | VARCHAR(255) | Auto-generated from first message |
| `created_at` | TIMESTAMP | Session creation time |
| `updated_at` | TIMESTAMP | Last message time |
| `llm_provider` | VARCHAR(50) | ollama, openai, anthropic |
| `model_name` | VARCHAR(100) | Specific model used |

### Messages Table
| Column | Type | Description |
|--------|------|-------------|
| `id` | VARCHAR(36) PK | UUID |
| `session_id` | VARCHAR(36) FK | Parent session |
| `role` | VARCHAR(20) | user, assistant, system |
| `content` | TEXT | Message body |
| `citations` | JSON | Array of citation objects |
| `has_artifact` | VARCHAR(20) | html, markdown, or null |
| `artifact_id` | VARCHAR(36) FK | Linked artifact |
| `created_at` | TIMESTAMP | Message time |
| `token_count` | INTEGER | Token usage |

### Artifacts Table
| Column | Type | Description |
|--------|------|-------------|
| `id` | VARCHAR(36) PK | UUID |
| `session_id` | VARCHAR(36) FK | Parent session |
| `artifact_type` | VARCHAR(20) | html or markdown |
| `title` | VARCHAR(255) | Artifact title |
| `content` | TEXT | Raw HTML or Markdown |
| `metadata_json` | JSON | Additional metadata |
| `created_at` | TIMESTAMP | Creation time |

## 3. API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | System health check |
| GET | `/api/models` | Available LLM models |
| POST | `/api/sessions` | Create new session |
| GET | `/api/sessions` | List all sessions |
| GET | `/api/sessions/{id}` | Get session details |
| DELETE | `/api/sessions/{id}` | Delete session |
| GET | `/api/sessions/{id}/messages` | Get session messages |
| POST | `/api/chat` | Non-streaming chat |
| POST | `/api/chat/stream` | SSE streaming chat |
| GET | `/api/artifacts/{id}` | Get artifact content |

### Chat Request Schema
```json
{
  "session_id": "uuid-or-null",
  "message": "string (1-10000 chars)",
  "llm_provider": "ollama|openai|anthropic|openrouter",
  "model_name": "model-id",
  "skill": "rag|ship30|artifact|null"
}
```

### SSE Stream Events
```
data: {"type": "session", "data": {"session_id": "uuid"}}
data: {"type": "token", "data": "Hello"}
data: {"type": "citations", "data": [...]}
data: {"type": "artifact", "data": {...}}
data: {"type": "error", "data": "message"}
data: {"type": "done", "data": ""}
```

## 4. RAG Pipeline

```
User Query
    │
    ▼
┌──────────────┐
│ ChromaDB     │  Cosine similarity search
│ Vector Store │  Top-K = 5 results
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Retrieval    │  Format citations with
│ Service      │  episode, guest, snippet
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Context      │  Build context string
│ Builder      │  from top-K results
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ LLM          │  System prompt + context
│ Generation   │  + conversation history
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Response +   │  Inline [Source N]
│ Citations    │  citations
└──────────────┘
```

### Ingestion Pipeline
```
Transcript Files (.md with YAML frontmatter)
    │  (from ChatPRD/lennys-podcast-transcripts)
    │  Each episode: episodes/<guest-slug>/transcript.md
    │  Frontmatter: guest, title, youtube_url, publish_date, keywords
    │
    ▼
┌──────────────┐
│ Loader       │  Parse files, extract
│              │  episode/guest metadata
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Chunker      │  1000 chars, 200 overlap
│              │  Sentence-boundary aware
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ ChromaDB     │  Default embedding model
│ Embed + Store│  (all-MiniLM-L6-v2)
└──────────────┘
```

## 5. Agent Routing

```
User Message
    │
    ▼
┌──────────────────┐
│ Skill Detection  │  Keyword-based routing
│                  │  (can be upgraded to
│                  │   LLM-based routing)
└──────┬───────────┘
       │
       ├──► "artifact" keywords ──► Artifact Agent
       ├──► "essay/write" keywords ──► Ship30 Agent
       └──► default ──► RAG Agent
```

## 6. Security & Artifact Isolation

### HTML Artifact Sandboxing Strategy

1. **DOMPurify sanitization** before rendering:
   - Allows standard HTML tags and `<style>` elements
   - Blocks `<iframe>`, `<object>`, `<embed>`, `<form>`
   - Removes event handler attributes (`onclick`, etc.)
   - Blocks `javascript:` URIs

2. **Sandboxed iframe** attributes:
   - `sandbox="allow-scripts"` — allows JavaScript execution
   - NO `allow-same-origin` — prevents access to parent page's cookies, localStorage, or DOM
   - This means the artifact runs in a unique origin, isolated from the app

3. **What this permits**: CSS animations, JavaScript interactivity, canvas rendering
4. **What this blocks**: Access to parent page, cookie theft, localStorage access, form submissions to external URLs (partially — CSP can further restrict)

### Risk Assessment
- **XSS via artifact**: Mitigated by DOMPurify + sandboxed iframe
- **Data exfiltration**: Mitigated by no `allow-same-origin`
- **Resource exhaustion**: Not fully mitigated — could add execution time limits

## 7. Deployment Topology

```
docker-compose.yml
├── backend (FastAPI + uvicorn)
│   ├── Port 8000
│   ├── Depends: postgres, ollama
│   └── Volume: ./backend
├── frontend (Vite dev / nginx prod)
│   ├── Port 5173 (dev) / 80 (prod)
│   └── Proxy /api → backend:8000
├── postgres
│   ├── Port 5432
│   └── Volume: pgdata
└── ollama (optional, external)
    └── Port 11434
```
