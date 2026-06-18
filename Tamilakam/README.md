# Advanced Tanglish to Tamil AI Converter (தமிழாக்கம்)

தமிழாக்கம் (Tamilaakkam) is a modern, premium web application that converts Tanglish (Tamil written in Roman/English characters) or images containing Tanglish text (via OCR) into fluent, grammatically correct, and natural written Tamil as spoken and written by native speakers.

---

## 🌟 Key Features

1. **Tanglish to Tamil Transliteration:** 
   * Leverages phonetic normalization rules, spell checking, dictionary lookup, and grammar matching.
   * Learns and maps variations of colloquial Tamil words (e.g., `nalaki` / `naalaiku` $\rightarrow$ `நாளைக்கு`, `seri` / `sari` $\rightarrow$ `சரி`).

2. **OCR Image Recognition (Tanglish & General):**
   * Integrates Tesseract OCR to scan uploaded documents or screenshots and extract Tanglish text.
   * Supports a local OCR engine and falls back to serverless browser-side OCR when offline.

3. **Colloquial Grammar Suffix Rules:**
   * Cleans up conversational speech transitions (e.g., automatically combines `"சரி"` + `"அஹ்"` $\rightarrow$ **`சரியா?`**).

4. **Advanced AI Refinement (Optional):**
   * Connects to the Gemini generative model (`gemini-1.5-flash`) to polish the translation, ensuring pronoun-verb agreement and natural social media tone (like WhatsApp or Instagram style).

5. **Premium Responsive UI:**
   * Stunning glassmorphism UI styled with Tailwind CSS and interactive micro-animations.
   * Quick utility buttons to **Copy to Clipboard** and **Download Output as TXT**.

---

## 🛠️ Technology Stack

* **Backend:** Python 3.x, Flask, CORS, Python-dotenv, Pytesseract, Pillow
* **Frontend:** HTML5, CSS3, Tailwind CSS, JavaScript, Tesseract.js (Offline OCR Fallback), Lucide Icons
* **AI Model:** Google Gemini API (`google-generativeai`)
* **Environment:** Windows (PowerShell compatible)

---

## 🚀 Setup & Installation

### Prerequisite: Install Tesseract OCR (For Image Uploads)
1. Download and install Tesseract OCR for Windows from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).
2. Install it in the default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`.
3. If you installed it elsewhere, update the path inside `app.py` line 31:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r"YOUR_TESSERACT_PATH"
   ```

### Step 1: Initialize the Project
Clone the repository or extract the ZIP file, then open your terminal in the project directory.

### Step 2: Set Up Virtual Environment & Dependencies
Create a Python virtual environment and install the required modules:
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Gemini API Key (Optional)
To enable advanced AI-powered text refinement:
1. Create a `.env` file in the root directory.
2. Add your Gemini API key:
   ```env
   GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
   ```

### Step 4: Run the Application
Start the Flask backend server:
```bash
python app.py
```
Open **`http://127.0.0.1:5000`** in your web browser to use the application.

---

## 📂 Project Structure

```
Tamilakam/
│
├── app.py                      # Flask Server (Routes, OCR and fallback handlers)
├── dataset_pipeline.py         # Loads dataset and maps words and phrases
├── verify_transliteration.py   # Benchmark evaluation script (accuracy tests)
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── dataset/                    # Conversational dataset split files
│   ├── train.csv
│   ├── test.csv
│   ├── validation.csv
│   └── generate_dataset.py     # Programmatic spelling variation generator
│
├── transliteration/            # Transliteration pipeline components
│   ├── pipeline.py
│   ├── spell_corrector.py
│   ├── grammar_corrector.py
│   ├── phonetic_normalizer.py
│   └── lm_post_processor.py    # Gemini LLM interface
│
├── templates/                  # Frontend HTML templates
│   ├── base.html
│   ├── index.html
│   ├── upload.html
│   ├── result.html
│   └── about.html
│
└── static/                     # CSS & JS assets
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```
