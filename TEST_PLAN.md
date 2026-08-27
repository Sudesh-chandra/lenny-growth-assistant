# Test Plan - Lenny Growth Assistant

## Overview

This document outlines the testing strategy for the Lenny Growth Assistant, including automated tests (unit, integration) and manual tests (UI/UX).

---

## 1. Automated Tests

### 1.1 Unit Tests

**Framework**: pytest (Python)
**Location**: `backend/tests/`
**Count**: 28 passing tests

#### Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| Vector Store | 5 | ChromaDB operations (search, count, persist) |
| Retrieval Service | 6 | Two-stage retrieval (vector + rerank) |
| Reranker | 4 | Cross-encoder scoring, fallback |
| LLM Client | 5 | Multi-provider fallback |
| Router Agent | 4 | Skill detection (RAG/artifact/essay) |
| Session Management | 4 | Create, read, delete sessions |

#### Running Tests

```bash
cd backend
pytest

# Output:
# ========================= test session starts =========================
# collected 28 items
# 
# tests/test_retrieval.py ..............                          [ 50%]
# tests/test_vector_store.py .....                                [ 68%]
# tests/test_reranker.py ....                                     [ 82%]
# tests/test_llm_client.py .....                                  [100%]
# 
# ========================= 28 passed in 2.34s =========================
```

#### Key Test Cases

**Test 1: Vector Search Returns Results**
```python
def test_search_with_results():
    """Verify vector search returns chunks with scores."""
    vector_store = VectorStore()
    results = vector_store.search("How to measure PMF?", top_k=5)
    
    assert len(results) == 5
    assert all('score' in r for r in results)
    assert all(r['score'] > 0 for r in results)
```

**Test 2: Reranking Improves Quality**
```python
def test_reranking_improves_precision():
    """Verify reranking ranks relevant chunks higher."""
    reranker = Reranker()
    documents = [
        {'text': 'B2B sales strategies', 'score': 0.82},
        {'text': 'B2B SaaS churn reduction tactics', 'score': 0.74},
    ]
    
    reranked = reranker.rerank("How do B2B SaaS companies reduce churn?", documents)
    
    # Exact match should be ranked higher
    assert 'churn reduction' in reranked[0]['text']
```

**Test 3: Multi-Provider Fallback**
```python
async def test_llm_fallback():
    """Verify LLM client falls back to next provider on failure."""
    client = LLMClient()
    
    # Mock primary provider to fail
    with patch('openai.ChatCompletion.create', side_effect=Exception("Auth failed")):
        response, provider = await client.complete_with_fallback(messages)
        
        # Should fall back to next provider
        assert provider == "anthropic"
        assert response is not None
```

**Test 4: Router Detects Skill**
```python
def test_router_detects_artifact_skill():
    """Verify router detects artifact keywords."""
    router = RouterAgent()
    
    skill = router.detect_skill("Write a PRD for a referral program")
    assert skill == "artifact"
    
    skill = router.detect_skill("How do top companies measure PMF?")
    assert skill == "rag"
```

### 1.2 Integration Tests

**Framework**: pytest + httpx (async)
**Location**: `backend/tests/integration/`

#### Test Coverage

| Endpoint | Tests | Coverage |
|----------|-------|----------|
| GET /health | 2 | Health check, vector store status |
| POST /api/chat | 5 | Streaming, citations, fallback |
| GET /api/sessions | 3 | List sessions, pagination |
| GET /api/sessions/{id} | 2 | Session detail, messages |
| DELETE /api/sessions/{id} | 2 | Soft delete, cascade |

#### Running Integration Tests

```bash
cd backend
pytest tests/integration/

# Requires:
# - Backend running on port 8000
# - PostgreSQL running on port 5432
# - ChromaDB populated (30,499 chunks)
```

#### Key Integration Tests

**Test 1: Chat Endpoint Returns Streaming Response**
```python
async def test_chat_streaming():
    """Verify chat endpoint streams tokens via SSE."""
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            "http://localhost:8000/api/chat",
            json={"message": "How do top companies measure PMF?"}
        ) as response:
            assert response.status_code == 200
            
            events = []
            async for line in response.aiter_lines():
                if line.startswith("event:"):
                    events.append(line.split(":")[1])
            
            assert "citations" in events
            assert "token" in events
            assert "done" in events
```

