"""Test the Gemini scraper"""
import sys
sys.path.insert(0, 'backend')

from gemini_scraper import scrape_gemini_storybook

# Test with user's link
url = "https://gemini.google.com/share/f3e564471c8f"

print(f"Testing scraper with: {url}")
print("="*60)

images, texts = scrape_gemini_storybook(url)

print("\n" + "="*60)
print(f"RESULTS:")
print(f"Images found: {len(images)}")
print(f"Text blocks found: {len(texts)}")

if texts:
    print("\nFirst few text blocks:")
    for i, text in enumerate(texts[:3]):
        print(f"\n{i+1}. {text[:200]}...")

if images:
    print(f"\nImage sizes:")
    for i, img in enumerate(images[:5]):
        print(f"  {i+1}. {img.width}x{img.height} pixels")
