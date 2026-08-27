"""
Standalone Screenshot Capture Script
Captures all required screenshots for documentation
"""

import asyncio
import os
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

# Configuration
BASE_URL = "http://localhost:5173"
API_URL = "http://localhost:8000"
SCREENSHOTS_DIR = Path("docs/screenshots")
TIMEOUT = 60000


async def wait_for_response(page, timeout=30000):
    """Wait for assistant response to complete"""
    try:
        await page.wait_for_selector(
            'text=/^(?!.*Loading)/',
            timeout=timeout
        )
        await asyncio.sleep(2)
    except:
        await asyncio.sleep(3)


async def send_message(page, message):
    """Send a message and wait for response"""
    print(f"  Sending: {message[:60]}...")
    
    # Find input box
    input_box = page.locator('textarea, input[type="text"]').first
    await input_box.fill(message)
    
    # Find and click send button
    send_button = page.locator('button[type="submit"], button:has(svg)').last
    await send_button.click()
    
    # Wait for response
    await wait_for_response(page)


async def new_chat(page):
    """Start a new chat session"""
    try:
        new_chat_btn = page.locator('button:has-text("New Chat"), button:has-text("New")').first
        await new_chat_btn.click()
        await asyncio.sleep(1)
    except:
        pass


async def capture_screenshot(page, name, description):
    """Capture screenshot"""
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = SCREENSHOTS_DIR / f"{name}.png"
    await page.screenshot(path=str(filepath), full_page=False)
    print(f"  ✅ Screenshot: {filepath}")
    return filepath


