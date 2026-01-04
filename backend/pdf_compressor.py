"""
Simple PDF compressor - just reduces file size without changing layout.
Perfect for Gemini Storybook PDFs before converting to booklet with other tools.
Uses PyMuPDF (fitz) - no system dependencies required!
"""
import fitz  # PyMuPDF
from PIL import Image
import io


def compress_pdf(input_path, output_path, quality=85, max_dimension=2000):
    """
    Compress a PDF by rendering each page as an image and reducing quality/size.
    This method preserves both images AND text from the original PDF.

    Args:
        input_path: Path to input PDF
        output_path: Path to save compressed PDF
        quality: JPEG quality (1-100, default 85)
        max_dimension: Maximum width/height for images (default 2000px)
    """
    print(f"Compressing PDF: {input_path}")

    # Open the PDF
    pdf_document = fitz.open(input_path)
    total_pages = len(pdf_document)
    print(f"Total pages: {total_pages}")

    # Create output PDF
    output_pdf = fitz.open()

    for page_num in range(total_pages):
        print(f"Processing page {page_num + 1}/{total_pages}...")

        # Get the page
        page = pdf_document[page_num]

        # Render page to image (pixmap)
        # Use matrix to scale down if needed (2.0 = 144 DPI, good quality)
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)

        # Convert pixmap to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Compress the image
        compressed_img = compress_image(img, quality, max_dimension)

        # Convert back to bytes for PyMuPDF
        img_buffer = io.BytesIO()
        compressed_img.save(img_buffer, format='JPEG', quality=quality, optimize=True)
        img_bytes = img_buffer.getvalue()

        # Create new page with same dimensions as original
        rect = page.rect
        new_page = output_pdf.new_page(width=rect.width, height=rect.height)

        # Insert the compressed image
        new_page.insert_image(rect, stream=img_bytes)

    # Save the output PDF
    output_pdf.save(output_path, garbage=4, deflate=True)
    output_pdf.close()
    pdf_document.close()

    print(f"Compressed PDF saved: {output_path}")
    print(f"Total pages in output: {total_pages}")


def compress_image(img, quality=85, max_dimension=2000):
    """
    Compress an image by reducing size and quality.

    Args:
        img: PIL Image
        quality: JPEG quality (1-100)
        max_dimension: Maximum width/height

    Returns:
        Compressed PIL Image
    """
    # Resize if too large
    if img.width > max_dimension or img.height > max_dimension:
        ratio = min(max_dimension / img.width, max_dimension / img.height)
        new_width = int(img.width * ratio)
        new_height = int(img.height * ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Convert to RGB if necessary (for JPEG)
    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')

    return img
