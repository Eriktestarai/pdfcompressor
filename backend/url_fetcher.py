"""
Fetch and parse Gemini Storybook content from URLs using Playwright headless browser.
"""
from typing import List, Tuple
from PIL import Image

# Import the working scraper
from gemini_scraper import scrape_gemini_storybook


async def fetch_gemini_storybook(url: str) -> Tuple[List[Image.Image], List[str]]:
    """
    Fetch a Gemini Storybook from a URL and extract images and text.

    Uses Playwright headless browser with stealth mode to bypass bot detection.

    Args:
        url: URL to the Gemini Storybook

    Returns:
        Tuple of (images, text_blocks)
    """
    # Use the Playwright scraper (runs synchronously)
    # Note: This is called from async context but scrape_gemini_storybook is sync
    # We run it in a thread pool to avoid blocking
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        images, texts = await loop.run_in_executor(
            pool,
            scrape_gemini_storybook,
            url
        )

    return images, texts


def validate_gemini_url(url: str) -> bool:
    """
    Validate if the URL looks like a Gemini Storybook URL.
    This is a basic check - adjust based on actual Gemini URL format.
    """
    # Check if it's a Gemini share URL
    return 'gemini.google.com/share' in url or url.startswith('http://') or url.startswith('https://')
