# 📚 Gemini Booklet Maker

En kraftfull webbapplikation för att bearbeta Gemini Storybook PDF:er - komprimera, dela spreads och skapa utskriftsklara booklets.

## 🎯 Syfte

Ursprungligen utvecklad för att hantera stora Google Gemini Storybook-PDF:er (ofta 200+ MB), men fungerar med vilken PDF som helst.

**Tre huvudfunktioner:**
1. 🗜️ **Komprimera** - Reducera filstorlek med upp till 99%
2. ✂️ **Dela Spreads** - Konvertera spreads till individuella A4-sidor (som StoryJar.app)
3. 📖 **Skapa Booklet** - Skapa utskriftsklara saddle-stitch booklets

**Exempel:** 200 MB Gemini Storybook → 2-3 MB komprimerad eller booklet redo för utskrift!

## ✨ Funktioner

### 🗜️ PDF Komprimering
- Reducerar stora PDF:er med upp till 99%
- Bevarar alla sidor i original ordning
- Visar statistik (original storlek, komprimerad storlek, minskning i %)

### ✂️ Dela Spreads (Split Spreads)
- Konverterar Gemini Storybook spreads till individuella A4-sidor
- En bild ELLER text per sida (precis som StoryJar.app)
- Perfekt för vidare bearbetning eller e-läsare

### 📖 Skapa Booklet
- Skapar utskriftsklar saddle-stitch booklet
- Automatisk sidrotation för dubbelsidig utskrift
- Skriv ut, vik, häfta - färdig bok!
- Följer standard som kopiatorer använder

### Övriga funktioner
- 📤 Drag-and-drop eller filuppladdning
- 💾 Ladda ner direkt
- 🔒 Säker - filer raderas automatiskt efter nedladdning
- 📱 Responsiv design för mobil och desktop

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

**Publikt tillgänglig:** https://pdfcompressor3.netlify.app/

### 🗜️ Komprimera PDF
1. Välj "Komprimera" läge
2. Ladda upp din PDF
3. Klicka "Komprimera PDF"
4. Ladda ner komprimerad fil

### ✂️ Dela Spreads
1. Välj "Dela Spreads" läge
2. Ladda upp Gemini Storybook PDF
3. Klicka "Dela Spreads"
4. Ladda ner PDF med individuella A4-sidor

### 📖 Skapa Booklet
1. Välj "Skapa Booklet" läge
2. Ladda upp Gemini Storybook PDF (rekommenderat: komprimera först om >50 MB)
3. Klicka "Skapa Booklet"
4. Ladda ner booklet
5. Skriv ut dubbelsidig (flip on long edge)
6. Vik i mitten och häfta - färdig bok!

**Lokalt (utveckling):**
1. Starta både backend och frontend
2. Öppna `http://localhost:3000`
3. Följ stegen ovan

## 🔧 Hur det fungerar

### PDF Komprimering

1. **Renderar** varje PDF-sida till en bild med PyMuPDF
2. **Komprimerar bilderna**:
   - Reducerar upplösning till max 2000px (behåller aspect ratio)
   - Applicerar JPEG-komprimering (quality=85)
   - Optimerar för minimal filstorlek
3. **Skapar ny PDF**:
   - Samma sidstorlek och antal sidor som original
   - Komprimerade bilder med deflate-kompression
   - Garbage collection för ytterligare storleksreducering
4. **Säkerhet**: Automatisk radering av filer efter nedladdning
5. **Resultat**: Upp till 99% minskning i filstorlek

### Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- PyMuPDF (fitz) - PDF rendering och komprimering
- Pillow - Bildbehandling och optimering
- UUID - Säkra filnamn

**Frontend:**
- React - UI framework
- Vite - Build tool & hot reload
- Modern CSS - Gradient design

**Deployment:**
- Backend: Railway (https://web-production-5fc1f.up.railway.app)
- Frontend: Netlify (https://pdfcompressor3.netlify.app)

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
- Kontrollera att filen är en giltig PDF
- Se till att PDF:en inte är korrupt
- Kolla backend-loggar för felmeddelanden
- Stora PDF:er (200+ MB) kan ta 1-2 minuter att komprimera

### CORS-fel
- Kontrollera att backend körs på port 8000
- Kontrollera CORS-inställningar i `backend/main.py`

## 📝 Licens

Fri att använda och modifiera!

## 🔒 Säkerhet

- **UUID-filnamn**: Slumpmässiga filnamn gör det omöjligt att gissa URL:er
- **Automatisk radering**: Filer raderas direkt efter nedladdning
- **Ephemeral storage**: Render's container-omstarter rensar temp-mappen
- **Ingen persistent lagring**: Inga filer sparas permanent

## 📊 Testresultat

**Exempel på komprimering:**
- Original: 201 MB (10 sidor)
- Komprimerad: 2.5 MB (10 sidor)
- Minskning: 98.8%
- Processtid: ~30 sekunder

## 🙏 Om projektet

Ursprungligen utvecklat för att komprimera stora Google Gemini Storybook-PDF:er, men fungerar utmärkt för alla typer av PDF-filer som behöver reduceras i storlek.
