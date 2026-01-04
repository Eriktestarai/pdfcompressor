"""Analyze the Gemini Storybook PDF structure"""
from PyPDF2 import PdfReader
import sys

pdf_path = "test_gemini.pdf"

try:
    reader = PdfReader(pdf_path)

    print(f"📄 PDF Analysis:")
    print(f"Total pages: {len(reader.pages)}")
    print(f"File size: 200.9 MB")
    print()

    # Analyze first few pages
    for i in range(min(3, len(reader.pages))):
        page = reader.pages[i]
        print(f"\n--- Page {i+1} ---")

        # Get text
        text = page.extract_text()
        print(f"Text length: {len(text)} characters")
        if text.strip():
            print(f"Text preview: {text[:200]}...")
        else:
            print("No extractable text")

        # Get images
        if '/XObject' in page['/Resources']:
            xObject = page['/Resources']['/XObject'].get_object()
            images = [obj for obj in xObject if xObject[obj]['/Subtype'] == '/Image']
            print(f"Number of images: {len(images)}")

            # Image details
            for j, img_name in enumerate(images[:2]):  # First 2 images
                img = xObject[img_name]
                print(f"  Image {j+1}: {img['/Width']}x{img['/Height']} pixels")
        else:
            print("No images found")

    print("\n" + "="*50)
    print("Summary:")
    print(f"This PDF has {len(reader.pages)} pages")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
