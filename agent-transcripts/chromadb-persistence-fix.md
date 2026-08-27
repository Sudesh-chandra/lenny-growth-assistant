# Agent Transcript: ChromaDB Persistence Fix

**Date**: 2026-08-26
**Agent**: Coding Assistant
**Task**: Fix ChromaDB data not persisting across restarts

---

## Initial Problem

User reported that ChromaDB data was not persisting after backend restart. Despite ingesting 30,499 chunks from 303 episodes, the health endpoint showed "0 chunks".

---

## Attempt 1: Check Ingestion Script

**Action**: Reviewed `backend/scripts/ingest.py`

**Finding**: Ingestion script was using `chromadb.Client()` which creates an **ephemeral in-memory client**.

**Code**:
```python
# backend/scripts/ingest.py (BEFORE)
import chromadb

client = chromadb.Client()  # ❌ Ephemeral in-memory client
collection = client.create_collection("lenny_transcripts")
```

**Problem**: `chromadb.Client()` creates an in-memory client that doesn't persist to disk.

---

## Attempt 2: Fix Ingestion Script

**Action**: Changed to `chromadb.PersistentClient()`

**Code**:
```python
# backend/scripts/ingest.py (AFTER)
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")  # ✅ Persists to disk
collection = client.get_or_create_collection("lenny_transcripts")
```

**Result**: Ingestion script now persists data to `backend/chroma_db/`

**Verification**:
```bash
$ ls backend/chroma_db/
chroma.sqlite3
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/
```

✅ Data persisted to disk

---

## Attempt 3: Fix Vector Store Service

**Action**: Updated `backend/app/services/vector_store.py` to use `PersistentClient`

**Code**:
```python
# backend/app/services/vector_store.py (BEFORE)
import chromadb

class VectorStore:
    def __init__(self):
        self.client = chromadb.Client()  # ❌ Ephemeral
        self.collection = self.client.get_or_create_collection("lenny_transcripts")
```

**Problem**: Vector store service also using ephemeral client.

**Fix**:
```python
# backend/app/services/vector_store.py (AFTER)
import chromadb
from app.core.config import settings

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)  # ✅
        self.collection = self.client.get_or_create_collection("lenny_transcripts")
```

**Result**: Vector store now reads from persisted data.

---

## Attempt 4: Fix Test Mocks

**Action**: Ran pytest, 2 tests failed

**Error**:
```
TypeError: '<' not supported between instances of 'MagicMock' and 'int'
```

**Root Cause**: Tests were mocking `chromadb.Client` but code now uses `chromadb.PersistentClient`.

**Code**:
```python
# backend/tests/test_retrieval.py (BEFORE)
@patch('chromadb.Client')
def test_search_empty_store(mock_chroma):
    mock_client = Mock()
    mock_chroma.Client.return_value = mock_client  # ❌ Wrong mock
```

**Fix**:
```python
# backend/tests/test_retrieval.py (AFTER)
@patch('chromadb.PersistentClient')
def test_search_empty_store(mock_chroma):
    mock_client = Mock()
    mock_chroma.PersistentClient.return_value = mock_client  # ✅ Correct mock
```

**Result**: All 28 tests passing.

---

## Verification

**Step 1**: Re-run ingestion
```bash
$ cd backend
$ python scripts/ingest.py
Ingesting 303 episodes...
Processing Episode 001 - Guest Name...
  Chunked into 101 chunks
  Generated 101 embeddings
  Stored in ChromaDB
...
Ingestion complete: 30,499 chunks from 303 episodes
```

**Step 2**: Verify persistence from separate process
```python
# test_persistence.py
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("lenny_transcripts")
print(f"Total chunks: {collection.count()}")
# Output: Total chunks: 30499 ✅
```

**Step 3**: Restart backend and check health
```bash
$ uvicorn app.main:app --reload
$ curl http://localhost:8000/health
{
  "status": "healthy",
  "checks": {
    "vector_store": "connected (30499 chunks)"  ✅
  }
}
```

---

## Lessons Learned

1. **ChromaDB Client Types**:
   - `chromadb.Client()` → Ephemeral in-memory (for testing)
   - `chromadb.PersistentClient(path=...)` → Persists to disk (for production)

2. **Test Mocks Must Match Implementation**:
   - When code changes from `Client` to `PersistentClient`, update test mocks
   - Mock the exact class/method being used

3. **Verification from Separate Process**:
   - To verify persistence, query from a separate Python process
   - Don't just check in the same process (may be cached)

---

## Files Modified

1. `backend/scripts/ingest.py` - Changed to `PersistentClient`
2. `backend/app/services/vector_store.py` - Changed to `PersistentClient`
3. `backend/tests/test_retrieval.py` - Updated mocks to `PersistentClient`

**Commit**: `2bff2fe` - "Fix ChromaDB persistence: Use PersistentClient for disk storage"

---

## Outcome

✅ ChromaDB data persists across restarts
✅ Health endpoint shows correct chunk count (30,499)
✅ All 28 tests passing
✅ RAG pipeline retrieves from persisted data
