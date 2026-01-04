"""
Scrape Gemini Storybook links using Playwright headless browser.
This allows us to extract text and images after JavaScript has rendered the page.
"""
from playwright.sync_api import sync_playwright
from PIL import Image
import io
import base64
import time
from typing import List, Tuple, Dict
import re


def scrape_gemini_storybook(url: str) -> Tuple[List[Image.Image], List[str]]:
    """
    Scrape a Gemini Storybook URL using headless browser.

    Args:
        url: URL to the Gemini Storybook share

    Returns:
        Tuple of (images, text_blocks)
    """
    images = []
    text_blocks = []

    with sync_playwright() as p:
        print(f"Launching browser to scrape: {url}")

        # Launch Chromium (headless with stealth mode)
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US'
        )

        # Remove webdriver flag
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()

        try:
            # Navigate to the Gemini share URL
            print("Loading page...")
            page.goto(url, wait_until='load', timeout=60000)

            # Wait for buttons to appear
            print("Waiting for buttons to load...")
            try:
                page.wait_for_selector('button', timeout=10000)
                print("  Buttons loaded")
            except:
                print("  No buttons found after timeout")

            time.sleep(2)  # Extra wait for dynamic content

            # Handle cookie consent if it appears
            print("Checking for cookie dialog...")
            try:
                # Try to click "Accept all" in multiple languages
                result = page.evaluate('''() => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    console.log('Total buttons found:', buttons.length);

                    // Debug: log all button texts
                    const buttonTexts = buttons.map(b => b.textContent.trim());
                    console.log('Button texts:', buttonTexts);

                    // Look for accept button in different languages
                    const acceptTexts = ['Accept all', 'Godkänn alla', 'Acceptera alla', 'Accepter tout'];
                    const acceptButton = buttons.find(b => {
                        const text = b.textContent.trim();
                        return acceptTexts.some(t => text.includes(t));
                    });

                    if (acceptButton) {
                        console.log('Found accept button, clicking...');
                        acceptButton.click();
                        return {status: 'accepted', buttons: buttonTexts.length};
                    }

                    // Fallback: try reject
                    const rejectTexts = ['Reject all', 'Avvisa alla', 'Refuser tout'];
                    const rejectButton = buttons.find(b => {
                        const text = b.textContent.trim();
                        return rejectTexts.some(t => text.includes(t));
                    });

                    if (rejectButton) {
                        console.log('Found reject button, clicking...');
                        rejectButton.click();
                        return {status: 'rejected', buttons: buttonTexts.length};
                    }

                    return {status: 'not_found', buttons: buttonTexts.length, texts: buttonTexts.slice(0, 10)};
                }''')

                print(f"  Found {result.get('buttons', 0)} buttons")
                if result.get('status') == 'accepted':
                    print("  ✓ Clicked Accept all button")
                    time.sleep(5)
                elif result.get('status') == 'rejected':
                    print("  ✓ Clicked Reject all button")
                    time.sleep(5)
                else:
                    print(f"  ✗ No cookie dialog found. Button texts: {result.get('texts', [])}")

            except Exception as e:
                print(f"  Cookie dialog handling failed: {e}")
                import traceback
                traceback.print_exc()
                pass

            # Wait for content to load (Gemini uses React, so we need to wait)
            print("Waiting for content to render...")
            time.sleep(10)  # Give React time to render

            # Take screenshot for debugging
            page.screenshot(path='debug_screenshot.png')
            print("  Screenshot saved to debug_screenshot.png")

            # Try to find storybook content
            # Gemini might use specific classes or data attributes

            # Extract images
            print("Extracting images...")
            img_elements = page.query_selector_all('img')

            for img_elem in img_elements:
                try:
                    # Get image source
                    src = img_elem.get_attribute('src')

                    if not src:
                        continue

                    # Skip small images (icons, avatars, etc.)
                    # Get natural dimensions if available
                    width = img_elem.evaluate('el => el.naturalWidth')
                    height = img_elem.evaluate('el => el.naturalHeight')

                    if width and height:
                        # Skip small images (likely UI elements)
                        if width < 100 or height < 100:
                            continue

                    # Handle data URLs
                    if src.startswith('data:image'):
                        # Extract base64 data
                        match = re.match(r'data:image/[^;]+;base64,(.+)', src)
                        if match:
                            img_data = base64.b64decode(match.group(1))
                            img = Image.open(io.BytesIO(img_data))
                            images.append(img)
                            print(f"  Extracted image: {img.width}x{img.height}")

                    # Handle regular URLs
                    elif src.startswith('http'):
                        # Download image
                        import httpx
                        response = httpx.get(src, timeout=30)
                        if response.status_code == 200:
                            img = Image.open(io.BytesIO(response.content))
                            images.append(img)
                            print(f"  Downloaded image: {img.width}x{img.height}")

                except Exception as e:
                    print(f"  Failed to extract image: {e}")
                    continue

            # Extract text content
            print("Extracting text...")

            # Try different selectors to find story content
            # Gemini might wrap content in specific divs
            text_selectors = [
                '[data-test-id*="conversation"]',
                '[role="presentation"]',
                '.conversation-content',
                'p',
                'div[class*="message"]',
                'div[class*="content"]'
            ]

            all_text_elements = []
            for selector in text_selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    all_text_elements.extend(elements)
                    break

            # Extract text from elements
            seen_texts = set()
            for elem in all_text_elements:
                try:
                    text = elem.inner_text().strip()

                    # Filter out short text (UI elements)
                    if text and len(text) > 20 and text not in seen_texts:
                        text_blocks.append(text)
                        seen_texts.add(text)
                        print(f"  Extracted text block: {len(text)} chars")

                except Exception as e:
                    continue

            # If no text found with selectors, try getting all visible text
            if not text_blocks:
                print("  No text found with selectors, trying body text...")
                body_text = page.evaluate('document.body.innerText')

                # Split into paragraphs
                paragraphs = [p.strip() for p in body_text.split('\n\n') if p.strip()]

                for para in paragraphs:
                    if len(para) > 20:
                        text_blocks.append(para)

        finally:
            browser.close()

    print(f"Scraping complete: {len(images)} images, {len(text_blocks)} text blocks")
    return images, text_blocks


def scrape_and_parse(url: str) -> Dict:
    """
    Scrape Gemini Storybook and return structured data.

    Returns:
        Dict with 'images', 'texts', and 'pages' (paired content)
    """
    images, texts = scrape_gemini_storybook(url)

    # Try to pair images with texts
    # Assume each image corresponds to a text block
    pages = []
    max_items = max(len(images), len(texts))

    for i in range(max_items):
        page = {}
        if i < len(images):
            page['image'] = images[i]
        if i < len(texts):
            page['text'] = texts[i]
        pages.append(page)

    return {
        'images': images,
        'texts': texts,
        'pages': pages
    }