**Test 2: Session Persistence**
```python
async def test_session_persistence():
    """Verify sessions persist to PostgreSQL."""
    async with httpx.AsyncClient() as client:
        # Create session via chat
        response = await client.post(
            "http://localhost:8000/api/chat",
            json={"message": "Test query"}
        )
        session_id = response.json()["session_id"]
        
        # Retrieve session
        response = await client.get(f"http://localhost:8000/api/sessions/{session_id}")
        assert response.status_code == 200
        
        session = response.json()
        assert session["id"] == session_id
        assert len(session["messages"]) > 0
```

---

## 2. Manual Test Plan (UI/UX)

### 2.1 Test Environment

**Browser**: Chrome 120+, Firefox 115+, Safari 17+
**Resolution**: Desktop (1920x1080), Tablet (768x1024), Mobile (375x667)
**Backend**: http://localhost:8000
**Frontend**: http://localhost:5173

### 2.2 Test Cases

#### TC-001: First-Time User Experience

**Steps**:
1. Open http://localhost:5173
2. Observe welcome screen

**Expected**:
- ✅ Lenny monogram logo displayed (64x64px)
- ✅ Greeting: "Hello, I'm Lenny's Growth Assistant"
- ✅ Subtitle: "Ask about product management..."
- ✅ 3-4 starter cards visible
- ✅ Input area with placeholder text

**Actual**: [Pass/Fail]

---

#### TC-002: Starter Card Interaction

**Steps**:
1. Click starter card: "How do top companies measure PMF?"
2. Observe input area

**Expected**:
- ✅ Input populated with starter card text
- ✅ Send button enabled
- ✅ No errors in console

**Actual**: [Pass/Fail]

---

#### TC-003: Send Query (RAG)

**Steps**:
1. Type: "How do B2B SaaS companies reduce churn?"
2. Press Enter or click Send
3. Observe response

**Expected**:
- ✅ Streaming indicator appears ("Thinking...")
- ✅ Tokens appear as they generate (streaming)
- ✅ Response completes within 3 seconds
- ✅ Citations displayed below response
- ✅ Each citation shows: source, guest, snippet, relevance score
- ✅ Response includes [Source N] citations

**Actual**: [Pass/Fail]

---

#### TC-004: Citation Interaction

**Steps**:
1. Click on a citation card
2. Observe behavior

**Expected**:
- ✅ Citation expands to show full details
- ✅ Source episode name visible
- ✅ Guest name visible
- ✅ Text snippet visible
- ✅ Relevance score visible

**Actual**: [Pass/Fail]

---

#### TC-005: Session Persistence

**Steps**:
1. Send a query (creates new session)
2. Refresh browser (F5)
3. Observe sidebar

**Expected**:
- ✅ Session appears in sidebar
- ✅ Session title auto-generated (first 50 chars)
- ✅ Click session → chat history loads
- ✅ Messages display in correct order
- ✅ Citations preserved in history

**Actual**: [Pass/Fail]

---

#### TC-006: Model Switching

**Steps**:
1. Click model dropdown in sidebar
2. Select "Anthropic"
3. Send a query

**Expected**:
- ✅ Model switches to Anthropic
- ✅ Response generated successfully
- ✅ UI shows which provider was used
- ✅ If Anthropic fails → automatic fallback

**Actual**: [Pass/Fail]

---

#### TC-007: Artifact Generation

**Steps**:
1. Type: "Write a PRD for a referral program"
2. Press Enter
3. Observe response

**Expected**:
- ✅ Router detects artifact skill
- ✅ Artifact agent generates HTML/Markdown
- ✅ Artifact renders in sandboxed iframe
- ✅ Toolbar shows: Copy, Download, Open in new tab
- ✅ Click "Copy" → copies code to clipboard
- ✅ Click "Download" → downloads as file

**Actual**: [Pass/Fail]

---

#### TC-008: Error Handling (Provider Failure)

**Steps**:
1. Set invalid API key in .env
2. Restart backend
3. Send a query

**Expected**:
- ✅ Primary provider fails
- ✅ Automatic fallback to next provider
- ✅ Response generated successfully
- ✅ UI shows which provider was actually used
- ✅ No errors visible to user

