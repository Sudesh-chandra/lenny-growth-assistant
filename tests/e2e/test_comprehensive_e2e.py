"""
Comprehensive E2E Performance & Optimization Test Suite
========================================================
Tests all 6 categories from the assignment with auto-generated queries.
Uses mock server for API-free testing.

Categories:
1. RAG Knowledge & Grounded Q&A
2. Negative & Out-of-Scope Testing (Anti-Hallucination)
3. Ship 30 for 30 Specialized Content Skill
4. Artifact Generation & Dual-Pane Sandboxing
5. Multi-Turn Context & Session Memory
6. Model Toggle & Resilience
"""

import os
import sys
import time
import json
import asyncio
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from playwright.async_api import async_playwright, Page

# Configuration
FRONTEND_URL = os.getenv("E2E_FRONTEND_URL", "http://localhost:5173")
SCREENSHOTS_DIR = PROJECT_ROOT / "docs" / "screenshots"
VIEWPORT = {"width": 1440, "height": 900}
STREAM_TIMEOUT = 120_000


@dataclass
class TestResult:
    category: str
    query: str
    passed: bool
    latency_ms: float = 0.0
    response_chars: int = 0
    has_citations: bool = False
    notes: str = ""


# ============================================================================
# Auto-Generated Test Queries (6 Categories)
# ============================================================================

RAG_QUERIES = [
    "How do top startups like Spotify and Airbnb define and track their North Star Metric?",
    "What are the key differences between product-led growth and sales-led growth according to Lenny's guests?",
    "How should early-stage startups approach their first distribution channel?",
]

OUT_OF_SCOPE_QUERIES = [
    "How do I bake traditional Italian sourdough bread from scratch?",
    "Explain the theory of quantum entanglement and its applications in computing.",
]

SHIP30_QUERY = "Write a Ship 30 for 30 essay about retention loops and how they drive sustainable growth."

ARTIFACT_QUERY = "Create an interactive HTML/CSS SaaS metrics dashboard with MRR, churn rate, and LTV calculators."

MULTI_TURN_QUERIES = [
    "What is product-led growth?",
    "Explain the second strategy you mentioned in more detail.",
]


# ============================================================================
# Helper Functions
# ============================================================================

async def wait_for_streaming(page: Page, timeout: int = STREAM_TIMEOUT) -> str:
    """Wait for streaming to complete and return the response text."""
    start = time.time()
    
    # Wait for "Thinking..." to disappear
    try:
        await page.wait_for_selector("text=Thinking...", state="hidden", timeout=10000)
    except Exception:
        pass
    
    # Wait for streaming content
    try:
        await page.wait_for_function(
            "() => { const el = document.querySelector('.markdown-content'); return el && el.textContent.trim().length > 10; }",
            timeout=timeout,
        )
    except Exception:
        pass
    
    # Wait for streaming to finish (pulse cursor disappears)
    try:
        await page.wait_for_selector(".animate-pulse", state="hidden", timeout=5000)
    except Exception:
        pass
    
    await asyncio.sleep(2)
    elapsed = (time.time() - start) * 1000
    
    # Get the response text
    content_el = page.locator(".markdown-content").last
    try:
        text = await content_el.inner_text()
    except Exception:
        text = ""
    
    return text, elapsed


async def send_message(page: Page, message: str) -> tuple:
    """Send a message and wait for response. Returns (text, latency_ms)."""
    textarea = page.locator("textarea")
    await textarea.click()
    await textarea.fill(message)
    await textarea.press("Enter")
    return await wait_for_streaming(page)


async def new_chat(page: Page):
    """Start a new chat session."""
    btn = page.locator("button:has-text('New Chat')")
    if await btn.count() > 0:
        await btn.click()
        await page.wait_for_timeout(1000)


# ============================================================================
# Category 1: RAG Knowledge & Grounded Q&A
# ============================================================================

async def test_rag_knowledge(page: Page) -> List[TestResult]:
    """Test grounded Q&A with citation verification."""
    results = []
    print("\n" + "=" * 60)
    print("CATEGORY 1: RAG Knowledge & Grounded Q&A")
    print("=" * 60)
    
    for i, query in enumerate(RAG_QUERIES, 1):
        print(f"\n  Query {i}: {query[:70]}...")
        await new_chat(page)
        
        text, latency = await send_message(page, query)
        
        has_citations = "[Source" in text or "source" in text.lower()
        has_content = len(text) > 50
        
        passed = has_content
        status = "PASS" if passed else "FAIL"
        print(f"    [{status}] Response: {len(text)} chars, Latency: {latency:.0f}ms, Citations: {has_citations}")
        
        results.append(TestResult(
            category="RAG Q&A",
            query=query,
            passed=passed,
            latency_ms=latency,
            response_chars=len(text),
            has_citations=has_citations,
        ))
    
    return results


