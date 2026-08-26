"""
Mock API Server for E2E Testing
================================
Provides realistic canned responses for all endpoints
so E2E tests can run without real LLM API keys.

Usage:
    python tests/e2e/mock_server.py
"""

import json
import asyncio
import uuid
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Lenny Growth Assistant Mock API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
sessions_db = {}
messages_db = {}
artifacts_db = {}


# ============================================================================
# Canned Responses
# ============================================================================

CANNED_RESPONSES = {
    "north_star": {
        "content": """## North Star Metrics in Top Startups

According to Lenny's guests, the **North Star Metric** is the single metric that best captures the core value your product delivers to customers.

### Key Principles

- **It must reflect customer value**, not just business revenue
- **It should be a leading indicator** of long-term growth
- **It needs to be measurable** and actionable by the team

### Examples from Lenny's Guests

1. **Spotify**: Time spent listening (not just signups)
2. **Airbnb**: Nights booked (reflects both supply and demand)
3. **Facebook**: Daily Active Users (engagement over registration)

### How to Define Yours

> "The North Star should be the metric that, if it goes up, means your customers are getting more value from your product." — Lenny Rachitsky

### Actionable Takeaway

Start by asking: *What is the one action that, when users take it, they're most likely to stick around?* That action, measured at scale, is often your North Star.

[Source 1] Lenny's Podcast - Episode on Growth Metrics
[Source 2] Interview with Sean Ellis on Product-Market Fit""",
        "citations": [
            {"source": "Growth Metrics Deep Dive", "guest": "Sean Ellis", "text_snippet": "The North Star metric captures the core value...", "chunk_id": "c1", "relevance_score": 0.92},
            {"source": "Product-Led Growth Strategies", "guest": "April Dunford", "text_snippet": "Leading indicators vs lagging indicators...", "chunk_id": "c2", "relevance_score": 0.87},
        ],
        "has_artifact": None,
    },
    "sourdough": {
        "content": """I don't have enough information from the available transcripts to answer this question thoroughly.

My knowledge is grounded in **Lenny's Podcast transcripts**, which focus on product management, growth strategies, and user research. Topics like baking sourdough bread fall outside this scope.

### What I Can Help With

- Product-led growth strategies
- User activation and retention
- Growth loops and viral mechanics
- Pricing and monetization
- Team building and hiring for product teams

Feel free to ask about any of these topics!""",
        "citations": [],
        "has_artifact": None,
    },
    "growth_loops_essay": {
        "content": """# The Hidden Engine of Sustainable Growth: Why Loops Beat Funnels

**Most startups are obsessed with funnels. They shouldn't be.**

Here's the uncomfortable truth: funnels leak. Every single stage loses users. You pour money into the top, and only a trickle comes out the bottom. The companies that win? They build **growth loops** — self-reinforcing systems where every new user makes the product better for the next user.

## The Problem with Funnels

Traditional growth funnels follow a linear path:

- **Awareness** → Interest → Consideration → Conversion → Retention

The issue? Each stage depends on the one before it. If awareness drops, everything downstream collapses. You're always one bad quarter away from a growth crisis.

## What Makes Loops Different

Growth loops are **circular**. The output of one cycle becomes the input of the next:

1. **User discovers product** → Uses it → Invites a friend → Friend discovers product → (loop repeats)

The magic? **Each iteration makes the loop stronger.** More users create more content, which attracts more users, which creates more content.

## Real Examples from Lenny's Guests

### Slack's Collaboration Loop
- Team adopts Slack → Invites more teammates → More conversations happen → Product becomes more valuable → More teams adopt

### Notion's Template Loop
- User creates template → Shares publicly → Others discover Notion → Create their own templates → (loop strengthens)

### Dropbox's Referral Loop
- User invites friend → Both get extra storage → Friend invites their friends → Storage network grows → (loop accelerates)

## The Three Types of Growth Loops

### 1. Viral Loops
Users invite other users as a natural part of using the product. Think: Calendly links, Figma share URLs, Loom videos.

### 2. Content Loops
User-generated content attracts new users through SEO or social sharing. Think: G2 reviews, Stack Overflow answers, Medium posts.

### 3. Paid Loops
Revenue from users funds acquisition of more users. Think: SaaS subscriptions funding Google Ads, which bring more subscribers.

## How to Build Your First Loop

**Step 1:** Map your user journey end-to-end
**Step 2:** Identify where users naturally interact with others
**Step 3:** Remove friction from that interaction
**Step 4:** Make the loop visible and measurable

> "The best growth loops feel like magic to the user. They don't feel like growth hacks — they feel like the product working exactly as intended." — Lenny Rachitsky

## The Takeaway

Stop pouring money into leaky funnels. Start building self-reinforcing loops. The startups that win the next decade will be the ones where **every new user makes the product better for the next user**.

**Your action item this week:** Map one growth loop in your product. Find the circular path where user behavior naturally leads to more user acquisition. Then optimize that single loop until it spins on its own.

[Source 1] Growth Loops Masterclass - Lenny's Podcast
[Source 2] Interview with Reforge on Viral Mechanics
[Source 3] Product-Led Growth Deep Dive""",
        "citations": [
            {"source": "Growth Loops Masterclass", "guest": "Brian Balfour", "text_snippet": "Funnels leak, loops compound...", "chunk_id": "c1", "relevance_score": 0.95},
            {"source": "Viral Mechanics Deep Dive", "guest": "Andrew Chen", "text_snippet": "The k-factor determines loop velocity...", "chunk_id": "c2", "relevance_score": 0.91},
        ],
        "has_artifact": "markdown",
        "artifact_data": {
            "artifact_type": "markdown",
            "title": "Essay: Growth Loops",
            "content": "# The Hidden Engine of Sustainable Growth: Why Loops Beat Funnels\n\n**Most startups are obsessed with funnels. They shouldn't be.**\n\nHere's the uncomfortable truth: funnels leak. Every single stage loses users. You pour money into the top, and only a trickle comes out the bottom. The companies that win? They build **growth loops** — self-reinforcing systems where every new user makes the product better for the next user.\n\n## The Problem with Funnels\n\nTraditional growth funnels follow a linear path:\n\n- **Awareness** → Interest → Consideration → Conversion → Retention\n\nThe issue? Each stage depends on the one before it. If awareness drops, everything downstream collapses. You're always one bad quarter away from a growth crisis.\n\n## What Makes Loops Different\n\nGrowth loops are **circular**. The output of one cycle becomes the input of the next:\n\n1. **User discovers product** → Uses it → Invites a friend → Friend discovers product → (loop repeats)\n\nThe magic? **Each iteration makes the loop stronger.** More users create more content, which attracts more users, which creates more content.\n\n## Real Examples from Lenny's Guests\n\n### Slack's Collaboration Loop\n- Team adopts Slack → Invites more teammates → More conversations happen → Product becomes more valuable → More teams adopt\n\n### Notion's Template Loop\n- User creates template → Shares publicly → Others discover Notion → Create their own templates → (loop strengthens)\n\n### Dropbox's Referral Loop\n- User invites friend → Both get extra storage → Friend invites their friends → Storage network grows → (loop accelerates)\n\n## The Three Types of Growth Loops\n\n### 1. Viral Loops\nUsers invite other users as a natural part of using the product. Think: Calendly links, Figma share URLs, Loom videos.\n\n### 2. Content Loops\nUser-generated content attracts new users through SEO or social sharing. Think: G2 reviews, Stack Overflow answers, Medium posts.\n\n### 3. Paid Loops\nRevenue from users funds acquisition of more users. Think: SaaS subscriptions funding Google Ads, which bring more subscribers.\n\n## How to Build Your First Loop\n\n**Step 1:** Map your user journey end-to-end\n**Step 2:** Identify where users naturally interact with others\n**Step 3:** Remove friction from that interaction\n**Step 4:** Make the loop visible and measurable\n\n> \"The best growth loops feel like magic to the user. They don't feel like growth hacks — they feel like the product working exactly as intended.\" — Lenny Rachitsky\n\n## The Takeaway\n\nStop pouring money into leaky funnels. Start building self-reinforcing loops. The startups that win the next decade will be the ones where **every new user makes the product better for the next user**.\n\n**Your action item this week:** Map one growth loop in your product. Find the circular path where user behavior naturally leads to more user acquisition. Then optimize that single loop until it spins on its own.\n\n[Source 1] Growth Loops Masterclass - Lenny's Podcast\n[Source 2] Interview with Reforge on Viral Mechanics\n[Source 3] Product-Led Growth Deep Dive",
        },
    },
    "pricing_dashboard": {
        "content": """Here's an interactive ROI calculator widget for your product growth team:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Growth ROI Calculator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .calculator { background: white; border-radius: 16px; padding: 40px; max-width: 500px; width: 100%; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        h1 { font-size: 24px; color: #1a202c; margin-bottom: 8px; }
        .subtitle { color: #718096; font-size: 14px; margin-bottom: 32px; }
        .input-group { margin-bottom: 24px; }
        label { display: block; font-size: 13px; font-weight: 600; color: #4a5568; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
        input[type="number"] { width: 100%; padding: 12px 16px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 16px; transition: border-color 0.2s; }
        input[type="number"]:focus { outline: none; border-color: #667eea; }
        .result { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 24px; border-radius: 12px; margin-top: 32px; text-align: center; }
        .result-label { font-size: 13px; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
        .result-value { font-size: 36px; font-weight: 700; }
        .result-sub { font-size: 14px; opacity: 0.8; margin-top: 8px; }
        .metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 24px; }
        .metric { background: #f7fafc; padding: 16px; border-radius: 8px; text-align: center; }
        .metric-value { font-size: 20px; font-weight: 700; color: #667eea; }
        .metric-label { font-size: 12px; color: #718096; margin-top: 4px; }
    </style>
</head>
<body>
    <div class="calculator">
        <h1>📈 Growth ROI Calculator</h1>
        <p class="subtitle">Estimate the return on your growth investments</p>
        <div class="input-group">
            <label>Monthly Users</label>
            <input type="number" id="users" value="10000" oninput="calculate()">
        </div>
        <div class="input-group">
            <label>Conversion Rate (%)</label>
            <input type="number" id="conversion" value="5" step="0.1" oninput="calculate()">
        </div>
        <div class="input-group">
            <label>Average Revenue Per User ($)</label>
            <input type="number" id="arpu" value="50" oninput="calculate()">
        </div>
        <div class="input-group">
            <label>Monthly Growth Spend ($)</label>
            <input type="number" id="spend" value="5000" oninput="calculate()">
        </div>
        <div class="result">
            <div class="result-label">Projected Monthly ROI</div>
            <div class="result-value" id="roi">$20,000</div>
            <div class="result-sub" id="roiPercent">400% return on investment</div>
        </div>
        <div class="metrics">
            <div class="metric">
                <div class="metric-value" id="customers">500</div>
                <div class="metric-label">New Customers</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="ltv">$25,000</div>
                <div class="metric-label">Monthly Revenue</div>
            </div>
        </div>
    </div>
    <script>
        function calculate() {
            const users = parseFloat(document.getElementById('users').value) || 0;
            const conversion = parseFloat(document.getElementById('conversion').value) || 0;
            const arpu = parseFloat(document.getElementById('arpu').value) || 0;
            const spend = parseFloat(document.getElementById('spend').value) || 0;
            const customers = Math.round(users * (conversion / 100));
            const revenue = customers * arpu;
            const roi = revenue - spend;
            const roiPercent = spend > 0 ? Math.round((roi / spend) * 100) : 0;
            document.getElementById('customers').textContent = customers.toLocaleString();
            document.getElementById('ltv').textContent = '$' + revenue.toLocaleString();
            document.getElementById('roi').textContent = '$' + roi.toLocaleString();
            document.getElementById('roiPercent').textContent = roiPercent + '% return on investment';
        }
        calculate();
    </script>
</body>
</html>
```

This calculator features real-time computation, a clean gradient design, and responsive layout. You can customize the inputs and styling to match your brand.""",
        "citations": [],
        "has_artifact": "html",
        "artifact_data": {
            "artifact_type": "html",
            "title": "Growth ROI Calculator",
            "content": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Growth ROI Calculator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .calculator { background: white; border-radius: 16px; padding: 40px; max-width: 500px; width: 100%; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        h1 { font-size: 24px; color: #1a202c; margin-bottom: 8px; }
        .subtitle { color: #718096; font-size: 14px; margin-bottom: 32px; }
        .input-group { margin-bottom: 24px; }
        label { display: block; font-size: 13px; font-weight: 600; color: #4a5568; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
        input[type="number"] { width: 100%; padding: 12px 16px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 16px; transition: border-color 0.2s; }
        input[type="number"]:focus { outline: none; border-color: #667eea; }
        .result { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 24px; border-radius: 12px; margin-top: 32px; text-align: center; }
        .result-label { font-size: 13px; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
        .result-value { font-size: 36px; font-weight: 700; }
        .result-sub { font-size: 14px; opacity: 0.8; margin-top: 8px; }
        .metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 24px; }
        .metric { background: #f7fafc; padding: 16px; border-radius: 8px; text-align: center; }
        .metric-value { font-size: 20px; font-weight: 700; color: #667eea; }
        .metric-label { font-size: 12px; color: #718096; margin-top: 4px; }
    </style>
</head>
<body>
    <div class="calculator">
        <h1>📈 Growth ROI Calculator</h1>
        <p class="subtitle">Estimate the return on your growth investments</p>
        <div class="input-group">
            <label>Monthly Users</label>
            <input type="number" id="users" value="10000" oninput="calculate()">
        </div>
        <div class="input-group">
            <label>Conversion Rate (%)</label>
            <input type="number" id="conversion" value="5" step="0.1" oninput="calculate()">
        </div>
        <div class="input-group">
            <label>Average Revenue Per User ($)</label>
            <input type="number" id="arpu" value="50" oninput="calculate()">
        </div>
        <div class="input-group">
            <label>Monthly Growth Spend ($)</label>
            <input type="number" id="spend" value="5000" oninput="calculate()">
        </div>
        <div class="result">
            <div class="result-label">Projected Monthly ROI</div>
            <div class="result-value" id="roi">$20,000</div>
            <div class="result-sub" id="roiPercent">400% return on investment</div>
        </div>
        <div class="metrics">
            <div class="metric">
                <div class="metric-value" id="customers">500</div>
                <div class="metric-label">New Customers</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="ltv">$25,000</div>
                <div class="metric-label">Monthly Revenue</div>
            </div>
        </div>
    </div>
    <script>
        function calculate() {
            const users = parseFloat(document.getElementById('users').value) || 0;
            const conversion = parseFloat(document.getElementById('conversion').value) || 0;
            const arpu = parseFloat(document.getElementById('arpu').value) || 0;
            const spend = parseFloat(document.getElementById('spend').value) || 0;
            const customers = Math.round(users * (conversion / 100));
            const revenue = customers * arpu;
            const roi = revenue - spend;
            const roiPercent = spend > 0 ? Math.round((roi / spend) * 100) : 0;
            document.getElementById('customers').textContent = customers.toLocaleString();
            document.getElementById('ltv').textContent = '$' + revenue.toLocaleString();
            document.getElementById('roi').textContent = '$' + roi.toLocaleString();
            document.getElementById('roiPercent').textContent = roiPercent + '% return on investment';
        }
        calculate();
    </script>
</body>
</html>""",
        },
    },
    "plg": {
        "content": """## Product-Led Growth (PLG) Explained

**Product-Led Growth** is a go-to-market strategy where the product itself is the primary driver of customer acquisition, conversion, and retention.

### Core Principles

- **Self-serve onboarding**: Users can try the product without talking to sales
- **Value-first**: Users experience the "aha moment" before paying
- **Viral mechanics**: The product naturally encourages sharing

### Key Metrics for PLG

1. **Time to Value (TTV)**: How quickly users reach the core value
2. **Activation Rate**: % of users who complete the key action
3. **Expansion Revenue**: Revenue from existing users growing their usage

### PLG vs Sales-Led

| Aspect | PLG | Sales-Led |
|--------|-----|-----------|
| Acquisition | Product virality | Outbound sales |
| Trial | Self-serve | Demo/POC |
| Conversion | In-product | Sales rep |
| Expansion | Usage-based | Account management |

### Examples

- **Slack**: Team adoption spreads organically
- **Figma**: Designers invite developers
- **Notion**: Templates shared publicly

> "In PLG, the product is the marketing, the sales team, and the customer success team all rolled into one." — Lenny Rachitsky

[Source 1] PLG Deep Dive - Lenny's Podcast
[Source 2] Interview with OpenView on Product-Led Strategies""",
        "citations": [
            {"source": "PLG Deep Dive", "guest": "Kyle Poyar", "text_snippet": "Product-led growth flips the traditional model...", "chunk_id": "c1", "relevance_score": 0.94},
        ],
        "has_artifact": None,
    },
}


def detect_intent(message: str) -> str:
    """Detect which canned response to use based on the message."""
    msg_lower = message.lower()
    if "north star" in msg_lower or "metric" in msg_lower:
        return "north_star"
    elif "sourdough" in msg_lower or "bread" in msg_lower or "bake" in msg_lower or "recipe" in msg_lower or "italian" in msg_lower:
        return "sourdough"
    elif "essay" in msg_lower or "ship 30" in msg_lower or "growth loop" in msg_lower:
        return "growth_loops_essay"
    elif "pricing" in msg_lower or "dashboard" in msg_lower or "calculator" in msg_lower or "widget" in msg_lower or "component" in msg_lower:
        return "pricing_dashboard"
    elif "plg" in msg_lower or "product-led" in msg_lower:
        return "plg"
    else:
        return "north_star"  # Default to a helpful response


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0-mock",
        "database": "connected (mock)",
        "llm_provider": "mock",
        "vector_store": "connected (303 chunks)",
    }


@app.get("/api/models")
async def list_models():
    return {
        "models": [
            {"provider": "ollama", "model_id": "llama3", "display_name": "Llama 3", "is_local": True, "is_available": True},
            {"provider": "openrouter", "model_id": "anthropic/claude-sonnet-4", "display_name": "Claude Sonnet 4", "is_local": False, "is_available": True},
            {"provider": "openai", "model_id": "gpt-4o", "display_name": "GPT-4o", "is_local": False, "is_available": True},
            {"provider": "anthropic", "model_id": "claude-3-sonnet-20240229", "display_name": "Claude 3 Sonnet", "is_local": False, "is_available": True},
        ],
        "active_provider": "openrouter",
        "active_model": "anthropic/claude-sonnet-4",
    }


@app.post("/api/sessions")
async def create_session(body: dict = {}):
    session_id = str(uuid.uuid4())
    session = {
        "id": session_id,
        "title": body.get("title", "New Chat"),
        "created_at": "2026-08-26T12:00:00Z",
        "updated_at": "2026-08-26T12:00:00Z",
        "llm_provider": body.get("llm_provider", "openrouter"),
        "model_name": body.get("model_name", "anthropic/claude-sonnet-4"),
    }
    sessions_db[session_id] = session
    messages_db[session_id] = []
    return session


@app.get("/api/sessions")
async def list_sessions():
    return list(sessions_db.values())


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    if session_id not in sessions_db:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions_db[session_id]


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    sessions_db.pop(session_id, None)
    messages_db.pop(session_id, None)
    return {"status": "deleted", "session_id": session_id}


@app.get("/api/sessions/{session_id}/messages")
async def get_messages(session_id: str):
    return messages_db.get(session_id, [])


@app.post("/api/chat")
async def chat(body: dict):
    """Non-streaming chat endpoint."""
    session_id = body.get("session_id") or str(uuid.uuid4())
    if session_id not in sessions_db:
        sessions_db[session_id] = {
            "id": session_id,
            "title": body.get("message", "New Chat")[:50],
            "created_at": "2026-08-26T12:00:00Z",
            "updated_at": "2026-08-26T12:00:00Z",
            "llm_provider": body.get("llm_provider", "openrouter"),
            "model_name": body.get("model_name", "anthropic/claude-sonnet-4"),
        }
        messages_db[session_id] = []

    intent = detect_intent(body["message"])
    response = CANNED_RESPONSES[intent]

    msg_id = str(uuid.uuid4())
    messages_db[session_id].append({
        "id": msg_id,
        "session_id": session_id,
        "role": "user",
        "content": body["message"],
        "citations": [],
        "has_artifact": None,
        "artifact_id": None,
        "created_at": "2026-08-26T12:00:00Z",
        "token_count": None,
    })

    artifact_id = None
    if response.get("artifact_data"):
        artifact_id = str(uuid.uuid4())
        artifacts_db[artifact_id] = {
            "id": artifact_id,
            "session_id": session_id,
            "artifact_type": response["artifact_data"]["artifact_type"],
            "title": response["artifact_data"]["title"],
            "content": response["artifact_data"]["content"],
            "metadata": None,
            "created_at": "2026-08-26T12:00:00Z",
        }

    messages_db[session_id].append({
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "role": "assistant",
        "content": response["content"],
        "citations": response.get("citations", []),
        "has_artifact": response.get("has_artifact"),
        "artifact_id": artifact_id,
        "created_at": "2026-08-26T12:00:00Z",
        "token_count": None,
    })

    return {
        "session_id": session_id,
        "message_id": msg_id,
        "content": response["content"],
        "citations": response.get("citations", []),
        "has_artifact": response.get("has_artifact"),
        "artifact_id": artifact_id,
        "artifact_title": response.get("artifact_data", {}).get("title"),
    }


@app.post("/api/chat/stream")
async def chat_stream(body: dict):
    """SSE streaming chat endpoint with canned responses."""
    session_id = body.get("session_id") or str(uuid.uuid4())
    if session_id not in sessions_db:
        sessions_db[session_id] = {
            "id": session_id,
            "title": body.get("message", "New Chat")[:50],
            "created_at": "2026-08-26T12:00:00Z",
            "updated_at": "2026-08-26T12:00:00Z",
            "llm_provider": body.get("llm_provider", "openrouter"),
            "model_name": body.get("model_name", "anthropic/claude-sonnet-4"),
        }
        messages_db[session_id] = []

    intent = detect_intent(body["message"])
    response = CANNED_RESPONSES[intent]

    async def event_generator():
        # Send session ID
        yield f"data: {json.dumps({'type': 'session', 'data': {'session_id': session_id}})}\n\n"
        await asyncio.sleep(0.1)

        # Send citations first
        if response.get("citations"):
            yield f"data: {json.dumps({'type': 'citations', 'data': response['citations']})}\n\n"
            await asyncio.sleep(0.1)

        # Stream the content token by token (word by word for realism)
        content = response["content"]
        words = content.split(" ")
        for i, word in enumerate(words):
            token = word + (" " if i < len(words) - 1 else "")
            yield f"data: {json.dumps({'type': 'token', 'data': token})}\n\n"
            await asyncio.sleep(0.02)  # 20ms per word = realistic streaming speed

        # Send artifact if present
        if response.get("artifact_data"):
            yield f"data: {json.dumps({'type': 'artifact', 'data': response['artifact_data']})}\n\n"
            await asyncio.sleep(0.1)

        # Send done
        yield f"data: {json.dumps({'type': 'done', 'data': ''})}\n\n"

        # Save to "database"
        messages_db[session_id].append({
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "role": "user",
            "content": body["message"],
            "citations": [],
            "has_artifact": None,
            "artifact_id": None,
            "created_at": "2026-08-26T12:00:00Z",
            "token_count": None,
        })

        artifact_id = None
        if response.get("artifact_data"):
            artifact_id = str(uuid.uuid4())
            artifacts_db[artifact_id] = {
                "id": artifact_id,
                "session_id": session_id,
                "artifact_type": response["artifact_data"]["artifact_type"],
                "title": response["artifact_data"]["title"],
                "content": response["artifact_data"]["content"],
                "metadata": None,
                "created_at": "2026-08-26T12:00:00Z",
            }

        messages_db[session_id].append({
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "role": "assistant",
            "content": content,
            "citations": response.get("citations", []),
            "has_artifact": response.get("has_artifact"),
            "artifact_id": artifact_id,
            "created_at": "2026-08-26T12:00:00Z",
            "token_count": None,
        })

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/artifacts/{artifact_id}")
async def get_artifact(artifact_id: str):
    if artifact_id not in artifacts_db:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifacts_db[artifact_id]


if __name__ == "__main__":
    import uvicorn
    print("🤖 Mock API Server starting on http://localhost:8001")
    print("   (Use this for E2E testing without real LLM API keys)")
    uvicorn.run(app, host="0.0.0.0", port=8001)