**Actual**: [Pass/Fail]

---

#### TC-009: Responsive Design (Mobile)

**Steps**:
1. Open Chrome DevTools
2. Set device: iPhone 12 (375x667)
3. Observe layout

**Expected**:
- ✅ Sidebar hidden by default
- ✅ Hamburger menu visible
- ✅ Click hamburger → sidebar slides in
- ✅ Click outside → sidebar closes
- ✅ Input area fixed to bottom
- ✅ Starter cards in single column
- ✅ Chat history full width

**Actual**: [Pass/Fail]

---

#### TC-010: Accessibility (Keyboard Navigation)

**Steps**:
1. Press Tab repeatedly
2. Observe focus order

**Expected**:
- ✅ Focus order: New Chat → Session List → Chat History → Input → Send
- ✅ Focus indicator visible (2px outline)
- ✅ All interactive elements focusable
- ✅ Enter key sends message
- ✅ Shift+Enter creates new line
- ✅ Escape closes sidebar (mobile)

**Actual**: [Pass/Fail]

---

#### TC-011: Accessibility (Screen Reader)

**Steps**:
1. Enable screen reader (VoiceOver, NVDA)
2. Navigate through app

**Expected**:
- ✅ ARIA labels on all interactive elements
- ✅ Semantic HTML (nav, main, section, article)
- ✅ Live regions announce streaming responses
- ✅ Announce: "Assistant is typing..." during streaming

**Actual**: [Pass/Fail]

---

#### TC-012: Performance (Latency)

**Steps**:
1. Send 10 different queries
2. Measure response time

**Expected**:
- ✅ Average latency <3 seconds
- ✅ P95 latency <5 seconds
- ✅ Streaming starts within 500ms
- ✅ No timeouts or errors

**Actual**: [Pass/Fail]

---

#### TC-013: Session Deletion

**Steps**:
1. Hover over session in sidebar
2. Click delete button
3. Confirm deletion

**Expected**:
- ✅ Delete button appears on hover
- ✅ Confirmation dialog appears
- ✅ Session removed from sidebar
- ✅ Session deleted from database
- ✅ Messages cascade deleted

**Actual**: [Pass/Fail]

---

#### TC-014: Dark Mode

**Steps**:
1. Observe color palette

**Expected**:
- ✅ Background: #0a0d14 (deep slate)
- ✅ Sidebar: #111622
- ✅ Input area: #1a1f2e
- ✅ Text: #e2e8f0 (light gray)
- ✅ Accent: #6366f1 (indigo)
- ✅ No neon purple or loud colors

**Actual**: [Pass/Fail]

---

#### TC-015: Brand Logos

**Steps**:
1. Observe provider logos in sidebar

**Expected**:
- ✅ OpenAI: Official knot SVG (green)
- ✅ Anthropic: Official "A" letterform (tan)
- ✅ Ollama: Llama-inspired icon (black)
- ✅ OpenRouter: Hexagon router mark (indigo)
- ✅ No generic placeholder icons

**Actual**: [Pass/Fail]

---

### 2.3 Test Results Summary

| Test ID | Test Name | Status | Notes |
|---------|-----------|--------|-------|
| TC-001 | First-Time User Experience | [ ] | |
| TC-002 | Starter Card Interaction | [ ] | |
| TC-003 | Send Query (RAG) | [ ] | |
| TC-004 | Citation Interaction | [ ] | |
| TC-005 | Session Persistence | [ ] | |
| TC-006 | Model Switching | [ ] | |
| TC-007 | Artifact Generation | [ ] | |
| TC-008 | Error Handling | [ ] | |
| TC-009 | Responsive Design | [ ] | |
| TC-010 | Accessibility (Keyboard) | [ ] | |
| TC-011 | Accessibility (Screen Reader) | [ ] | |
| TC-012 | Performance | [ ] | |
| TC-013 | Session Deletion | [ ] | |
| TC-014 | Dark Mode | [ ] | |
| TC-015 | Brand Logos | [ ] | |

**Overall**: [ ] Pass / [ ] Fail

---

## 3. Performance Tests

### 3.1 Load Testing

**Tool**: k6 or Artillery
**Target**: 100 concurrent users

