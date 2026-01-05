"""
Create saddle-stitch booklet from split PDF pages.
Like online2pdf.com: 2 pages per A4 landscape, ready for duplex printing.
"""
import fitz  # PyMuPDF
from PIL import Image
import io


def create_booklet_from_split(input_path, output_path):
    """
    Create a saddle-stitch booklet from split PDF pages.

    Takes individual pages (from spread_splitter) and arranges them
    in saddle-stitch order for duplex printing and binding.

    Args:
        input_path: Path to split PDF (individual A4 pages)
        output_path: Path to save booklet PDF

    Returns:
        dict: Statistics about the conversion
    """
    print(f"Creating booklet from split PDF: {input_path}")

    # Open split PDF
    pdf_document = fitz.open(input_path)
    total_pages = len(pdf_document)

    print(f"Split PDF has {total_pages} pages")

    # Pad to multiple of 4 for saddle-stitch
    pages_needed = total_pages
    while pages_needed % 4 != 0:
        pages_needed += 1

    blank_pages_to_add = pages_needed - total_pages
    print(f"Adding {blank_pages_to_add} blank pages for booklet (total: {pages_needed} pages)")

    # Extract all pages as images
    page_images = []
    for page_num in range(total_pages):
        page = pdf_document[page_num]

        # Render at 144 DPI for good quality
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        page_images.append(img)

    pdf_document.close()

    # Add blank pages if needed
    if blank_pages_to_add > 0:
        blank = Image.new('RGB', page_images[0].size, 'white')
        for _ in range(blank_pages_to_add):
            page_images.append(blank)

    print(f"\nCreating saddle-stitch booklet with {pages_needed} pages...")

    # Create output PDF
    output_pdf = fitz.open()

    # Calculate saddle-stitch page order
    # For duplex printing: [last, first], [second, second-last], etc.
    num_sheets = pages_needed // 2  # Each sheet = 2 PDF pages (front and back)

    page_pairs = []
    left_idx = 0
    right_idx = pages_needed - 1

    while left_idx < right_idx:
        # Each iteration creates one PDF page (one side of a physical sheet)
        page_pairs.append((right_idx, left_idx))  # [last, first]
        right_idx -= 1
        left_idx += 1

        if left_idx <= right_idx:
            page_pairs.append((right_idx, left_idx))  # [second-last, second] - swapped for correct rotation
            left_idx += 1
            right_idx -= 1

    # Create booklet pages (A4 landscape with 2 pages side by side)
    for idx, (left_page_idx, right_page_idx) in enumerate(page_pairs):
        # Create A4 landscape page (842x595 points)
        pdf_page = output_pdf.new_page(width=842, height=595)

        # Rotate every other page 180° for duplex printing
        rotate = (idx % 2 == 1)
        rotation_text = " (rotated 180°)" if rotate else ""
        print(f"  Booklet page {idx + 1}: [{left_page_idx + 1}, {right_page_idx + 1}]{rotation_text}")

        # Get images
        left_img = page_images[left_page_idx]
        right_img = page_images[right_page_idx]

        # Rotate if needed
        if rotate:
            left_img = left_img.rotate(180, expand=False)
            right_img = right_img.rotate(180, expand=False)

        # Resize to fit half A4 landscape (421x595)
        left_resized = resize_to_fit(left_img, 421, 595)
        right_resized = resize_to_fit(right_img, 421, 595)

        # Convert to JPEG
        left_buffer = io.BytesIO()
        left_resized.save(left_buffer, format='JPEG', quality=85, optimize=True)

        right_buffer = io.BytesIO()
        right_resized.save(right_buffer, format='JPEG', quality=85, optimize=True)

        # Insert images side by side (centered vertically)
        left_rect = center_on_half_page(left_resized.size, is_left=True)
        right_rect = center_on_half_page(right_resized.size, is_left=False)

        pdf_page.insert_image(left_rect, stream=left_buffer.getvalue())
        pdf_page.insert_image(right_rect, stream=right_buffer.getvalue())

    # Save booklet
    output_pdf.save(output_path, garbage=4, deflate=True)
    output_pdf.close()

    print(f"\n✅ Booklet created: {output_path}")
    print(f"📄 {len(page_pairs)} pages (print double-sided, fold, staple)")
    print(f"🖨️  Printer setting: Duplex - flip on long edge")

    return {
        "input_pages": total_pages,
        "booklet_pages": len(page_pairs),
        "sheets": num_sheets,
        "format": "A4 landscape, 2 pages per sheet, saddle-stitch"
    }


def resize_to_fit(image, max_width, max_height):
    """Resize image to fit within dimensions while maintaining aspect ratio."""
    width, height = image.size
    ratio = min(max_width / width, max_height / height)

    if ratio < 1:
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        return image.resize((new_width, new_height), Image.LANCZOS)

    return image


def center_on_half_page(image_size, is_left):
    """Calculate rectangle to center image on left or right half of A4 landscape."""
    img_width, img_height = image_size

    # Half A4 landscape dimensions
    half_width = 421
    page_height = 595

    # Center the image vertically
    y0 = (page_height - img_height) / 2
    y1 = y0 + img_height

    if is_left:
        # Left half
        x0 = (half_width - img_width) / 2
        x1 = x0 + img_width
    else:
        # Right half
        x0 = 421 + (half_width - img_width) / 2
        x1 = x0 + img_width

    return fitz.Rect(x0, y0, x1, y1)
