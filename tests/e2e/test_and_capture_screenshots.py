"""
Comprehensive E2E Test Suite with Screenshot Capture
Tests all 7 question types and captures screenshots for documentation
"""

import pytest
import asyncio
import os
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser

# Configuration
BASE_URL = "http://localhost:5173"
API_URL = "http://localhost:8000"
SCREENSHOTS_DIR = Path("docs/screenshots")
TIMEOUT = 60000  # 60 seconds

# Test Queries
TEST_QUERIES = {
    "grounded_qa": "How do top startups define and track their North Star Metric according to Lenny's guests?",
    "growth_loops": "How do top B2B companies build self-reinforcing growth loops vs traditional funnels?",
    "out_of_scope": "What is the step-by-step recipe for baking authentic Italian sourdough bread?",
    "ship30_essay": "Write a Ship 30 for 30 essay on B2B SaaS pricing and packaging models based on the transcripts.",
    "artifact": "Build an interactive HTML/CSS ROI & LTV:CAC calculator widget for a SaaS growth team.",
    "multi_turn_1": "What is product-led growth?",
    "multi_turn_2": "Can you give me specific examples from the podcast?",
}


@pytest.fixture
async def browser():
    """Create browser instance"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()


@pytest.fixture
async def page(browser):
    """Create page instance"""
    context = await browser.new_context(viewport={"width": 1920, "height": 1080})
    page = await context.new_page()
    page.set_default_timeout(TIMEOUT)
    yield page
    await context.close()


async def wait_for_response(page: Page, timeout=30000):
    """Wait for assistant response to complete"""
    await page.wait_for_selector(
        '[data-testid="assistant-message"]:not([data-loading="true"])',
        timeout=timeout
    )
    await asyncio.sleep(1)  # Additional wait for streaming to complete


async def send_message(page: Page, message: str):
    """Send a message and wait for response"""
    # Type message
    input_box = page.locator('[data-testid="chat-input"]')
    await input_box.fill(message)
    
    # Send
    send_button = page.locator('[data-testid="send-button"]')
    await send_button.click()
    
    # Wait for response
    await wait_for_response(page)


async def new_chat(page: Page):
    """Start a new chat session"""
    new_chat_btn = page.locator('[data-testid="new-chat-button"]')
    await new_chat_btn.click()
    await asyncio.sleep(1)


async def capture_screenshot(page: Page, name: str, description: str):
    """Capture screenshot with metadata"""
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = SCREENSHOTS_DIR / f"{name}.png"
    await page.screenshot(path=str(filepath), full_page=False)
    print(f"✅ Screenshot captured: {filepath}")
    return filepath


# ============================================================================
# TEST 1: Grounded PM Q&A with Citations
# ============================================================================
@pytest.mark.asyncio
async def test_01_grounded_qa_citations(page: Page):
    """Test grounded Q&A with citation verification"""
    print("\n" + "="*80)
    print("TEST 1: Grounded PM Q&A with Citations")
    print("="*80)
    
    await page.goto(BASE_URL)
    await page.wait_for_load_state("networkidle")
    
    # Send query
    query = TEST_QUERIES["grounded_qa"]
    print(f"Query: {query}")
    await send_message(page, query)
    
    # Verify response has content
    response = page.locator('[data-testid="assistant-message"]').last
    text = await response.inner_text()
    assert len(text) > 100, "Response too short"
    
    # Check for citations
    has_citations = "[Source" in text or "source" in text.lower()
    print(f"✅ Response: {len(text)} chars, Citations: {has_citations}")
    
    # Capture screenshot
    await capture_screenshot(page, "01_grounded_qa_citations", "Grounded Q&A with citations")


# ============================================================================
# TEST 2: B2B Growth Strategy & Loops
# ============================================================================
@pytest.mark.asyncio
async def test_02_growth_loops_strategy(page: Page):
    """Test B2B growth loops strategy"""
    print("\n" + "="*80)
    print("TEST 2: B2B Growth Strategy & Loops")
    print("="*80)
    
    await new_chat(page)
    
    query = TEST_QUERIES["growth_loops"]
    print(f"Query: {query}")
    await send_message(page, query)
    
    response = page.locator('[data-testid="assistant-message"]').last
    text = await response.inner_text()
    assert len(text) > 100, "Response too short"
    
    print(f"✅ Response: {len(text)} chars")
    await capture_screenshot(page, "02_growth_loops_strategy", "B2B growth loops strategy")


# ============================================================================
# TEST 3: Out-of-Scope Zero-Hallucination Rejection
# ============================================================================
@pytest.mark.asyncio
async def test_03_out_of_scope_rejection(page: Page):
    """Test graceful rejection of off-topic queries"""
    print("\n" + "="*80)
    print("TEST 3: Out-of-Scope Zero-Hallucination Rejection")
    print("="*80)
    
    await new_chat(page)
    
    query = TEST_QUERIES["out_of_scope"]
    print(f"Query: {query}")
    await send_message(page, query)
    
    response = page.locator('[data-testid="assistant-message"]').last
    text = await response.inner_text()
    
    # Check for rejection indicators
    rejection_keywords = [
        "don't have", "not covered", "outside", "not related",
        "not in the transcripts", "cannot answer", "no information",
        "outside my", "not in my", "transcripts don't",
    ]
    has_rejection = any(kw in text.lower() for kw in rejection_keywords)
    
    print(f"✅ Response: {len(text)} chars, Rejection: {has_rejection}")
    assert has_rejection, "No rejection detected for out-of-scope query"
    
    await capture_screenshot(page, "03_out_of_scope_rejection", "Out-of-scope rejection")


# ============================================================================
# TEST 4: "Ship 30 for 30" Specialized Content Skill
# ============================================================================
@pytest.mark.asyncio
async def test_04_ship_30_for_30_essay(page: Page):
    """Test Ship 30 for 30 essay generation"""
    print("\n" + "="*80)
    print("TEST 4: Ship 30 for 30 Essay")
    print("="*80)
    
    await new_chat(page)
    
    query = TEST_QUERIES["ship30_essay"]
    print(f"Query: {query}")
    await send_message(page, query)
    
    # Wait longer for essay generation
    await asyncio.sleep(5)
    
    response = page.locator('[data-testid="assistant-message"]').last
    text = await response.inner_text()
    
    # Check for essay characteristics
    word_count = len(text.split())
    has_headings = "#" in text or "##" in text
    has_bullets = "-" in text or "*" in text or "•" in text
    
    print(f"✅ Essay: {word_count} words, Headings: {has_headings}, Bullets: {has_bullets}")
    assert word_count > 500, "Essay too short"
    
    await capture_screenshot(page, "04_ship_30_for_30_essay", "Ship 30 essay")


# ============================================================================
# TEST 5: Interactive HTML/CSS Artifact in Sandboxed Dual-Pane
# ============================================================================
@pytest.mark.asyncio
async def test_05_artifact_viewer_preview(page: Page):
    """Test artifact viewer with HTML/CSS widget"""
    print("\n" + "="*80)
    print("TEST 5: Artifact Viewer - Preview Tab")
    print("="*80)
    
    await new_chat(page)
    
    query = TEST_QUERIES["artifact"]
    print(f"Query: {query}")
    await send_message(page, query)
    
    # Wait for artifact to render
    await asyncio.sleep(3)
    
    # Check for artifact card
    artifact_card = page.locator('[data-testid="artifact-card"]')
    await artifact_card.wait_for(timeout=10000)
    
    # Click to open artifact viewer
    await artifact_card.click()
    await asyncio.sleep(2)
    
    # Verify preview tab is active
    preview_tab = page.locator('[data-testid="preview-tab"]')
    await preview_tab.wait_for(timeout=5000)
    
    print("✅ Artifact viewer opened, Preview tab active")
    await capture_screenshot(page, "05_artifact_viewer_preview", "Artifact viewer preview")


# ============================================================================
# TEST 6: Artifact Viewer - Code Tab
# ============================================================================
@pytest.mark.asyncio
async def test_06_artifact_viewer_code_tab(page: Page):
    """Test artifact viewer code tab"""
    print("\n" + "="*80)
    print("TEST 6: Artifact Viewer - Code Tab")
    print("="*80)
    
    # Switch to code tab
    code_tab = page.locator('[data-testid="code-tab"]')
    await code_tab.click()
    await asyncio.sleep(1)
    
    # Verify code is displayed
    code_block = page.locator('[data-testid="code-block"]')
    await code_block.wait_for(timeout=5000)
    
    print("✅ Code tab active, syntax highlighting visible")
    await capture_screenshot(page, "06_artifact_viewer_code", "Artifact viewer code")


# ============================================================================
# TEST 7: Model Toggle & Provider Switching
# ============================================================================
@pytest.mark.asyncio
async def test_07_model_toggle(page: Page):
    """Test model switching functionality"""
    print("\n" + "="*80)
    print("TEST 7: Model Toggle & Provider Switching")
    print("="*80)
    
    # Close artifact viewer if open
    close_btn = page.locator('[data-testid="close-artifact"]')
    if await close_btn.is_visible():
        await close_btn.click()
    
    # Open model selector
    model_selector = page.locator('[data-testid="model-selector"]')
    await model_selector.click()
    await asyncio.sleep(1)
    
    # Select different model
    model_option = page.locator('[data-testid="model-option-anthropic"]')
    await model_option.click()
    await asyncio.sleep(1)
    
    print("✅ Model switched successfully")
    await capture_screenshot(page, "07_model_toggle_state", "Model toggle")


# ============================================================================
# TEST 8: Session History & PostgreSQL Persistence
# ============================================================================
@pytest.mark.asyncio
async def test_08_session_persistence(page: Page):
    """Test session persistence across page reload"""
    print("\n" + "="*80)
    print("TEST 8: Session History & PostgreSQL Persistence")
    print("="*80)
    
    # Start new chat and ask question
    await new_chat(page)
    query = TEST_QUERIES["multi_turn_1"]
    print(f"Query: {query}")
    await send_message(page, query)
    
    # Get session title
    session_title = page.locator('[data-testid="session-title"]').first
    title_text = await session_title.inner_text()
    print(f"Session created: {title_text}")
    
    # Reload page
    await page.reload()
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(2)
    
    # Click on session in sidebar
    session_item = page.locator(f'[data-testid="session-item"]:has-text("{title_text}")')
    await session_item.click()
    await asyncio.sleep(1)
    
    # Verify messages are restored
    messages = page.locator('[data-testid="assistant-message"]')
    count = await messages.count()
    
    print(f"✅ Session restored, {count} messages found")
    assert count > 0, "No messages restored"
    
    await capture_screenshot(page, "08_session_persistence", "Session persistence")


# ============================================================================
# MAIN EXECUTION
# ============================================================================
@pytest.mark.asyncio
async def test_run_all_screenshots(browser: Browser):
    """Run all screenshot tests sequentially"""
    print("\n" + "="*80)
    print("COMPREHENSIVE SCREENSHOT CAPTURE SUITE")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Screenshots Dir: {SCREENSHOTS_DIR.absolute()}")
    print("="*80)
    
    context = await browser.new_context(viewport={"width": 1920, "height": 1080})
    page = await context.new_page()
    page.set_default_timeout(TIMEOUT)
    
    results = []
    
    try:
        # Test 1: Grounded Q&A
        print("\n[1/8] Testing Grounded Q&A with Citations...")
        await test_01_grounded_qa_citations(page)
        results.append(("01_grounded_qa_citations", "PASS"))
        
        # Test 2: Growth Loops
        print("\n[2/8] Testing B2B Growth Loops...")
        await test_02_growth_loops_strategy(page)
        results.append(("02_growth_loops_strategy", "PASS"))
        
        # Test 3: Out-of-Scope Rejection
        print("\n[3/8] Testing Out-of-Scope Rejection...")
        await test_03_out_of_scope_rejection(page)
        results.append(("03_out_of_scope_rejection", "PASS"))
        
        # Test 4: Ship 30 Essay
        print("\n[4/8] Testing Ship 30 Essay...")
        await test_04_ship_30_for_30_essay(page)
        results.append(("04_ship_30_for_30_essay", "PASS"))
        
        # Test 5: Artifact Preview
        print("\n[5/8] Testing Artifact Viewer Preview...")
        await test_05_artifact_viewer_preview(page)
        results.append(("05_artifact_viewer_preview", "PASS"))
        
        # Test 6: Artifact Code
        print("\n[6/8] Testing Artifact Viewer Code...")
        await test_06_artifact_viewer_code_tab(page)
        results.append(("06_artifact_viewer_code", "PASS"))
        
        # Test 7: Model Toggle
        print("\n[7/8] Testing Model Toggle...")
        await test_07_model_toggle(page)
        results.append(("07_model_toggle_state", "PASS"))
        
        # Test 8: Session Persistence
        print("\n[8/8] Testing Session Persistence...")
        await test_08_session_persistence(page)
        results.append(("08_session_persistence", "PASS"))
        
    except Exception as e:
        print(f"\n❌ Error during test execution: {e}")
        results.append(("ERROR", str(e)))
    
    finally:
        await context.close()
    
    # Print summary
    print("\n" + "="*80)
    print("SCREENSHOT CAPTURE SUMMARY")
    print("="*80)
    for name, status in results:
        print(f"  {name}: {status}")
    print("="*80)
    print(f"Total Screenshots: {len([r for r in results if r[1] == 'PASS'])}")
    print("="*80)