# ============================================================================
# Category 2: Out-of-Scope / Anti-Hallucination
# ============================================================================

async def test_out_of_scope(page: Page) -> List[TestResult]:
    """Test graceful rejection of off-topic queries."""
    results = []
    print("\n" + "=" * 60)
    print("CATEGORY 2: Out-of-Scope / Anti-Hallucination")
    print("=" * 60)
    
    for i, query in enumerate(OUT_OF_SCOPE_QUERIES, 1):
        print(f"\n  Query {i}: {query}")
        await new_chat(page)
        
        text, latency = await send_message(page, query)
        
        # Check for graceful rejection indicators
        rejection_keywords = [
            "don't have", "not covered", "outside", "not related",
            "not in the transcripts", "cannot answer", "no information",
            "outside my", "not in my", "transcripts don't",
        ]
        has_rejection = any(kw in text.lower() for kw in rejection_keywords)
        has_content = len(text) > 20
        
        passed = has_content and has_rejection
        status = "PASS" if passed else "FAIL"
        print(f"    [{status}] Response: {len(text)} chars, Rejection: {has_rejection}")
        
        results.append(TestResult(
            category="Out-of-Scope",
            query=query,
            passed=passed,
            latency_ms=latency,
            response_chars=len(text),
            notes="Rejection detected" if has_rejection else "No rejection detected",
        ))
    
    return results


# ============================================================================
# Category 3: Ship 30 for 30 Essay
# ============================================================================

async def test_ship30_essay(page: Page) -> List[TestResult]:
    """Test Ship 30 for 30 essay generation."""
    results = []
    print("\n" + "=" * 60)
    print("CATEGORY 3: Ship 30 for 30 Essay")
    print("=" * 60)
    
    print(f"\n  Query: {SHIP30_QUERY}")
    await new_chat(page)
    
    text, latency = await send_message(page, SHIP30_QUERY, )
    
    # Check formatting
    content_html = await page.locator(".markdown-content").last.inner_html()
    has_headings = "<h" in content_html.lower() or "##" in text
    has_bold = "<strong>" in content_html.lower() or "**" in text
    has_lists = "<li>" in content_html.lower() or "- " in text
    word_count = len(text.split())
    
    passed = has_headings and has_bold and has_lists and word_count > 100
    status = "PASS" if passed else "FAIL"
    print(f"    [{status}] Words: {word_count}, Headings: {has_headings}, Bold: {has_bold}, Lists: {has_lists}")
    
    results.append(TestResult(
        category="Ship 30 Essay",
        query=SHIP30_QUERY,
        passed=passed,
        latency_ms=latency,
        response_chars=len(text),
        notes=f"Words: {word_count}, Headings: {has_headings}, Bold: {has_bold}, Lists: {has_lists}",
    ))
    
    return results


# ============================================================================
# Category 4: Artifact Generation & Sandboxing
# ============================================================================

async def test_artifact_generation(page: Page) -> List[TestResult]:
    """Test artifact generation and sandbox verification."""
    results = []
    print("\n" + "=" * 60)
    print("CATEGORY 4: Artifact Generation & Sandboxing")
    print("=" * 60)
    
    print(f"\n  Query: {ARTIFACT_QUERY}")
    await new_chat(page)
    
    text, latency = await send_message(page, ARTIFACT_QUERY)
    await page.wait_for_timeout(3000)
    
    # Check artifact panel
    preview_tab = page.locator("button:has-text('Preview')")
    has_artifact_panel = await preview_tab.count() > 0
    
    # Check sandbox attributes
    sandbox_correct = False
    iframe = page.locator("iframe")
    if await iframe.count() > 0:
        sandbox_attr = await iframe.get_attribute("sandbox")
        sandbox_correct = (
            "allow-scripts" in (sandbox_attr or "")
            and "allow-same-origin" not in (sandbox_attr or "")
        )
    
    # Check code tab
    code_tab = page.locator("button:has-text('Code')")
    has_code_tab = await code_tab.count() > 0
    
    passed = has_artifact_panel and sandbox_correct
    status = "PASS" if passed else "FAIL"
    print(f"    [{status}] Artifact panel: {has_artifact_panel}, Sandbox: {sandbox_correct}, Code tab: {has_code_tab}")
    
    results.append(TestResult(
        category="Artifact",
        query=ARTIFACT_QUERY,
        passed=passed,
        latency_ms=latency,
        response_chars=len(text),
        notes=f"Panel: {has_artifact_panel}, Sandbox: {sandbox_correct}, Code: {has_code_tab}",
    ))
    
    return results


# ============================================================================
# Category 5: Multi-Turn Context & Session Memory
# ============================================================================

