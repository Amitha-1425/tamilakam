import re
from dataset_pipeline import ConversationalDatasetPipeline
from transliteration.spell_corrector import TanglishSpellCorrector
from transliteration.grammar_corrector import TamilGrammarCorrector
from transliteration.lm_post_processor import GeminiPostProcessor

# The TransliterationPipeline leverages ConversationalDatasetPipeline and
# TanglishSpellCorrector, both of which are enhanced with a phonetic normalization layer
# to support variations of Tanglish inputs dynamically.

class TransliterationPipeline:
    def __init__(self, dataset_path=None, gemini_api_key=None, local_transliterate_fn=None):
        self.dataset = ConversationalDatasetPipeline(dataset_path)
        
        known_words = list(self.dataset.words.keys()) + list(self.dataset.phrases.keys())
        self.spell_corrector = TanglishSpellCorrector(known_words)
        self.grammar_corrector = TamilGrammarCorrector()
        self.lm_processor = GeminiPostProcessor(gemini_api_key)
        self.local_transliterate_fn = local_transliterate_fn

    def process(self, text):
        steps = {
            "raw_input": text,
            "spell_corrected": "",
            "phrase_match": False,
            "transliterated": "",
            "grammar_corrected": "",
            "lm_refined": "",
            "final_output": "",
            "gemini_active": self.lm_processor.is_configured()
        }

        if not text or not text.strip():
            return steps

        cleaned_input = self.dataset.clean_text(text)
        
        # 1. Exact phrase match in the dataset first
        phrase_lookup = self.dataset.lookup_phrase(cleaned_input)
        if phrase_lookup:
            steps["spell_corrected"] = text
            steps["phrase_match"] = True
            steps["transliterated"] = phrase_lookup
            steps["grammar_corrected"] = self.grammar_corrector.correct_sentence(phrase_lookup)
            
            if self.lm_processor.is_configured():
                refined = self.lm_processor.post_process(text, steps["grammar_corrected"])
                steps["lm_refined"] = refined
                steps["final_output"] = refined
            else:
                steps["final_output"] = steps["grammar_corrected"]
                
            return steps

        # 2. Spell correction
        corrected_text = self.spell_corrector.correct_sentence(text)
        steps["spell_corrected"] = corrected_text
        
        # Re-check phrase lookup with spell corrected text
        cleaned_corrected = self.dataset.clean_text(corrected_text)
        phrase_lookup_corrected = self.dataset.lookup_phrase(cleaned_corrected)
        if phrase_lookup_corrected:
            steps["phrase_match"] = True
            steps["transliterated"] = phrase_lookup_corrected
            steps["grammar_corrected"] = self.grammar_corrector.correct_sentence(phrase_lookup_corrected)
            
            if self.lm_processor.is_configured():
                refined = self.lm_processor.post_process(corrected_text, steps["grammar_corrected"])
                steps["lm_refined"] = refined
                steps["final_output"] = refined
            else:
                steps["final_output"] = steps["grammar_corrected"]
                
            return steps

        # 3. Word-by-word transliteration (dataset words lookup first, then local phonetic function)
        tokens = re.split(r'(\s+|[^\w\'])', corrected_text)
        transliterated_tokens = []
        
        for token in tokens:
            if re.match(r'^[a-zA-Z\']+$', token):
                word_lookup = self.dataset.lookup_word(token)
                if word_lookup:
                    transliterated_tokens.append(word_lookup)
                else:
                    if self.local_transliterate_fn:
                        transliterated_tokens.append(self.local_transliterate_fn(token))
                    else:
                        transliterated_tokens.append(token)
            else:
                transliterated_tokens.append(token)
                
        transliterated_text = "".join(transliterated_tokens)
        steps["transliterated"] = transliterated_text
        
        # 4. Tamil grammar and orthography correction
        grammar_corrected_text = self.grammar_corrector.correct_sentence(transliterated_text)
        steps["grammar_corrected"] = grammar_corrected_text
        
        # 5. Language model refinement
        if self.lm_processor.is_configured():
            refined_text = self.lm_processor.post_process(corrected_text, grammar_corrected_text)
            steps["lm_refined"] = refined_text
            steps["final_output"] = refined_text
        else:
            steps["final_output"] = grammar_corrected_text
            
        return steps
