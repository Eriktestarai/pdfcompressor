"""
Create a test PDF that simulates Gemini Storybook format.
This PDF will have images and text that can be used to test the booklet maker.
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image(text, width=400, height=300, color="#4A90E2"):
    """Create a simple colored image with text"""
    img = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(img)

    # Add some text to the image
    try:
        # Try to use a default font
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        # Fallback to default font
        font = ImageFont.load_default()

    # Center the text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(position, text, fill="white", font=font)

    return img

def create_gemini_test_pdf(output_path):
    """Create a test PDF with 3 pages, each with an image and text"""
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    stories = [
        {
            "title": "Sida 1",
            "text": "Det var en gång en liten robot som bodde i skogen. Roboten älskade att samla kottar och löv.",
            "color": "#E74C3C"
        },
        {
            "title": "Sida 2",
            "text": "En dag mötte roboten en vänlig ekorre. Ekorren visade roboten var de bästa kottarna fanns.",
            "color": "#3498DB"
        },
        {
            "title": "Sida 3",
            "text": "Roboten och ekorren blev bästa vänner och levde lyckliga i skogen för alltid.",
            "color": "#2ECC71"
        }
    ]

    for story in stories:
        # Create an image for this page
        img = create_test_image(story["title"], color=story["color"])

        # Save image to BytesIO
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        # Draw image (centered at top)
        img_width = 400
        img_height = 300
        x = (width - img_width) / 2
        y = height - img_height - 100

        c.drawImage(ImageReader(img_buffer), x, y, width=img_width, height=img_height)

        # Draw text below image
        text_y = y - 50
        c.setFont("Helvetica", 14)

        # Word wrap the text
        words = story["text"].split()
        line = []
        for word in words:
            line.append(word)
            test_line = ' '.join(line)
            if c.stringWidth(test_line, "Helvetica", 14) > width - 100:
                line.pop()
                c.drawString(50, text_y, ' '.join(line))
                text_y -= 20
                line = [word]

        if line:
            c.drawString(50, text_y, ' '.join(line))

        # Move to next page
        c.showPage()

    c.save()
    print(f"Test PDF created: {output_path}")

if __name__ == "__main__":
    create_gemini_test_pdf("test_storybook.pdf")
