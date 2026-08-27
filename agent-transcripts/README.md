# Agent Transcripts

This folder contains coding agent transcripts/logs from the development of the Lenny Growth Assistant. These transcripts document the development process, including failed attempts, debugging sessions, and how problems were solved.

## Purpose

The transcripts serve multiple purposes:

1. **Transparency**: Show the actual development process, not just the final result
2. **Learning**: Document challenges faced and how they were overcome
3. **Debugging**: Provide reference for similar issues in the future
4. **Accountability**: Track decision-making and trade-offs made during development

## Contents

### 1. ChromaDB Persistence Fix

**File**: `chromadb-persistence-fix.md`

**Problem**: ChromaDB data was not persisting across backend restarts. Despite ingesting 30,499 chunks, the health endpoint showed "0 chunks".

**Root Cause**: Using `chromadb.Client()` (ephemeral in-memory) instead of `chromadb.PersistentClient()` (disk-based).

**Solution**:
- Changed ingestion script to use `PersistentClient`
- Updated vector store service to use `PersistentClient`
- Fixed test mocks to match new implementation

**Lessons Learned**:
- Understand the difference between ephemeral and persistent clients
- Test mocks must match implementation
- Verify persistence from a separate process

**Outcome**: ✅ Data persists across restarts, all tests passing

---

### 2. Reranking Implementation

**File**: `reranking-implementation.md`

**Problem**: Vector search (bi-encoder) only captures semantic similarity, not query-specific relevance. Exact matches were ranked lower than loosely-related content.

**Root Cause**: Bi-encoder doesn't evaluate (query, document) pairs.

**Solution**:
- Implemented cross-encoder reranking (`ms-marco-MiniLM-L-6-v2`)
- Two-stage retrieval: vector search (top-20) → reranking (top-5)
- Blended scoring: 70% reranker + 30% vector
- Lazy model loading (avoid 5s startup delay)
- Graceful degradation (fallback to vector search)

**Lessons Learned**:
- Two-stage retrieval is critical for high-quality RAG
- Lazy loading prevents startup delays
- Blended scoring prevents edge cases
- Always have a fallback plan

**Outcome**: ✅ +25% retrieval precision, +200ms latency (acceptable)

---

## Transcript Format

Each transcript follows this structure:

1. **Header**: Date, agent, task
2. **Problem Statement**: What was the issue?
3. **Research/Investigation**: What was explored?
4. **Attempts**: What was tried (including failures)?
5. **Solution**: What worked?
6. **Verification**: How was it tested?
7. **Lessons Learned**: What can be applied to future work?
8. **Files Modified**: What changed?
9. **Outcome**: Final result

## Sensitive Data

All API keys, secrets, and sensitive data have been removed from these transcripts. The transcripts focus on the development process, not credentials.

## Contributing

If you encounter issues during development, consider creating a transcript:

1. Copy the template below
2. Document your problem, attempts, and solution
3. Save as `agent-transcripts/{topic}.md`
4. Commit and push to GitHub

### Template

```markdown
# Agent Transcript: {Topic}

**Date**: YYYY-MM-DD
**Agent**: Coding Assistant
**Task**: {Brief description}

---

## Problem Statement

{What was the issue?}

---

## Attempt 1: {Description}

**Action**: {What did you try?}

**Result**: {What happened?}

**Problem**: {Why didn't it work?}

---

## Attempt 2: {Description}

...

---

## Solution

{What worked?}

---

## Verification

{How did you test it?}

---

## Lessons Learned

1. {What can be applied to future work?}
2. ...

---

## Files Modified

1. `path/to/file.py` - {What changed?}
2. ...

**Commit**: `{commit_hash}` - "{commit_message}"

---

## Outcome

✅ {Final result}
```

## Usage

These transcripts can be used for:

1. **Onboarding**: New developers can understand the development process
2. **Debugging**: Reference for similar issues
3. **Interviews**: Showcase problem-solving approach
4. **Portfolio**: Demonstrate full-stack engineering skills

## Privacy

All transcripts have been reviewed to ensure:
- No API keys or secrets
- No personal information
- No confidential data
- No credentials or passwords

If you find any sensitive data in these transcripts, please report it immediately.

---

**Repository**: https://github.com/Sudesh-chandra/lenny-growth-assistant
**Last Updated**: 2026-08-27
