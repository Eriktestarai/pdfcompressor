# 🗜️ Gemini PDF Komprimering

En webbapplikation som komprimerar Google Gemini Storybook-PDF:er till mycket mindre filstorlekar.

## 🎯 Syfte

När du laddar ner en storybook från Google Gemini's Storybook-funktion får du en PDF som ofta är 200+ MB stor. Detta verktyg komprimerar PDF:en till under 3 MB (ca 98-99% minskning) samtidigt som alla sidor och bilder bevaras.

**Tidigare:** Använde Storyjar.app som mellanhand
**Nu:** Egen lösning för komprimering - använd sedan annat verktyg för booklet-konvertering!

## ✨ Funktioner

- 📤 **Drag-and-drop** eller filuppladdning
- 🗜️ **Komprimerar PDF** från 200+ MB till 2-3 MB
- 🖼️ **Bevarar alla sidor** i original ordning
- 📊 **Visar statistik** - original storlek, komprimerad storlek, minskning i %
- 💾 **Ladda ner direkt** som komprimerad PDF
- 🎨 **Snygg UI** med modern design

## 🏗️ Arkitektur

```
gemini-booklet-maker/
├── backend/           # Python FastAPI server
│   ├── main.py       # API endpoints
│   ├── pdf_processor.py  # PDF konvertering
│   └── requirements.txt
└── frontend/          # React webapp
    ├── src/
    │   ├── App.jsx   # Huvudkomponent
    │   └── App.css   # Styling
    └── package.json
```

## 🚀 Kom igång

### Backend (Python FastAPI)

```bash
cd backend

# Skapa virtual environment
python3 -m venv venv
source venv/bin/activate  # På Windows: venv\Scripts\activate

# Installera dependencies
pip install -r requirements.txt

# Starta servern
python main.py
# eller
uvicorn main:app --reload
```

Backend körs på: `http://localhost:8000`

### Frontend (React)

```bash
cd frontend

# Installera dependencies
npm install

# Starta dev server
npm run dev
```

Frontend körs på: `http://localhost:3000`

## 📖 Användning

1. **Starta både backend och frontend**
2. **Öppna** `http://localhost:3000` i din webbläsare
3. **Ladda upp** din Gemini Storybook-PDF (drag-and-drop eller klicka)
4. **Klicka** på "Komprimera PDF"
5. **Ladda ner** din komprimerade PDF
6. **(Valfritt)** Använd annat verktyg för att konvertera till booklet-format

## 🔧 Hur det fungerar

### PDF Compression

1. **Läser** Gemini's PDF med PyPDF2
2. **Extraherar den största bilden** från varje sida
3. **Komprimerar bilderna**:
   - Reducerar upplösning till max 2000px (behåller aspect ratio)
   - Applicerar JPEG-komprimering (quality=85)
   - Optimerar PNG-format
4. **Skapar ny PDF** med ReportLab:
   - Samma sidstorlek som original
   - En komprimerad bild per sida
   - Bevarar ordning och antal sidor
5. **Resultat**: 98-99% minskning i filstorlek (200MB → 2-3MB)

### Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- PyPDF2 - PDF läsning
- ReportLab - PDF skapande
- Pillow - Bildhantering

**Frontend:**
- React - UI framework
- Vite - Build tool
- Modern CSS - Gradient design

## 🎨 Anpassningar

### Ändra komprimeringsinställningar

I `backend/pdf_compressor.py` eller när du anropar funktionen i `backend/main.py`:

```python
# Högre kvalitet (större filstorlek)
compress_pdf(input_path, output_path, quality=95, max_dimension=3000)

# Lägre kvalitet (mindre filstorlek)
compress_pdf(input_path, output_path, quality=70, max_dimension=1500)

# Standard (rekommenderat)
compress_pdf(input_path, output_path, quality=85, max_dimension=2000)
```

**Parameters:**
- `quality`: JPEG-kvalitet (1-100). Högre = bättre kvalitet, större fil
- `max_dimension`: Max bredd/höjd i pixlar. Bilder skalas ner om de är större

### Ändra design

Editera `frontend/src/App.css` för att anpassa färger, animationer, etc.

## 🐛 Felsökning

### Backend startar inte
- Kontrollera att virtual environment är aktiverat
- Kör `pip install -r requirements.txt` igen

### Frontend startar inte
- Kör `npm install` igen
- Kontrollera att port 3000 inte redan används

### PDF komprimering misslyckas
- Kontrollera att PDF:en är från Gemini Storybook
- Se till att PDF:en innehåller bilder (texten extraheras inte)
- Kolla backend-loggar för felmeddelanden
- Stora PDF:er (200+ MB) kan ta 1-2 minuter att komprimera

### CORS-fel
- Kontrollera att backend körs på port 8000
- Kontrollera CORS-inställningar i `backend/main.py`

## 📝 Licens

Fri att använda och modifiera!

## 🙏 Credits

Skapad för att komprimera stora Google Gemini Storybook-PDF:er. Använd sedan valfritt verktyg (t.ex. online2pdf.com) för att konvertera den komprimerade PDF:en till booklet-format.

## 📊 Testresultat

**Test med verklig Gemini Storybook:**
- Original: 201 MB (10 sidor)
- Komprimerad: 2.5 MB (10 sidor)
- Minskning: 98.8%
- Tid: ~30 sekunder
