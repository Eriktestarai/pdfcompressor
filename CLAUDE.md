# PDF Compressor - Claude Code Project

> A simple and secure web application that compresses PDF files to reduce file size by up to 99%.

## Project Overview

**Purpose:** Provide a fast, secure PDF compression service with automatic file cleanup.

**Stack:**
- Backend: Python 3.11 + FastAPI
- Frontend: React + Vite
- PDF Processing: PyMuPDF (fitz) + Pillow (image optimization)
- Security: UUID filenames + auto-delete after download

**Deployment:**
- Backend: Render (https://pdfcompressor-backend.onrender.com)
- Frontend: Netlify (https://pdfcompressor3.netlify.app)

## Project Structure

```
pdf-compressor/
├── backend/
│   ├── main.py              # FastAPI app with endpoints
│   ├── pdf_compressor.py    # PDF compression logic (PyMuPDF)
│   ├── requirements.txt     # Python dependencies
│   ├── runtime.txt          # Python version for Render
│   └── temp/               # Auto-created: uploaded & output PDFs
└── frontend/
    ├── src/
    │   ├── App.jsx         # Main React component
    │   ├── App.css         # Styling
    │   └── main.jsx        # React entry point
    ├── index.html          # HTML template
    ├── vite.config.js      # Vite configuration
    └── package.json        # Node dependencies
```

## Development Workflow

### Starting the Application

**Backend:**
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py  # Runs on http://localhost:8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev  # Runs on http://localhost:3000
```

### Making Changes

**Backend (PDF Compression):**
- Main API: `backend/main.py:*`
- Compression logic: `backend/pdf_compressor.py:*`
- Test changes: Upload a PDF through frontend or production site

**Frontend (UI):**
- Main component: `frontend/src/App.jsx:*`
- Styling: `frontend/src/App.css:*`
- See changes immediately (Vite hot reload)

**Deployment:**
- Push to GitHub → Netlify auto-deploys frontend
- Backend on Render redeploys automatically from GitHub

## Key Files & Their Purposes

| File | Purpose | When to Edit |
|------|---------|--------------|
| `backend/main.py` | API endpoints, file handling, security | Add endpoints, change CORS, modify cleanup |
| `backend/pdf_compressor.py` | PDF compression with PyMuPDF | Adjust quality, resolution, compression |
| `frontend/src/App.jsx` | UI logic, upload handling | Change UI flow, add features |
| `frontend/src/App.css` | Styling & animations | Change design, colors, layout |

## Verification Commands

After making changes, verify:

**Backend:**
```bash
# Check syntax
python -m py_compile backend/main.py backend/pdf_processor.py

# Test API is running
curl http://localhost:8000/
```

**Frontend:**
```bash
# Type checking (if using TypeScript - currently using JSX)
# npm run typecheck

# Build for production
npm run build
```

**End-to-end test:**
1. Start both backend and frontend
2. Upload a test PDF (any PDF)
3. Verify compression stats are shown
4. Download and check file size reduction
5. Verify file quality is acceptable

## Common Tasks

### Adjust Compression Quality
Edit `backend/pdf_compressor.py` or `backend/main.py:66`:
```python
# Higher quality (larger file)
compress_pdf(input_path, output_path, quality=95, max_dimension=3000)

# Lower quality (smaller file)
compress_pdf(input_path, output_path, quality=70, max_dimension=1500)

# Current default (recommended)
compress_pdf(input_path, output_path, quality=85, max_dimension=2000)
```

**Parameters:**
- `quality`: JPEG quality 1-100 (higher = better quality, larger file)
- `max_dimension`: Max width/height in pixels (images scaled down if larger)

### Change Compression Settings
Edit `backend/pdf_compressor.py:19-20`:
```python
mat = fitz.Matrix(2.0, 2.0)  # 144 DPI rendering
# Increase for higher quality: fitz.Matrix(3.0, 3.0)  # 216 DPI
```

### Customize UI Colors
Edit `frontend/src/App.css` - main gradients:
```css
/* Primary gradient (header, buttons) */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Success gradient */
background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
```

## Important Notes

### File Boundaries
- **Safe to edit:** All source files in `backend/` and `frontend/src/`
- **Auto-generated:** `backend/temp/`, `frontend/dist/`, `node_modules/`
- **Don't commit:** PDFs, virtual environments, node_modules

### PDF Compression Details
- Uses PyMuPDF to render each page to high-quality image
- Compresses images with Pillow (JPEG quality 85, max 2000px)
- Creates new PDF with compressed images and deflate compression
- Garbage collection for additional size reduction
- Result: Up to 99% file size reduction

### Security Features
- **UUID filenames**: Random UUIDs prevent file URL guessing
- **Auto-delete**: Files deleted immediately after download (BackgroundTasks)
- **Ephemeral storage**: Render clears temp files on container restart
- **No persistent storage**: Files never saved permanently
- **CORS protection**: Only allowed origins can access API

### CORS Configuration
Backend allows requests from:
- `http://localhost:3000` (Vite dev server)
- `http://localhost:5173` (Alternative Vite port)
- `https://pdfcompressor3.netlify.app` (Production)

Add more origins in `backend/main.py:16-21` if needed.

### Error Handling
- Backend validates PDF files before processing
- Frontend shows user-friendly error messages
- Temporary files are cleaned up on errors
- Upload files deleted immediately after compression

## Deployment (Already Live)

**Backend (Render):**
- Repository: https://github.com/Eriktestarai/pdfcompressor
- Live URL: https://pdfcompressor-backend.onrender.com
- Auto-deploys from GitHub main branch
- Python version: 3.11.11 (runtime.txt)
- Free tier: Spins down after 15 min inactivity

**Frontend (Netlify):**
- Live URL: https://pdfcompressor3.netlify.app
- Auto-deploys from GitHub main branch
- Build command: `npm run build`
- Publish directory: `dist`

**To Update:**
1. Make changes locally
2. Commit and push to GitHub
3. Netlify/Render auto-deploy within 1-2 minutes

## Swedish UI Text

The application uses Swedish for user-facing text:
- "Ladda upp" = Upload
- "Konvertera" = Convert
- "Booklet" = Booklet (same in Swedish)

Edit strings in `frontend/src/App.jsx` to change language.
