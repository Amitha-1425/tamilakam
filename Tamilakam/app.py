import os
import re
import uuid
import requests
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

def load_env():
    # Look for .env in current directory
    env_path = Path(__file__).resolve().parent / ".env"
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

# Load .env configuration
load_env()

import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from transliteration.pipeline import TransliterationPipeline

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = Path(__file__).resolve().parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER



def clean_and_transliterate_word(word):
    # Phonetic definitions for Tamil (Abugida script)
    vowels = {
        'aa': ('ஆ', 'ா'),
        'ae': ('ஏ', 'ே'),
        'ai': ('ஐ', 'ை'),
        'ee': ('ஈ', 'ீ'),
        'ii': ('ஈ', 'ீ'),
        'oo': ('ஓ', 'ோ'),
        'ou': ('ஔ', 'ௌ'),
        'ow': ('ஔ', 'ௌ'),
        'uu': ('ஊ', 'ூ'),
        'ey': ('ஏ', 'ே'),
        'ay': ('ஐ', 'ை'),
        'oa': ('ஓ', 'ோ'),
        'a': ('அ', 'ா'),  # Inherent vowel or long sign depending on context
        'e': ('எ', 'ெ'),
        'i': ('இ', 'ி'),
        'o': ('ஒ', 'ொ'),
        'u': ('உ', 'ு'),
        'y': ('இ', 'ி'),
    }

    consonants = {
        'thth': 'த',
        'cch': 'ச',
        'ksh': 'க்ஷ',
        'ng': 'ங',
        'nj': 'ஞ',
        'th': 'த',
        'dh': 'த',
        'zh': 'ழ',
        'sh': 'ஷ',
        'ch': 'ச',
        'ph': 'ப',
        'kh': 'க',
        'gh': 'க',
        'bh': 'ப',
        'nh': 'ந',
        'lh': 'ள',
        'kk': 'க',
        'pp': 'ப',
        'tt': 'ட',
        'cc': 'ச',
        'rr': 'ற',
        'll': 'ல',
        'mm': 'ம',
        'nn': 'ன',
        'gg': 'க',
        'bb': 'ப',
        'dd': 'ட',
        'ss': 'ச',
        'k': 'க',
        'g': 'க',
        'c': 'ச',
        'j': 'ஜ',
        't': 'ட',
        'd': 'ட',
        'p': 'ப',
        'b': 'ப',
        'r': 'ர',
        'l': 'ல',
        'v': 'வ',
        'w': 'வ',
        'z': 'ழ',
        's': 'ச',
        'h': 'ஹ',
        'n': 'ன',
        'y': 'ய',
        'm': 'ம',
        'f': 'ப',
    }

    i = 0
    n_len = len(word)
    tamil_chars = []

    while i < n_len:
        # 1. Greedy consonant cluster match
        consonant_found = None
        consonant_len = 0
        
        for c_cand in sorted(consonants.keys(), key=len, reverse=True):
            if word[i:i+len(c_cand)] == c_cand:
                consonant_found = c_cand
                consonant_len = len(c_cand)
                break
        
        if consonant_found:
            base_char = consonants[consonant_found]
            
            # Context adjustments for n
            if consonant_found == 'n':
                if i == 0:
                    base_char = 'ந'
                elif i + 1 < n_len and word[i+1] in ['d', 't']:
                    if i + 2 < n_len and word[i+2] == 'h':
                        base_char = 'ந'
                    else:
                        base_char = 'ண்' if word[i+1] == 'd' else 'ந்'
                elif i + 1 < n_len and word[i+1] in ['g', 'k']:
                    base_char = 'ங'
                elif i + 1 == n_len:
                    base_char = 'ன்'

            # Context adjustments for ng and nj conjuncts
            elif consonant_found == 'ng':
                base_char = 'ங்' + 'க'
            elif consonant_found == 'nj':
                base_char = 'ஞ்' + 'ச'

            # Context adjustments for t / d
            elif consonant_found in ['t', 'd']:
                if i == 0:
                    base_char = 'த'
                elif i > 0 and word[i-1] == 'n':
                    pass

            # Context adjustments for l
            elif consonant_found == 'l':
                if i + 1 == n_len and (word.endswith('gal') or word.endswith('kal') or word.endswith('al')):
                    base_char = 'ள'

            # Verb suffix / participle contexts (e.g. ringa -> றீங்க)
            elif consonant_found == 'r':
                if i + 1 < n_len and word[i+1] in ['i', 'e'] and i + 2 < n_len and word[i+2:i+4] == 'ng':
                    base_char = 'ற'

            # 2. Check if vowel cluster follows
            next_idx = i + consonant_len
            vowel_found = None
            vowel_len = 0
            
            for v_cand in sorted(vowels.keys(), key=len, reverse=True):
                if word[next_idx:next_idx+len(v_cand)] == v_cand:
                    vowel_found = v_cand
                    vowel_len = len(v_cand)
                    break
            
            if vowel_found:
                _, v_sign = vowels[vowel_found]
                
                # Heuristics for 'a' (inherent vs long 'ா')
                if vowel_found == 'a':
                    v_sign = ''  # default to inherent
                    
                    # Short word first vowel heuristic
                    if consonant_found == 'n' and i == 0 and n_len == 4 and word.endswith('du'):
                        v_sign = 'ா'
                    elif consonant_found in ['v', 'w'] and i == 0 and word.startswith(('vang', 'vaang')):
                        v_sign = 'ா'
                    elif consonant_found == 'y' and i == 0 and word == 'ya':
                        v_sign = 'ா'
                
                # Final 'e' mapping to 'ே'
                if vowel_found == 'e' and next_idx + vowel_len == n_len:
                    v_sign = 'ே'

                # Word-ending '-en' mapping to long 'ே' + 'ன்'
                if vowel_found == 'e' and next_idx + vowel_len + 1 == n_len and word[next_idx + vowel_len] == 'n':
                    v_sign = 'ே'
                
                # Handle double consonant representations
                is_double = (len(consonant_found) == 2 and 
                             consonant_found[0] == consonant_found[1] and 
                             consonant_found not in ['th', 'dh', 'zh', 'sh', 'ch', 'ph', 'kh', 'gh', 'bh', 'nh', 'lh', 'ng', 'nj'])
                
                if is_double:
                    single_c = consonant_found[0]
                    pure_c = consonants.get(single_c, 'க') + '்'
                    tamil_chars.append(pure_c + base_char + v_sign)
                elif consonant_found == 'thth':
                    tamil_chars.append('த்' + 'த' + v_sign)
                elif consonant_found == 'cch':
                    tamil_chars.append('ச்' + 'ச' + v_sign)
                else:
                    if base_char.endswith('்'):
                        base_char = base_char[:-1]
                    tamil_chars.append(base_char + v_sign)
                    
                i += consonant_len + vowel_len
            else:
                # Consonant not followed by a vowel -> pure consonant with pulli
                if consonant_found == 'ng':
                    tamil_chars.append('ங்')
                elif consonant_found == 'nj':
                    tamil_chars.append('ஞ்')
                elif not base_char.endswith('்'):
                    tamil_chars.append(base_char + '்')
                else:
                    tamil_chars.append(base_char)
                i += consonant_len
        else:
            # No consonant, check independent vowel
            vowel_found = None
            vowel_len = 0
            
            for v_cand in sorted(vowels.keys(), key=len, reverse=True):
                if word[i:i+len(v_cand)] == v_cand:
                    vowel_found = v_cand
                    vowel_len = len(v_cand)
                    break
                    
            if vowel_found:
                v_ind, _ = vowels[vowel_found]
                
                # Independent final 'e'
                if vowel_found == 'e' and i + vowel_len == n_len:
                    v_ind = 'ஏ'
                    
                tamil_chars.append(v_ind)
                i += vowel_len
            else:
                tamil_chars.append(word[i])
                i += 1
                
    return "".join(tamil_chars)

