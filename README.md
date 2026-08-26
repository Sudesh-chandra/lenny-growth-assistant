# The Lenny Growth Assistant

An AI-powered conversational web application that transforms Lenny's Podcast transcripts into an intelligent assistant for product management and growth. Features grounded Q&A with citations, Ship 30 for 30 content generation, and interactive artifact creation.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  React + Vite + Tailwind (Frontend)                         │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ Sidebar  │  │ Chat View    │  │ Artifact Viewer    │   │
│  │ Sessions │  │ SSE Stream   │  │ Sandboxed iframe   │   │
│  │ Models   │  │ Citations    │  │ DOMPurify + CSP    │   │
│  └──────────┘  └──────────────┘  └────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP / SSE
┌──────────────────────────┴──────────────────────────────────┐
│  FastAPI Backend                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Agent Router → RAG Agent | Ship30 Agent | Artifact Agent││
│  ├─────────────────────────────────────────────────────────┤│
│  │ LLM Layer: Ollama (local) | OpenAI | Anthropic | OpenRouter ││
│  ├─────────────────────────────────────────────────────────┤│
│  │ Retrieval Service → ChromaDB Vector Store               ││
│  └─────────────────────────────────────────────────────────┘│
└──────┬──────────────────────────┬───────────────────────────┘
       │                          │
┌──────┴──────┐          ┌───────┴────────┐
│ PostgreSQL  │          │ ChromaDB       │
│ Sessions    │          │ Embeddings     │
│ Messages    │          │ Transcript     │
│ Artifacts   │          │ Chunks         │
└─────────────┘          └────────────────┘
```

## Product Screenshots

### Landing Page & Model Toggle
![Landing Page](screenshots/01_landing_page_and_model_toggle.png)
*Sidebar with session management, 4 provider options (Local/OpenRouter/OpenAI/Claude), and suggestion cards.*

### Grounded Q&A with Citations
![Grounded Q&A](screenshots/02_grounded_qa_with_citations.png)
*Structured response with skimmable headings, bullet points, and inline transcript citations.*

### Out-of-Scope Rejection
![Out-of-Scope](screenshots/03_out_of_scope_rejection.png)
*Graceful rejection of off-topic queries without hallucination.*

### Ship 30 for 30 Essay
![Ship 30 Essay](screenshots/04_ship_30_for_30_essay.png)
*Dedicated essay generation with bold hook, skimmable headings, bullet points, and actionable takeaways.*

### Artifact Viewer — Preview Tab
![Artifact Preview](screenshots/05_artifact_viewer_preview.png)
*Dual-pane layout with sandboxed iframe rendering of HTML/CSS artifacts.*

### Artifact Viewer — Code Tab
![Artifact Code](screenshots/06_artifact_viewer_code_tab.png)
*Syntax-highlighted source code with copy button.*

### Session Persistence
![Session Persistence](screenshots/07_session_persistence.png)
*Conversation history persists in sidebar across page reloads via PostgreSQL.*

## Prerequisites

- **Docker & Docker Compose** (recommended) OR
- **Python 3.11+** and **Node.js 20+** (for manual setup)
- **Ollama** (for local LLM) — [install here](https://ollama.com/download)
- **PostgreSQL 16** (if not using Docker)

## Quick Start (Docker — One Command)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd lenny-growth-assistant

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys (optional — Ollama works without cloud keys)

# 3. Pull an Ollama model
ollama pull llama3

# 4. Start everything
docker compose up --build

# 5. Open the app
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API docs: http://localhost:8000/docs
```

## Manual Setup (Without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
# (Tables auto-create on first run)

# Ingest transcripts into vector store
python -m scripts.ingest

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
# Open http://localhost:5173
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes* | `postgresql://...` | PostgreSQL connection string |
| `LLM_PROVIDER` | No | `openrouter` | LLM provider: `ollama`, `openai`, `anthropic`, `openrouter` |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | No | `llama3` | Default Ollama model |
| `OPENAI_API_KEY` | For OpenAI | — | OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4-turbo-preview` | Default OpenAI model |
| `ANTHROPIC_API_KEY` | For Anthropic | — | Anthropic API key |
| `ANTHROPIC_MODEL` | No | `claude-3-sonnet-20240229` | Default Anthropic model |
| `OPENROUTER_API_KEY` | For OpenRouter | — | OpenRouter API key (200+ models) |
| `OPENROUTER_MODEL` | No | `anthropic/claude-sonnet-4` | Default OpenRouter model |
| `CHROMA_PERSIST_DIR` | No | `./chroma_db` | ChromaDB storage directory |
| `CHUNK_SIZE` | No | `1000` | Transcript chunk size (chars) |
| `TOP_K_RESULTS` | No | `5` | Number of retrieval results |

*Not required when using Docker Compose (auto-configured).

## Using Local Models with Ollama

```bash
# Install Ollama: https://ollama.com/download