**Test Plan**:
```javascript
// k6 load test
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 100,
  duration: '5m',
};

export default function () {
  const res = http.post('http://localhost:8000/api/chat', {
    message: 'How do top companies measure PMF?',
  });
  
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 3s': (r) => r.timings.duration < 3000,
  });
  
  sleep(1);
}
```

**Expected Results**:
- ✅ 100 concurrent users supported
- ✅ P95 latency <5 seconds
- ✅ Error rate <1%
- ✅ No memory leaks

### 3.2 Stress Testing

**Target**: 500 concurrent users (beyond capacity)

**Expected Results**:
- ⚠️ Latency increases (acceptable)
- ⚠️ Some timeouts (acceptable)
- ❌ No crashes or data corruption

---

## 4. Security Tests

### 4.1 Input Validation

**Test**: SQL Injection
```
POST /api/chat
{"message": "'; DROP TABLE sessions; --"}
```

**Expected**: ✅ Input sanitized, no SQL injection

### 4.2 XSS Prevention

**Test**: XSS in artifact
```
<iframe>
  <script>alert('XSS')</script>
</iframe>
```

**Expected**: ✅ Sandboxed iframe blocks script execution

### 4.3 API Key Security

**Test**: Check .env not in Git
```bash
git ls-files | grep .env
```

**Expected**: ✅ No output (.env excluded)

---

## 5. Regression Tests

### 5.1 After Each Sprint

**Run**:
1. All unit tests (28 tests)
2. All integration tests
3. Manual test plan (TC-001 to TC-015)

**Expected**: ✅ All tests pass

### 5.2 Before Release

**Run**:
1. Full test suite
2. Load testing (100 concurrent users)
3. Security testing (SQL injection, XSS)
4. Accessibility audit (WCAG 2.1 AA)

**Expected**: ✅ All tests pass, no critical issues

---

## 6. Test Data

### Sample Queries

**RAG Queries**:
1. "How do top companies measure Product-Market Fit?"
2. "What growth loops work for B2B SaaS?"
3. "How do you build a successful referral program?"
4. "What are the best retention strategies?"
5. "Explain the 'Jobs to be Done' framework"

**Artifact Queries**:
1. "Write a PRD for a referral program"
2. "Create a dashboard for tracking growth metrics"
3. "Build a calculator for SaaS pricing"

**Essay Queries**:
1. "Ship 30: The future of product management"
2. "Write an essay on growth loops"

### Expected Citations

**Query**: "How do top companies measure PMF?"

**Expected Citations**:
1. Episode with Sean Ellis (PMF test)
2. Episode with retention metrics
3. Episode with 40% rule

**Relevance Threshold**: ≥0.5

---

## 7. Test Environment Setup

### Prerequisites

1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python scripts/ingest.py  # Ingest transcripts
   uvicorn app.main:app --reload
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Database**:
   ```bash
   docker-compose up -d postgres
   ```

4. **ChromaDB**:
   - Populated with 30,499 chunks
   - Path: `backend/chroma_db/`

### Test Execution

```bash
# Run all tests
cd backend
pytest

# Run manual tests
# Open http://localhost:5173 and follow TC-001 to TC-015
```

---

## 8. Defect Tracking

### Defect Severity

| Severity | Description | Example |
|----------|-------------|---------|
| **Critical** | System crash, data loss | Database connection fails |
| **High** | Major feature broken | RAG returns no citations |
| **Medium** | Minor feature broken | Citation doesn't expand |
| **Low** | Cosmetic issue | Misaligned text |

### Defect Template

```markdown
**Defect ID**: DEF-001
**Severity**: [Critical/High/Medium/Low]
**Test Case**: TC-003
**Description**: Response doesn't include citations
**Steps to Reproduce**:
1. Send query: "How do top companies measure PMF?"
2. Observe response

**Expected**: Response includes [Source N] citations
**Actual**: No citations displayed
**Environment**: Chrome 120, macOS
**Screenshot**: [link]
```

---

## 9. Sign-Off

**Tested By**: [Name]
**Date**: [YYYY-MM-DD]
**Result**: [Pass/Fail]

**Approvals**:
- [ ] Product Manager
- [ ] Engineering Lead
- [ ] QA Lead

---

**Repository**: https://github.com/Sudesh-chandra/lenny-growth-assistant
**Last Updated**: 2026-08-27
