from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from pathlib import Path
from pdf_compressor import compress_pdf
from booklet_creator import create_booklet_from_gemini
from spread_splitter import split_gemini_spreads
from booklet_from_split import create_booklet_from_split
import uuid

app = FastAPI(title="PDF Compressor")

# CORS setup for local development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "https://pdfcompressor3.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create temp directories
UPLOAD_DIR = Path("temp/uploads")
OUTPUT_DIR = Path("temp/outputs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class URLRequest(BaseModel):
    url: str


@app.get("/")
def read_root():
    return {"message": "PDF Compressor API", "status": "running"}


@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF and compress it to reduce file size.
    Files are automatically deleted after download for security.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # Generate unique filename using UUID for security
    unique_id = str(uuid.uuid4())
    upload_filename = f"{unique_id}_upload.pdf"
    output_filename = f"{unique_id}_compressed.pdf"

    upload_path = UPLOAD_DIR / upload_filename
    output_path = OUTPUT_DIR / output_filename

    # Save uploaded file
    with upload_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Compress the PDF
        compress_pdf(str(upload_path), str(output_path), quality=85, max_dimension=2000)

        # Get file sizes for reporting
        original_size = upload_path.stat().st_size
        compressed_size = output_path.stat().st_size
        reduction = 100 * (1 - compressed_size / original_size)

        # Clean up upload immediately
        upload_path.unlink()

        # Return info with original filename for user download
        original_name = file.filename.replace('.pdf', '')
        download_filename = f"compressed_{original_name}.pdf"

        return {
            "message": "PDF compressed successfully",
            "filename": output_filename,  # UUID filename for security
            "download_url": f"/download/{output_filename}?name={download_filename}",
            "stats": {
                "original_size_mb": round(original_size / (1024 * 1024), 2),
                "compressed_size_mb": round(compressed_size / (1024 * 1024), 2),
                "reduction_percent": round(reduction, 1)
            }
        }

    except Exception as e:
        # Clean up on error
        if upload_path.exists():
            upload_path.unlink()
        if output_path.exists():
            output_path.unlink()
        raise HTTPException(status_code=500, detail=f"Compression failed: {str(e)}")


def delete_file(file_path: Path):
    """Background task to delete file after download"""
    try:
        if file_path.exists():
            file_path.unlink()
            print(f"✓ Deleted file: {file_path.name}")
    except Exception as e:
        print(f"✗ Error deleting file {file_path.name}: {e}")


@app.get("/download/{filename}")
async def download_file(filename: str, name: str = None, background_tasks: BackgroundTasks = None):
    """
    Download the compressed PDF.
    File is automatically deleted after download for security.
    """
    file_path = OUTPUT_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Use provided name or default to filename
    download_name = name if name else filename

    # Schedule file deletion after response is sent
    if background_tasks:
        background_tasks.add_task(delete_file, file_path)

    return FileResponse(
        path=file_path,
        filename=download_name,
        media_type="application/pdf"
    )


# URL-based conversion disabled - not implemented
# Users should download their PDF first, then upload it for compression


@app.post("/convert-to-booklet")
async def convert_to_booklet(file: UploadFile = File(...)):
    """
    Upload a Gemini Storybook PDF and convert it to a printable booklet format.
    Process: Split spreads → Create saddle-stitch booklet
    Files are automatically deleted after download for security.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # Generate unique filename using UUID for security
    unique_id = str(uuid.uuid4())
    upload_filename = f"{unique_id}_upload.pdf"
    split_filename = f"{unique_id}_split.pdf"
    output_filename = f"{unique_id}_booklet.pdf"

    upload_path = UPLOAD_DIR / upload_filename
    split_path = OUTPUT_DIR / split_filename
    output_path = OUTPUT_DIR / output_filename

    # Save uploaded file
    with upload_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Step 1: Split spreads
        split_stats = split_gemini_spreads(str(upload_path), str(split_path), quality=85)

        # Step 2: Create booklet from split pages
        booklet_stats = create_booklet_from_split(str(split_path), str(output_path))

        # Get file sizes for reporting
        original_size = upload_path.stat().st_size
        booklet_size = output_path.stat().st_size
        reduction = 100 * (1 - booklet_size / original_size)

        # Clean up temporary files immediately
        upload_path.unlink()
        split_path.unlink()

        # Return info with original filename for user download
        original_name = file.filename.replace('.pdf', '')
        download_filename = f"{original_name}_booklet.pdf"

        return {
            "message": "Booklet created successfully",
            "filename": output_filename,  # UUID filename for security
            "download_url": f"/download/{output_filename}?name={download_filename}",
            "stats": {
                "original_size_mb": round(original_size / (1024 * 1024), 2),
                "booklet_size_mb": round(booklet_size / (1024 * 1024), 2),
                "reduction_percent": round(reduction, 1),
                "original_pages": split_stats["original_pages"],
                "booklet_pages": booklet_stats["booklet_pages"],
                "sheets": booklet_stats["sheets"],
                "format": booklet_stats["format"]
            }
        }

    except Exception as e:
        # Clean up on error
        if upload_path.exists():
            upload_path.unlink()
        if split_path.exists():
            split_path.unlink()
        if output_path.exists():
            output_path.unlink()
        raise HTTPException(status_code=500, detail=f"Booklet creation failed: {str(e)}")


@app.post("/split-spreads")
async def split_spreads(file: UploadFile = File(...)):
    """
    Upload a Gemini Storybook PDF and split spreads into individual pages.
    Like StoryJar: one image OR text per A4 page.
    Files are automatically deleted after download for security.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # Generate unique filename using UUID for security
    unique_id = str(uuid.uuid4())
    upload_filename = f"{unique_id}_upload.pdf"
    output_filename = f"{unique_id}_split.pdf"

    upload_path = UPLOAD_DIR / upload_filename
    output_path = OUTPUT_DIR / output_filename

    # Save uploaded file
    with upload_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Split spreads
        stats = split_gemini_spreads(str(upload_path), str(output_path), quality=85)

        # Get file sizes for reporting
        original_size = upload_path.stat().st_size
        split_size = output_path.stat().st_size
        reduction = 100 * (1 - split_size / original_size)

        # Clean up upload immediately
        upload_path.unlink()

        # Return info with original filename for user download
        original_name = file.filename.replace('.pdf', '')
        download_filename = f"{original_name}_split.pdf"

        return {
            "message": "Spreads split successfully",
            "filename": output_filename,  # UUID filename for security
            "download_url": f"/download/{output_filename}?name={download_filename}",
            "stats": {
                "original_size_mb": round(original_size / (1024 * 1024), 2),
                "split_size_mb": round(split_size / (1024 * 1024), 2),
                "reduction_percent": round(reduction, 1),
                "original_pages": stats["original_pages"],
                "output_pages": stats["output_pages"],
                "format": stats["format"]
            }
        }

    except Exception as e:
        # Clean up on error
        if upload_path.exists():
            upload_path.unlink()
        if output_path.exists():
            output_path.unlink()
        raise HTTPException(status_code=500, detail=f"Spread splitting failed: {str(e)}")


@app.delete("/cleanup/{filename}")
async def cleanup_file(filename: str):
    """
    Delete a processed file from the server.
    """
    file_path = OUTPUT_DIR / filename

    if file_path.exists():
        file_path.unlink()
        return {"message": "File deleted successfully"}

    return {"message": "File not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