def local_fallback_transliteration(sentence):
    words = sentence.strip().split()
    translated_words = []
    
    for word in words:
        word_lower = word.strip().lower()
        if not word_lower:
            continue
            
        # Split by alphabetic parts to keep punctuation intact
        parts = re.split(r'([a-z]+)', word_lower)
        translated_parts = []
        
        for part in parts:
            if part.isalpha():
                word_lookup = pipeline.dataset.lookup_word(part)
                if word_lookup:
                    translated_parts.append(word_lookup)
                else:
                    translated_parts.append(clean_and_transliterate_word(part))
            else:
                translated_parts.append(part)
        translated_words.append("".join(translated_parts))
        
    return " ".join(translated_words)


# Initialize our new conversational transliteration pipeline
pipeline = TransliterationPipeline(
    gemini_api_key=os.environ.get("GEMINI_API_KEY", "").strip(),
    local_transliterate_fn=local_fallback_transliteration
)



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
    uploaded_file = request.files.get("image")
    has_file = uploaded_file and uploaded_file.filename
    image_name = uploaded_file.filename if has_file else "Typed Text"
    typed_text = request.form.get("tanglish_text", "").strip()
    task_type = request.form.get("task_type", "tanglish_ocr").strip()
    
    ocr_text = ""
    saved_path = None
    image_url = None
    used_engine = "local_phonetic_rules"
    
    # Process Image and perform OCR via Serverless API if image task and file is uploaded
    if task_type in ["tanglish_ocr", "general_ocr"] and uploaded_file and uploaded_file.filename:
        filename = f"{uuid.uuid4().hex}_{uploaded_file.filename}"
        saved_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        uploaded_file.save(saved_path)
        image_url = f"/uploads/{filename}"
        image_name = uploaded_file.filename
        
        # Try local Tesseract OCR first
        try:
            print(f"Running local Tesseract OCR on {saved_path}")
            ocr_text = pytesseract.image_to_string(Image.open(saved_path)).strip()
            print(f"Local OCR text extracted: {ocr_text}")
            used_engine = "local_tesseract_ocr"
        except Exception as local_ocr_err:
            print(f"Local Tesseract OCR failed: {local_ocr_err}. Falling back to Magic Loops...")
            try:
                # Upload file to Magic Loops upload API
                with open(saved_path, 'rb') as f:
                    upload_resp = requests.post("https://magicloops.dev/api/upload", files={"file": f})
                
                if upload_resp.ok:
                    upload_data = upload_resp.json()
                    magic_url = upload_data.get("url")
                    
                    if magic_url:
                        # Select specific loop depending on OCR type
                        loop_id = "6bf53958-18d7-44ac-a012-a473e218ccdb" if task_type == "tanglish_ocr" else "55f7c500-d48a-4f9b-9420-8c22fac8c5c4"
                        
                        ocr_resp = requests.post(
                            f"https://magicloops.dev/api/loop/{loop_id}/run",
                            json={"imageUrl": magic_url}
                        )
                        if ocr_resp.ok:
                            ocr_result = ocr_resp.json()
                            # Parse string or dictionary formats
                            if isinstance(ocr_result, dict):
                                ocr_text = ocr_result.get("text", "") or ocr_result.get("output", "") or str(ocr_result)
                            else:
                                ocr_text = str(ocr_result)
                            used_engine = "serverless_ocr"
                        else:
                            print(f"Magic Loops OCR failed: {ocr_resp.text}")
                else:
                    print(f"Magic Loops upload failed: {upload_resp.text}")
                    
            except Exception as ocr_err:
                print(f"Serverless OCR exception: {ocr_err}")
            
    # Determine the text input to use
    tanglish_input = ocr_text or typed_text
    
    # If it is general OCR, return the raw OCR text without translation to Tamil
    if task_type == "general_ocr":
        if not tanglish_input and not ocr_text:
            return jsonify({"error": "No image provided for General OCR."}), 400
        
        response_data = {
            "ocr_text": tanglish_input,
            "tanglish_text": tanglish_input,
            "tamil_text": "",
            "engine_used": used_engine if ocr_text else "none",
            "task_type": "general_ocr"
        }
        if image_url:
            response_data["image_url"] = image_url
            response_data["image_name"] = image_name
        return jsonify(response_data)
        
    if not tanglish_input:
        return jsonify({
            "error": "No input provided. Please upload an image or supply 'tanglish_text'."
        }), 400
        
    # Proactively update pipeline's API key if it changes in env
    pipeline.lm_processor.api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if pipeline.lm_processor.api_key and not pipeline.lm_processor.is_configured():
        pipeline.lm_processor.configure_model()

    # Process text through the conversational transliteration pipeline
    pipeline_results = pipeline.process(tanglish_input)
    tamil_output = pipeline_results["final_output"]

    if pipeline_results["gemini_active"]:
        used_engine = "gemini_post_processed"
    elif pipeline_results["phrase_match"]:
        used_engine = "conversational_dataset_match"
    else:
        used_engine = "local_phonetic_pipeline"

    response_data = {
        "ocr_text": tanglish_input,
        "tanglish_text": tanglish_input,
        "tamil_text": tamil_output,
        "engine_used": used_engine,
        "task_type": task_type
    }
    if image_url:
        response_data["image_url"] = image_url
        response_data["image_name"] = image_name
        
    return jsonify(response_data)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