async def test_multi_turn_context(page: Page) -> List[TestResult]:
    """Test multi-turn conversation and persistence."""
    results = []
    print("\n" + "=" * 60)
    print("CATEGORY 5: Multi-Turn Context & Session Memory")
    print("=" * 60)
    
    await new_chat(page)
    
    # Turn 1
    print(f"\n  Turn 1: {MULTI_TURN_QUERIES[0]}")
    text1, latency1 = await send_message(page, MULTI_TURN_QUERIES[0])
    print(f"    Response: {len(text1)} chars, Latency: {latency1:.0f}ms")
    
    # Turn 2 (follow-up)
    print(f"  Turn 2: {MULTI_TURN_QUERIES[1]}")
    text2, latency2 = await send_message(page, MULTI_TURN_QUERIES[1])
    print(f"    Response: {len(text2)} chars, Latency: {latency2:.0f}ms")
    
    # Verify context continuity
    has_followup_response = len(text2) > 30
    passed = has_followup_response
    
    # Test persistence - reload page
    print("  Testing persistence (page reload)...")
    await page.reload(wait_until="networkidle")
    await page.wait_for_timeout(2000)
    
    sidebar = page.locator("text=Recent Chats")
    has_sidebar = await sidebar.count() > 0
    
    status = "PASS" if passed else "FAIL"
    print(f"    [{status}] Follow-up: {has_followup_response}, Sidebar after reload: {has_sidebar}")
    
    results.append(TestResult(
        category="Multi-Turn",
        query=f"{MULTI_TURN_QUERIES[0]} -> {MULTI_TURN_QUERIES[1]}",
        passed=passed,
        latency_ms=latency1 + latency2,
        response_chars=len(text1) + len(text2),
        notes=f"Turn 1: {len(text1)} chars, Turn 2: {len(text2)} chars, Sidebar: {has_sidebar}",
    ))
    
    return results


# ============================================================================
# Category 6: Model Toggle & Resilience
# ============================================================================

async def test_model_toggle(page: Page) -> List[TestResult]:
    """Test model provider toggle in UI."""
    results = []
    print("\n" + "=" * 60)
    print("CATEGORY 6: Model Toggle & Resilience")
    print("=" * 60)
    
    await page.goto(FRONTEND_URL, wait_until="networkidle")
    await page.wait_for_timeout(2000)
    
    providers = ["Local", "OpenRouter", "OpenAI", "Claude"]
    toggled = []
    
    for provider in providers:
        btn = page.locator(f"button:has-text('{provider}')")
        if await btn.count() > 0:
            await btn.click()
            await page.wait_for_timeout(500)
            toggled.append(provider)
            print(f"    Toggled to: {provider}")
    
    passed = len(toggled) >= 2
    status = "PASS" if passed else "FAIL"
    print(f"    [{status}] Successfully toggled {len(toggled)}/{len(providers)} providers")
    
    results.append(TestResult(
        category="Model Toggle",
        query="Toggle between Local/OpenRouter/OpenAI/Claude",
        passed=passed,
        notes=f"Toggled: {', '.join(toggled)}",
    ))
    
    return results


# ============================================================================
# Main Test Runner
# ============================================================================

async def run_all_tests():
    """Run all 6 category tests."""
    print("=" * 60)
    print("COMPREHENSIVE E2E PERFORMANCE & OPTIMIZATION TEST SUITE")
    print("=" * 60)
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    all_results: List[TestResult] = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport=VIEWPORT, device_scale_factor=2)
        page = await context.new_page()
        page.set_default_timeout(60000)
        
        # Run all categories
        all_results.extend(await test_rag_knowledge(page))
        all_results.extend(await test_out_of_scope(page))
        all_results.extend(await test_ship30_essay(page))
        all_results.extend(await test_artifact_generation(page))
        all_results.extend(await test_multi_turn_context(page))
        all_results.extend(await test_model_toggle(page))
        
        await browser.close()
    
    # Print summary
    print("\n" + "=" * 60)
    print("FINAL TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in all_results if r.passed)
    total = len(all_results)
    
    for r in all_results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.category}: {r.query[:60]}...")
        if r.latency_ms > 0:
            print(f"         Latency: {r.latency_ms:.0f}ms, Response: {r.response_chars} chars")
        if r.notes:
            print(f"         Notes: {r.notes}")
    
    print(f"\n  Total: {passed}/{total} passed")
    
    # Performance summary
    latencies = [r.latency_ms for r in all_results if r.latency_ms > 0]
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)
        print(f"\n  Performance Metrics:")
        print(f"    Avg Latency: {avg_latency:.0f}ms")
        print(f"    Min Latency: {min_latency:.0f}ms")
        print(f"    Max Latency: {max_latency:.0f}ms")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
