# 🚀 Snabbstart

## 1. Starta Backend

```bash
cd backend
source venv/bin/activate
python main.py
```

Backend körs på: **http://localhost:8000**

## 2. Starta Frontend (i nytt terminalfönster)

```bash
cd frontend
npm run dev
```

Frontend körs på: **http://localhost:3000**

## 3. Använd Applikationen

1. Öppna **http://localhost:3000** i din webbläsare
2. Ladda upp din Gemini Storybook PDF
3. Klicka på "Skapa Booklet"
4. Ladda ner din konverterade PDF

## Tips

- Håll båda servrarna igång i separata terminalfönster
- Backend visar loggar för varje konvertering
- Tryck Ctrl+C i respektive terminal för att stoppa servrarna

## Första gången?

Om du inte har installerat dependencies än:

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```
