"""
Create booklet-format PDFs from Gemini Storybook PDFs.
Each spread becomes one A4 page with proper layout for printing.
"""
import fitz  # PyMuPDF
from PIL import Image
import io


def create_booklet_from_gemini(input_path, output_path, quality=85):
    """
    Convert a Gemini Storybook PDF to a printable booklet format.

    Gemini PDFs have each spread as a full-page image (11 identical copies).
    We extract one copy per page and create an A4 booklet ready for printing.

    Args:
        input_path: Path to Gemini Storybook PDF
        output_path: Path to save booklet PDF
        quality: JPEG quality for compression (1-100)

    Returns:
        dict: Statistics about the conversion
    """
    print(f"Creating booklet from: {input_path}")

    # Open source PDF
    pdf_document = fitz.open(input_path)
    total_pages = len(pdf_document)

    # Create output PDF (A4 landscape for spreads)
    output_pdf = fitz.open()

    for page_num in range(total_pages):
        page = pdf_document[page_num]

        # Render the entire page as an image (Gemini pages are visual-only)
        # Use 2x scale (144 DPI) for good quality
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)

        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Compress the image
        img_compressed = compress_image(img, quality, max_dimension=2000)

        # Save compressed image to bytes
        img_buffer = io.BytesIO()
        img_compressed.save(img_buffer, format='JPEG', quality=quality, optimize=True)
        img_bytes = img_buffer.getvalue()

        # Create A4 landscape page (842 x 595 points)
        a4_landscape = fitz.Rect(0, 0, 842, 595)
        new_page = output_pdf.new_page(width=a4_landscape.width, height=a4_landscape.height)

        # Insert image to fill the page
        new_page.insert_image(a4_landscape, stream=img_bytes)

        print(f"Processed page {page_num + 1}/{total_pages}")

    # Save with compression
    output_pdf.save(output_path, garbage=4, deflate=True)
    output_pdf.close()
    pdf_document.close()

    print(f"Booklet created: {output_path}")

    return {
        "pages": total_pages,
        "format": "A4 landscape",
        "ready_for_print": True
    }


def compress_image(image, quality=85, max_dimension=2000):
    """
    Compress an image by reducing size and quality.

    Args:
        image: PIL Image object
        quality: JPEG quality (1-100)
        max_dimension: Maximum width or height in pixels

    Returns:
        PIL Image: Compressed image
    """
    # Convert to RGB if needed
    if image.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'P':
            image = image.convert('RGBA')
        background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
        image = background
    elif image.mode != 'RGB':
        image = image.convert('RGB')

    # Resize if too large
    width, height = image.size
    if width > max_dimension or height > max_dimension:
        ratio = min(max_dimension / width, max_dimension / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        image = image.resize((new_width, new_height), Image.LANCZOS)

    return image
