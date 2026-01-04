"""Debug cookie dialog to understand its structure"""
import sys
sys.path.insert(0, 'backend')

from playwright.sync_api import sync_playwright
import time

url = "https://gemini.google.com/share/f3e564471c8f"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # visible browser for debugging
    page = browser.new_page()

    print(f"Loading: {url}")
    page.goto(url, wait_until='domcontentloaded')

    time.sleep(3)

    # Get all buttons
    print("\n=== Finding all buttons ===")
    buttons_html = page.evaluate('''() => {
        const buttons = Array.from(document.querySelectorAll('button'));
        return buttons.map((b, i) => ({
            index: i,
            text: b.textContent.trim(),
            html: b.outerHTML.substring(0, 200)
        }));
    }''')

    for btn in buttons_html:
        print(f"\nButton {btn['index']}:")
        print(f"  Text: {btn['text']}")
        print(f"  HTML: {btn['html']}...")

    # Check for iframes
    print("\n=== Checking for iframes ===")
    iframes = page.frames
    print(f"Found {len(iframes)} frames")

    # Wait for user to see
    print("\nBrowser will stay open for 60 seconds...")
    time.sleep(60)

    browser.close()