# Pull a model
ollama pull llama3        # Recommended (8B, good quality)
ollama pull mistral       # Alternative (7B, faster)
ollama pull codellama     # For code-heavy artifacts

# Verify it's running
curl http://localhost:11434/api/tags

# The app will automatically detect available models
```

## Using OpenRouter (200+ Cloud Models)

[OpenRouter](https://openrouter.ai) provides a unified API for 200+ models including Claude, GPT-4, Gemini, Llama, and more.

```bash
# 1. Get an API key from https://openrouter.ai/keys
# 2. Add to .env:
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=anthropic/claude-sonnet-4

# 3. Select OpenRouter in the UI sidebar toggle
# Available models include:
#   - anthropic/claude-sonnet-4
#   - openai/gpt-4o
#   - google/gemini-2.0-flash-001
#   - meta-llama/llama-3.1-70b-instruct
#   - deepseek/deepseek-chat
```

## Running Tests

```bash
cd backend

# Install test dependencies (included in requirements.txt)
pip install pytest pytest-asyncio

# Run all tests
pytest -v

# Run specific test file
pytest tests/test_agents.py -v

# Run with coverage
pip install pytest-cov
pytest --cov=app --cov-report=term-missing

# E2E Browser Tests (Playwright)
pip install playwright
python -m playwright install chromium

# Start the app first (Docker or manual), then:
python tests/e2e/test_ui_and_capture_screenshots.py
# Screenshots saved to docs/screenshots/
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | System health check |
| `GET` | `/api/models` | Available LLM models |
| `POST` | `/api/sessions` | Create new session |
| `GET` | `/api/sessions` | List all sessions |
| `DELETE` | `/api/sessions/{id}` | Delete session |
| `GET` | `/api/sessions/{id}/messages` | Get session messages |
| `POST` | `/api/chat` | Chat (non-streaming) |
| `POST` | `/api/chat/stream` | Chat (SSE streaming) |
| `GET` | `/api/artifacts/{id}` | Get artifact |

## Project Structure

```
lenny-growth-assistant/
├── backend/
│   ├── app/
│   │   ├── agents/          # Agent routing & skills
│   │   │   ├── router.py    # Skill detection & routing
│   │   │   ├── rag_agent.py # Grounded Q&A with citations
│   │   │   ├── ship30_agent.py  # Content generation
│   │   │   └── artifact_agent.py # HTML/MD artifact gen
│   │   ├── core/            # Config, database, logging
│   │   ├── models/          # SQLAlchemy models
│   │   ├── routers/         # FastAPI route handlers
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # LLM clients, retrieval, vector store
│   │   └── main.py          # FastAPI application entry
│   ├── scripts/
│   │   └── ingest.py        # Transcript ingestion
│   ├── tests/               # pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── Sidebar.tsx
│   │   │   ├── ChatView.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   └── ArtifactViewer.tsx
│   │   ├── lib/             # API client, types
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── Dockerfile
│   └── package.json
├── data/transcripts/        # Lenny's Podcast transcripts
├── docs/                    # PRD, design, architecture docs
├── agent_transcripts/       # Agent execution logs
├── docker-compose.yml
├── .env.example
└── README.md
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Ollama connection refused** | Ensure Ollama is running: `ollama serve`. Check `OLLAMA_BASE_URL` in `.env` |
| **Database connection failed** | Check PostgreSQL is running. Verify `DATABASE_URL` format |
| **No citations in responses** | Run transcript ingestion: `python -m scripts.ingest`. Check vector store has data |
| **Frontend can't connect to API** | Check `VITE_API_URL` and CORS settings in backend |
| **Artifact not rendering** | Check browser console for CSP errors. Verify DOMPurify is configured |
| **Slow responses** | Local models are slower than cloud. Try a smaller model or switch to cloud |
| **Docker build fails** | Ensure Docker has enough memory (4GB+). Try `docker compose build --no-cache` |

## Security Notes

- **Artifact Isolation**: HTML artifacts are rendered in sandboxed iframes (`sandbox="allow-scripts"` without `allow-same-origin`) and sanitized with DOMPurify before rendering. This prevents XSS attacks and data exfiltration.
- **No Secrets Committed**: API keys are managed through `.env` files (never committed to git).
- **CORS**: Backend only accepts requests from configured frontend origins.
- **Input Validation**: All API inputs are validated with Pydantic schemas.

## License

MIT
