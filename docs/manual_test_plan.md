# Manual Test Plan — Lenny Growth Assistant UI

## Prerequisites
- Backend running on port 8000
- Frontend running on port 5173
- Ollama running with at least one model pulled
- PostgreSQL running and accessible
- Transcripts ingested (`python -m scripts.ingest`)

---

## Test 1: Application Startup & Health

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1.1 | Open http://localhost:5173 | Frontend loads with sidebar, welcome screen |
| 1.2 | Check http://localhost:8000/health | Returns JSON with status "healthy" |
| 1.3 | Check http://localhost:8000/docs | Swagger UI shows all endpoints |
| 1.4 | Verify sidebar shows model selector | Ollama/Local toggle visible with model dropdown |

## Test 2: Session Management

| Step | Action | Expected Result |
|------|--------|-----------------|
| 2.1 | Click "New Chat" | Fresh chat view with suggestion cards |
| 2.2 | Type a message and press Enter | User message appears in chat |
| 2.3 | Wait for response | Assistant response streams token by token |
| 2.4 | Check sidebar | New session appears in session list |
| 2.5 | Refresh the page | Session persists, messages reload |
| 2.6 | Click on a different session | Previous messages load for that session |
| 2.7 | Hover over session → click delete | Session removed from list |

## Test 3: Grounded Q&A (RAG)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 3.1 | Ask "What is product-led growth?" | Response with [Source N] citations |
| 3.2 | Check citation badges below response | Badges show episode names and guests |
| 3.3 | Hover over citation badge | Tooltip shows source details |
| 3.4 | Ask a follow-up question | Response maintains conversation context |
| 3.5 | Ask something outside scope (e.g., "What's the weather?") | Graceful response acknowledging limits |

## Test 4: Ship 30 for 30 Content Skill

| Step | Action | Expected Result |
|------|--------|-----------------|
| 4.1 | Type "Write an essay about growth loops" | Response streams with essay formatting |
| 4.2 | Check response format | Has hook, subheadings, bullets, bold text |
| 4.3 | Check artifact panel | Markdown artifact slides in from right |
| 4.4 | Toggle to "Code" tab | Raw Markdown visible with syntax formatting |
| 4.5 | Click copy button | Content copied to clipboard, checkmark shown |

## Test 5: Artifact Generation

| Step | Action | Expected Result |
|------|--------|-----------------|
| 5.1 | Type "Create a pricing dashboard component" | Response with HTML code block |
| 5.2 | Check artifact panel opens | HTML artifact renders in sandboxed iframe |
| 5.3 | Verify Preview tab | Component renders correctly with styling |
| 5.4 | Toggle to Code tab | Raw HTML/CSS/JS visible |
| 5.5 | Close artifact panel | Panel slides away, chat expands |

## Test 6: Model Switching

| Step | Action | Expected Result |
|------|--------|-----------------|
| 6.1 | Check model selector shows Ollama | Green indicator, model name displayed |
| 6.2 | Switch to OpenAI (if key configured) | Provider changes, model dropdown updates |
| 6.3 | Send a message with new provider | Response comes from selected model |
| 6.4 | Switch back to Ollama | Provider toggle updates correctly |

## Test 7: Error Handling

| Step | Action | Expected Result |
|------|--------|-----------------|
| 7.1 | Stop Ollama, send a message | Error toast appears with clear message |
| 7.2 | Dismiss error toast | Toast disappears |
| 7.3 | Restart Ollama, send message | Response works normally |
| 7.4 | Send empty message | Send button disabled, no request sent |

## Test 8: Responsive Design

| Step | Action | Expected Result |
|------|--------|-----------------|
| 8.1 | Resize browser to mobile width | Sidebar collapses, toggle button visible |
| 8.2 | Click sidebar toggle | Sidebar slides in/out |
| 8.3 | Open artifact panel on narrow screen | Artifact takes appropriate space |

## Test 9: Accessibility

| Step | Action | Expected Result |
|------|--------|-----------------|
| 9.1 | Tab through all interactive elements | Focus rings visible on all elements |
| 9.2 | Press Enter on focused button | Button activates |
| 9.3 | Use screen reader on chat | Messages announced with role (user/assistant) |
| 9.4 | Zoom to 200% | Layout doesn't break, content readable |
