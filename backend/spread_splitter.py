"""
Split Gemini Storybook PDF spreads into individual A4 pages.
Replicates what StoryJar.app does: one image OR text per page.
"""
import fitz  # PyMuPDF
from PIL import Image
import io


def split_gemini_spreads(input_path, output_path, quality=85, max_dimension=2000):
    """
    Split Gemini Storybook PDF spreads into individual A4 pages.

    Process:
    - First page (cover): Keep as one full A4 page
    - Subsequent pages: Split each spread into:
      * Left half (image) → one A4 page
      * Right half (text) → one A4 page

    Args:
        input_path: Path to Gemini Storybook PDF
        output_path: Path to save split PDF
        quality: JPEG quality for compression (1-100)
        max_dimension: Maximum width or height in pixels

    Returns:
        dict: Statistics about the conversion
    """
    print(f"Splitting Gemini spreads from: {input_path}")

    # Open source PDF
    pdf_document = fitz.open(input_path)
    total_pages = len(pdf_document)

    print(f"Original PDF has {total_pages} pages")

    # Create output PDF (A4 portrait: 595x842 points)
    output_pdf = fitz.open()

    individual_page_count = 0

    for page_num in range(total_pages):
        page = pdf_document[page_num]

        # Render page at 144 DPI for good quality
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Compress image
        img_compressed = compress_image(img, quality, max_dimension)

        if page_num == 0:
            # First page: Cover - take RIGHT half only (like other pages)
            print(f"  Page {page_num + 1}: Cover (taking right half)")

            # Split in half and take right side (cover)
            width, height = img_compressed.size
            mid = width // 2
            cover_img = img_compressed.crop((mid, 0, width, height))

            # Create A4 portrait page
            pdf_page = output_pdf.new_page(width=595, height=842)

            # Resize to fill A4
            img_filled = resize_to_fill_a4(cover_img)

            # Convert to JPEG
            img_buffer = io.BytesIO()
            img_filled.save(img_buffer, format='JPEG', quality=quality, optimize=True)

            # Insert filling entire A4
            pdf_page.insert_image(fitz.Rect(0, 0, 595, 842), stream=img_buffer.getvalue())

            individual_page_count += 1

        else:
            # Split spread in half
            width, height = img_compressed.size
            mid = width // 2

            # Right half FIRST (text) - like StoryJar
            right_img = img_compressed.crop((mid, 0, width, height))
            print(f"  Page {page_num + 1}: Split → Right (text)")

            # Create A4 page for right half
            pdf_page_right = output_pdf.new_page(width=595, height=842)
            right_filled = resize_to_fill_a4(right_img)

            right_buffer = io.BytesIO()
            right_filled.save(right_buffer, format='JPEG', quality=quality, optimize=True)

            pdf_page_right.insert_image(fitz.Rect(0, 0, 595, 842), stream=right_buffer.getvalue())

            individual_page_count += 1

            # Left half SECOND (image)
            left_img = img_compressed.crop((0, 0, mid, height))
            print(f"  Page {page_num + 1}: Split → Left (image)")

            # Create A4 page for left half
            pdf_page_left = output_pdf.new_page(width=595, height=842)
            left_filled = resize_to_fill_a4(left_img)

            left_buffer = io.BytesIO()
            left_filled.save(left_buffer, format='JPEG', quality=quality, optimize=True)

            pdf_page_left.insert_image(fitz.Rect(0, 0, 595, 842), stream=left_buffer.getvalue())

            individual_page_count += 1

    pdf_document.close()

    # Save output PDF
    output_pdf.save(output_path, garbage=4, deflate=True)
    output_pdf.close()

    print(f"\n✅ Split PDF created: {output_path}")
    print(f"📄 {individual_page_count} individual pages (1 image or text per page)")

    return {
        "original_pages": total_pages,
        "output_pages": individual_page_count,
        "format": "A4 portrait, one image/text per page"
    }


def resize_to_fill_a4(image):
    """
    Resize image to fill entire A4 portrait (595x842 points @ 72 DPI).
    Crops if necessary to maintain aspect ratio while filling the page.
    """
    # A4 at 72 DPI
    target_width = 595
    target_height = 842

    width, height = image.size

    # Calculate ratio to fill (use max instead of min to fill, not fit)
    ratio = max(target_width / width, target_height / height)

    # Resize to fill
    new_width = int(width * ratio)
    new_height = int(height * ratio)
    img_resized = image.resize((new_width, new_height), Image.LANCZOS)

    # Crop to exact A4 size if needed (center crop)
    if new_width > target_width or new_height > target_height:
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        img_resized = img_resized.crop((left, top, right, bottom))

    return img_resized


def resize_to_fit_a4(image):
    """
    Resize image to fit within A4 portrait (595x842 points @ 72 DPI)
    while maintaining aspect ratio.
    """
    # A4 at 72 DPI
    max_width = 595
    max_height = 842

    width, height = image.size
    ratio = min(max_width / width, max_height / height)

    if ratio < 1:
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        return image.resize((new_width, new_height), Image.LANCZOS)

    return image


def center_image_on_a4(image_size):
    """Calculate rectangle to center image on A4 page."""
    img_width, img_height = image_size

    # A4 dimensions
    a4_width = 595
    a4_height = 842

    # Center the image
    x0 = (a4_width - img_width) / 2
    y0 = (a4_height - img_height) / 2
    x1 = x0 + img_width
    y1 = y0 + img_height

    return fitz.Rect(x0, y0, x1, y1)


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
