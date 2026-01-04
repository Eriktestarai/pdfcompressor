from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from pathlib import Path
from pdf_compressor import compress_pdf

app = FastAPI(title="Gemini Booklet Maker")

# CORS setup for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
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
    return {"message": "Gemini Booklet Maker API", "status": "running"}


@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    """
    Upload a Gemini Storybook PDF and compress it to reduce file size.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # Save uploaded file
    upload_path = UPLOAD_DIR / file.filename
    with upload_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Compress the PDF
        output_filename = f"compressed_{file.filename}"
        output_path = OUTPUT_DIR / output_filename

        compress_pdf(str(upload_path), str(output_path), quality=85, max_dimension=2000)

        # Get file sizes for reporting
        original_size = upload_path.stat().st_size
        compressed_size = output_path.stat().st_size
        reduction = 100 * (1 - compressed_size / original_size)

        # Clean up upload
        upload_path.unlink()

        return {
            "message": "PDF compressed successfully",
            "filename": output_filename,
            "download_url": f"/download/{output_filename}",
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
        raise HTTPException(status_code=500, detail=f"Compression failed: {str(e)}")


@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download the converted booklet PDF.
    """
    file_path = OUTPUT_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf"
    )


# URL-based conversion disabled - not working reliably
# User will download PDF from Gemini first, then compress it
#
# @app.post("/convert-from-url")
# async def convert_from_url(request: URLRequest):
#     """
#     Fetch a Gemini Storybook from a URL and convert it to booklet format.
#     """
#     raise HTTPException(status_code=501, detail="URL conversion temporarily disabled. Please download the PDF from Gemini and upload it directly.")


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
