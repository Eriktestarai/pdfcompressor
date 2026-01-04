from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import io
import os
from pathlib import Path


def extract_images_from_pdf(pdf_path):
    """
    Extract all images from a PDF file.
    Returns a list of PIL Image objects.
    """
    images = []
    reader = PdfReader(pdf_path)

    for page_num, page in enumerate(reader.pages):
        if '/XObject' in page['/Resources']:
            xObject = page['/Resources']['/XObject'].get_object()

            for obj in xObject:
                if xObject[obj]['/Subtype'] == '/Image':
                    try:
                        size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                        data = xObject[obj].get_data()

                        # Handle different color spaces
                        if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                            mode = "RGB"
                        elif xObject[obj]['/ColorSpace'] == '/DeviceGray':
                            mode = "L"
                        else:
                            mode = "RGB"

                        img = Image.frombytes(mode, size, data)
                        images.append(img)
                    except Exception as e:
                        print(f"Could not extract image from page {page_num}: {e}")
                        continue

    return images


def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF, attempting to preserve page structure.
    Returns a list of text blocks (one per page/scene).
    """
    reader = PdfReader(pdf_path)
    text_blocks = []

    for page in reader.pages:
        text = page.extract_text()
        if text.strip():
            # Split by double newlines to get paragraphs
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            text_blocks.extend(paragraphs)

    return text_blocks


def create_booklet_pdf(images, text_blocks, output_path, page_size=letter):
    """
    Create a booklet PDF with image on left, text on right.

    Args:
        images: List of PIL Image objects
        text_blocks: List of text strings
        output_path: Path to save the output PDF
        page_size: Page size tuple (default: letter)
    """
    c = canvas.Canvas(output_path, pagesize=page_size)
    width, height = page_size

    # Calculate layout
    margin = 0.5 * inch
    image_width = (width / 2) - (margin * 1.5)
    text_width = (width / 2) - (margin * 1.5)
    content_height = height - (2 * margin)

    # Pair images with text
    max_items = max(len(images), len(text_blocks))

    for i in range(max_items):
        # Draw image on left side
        if i < len(images):
            img = images[i]

            # Save image to BytesIO for reportlab
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)

            # Calculate image dimensions to fit in left half
            img_ratio = img.width / img.height
            target_ratio = image_width / content_height

            if img_ratio > target_ratio:
                # Image is wider - fit to width
                draw_width = image_width
                draw_height = image_width / img_ratio
            else:
                # Image is taller - fit to height
                draw_height = content_height
                draw_width = content_height * img_ratio

            # Center image vertically if needed
            img_y = margin + (content_height - draw_height) / 2

            c.drawImage(
                ImageReader(img_buffer),
                margin,
                img_y,
                width=draw_width,
                height=draw_height,
                preserveAspectRatio=True
            )

        # Draw text on right side
        if i < len(text_blocks):
            text = text_blocks[i]

            # Create text object
            text_obj = c.beginText()
            text_obj.setTextOrigin(
                width / 2 + margin,
                height - margin
            )
            text_obj.setFont("Helvetica", 12)
            text_obj.setLeading(16)  # Line spacing

            # Word wrap text to fit in right column
            words = text.split()
            current_line = []

            for word in words:
                current_line.append(word)
                test_line = ' '.join(current_line)

                # Check if line is too wide
                if c.stringWidth(test_line, "Helvetica", 12) > text_width:
                    # Remove last word and draw the line
                    current_line.pop()
                    if current_line:
                        text_obj.textLine(' '.join(current_line))
                        current_line = [word]

            # Draw remaining words
            if current_line:
                text_obj.textLine(' '.join(current_line))

            c.drawText(text_obj)

        # Move to next page
        c.showPage()

    c.save()


def process_gemini_pdf(input_path, output_path):
    """
    Main processing function: extract images and text from Gemini PDF
    and create a booklet-formatted PDF.

    Automatically detects PDF type:
    - Gemini Storybook (image-only): uses specialized processor
    - Regular PDF with text: uses standard booklet creator
    """
    print(f"Processing {input_path}...")

    # Extract content to determine PDF type
    text_blocks = extract_text_from_pdf(input_path)
    total_text_length = sum(len(text) for text in text_blocks)

    # Check if this is a Gemini Storybook (no extractable text)
    if total_text_length < 50:  # Very little or no text
        print("Detected Gemini Storybook format (image-only PDF)")
        # Use specialized Gemini Storybook processor
        from gemini_storybook_processor import process_gemini_storybook_pdf
        return process_gemini_storybook_pdf(input_path, output_path)

    # Standard PDF with text
    print("Processing as standard PDF with text")
    images = extract_images_from_pdf(input_path)

    print(f"Extracted {len(images)} images and {len(text_blocks)} text blocks")

    if not images and not text_blocks:
        raise ValueError("No content could be extracted from PDF")

    # Create booklet
    create_booklet_pdf(images, text_blocks, output_path)

    print(f"Booklet created: {output_path}")
    return output_path
