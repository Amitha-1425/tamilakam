# தமிழாக்கம் (Tamilaakkam) — Tanglish-to-Tamil Conversion System

Tamilaakkam is a modern web application that converts Tanglish (Tamil written in English/Latin characters) into correct Unicode Tamil text. It supports direct manual text input and browser-side Image OCR (Optical Character Recognition) to extract and translate written text.

The system uses a hybrid translation architecture:
1. **Serverless Magic Loops API**: Queries a cloud endpoint for rapid, highly-accurate transliteration.
2. **Local Rule-Based Phonetic Engine**: Falls back completely offline to a custom abugida-based transliteration module if the internet or serverless loop is offline.
3. **In-Browser OCR**: Leverages client-side WebAssembly `Tesseract.js` directly in the browser to extract text from images before translating.

---

## 📁 Repository Structure

The repository has been optimized to be extremely lightweight (under 1MB, excluding `.venv`):

```
Tamilakam/
│
├── .gitignore                  # Prevents .venv, caches, and uploaded files from being tracked
├── sample.html                 # Standalone, 100% serverless single-page app
│
└── tamilaakkam/
    ├── README.md               # This documentation guide
    ├── requirements.txt        # Backend dependencies (Flask, Flask-Cors, requests)
    ├── .env                    # Backend configuration (Gemini API fallback option)
    │
    └── flask_api/              # Backend Flask web service
        ├── app.py              # Main Flask server & local phonetic transliterator
        ├── static/             # CSS stylesheets, Javascript router, static placeholders
        └── templates/          # HTML pages (Home, Upload, Results, About)
```

---

## 🚀 Standalone Client-Only Mode (`sample.html`)

If you do not want to run a local python backend, you can run the system in **100% Serverless Mode** by opening `sample.html` directly:
1. Double-click the [sample.html](file:///c:/Users/midhu/OneDrive/Desktop/Tamilakam/sample.html) file at the root of the project to open it in any browser (or run via Live Server).
2. It uses browser-side `Tesseract.js` for OCR and serverless cloud APIs for transliteration. No server startup or python dependencies required!

---

## 🐍 Flask Web Application Setup

To run the full Flask web application locally:

### Step 1: Initialize Virtual Environment & Install Packages
Make sure you have Python 3.8+ installed. Open a PowerShell/Terminal window in the project folder:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
.venv\Scripts\activate

# Install the lightweight Flask requirements
pip install -r tamilaakkam/requirements.txt
```

### Step 2: Start the Backend Server
Run the Flask server:
```bash
python tamilaakkam/flask_api/app.py
```
The server will start on `http://127.0.0.1:5000`.

### Step 3: Run the Frontend
- If using Live Server, open `http://127.0.0.1:5500/tamilaakkam/flask_api/templates/upload.html` in your browser.
- Alternatively, you can visit the Flask server directly at `http://127.0.0.1:5000/upload`.
- Type manual text or upload an image and click **தமிழாக்கம் செய்** to convert. The results page will render your translation beautifully!
