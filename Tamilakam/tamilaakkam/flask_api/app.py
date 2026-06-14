import os
import sys
import uuid
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

def load_env():
    # Look for .env in current file's directory, parent directory, and grandparent directory
    current_dir = Path(__file__).resolve().parent
    for _ in range(3):
        env_path = current_dir / ".env"
        if env_path.exists():
            print(f"Loading environment from {env_path}")
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, val = line.split("=", 1)
                        val = val.strip()
                        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                            val = val[1:-1]
                        os.environ[key.strip()] = val
            break
        current_dir = current_dir.parent

# Load variables from .env on startup
load_env()

# Add project root directory to python path for modular imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

extract_text_from_image = None
try:
    from ocr.ocr_engine import extract_text_from_image
except ImportError:
    try:
        from tamilaakkam.ocr.ocr_engine import extract_text_from_image
    except ImportError:
        print("Warning: OCR engine module could not be loaded.")

TransliteratePredictor = None
try:
    from transliteration.inference import TransliteratePredictor
except ImportError:
    try:
        from tamilaakkam.transliteration.inference import TransliteratePredictor
    except ImportError:
        print("Warning: Transliteration predictor module could not be loaded.")

try:
    import google.generativeai as genai
except ImportError:
    genai = None

app = Flask(__name__)
CORS(app) # Enable CORS for frontend integration

# Configuration
UPLOAD_FOLDER = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Initialize Transliterate Predictor
predictor = None
try:
    predictor = TransliteratePredictor(
        model_dir=str(Path(__file__).resolve().parents[1] / "checkpoints"),
        vocab_dir=str(Path(__file__).resolve().parents[1] / "dataset")
    )
except Exception as e:
    print(f"Warning: Transliteration model could not be loaded: {e}.")
    print("Ensure you run train.py first to generate vocab/checkpoints.")

@app.route("/")
@app.route("/index.html")
def index():
    return render_template("index.html")

@app.route("/upload")
@app.route("/upload.html")
def upload_page():
    return render_template("upload.html")

@app.route("/result")
@app.route("/result.html")
def result_page():
    return render_template("result.html")

@app.route("/about")
@app.route("/about.html")
def about_page():
    return render_template("about.html")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/convert", methods=["POST"])
@app.route("/api/convert", methods=["POST"])
def convert():
    """
    POST /convert or /api/convert
    Accepts:
        - image (file): Image file containing printed or handwritten Tanglish text.
        - tanglish_text (form string, optional): Directly typed Tanglish text if no image is uploaded.
    
    Process:
        Image -> Preprocessing -> PaddleOCR -> Tanglish Text -> PyTorch Seq2Seq Model -> Tamil Unicode.
    
    Returns:
        JSON with 'ocr_text'/'tanglish_text' (Tanglish) and 'tamil_text' (Tamil Unicode).
    """
    uploaded_file = request.files.get("image")
    typed_text = request.form.get("tanglish_text", "").strip()
    
    ocr_text = ""
    saved_path = None
    image_url = None
    image_name = None
    
    # 1. Process Image and perform OCR if file is uploaded
    if uploaded_file and uploaded_file.filename:
        filename = f"{uuid.uuid4().hex}_{uploaded_file.filename}"
        saved_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        uploaded_file.save(saved_path)
        image_url = f"/uploads/{filename}"
        image_name = uploaded_file.filename
        
        if extract_text_from_image is None:
            return jsonify({
                "error": "OCR extraction failed: Local OCR engine is not available on this server."
            }), 500
            
        try:
            ocr_text = extract_text_from_image(saved_path)
        except Exception as ocr_err:
            return jsonify({
                "error": f"OCR extraction failed: {str(ocr_err)}"
            }), 500
            
    # 2. Get the raw text input (OCR output or direct typed text fallback)
    tanglish_input = ocr_text or typed_text
    
    if not tanglish_input:
        return jsonify({
            "error": "No input provided. Please upload an image or supply 'tanglish_text'."
        }), 400
        
    # 3. Transliterate text
    tamil_output = ""

    # Determine if Gemini is configured
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    is_gemini_configured = api_key and api_key.upper() != "YOUR_GEMINI_API_KEY_HERE"
    force_local = os.environ.get("FORCE_LOCAL_MODEL", "").strip().lower() in ("true", "1", "yes")

    checkpoints_dir = Path(__file__).resolve().parents[1] / "checkpoints"
    has_trained_weights = (checkpoints_dir / "best_model.pth").exists() or (checkpoints_dir / "latest_model.pth").exists()
    use_gemini = is_gemini_configured and not force_local

    # Try Gemini first for accurate, corrected Tamil output
    if use_gemini and genai:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""
