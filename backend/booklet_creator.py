"""
Create booklet-format PDFs from Gemini Storybook PDFs.
Each spread becomes one A4 page with proper layout for printing.
"""
import fitz  # PyMuPDF
from PIL import Image
import io


def create_booklet_from_gemini(input_path, output_path, quality=85):
    """
    Convert a Gemini Storybook PDF to a printable booklet format with proper imposition.

    Creates a saddle-stitch booklet where:
    - Pages are arranged for duplex (double-sided) printing
    - Alternating pages are rotated 180° for proper booklet folding
    - Print, fold in half, staple = ready book!

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

    # Render all pages to images first
    print("Rendering pages...")
    page_images = []
    for page_num in range(total_pages):
        page = pdf_document[page_num]

        # Render page at 144 DPI
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Compress
        img_compressed = compress_image(img, quality, max_dimension=2000)
        page_images.append(img_compressed)
        print(f"  Rendered page {page_num + 1}/{total_pages}")

    pdf_document.close()

    # Calculate booklet page order (saddle-stitch imposition)
    # For duplex printing: [back, front], [front, back], etc.
    num_sheets = (total_pages + 3) // 4  # Round up to nearest 4 pages
    total_booklet_pages = num_sheets * 4

    # Add blank pages if needed
    while len(page_images) < total_booklet_pages:
        # Create blank white page
        blank = Image.new('RGB', page_images[0].size, 'white')
        page_images.append(blank)

    print(f"\nCreating booklet with {num_sheets} sheets ({total_booklet_pages} pages)...")

    # Create output PDF
    output_pdf = fitz.open()

    # Generate page pairs for saddle-stitch
    # Sheet 0: [12, 1] front, [2, 11] back
    # Sheet 1: [10, 3] front, [4, 9] back
    # Sheet 2: [8, 5] front, [6, 7] back
    for sheet_num in range(num_sheets):
        # Front of sheet
        left_page_idx = total_booklet_pages - 1 - (sheet_num * 2)
        right_page_idx = sheet_num * 2

        print(f"  Sheet {sheet_num + 1}/{num_sheets} FRONT: pages {left_page_idx + 1} (rotated) & {right_page_idx + 1}")

        # FRONT of sheet
        front_page = output_pdf.new_page(width=842, height=595)

        # Left half - rotated 180°
        left_img = page_images[left_page_idx].rotate(180, expand=False)
        left_buffer = io.BytesIO()
        left_img.save(left_buffer, format='JPEG', quality=quality, optimize=True)
        front_page.insert_image(fitz.Rect(0, 0, 421, 595), stream=left_buffer.getvalue())

        # Right half - normal
        right_img = page_images[right_page_idx]
        right_buffer = io.BytesIO()
        right_img.save(right_buffer, format='JPEG', quality=quality, optimize=True)
        front_page.insert_image(fitz.Rect(421, 0, 842, 595), stream=right_buffer.getvalue())

        # BACK of sheet
        back_left_idx = sheet_num * 2 + 1
        back_right_idx = total_booklet_pages - 2 - (sheet_num * 2)

        print(f"  Sheet {sheet_num + 1}/{num_sheets} BACK:  pages {back_left_idx + 1} & {back_right_idx + 1} (rotated)")

        back_page = output_pdf.new_page(width=842, height=595)

        # Left half - normal
        back_left_img = page_images[back_left_idx]
        back_left_buffer = io.BytesIO()
        back_left_img.save(back_left_buffer, format='JPEG', quality=quality, optimize=True)
        back_page.insert_image(fitz.Rect(0, 0, 421, 595), stream=back_left_buffer.getvalue())

        # Right half - rotated 180°
        back_right_img = page_images[back_right_idx].rotate(180, expand=False)
        back_right_buffer = io.BytesIO()
        back_right_img.save(back_right_buffer, format='JPEG', quality=quality, optimize=True)
        back_page.insert_image(fitz.Rect(421, 0, 842, 595), stream=back_right_buffer.getvalue())

    # Save
    output_pdf.save(output_path, garbage=4, deflate=True)
    output_pdf.close()

    print(f"\n✅ Booklet created: {output_path}")
    print(f"📄 {num_sheets} sheets (print double-sided, fold, staple)")

    return {
        "pages": total_pages,
        "sheets": num_sheets,
        "format": "A4 landscape saddle-stitch",
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