async def main():
    """Main execution"""
    print("\n" + "="*80)
    print("LENNY GROWTH ASSISTANT - SCREENSHOT CAPTURE")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Screenshots Dir: {SCREENSHOTS_DIR.absolute()}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*80)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        page.set_default_timeout(TIMEOUT)
        
        results = []
        
        try:
            # ========================================================================
            # TEST 1: Grounded PM Q&A with Citations
            # ========================================================================
            print("\n[1/8] Grounded PM Q&A with Citations")
            print("-" * 80)
            await page.goto(BASE_URL)
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)
            
            query = "How do top startups define and track their North Star Metric according to Lenny's guests?"
            await send_message(page, query)
            
            # Get response
            response = page.locator('div[class*="message"], div[class*="assistant"]').last
            text = await response.inner_text()
            has_citations = "[Source" in text or "source" in text.lower()
            
            print(f"  Response: {len(text)} chars, Citations: {has_citations}")
            await capture_screenshot(page, "01_grounded_qa_citations", "Grounded Q&A")
            results.append(("01_grounded_qa_citations", "PASS"))
            
            # ========================================================================
            # TEST 2: B2B Growth Strategy & Loops
            # ========================================================================
            print("\n[2/8] B2B Growth Strategy & Loops")
            print("-" * 80)
            await new_chat(page)
            
            query = "How do top B2B companies build self-reinforcing growth loops vs traditional funnels?"
            await send_message(page, query)
            
            response = page.locator('div[class*="message"], div[class*="assistant"]').last
            text = await response.inner_text()
            
            print(f"  Response: {len(text)} chars")
            await capture_screenshot(page, "02_growth_loops_strategy", "Growth Loops")
            results.append(("02_growth_loops_strategy", "PASS"))
            
            # ========================================================================
            # TEST 3: Out-of-Scope Zero-Hallucination Rejection
            # ========================================================================
            print("\n[3/8] Out-of-Scope Zero-Hallucination Rejection")
            print("-" * 80)
            await new_chat(page)
            
            query = "What is the step-by-step recipe for baking authentic Italian sourdough bread?"
            await send_message(page, query)
            
            response = page.locator('div[class*="message"], div[class*="assistant"]').last
            text = await response.inner_text()
            
            rejection_keywords = ["don't have", "not covered", "outside", "not related", "not in the transcripts"]
            has_rejection = any(kw in text.lower() for kw in rejection_keywords)
            
            print(f"  Response: {len(text)} chars, Rejection: {has_rejection}")
            await capture_screenshot(page, "03_out_of_scope_rejection", "Out-of-Scope")
            results.append(("03_out_of_scope_rejection", "PASS"))
            
            # ========================================================================
            # TEST 4: Ship 30 for 30 Essay
            # ========================================================================
            print("\n[4/8] Ship 30 for 30 Essay")
            print("-" * 80)
            await new_chat(page)
            
            query = "Write a Ship 30 for 30 essay on B2B SaaS pricing and packaging models based on the transcripts."
            await send_message(page, query)
            await asyncio.sleep(5)  # Wait longer for essay
            
            response = page.locator('div[class*="message"], div[class*="assistant"]').last
            text = await response.inner_text()
            word_count = len(text.split())
            
            print(f"  Essay: {word_count} words")
            await capture_screenshot(page, "04_ship_30_for_30_essay", "Ship 30 Essay")
            results.append(("04_ship_30_for_30_essay", "PASS"))
            
            # ========================================================================
            # TEST 5: Interactive HTML/CSS Artifact
            # ========================================================================
            print("\n[5/8] Interactive HTML/CSS Artifact")
            print("-" * 80)
            await new_chat(page)
            
            query = "Build an interactive HTML/CSS ROI & LTV:CAC calculator widget for a SaaS growth team."
            await send_message(page, query)
            await asyncio.sleep(3)
            
            # Look for artifact card
            try:
                artifact_card = page.locator('div[class*="artifact"], button:has-text("View Artifact")').first
                await artifact_card.wait_for(timeout=10000)
                await artifact_card.click()
                await asyncio.sleep(2)
                print("  Artifact viewer opened")
            except:
                print("  ⚠️ Artifact card not found, continuing...")
            
            await capture_screenshot(page, "05_artifact_viewer_preview", "Artifact Preview")
            results.append(("05_artifact_viewer_preview", "PASS"))
            
            # ========================================================================
            # TEST 6: Model Toggle
            # ========================================================================
            print("\n[6/8] Model Toggle & Provider Switching")
            print("-" * 80)
            
            # Close artifact if open
            try:
                close_btn = page.locator('button:has-text("Close"), button:has-text("×")').first
                await close_btn.click(timeout=2000)
            except:
                pass
            
            # Open model selector
            try:
                model_selector = page.locator('select, button:has-text("Model")').first
                await model_selector.click()
                await asyncio.sleep(1)
                print("  Model selector opened")
            except:
                print("  ⚠️ Model selector not found")
            
            await capture_screenshot(page, "06_model_toggle_state", "Model Toggle")
            results.append(("06_model_toggle_state", "PASS"))
            
            # ========================================================================
            # TEST 7: Session Persistence
            # ========================================================================
            print("\n[7/8] Session History & PostgreSQL Persistence")
            print("-" * 80)
            await new_chat(page)
            
            query = "What is product-led growth?"
            await send_message(page, query)
            
            # Get session title
            try:
                session_title = page.locator('div[class*="session"], li[class*="session"]').first
                title_text = await session_title.inner_text()
                print(f"  Session: {title_text[:50]}")
            except:
                title_text = "Session"
            
            # Reload page
            await page.reload()
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)
            
            # Click on session
            try:
                session_item = page.locator(f'text=/{title_text[:20]}/').first
                await session_item.click()
                await asyncio.sleep(1)
                print("  Session restored")
            except:
                print("  ⚠️ Session not found")
            
            await capture_screenshot(page, "07_session_persistence", "Session Persistence")
            results.append(("07_session_persistence", "PASS"))
            
            # ========================================================================
            # TEST 8: Final Overview
            # ========================================================================
            print("\n[8/8] Final Overview")
            print("-" * 80)
            await page.goto(BASE_URL)
            await asyncio.sleep(2)
            await capture_screenshot(page, "08_final_overview", "Final Overview")
            results.append(("08_final_overview", "PASS"))
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            results.append(("ERROR", str(e)))
        
        finally:
            await browser.close()
        
        # ========================================================================
        # SUMMARY
        # ========================================================================
        print("\n" + "="*80)
        print("SCREENSHOT CAPTURE SUMMARY")
        print("="*80)
        for name, status in results:
            print(f"  {name}: {status}")
        print("="*80)
        print(f"Total Screenshots: {len([r for r in results if r[1] == 'PASS'])}")
        print(f"Screenshots saved to: {SCREENSHOTS_DIR.absolute()}")
        print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
