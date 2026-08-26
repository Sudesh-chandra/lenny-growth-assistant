# Demo Video Script — The Lenny Growth Assistant
## Target: 2–3 minutes, camera enabled

---

## Scene 1: Problem Statement (0:00 – 0:30)

**[Camera on, screen showing the app's welcome screen]**

> "Hi, I'm [Your Name]. Today I'm walking you through **The Lenny Growth Assistant** — a full-stack AI application I built as a forward-deployment engagement.
>
> Here's the problem: Lenny's Podcast has hundreds of episodes covering product management, growth strategy, and user research. But finding specific insights across this massive library means re-listening to hours of content. Product teams need **quick, grounded answers** with proper attribution — not generic AI responses.
>
> So I built an assistant that ingests all 303 episodes, answers questions with **traceable citations**, generates formatted content, and creates interactive artifacts — all in a polished web interface."

---

## Scene 2: Live Product Demo (0:30 – 1:45)

**[Switch to screen recording of the app]**

### Grounded Q&A
> "Let me start with the core experience — grounded Q&A. I'll ask a product question."

**[Type: "What is product-led growth?"]**

> "Notice the response streams token by token using Server-Sent Events. More importantly, see these citation badges? Each one links back to a specific Lenny's Podcast episode and guest. This isn't hallucinated — it's grounded in real transcript data retrieved from our vector store."

**[Hover over a citation badge to show the tooltip]**

### Out-of-Scope Handling
> "Now let me test what happens when I ask something completely outside the knowledge base."

**[Type: "What's the best recipe for pasta carbonara?"]**

> "The assistant gracefully acknowledges the limits of its knowledge rather than making something up. This strict grounding is critical for trust."

### Ship 30 for 30 Content Skill
> "Next, the content generation skill. I'll ask it to write a Ship 30 essay."

**[Type: "Write an essay about growth loops based on Lenny's transcripts"]**

> "The response follows Ship 30 for 30 principles: a strong hook, skimmable subheadings, bullet points, selective bold text, and actionable takeaways — all around 1,250 words. The Markdown renders in the artifact panel on the right."

### Artifact Generation
> "Finally, let me generate an interactive HTML artifact."

**[Type: "Create a pricing dashboard component"]**

> "A complete HTML/CSS component renders in a **sandboxed iframe** right next to the chat. I can toggle between the Preview and the raw Code view, and copy the code with one click."

---

## Scene 3: Local Ollama Demonstration (1:45 – 2:15)

**[Switch to terminal showing Ollama]**

> "A key requirement was supporting **local LLMs** for environments where cloud APIs aren't an option. Let me switch to Ollama."

**[In the UI sidebar, click "Local" to switch to Ollama]**

> "The sidebar shows the model toggle — Local, OpenRouter, OpenAI, and Claude. I'll switch to Local Ollama running Llama 3."

**[Send a simple question like "How do activation metrics work?"]**

> "The response comes from the local model. The architecture uses an adapter pattern — a unified interface that routes to whichever provider is selected, so the application code doesn't change at all.
>
> In production, you'd use cloud models for quality, but Ollama gives you a fully offline demo path."

---

## Scene 4: Key Technical Trade-off (2:15 – 2:45)

**[Camera back on, or screen showing architecture diagram]**

> "One important trade-off I want to highlight is the **artifact security model**.
>
> Generated HTML is inherently untrusted — an LLM could produce JavaScript that steals cookies or accesses localStorage. My solution is **defense in depth**:
>
> First, **DOMPurify** sanitizes the HTML before rendering — stripping iframes, event handlers, and javascript URIs. Second, the artifact renders inside a **sandboxed iframe** with `sandbox='allow-scripts'` but explicitly **without** `allow-same-origin`. This means the artifact runs in a unique origin, completely isolated from the parent application.
>
> It can execute JavaScript for interactivity, but it **cannot** access the app's cookies, DOM, or storage. This is the same approach used by production artifact systems."

---

## Scene 5: Wrap-Up (2:45 – 3:00)

**[Camera on]**

> "The full stack is deployable with a single `docker compose up` command — PostgreSQL, FastAPI backend, React frontend, all orchestrated together.
>
> The code is clean, tested with 28 automated tests, and documented with a PRD, architecture doc, and design doc.
>
> Thanks for watching — I'm happy to dive deeper into any part of the implementation."

---

## Pre-Recording Checklist

- [ ] Ollama running with `llama3` pulled (`ollama pull llama3`)
- [ ] Transcripts ingested (`python -m scripts.ingest`)
- [ ] Backend running (`uvicorn app.main:app --reload`)
- [ ] Frontend running (`npm run dev`)
- [ ] All 3 API keys configured in `.env` (OpenAI, Anthropic, OpenRouter)
- [ ] Browser at http://localhost:5173 with clean session
- [ ] Terminal ready to show `ollama list` and `curl localhost:11434/api/tags`
- [ ] Screen recording software ready (OBS, Loom, or Zoom)
- [ ] Camera enabled and well-lit
- [ ] Practice run-through completed once