You are an expert translator converting Tanglish (Tamil text written in English/Latin letters) into natural, grammatically correct Unicode Tamil text.

Task:
Translate the input Tanglish text into proper Tamil. Correct any spelling errors, grammar mistakes, and slang in the source text to ensure the resulting Tamil is natural and grammatically perfect.

Rules:
1. Output ONLY the translated Tamil text. Do not include any explanation, prefix, suffix, or note.
2. Use standard Tamil spelling and proper Unicode Tamil characters.
3. If the input contains mixed English words (e.g., "pure", "vibe", "life", "vibe check"), convert them to contextually appropriate Tamil words or transliterate them naturally into Tamil characters if they are common loan words (e.g., "life" -> "வாழ்க்கை", "vibe" -> "உணர்வு" or "வைப்", "pure" -> "தூய்மையான" or "பியூர்").
4. Fix grammar structures: ensure correct sentence endings, pronouns, and verb conjugations.

Examples:
- Input: "Vanakkam Tamilakam. Namma mozhi nam perumai."
  Output: "வணக்கம் தமிழகம். நம்ம மொழி நம் பெருமை."
- Input: "solren nalla ketuko"
  Output: "சொல்றேன் நல்லா கேட்டுக்கோ."
- Input: "Nee rombha pure. eppovum epadive ru."
  Output: "நீ ரொம்ப தூய்மையானவன் (அல்லது பியூர்). எப்போதும் இப்படியே இரு."
- Input: "Maridadha life ods vibe"
  Output: "மாறிடாத வாழ்க்கையின் உணர்வு."

Input Tanglish:
{tanglish_input}
"""
            resp_gen = model.generate_content(prompt)
            text_attr = getattr(resp_gen, "text", None) or getattr(resp_gen, "output", None) or str(resp_gen)
            tamil_output = text_attr.strip()
        except Exception as gemini_err:
            print(f"Gemini translation failed: {gemini_err}. Falling back to Magic Loops or local model.")

    # Fall back to Magic Loops API if Gemini is unavailable or failed
    if not tamil_output:
        try:
            import requests
            resp = requests.post(
                "https://magicloops.dev/api/loop/cfea40be-57cc-4495-ae35-9712d9d52af8/run",
                json={"tanglishText": tanglish_input},
                timeout=15
            )
            if resp.status_code == 200:
                tamil_output = resp.json().get("tamilText", "")
        except Exception as e:
            print(f"Magic Loops API transliteration failed: {e}. Falling back to local model.")

    # Final fallback: local trained model
    if not tamil_output:
        if has_trained_weights and predictor:
            try:
                tamil_output = predictor.predict_sentence(tanglish_input)
            except Exception as pred_err:
                return jsonify({
                    "error": f"All translation methods failed. Local model prediction error: {str(pred_err)}"
                }), 500
        else:
            return jsonify({
                "error": "Translation failed. Gemini not configured/failed, Magic Loops API failed, and local model checkpoints missing. Please set a valid GEMINI_API_KEY in your .env file."
            }), 400

    response_data = {
        "ocr_text": tanglish_input,
        "tanglish_text": tanglish_input,
        "tamil_text": tamil_output
    }
    if image_url:
        response_data["image_url"] = image_url
        response_data["image_name"] = image_name
        
    return jsonify(response_data)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)