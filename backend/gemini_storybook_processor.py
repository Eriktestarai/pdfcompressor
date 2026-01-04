"""
Process Gemini Storybook PDFs specifically.
These PDFs have no extractable text - everything is images.
"""
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import io


def extract_all_images_by_page(pdf_path):
    """
    Extract all images from a Gemini Storybook PDF, organized by page.

    Returns:
        List of lists - each inner list contains all images from one page
    """
    reader = PdfReader(pdf_path)
    pages_images = []

    for page_num, page in enumerate(reader.pages):
        page_imgs = []

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
                        page_imgs.append(img)
                    except Exception as e:
                        print(f"Could not extract image from page {page_num}: {e}")
                        continue

        if page_imgs:
            pages_images.append(page_imgs)

    return pages_images


def find_main_images(page_images, target_count=2):
    """
    From a page of images, find the most important ones.
    Typically we want the largest or most visually interesting images.

    Args:
        page_images: List of PIL Images from one page
        target_count: How many images to select (default 2 for booklet layout)

    Returns:
        List of selected PIL Images
    """
    # Sort by size (area)
    sorted_imgs = sorted(page_images, key=lambda img: img.width * img.height, reverse=True)

    # Take the largest N images
    return sorted_imgs[:target_count]


def create_gemini_storybook_booklet(pdf_path, output_path, page_size=letter):
    """
    Create a booklet from a Gemini Storybook PDF.

    Since Gemini Storybooks have no text, we:
    1. Extract all images from each page
    2. Select the most important images per page
    3. Create a clean booklet layout with those images

    Args:
        pdf_path: Path to Gemini Storybook PDF
        output_path: Path to save booklet PDF
        page_size: Page size for booklet (default: letter)
    """
    print(f"Processing Gemini Storybook: {pdf_path}")

    # Extract all images organized by page
    pages_images = extract_all_images_by_page(pdf_path)

    print(f"Found {len(pages_images)} pages with images")

    if not pages_images:
        raise ValueError("No images found in PDF")

    # Create booklet
    c = canvas.Canvas(output_path, pagesize=page_size)
    width, height = page_size

    margin = 0.5 * inch
    content_width = width - (2 * margin)
    content_height = height - (2 * margin)

    for page_num, page_imgs in enumerate(pages_images):
        print(f"Processing page {page_num + 1} with {len(page_imgs)} images")

        # Select main images for this page (pick 1-2 best images)
        main_images = find_main_images(page_imgs, target_count=1)

        if not main_images:
            continue

        # Layout: Full page image (centered)
        img = main_images[0]

        # Calculate dimensions to fit on page
        img_ratio = img.width / img.height
        page_ratio = content_width / content_height

        if img_ratio > page_ratio:
            # Image is wider - fit to width
            draw_width = content_width
            draw_height = content_width / img_ratio
        else:
            # Image is taller - fit to height
            draw_height = content_height
            draw_width = content_height * img_ratio

        # Center on page
        x = margin + (content_width - draw_width) / 2
        y = margin + (content_height - draw_height) / 2

        # Convert to BytesIO for reportlab
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        # Draw image
        c.drawImage(
            ImageReader(img_buffer),
            x,
            y,
            width=draw_width,
            height=draw_height,
            preserveAspectRatio=True
        )

        # Add page number at bottom
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.drawCentredString(width / 2, margin / 2, f"{page_num + 1}")

        # Next page
        c.showPage()

    c.save()
    print(f"Booklet created: {output_path}")
    print(f"Total pages in booklet: {len(pages_images)}")


def process_gemini_storybook_pdf(input_path, output_path):
    """
    Main entry point for processing Gemini Storybook PDFs.
    """
    create_gemini_storybook_booklet(input_path, output_path)
    return output_path
