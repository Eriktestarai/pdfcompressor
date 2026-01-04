# Gemini Booklet Maker - Claude Code Project

> A web application that converts Google Gemini Storybook PDFs into booklet format with images on the left and text on the right.

## Project Overview

**Purpose:** Eliminate dependency on third-party service (Storyjar.app) by creating own PDF conversion tool.

**Stack:**
- Backend: Python 3.x + FastAPI
- Frontend: React + Vite
- PDF Processing: PyPDF2 (reading) + ReportLab (creation) + Pillow (images)

## Project Structure

```
gemini-booklet-maker/
├── backend/
│   ├── main.py              # FastAPI app with endpoints
│   ├── pdf_processor.py     # PDF extraction and booklet creation
│   ├── requirements.txt     # Python dependencies
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

**Backend (PDF Processing):**
- Main API: `backend/main.py:*`
- PDF logic: `backend/pdf_processor.py:*`
- Test changes: Upload a PDF through frontend

**Frontend (UI):**
- Main component: `frontend/src/App.jsx:*`
- Styling: `frontend/src/App.css:*`
- See changes immediately (Vite hot reload)

## Key Files & Their Purposes

| File | Purpose | When to Edit |
|------|---------|--------------|
| `backend/main.py` | API endpoints, file handling | Add new endpoints, change CORS |
| `backend/pdf_processor.py` | PDF extraction & creation | Change layout, page size, formatting |
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
2. Upload a test PDF from Gemini
3. Verify booklet downloads correctly
4. Check layout in PDF viewer

## Common Tasks

### Change Page Size
Edit `backend/pdf_processor.py`:
```python
from reportlab.lib.pagesizes import A4  # or letter, etc.
create_booklet_pdf(..., page_size=A4)
```

### Adjust Image/Text Ratio
Edit `backend/pdf_processor.py` in `create_booklet_pdf()`:
```python
# Current: 50/50 split
image_width = (width / 2) - (margin * 1.5)
text_width = (width / 2) - (margin * 1.5)

# Example: 60/40 split (more space for images)
image_width = (width * 0.6) - (margin * 1.5)
text_width = (width * 0.4) - (margin * 1.5)
```

### Change Text Styling
Edit `backend/pdf_processor.py` in `create_booklet_pdf()`:
```python
text_obj.setFont("Helvetica", 12)  # Font name, size
text_obj.setLeading(16)  # Line spacing
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

### PDF Processing Details
- Uses PyPDF2 to extract images and text from source PDF
- Each image is paired with corresponding text block
- ReportLab creates new PDF with custom layout
- Handles missing images or text gracefully

### CORS Configuration
Backend allows requests from:
- `http://localhost:3000` (Vite dev server)
- `http://localhost:5173` (Alternative Vite port)

Add more origins in `backend/main.py` if needed.

### Error Handling
- Backend validates PDF files before processing
- Frontend shows user-friendly error messages
- Temporary files are cleaned up on errors

## Deployment Considerations

**Backend:**
- Set environment variables for production URLs
- Configure proper file size limits
- Add file cleanup cron job for `temp/` directory
- Use production ASGI server (Gunicorn + Uvicorn)

**Frontend:**
- Build with `npm run build`
- Serve `dist/` folder with nginx or similar
- Update API URL to production backend

## Swedish UI Text

The application uses Swedish for user-facing text:
- "Ladda upp" = Upload
- "Konvertera" = Convert
- "Booklet" = Booklet (same in Swedish)

Edit strings in `frontend/src/App.jsx` to change language.
