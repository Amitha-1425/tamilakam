import os

class GeminiPostProcessor:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "").strip()
        self.model = None
        
        if self.api_key and self.api_key.upper() != "YOUR_GEMINI_API_KEY_HERE":
            self.configure_model()

    def configure_model(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        except ImportError:
            print("Warning: google-generativeai package not installed. Gemini post-processing will be disabled.")
            self.model = None
        except Exception as e:
            print(f"Error configuring Gemini: {e}")
            self.model = None

    def is_configured(self):
        return self.model is not None

    def post_process(self, raw_tanglish, transliterated_tamil):
        if not self.is_configured():
            return transliterated_tamil

        if not raw_tanglish or not transliterated_tamil:
            return transliterated_tamil

        prompt = f"""
You are an expert Tamil language linguist specializing in conversational Tamil, social media dialogues, and Tanglish-to-Tamil conversion.

Task:
Refine the provided initial transliterated Tamil text by comparing it with the original raw Tanglish input. Correct any spelling errors, grammatical mistakes, structural alignment issues, and improper word endings. The output should be natural, grammatically correct conversational Tamil (social media tone), NOT formal written Tamil unless the input was formal.

Rules:
1. Output ONLY the refined Tamil text. Do not include any explanations, side notes, introduction, or prefix.
2. Maintain the conversational/colloquial tone of the original Tanglish (e.g. "இருக்கேன்" instead of "இருக்கிறேன்", "நல்லா" instead of "நன்றாக").
3. Fix grammar errors: check pronoun-verb agreement (e.g. "நான்... இருக்கேன்", "நீ... இருக்கிறாய்" or "இருக்க"), sentence structure, and appropriate question endings (e.g., adding "?").
4. If a common English loanword is used in Tanglish and cannot be translated nicely, transliterate it naturally into Tamil characters (e.g. "super" -> "சூப்பர்", "vibe" -> "வைப்").

Input Context:
- Raw Tanglish: "{raw_tanglish}"
- Initial Transliteration: "{transliterated_tamil}"

Examples:
- Raw Tanglish: "epdi iruka"
- Initial Transliteration: "எப்டி இருகா"
- Output: "எப்படி இருக்க?"

- Raw Tanglish: "naan nala iruken"
- Initial Transliteration: "நான் நல இருகேன்"
- Output: "நான் நல்லா இருக்கேன்"

- Raw Tanglish: "solren nalla ketuko"
- Initial Transliteration: "சொல்ரேன் நல்லா கெடுகோ"
- Output: "சொல்றேன் நல்லா கேட்டுக்கோ"

Output refined Tamil text:
"""
        try:
            response = self.model.generate_content(prompt)
            text_val = getattr(response, "text", None) or str(response)
            refined_text = text_val.strip()
            if refined_text:
                return refined_text
        except Exception as e:
            print(f"Gemini post-processing error: {e}")
            
        return transliterated_tamil
