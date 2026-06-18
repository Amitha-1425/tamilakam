import os
import json
import re

class ConversationalDatasetPipeline:
    def __init__(self, dataset_path=None):
        if dataset_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            dataset_path = os.path.join(current_dir, "dataset", "train.csv")
        
        self.dataset_path = dataset_path
        self.phrases = {}
        self.words = {}
        self.phonetic_phrases = {}
        self.phonetic_words = {}
        self.load_dataset()

    def load_dataset(self):
        """Loads conversational pairs from CSV dataset."""
        self.phrases = {}
        self.words = {}
        self.phonetic_phrases = {}
        self.phonetic_words = {}
        
        if not os.path.exists(self.dataset_path):
            return

        try:
            import csv
            from transliteration.phonetic_normalizer import TanglishPhoneticNormalizer

            with open(self.dataset_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)  # Skip header
                
                for row in reader:
                    if len(row) < 2:
                        continue
                    tanglish, tamil = row[0].strip(), row[1].strip()
                    
                    cleaned_tanglish = self.clean_text(tanglish)
                    cleaned_tanglish_no_punct = self.clean_punctuation(cleaned_tanglish)
                    
                    # Store phrase mapping
                    self.phrases[cleaned_tanglish] = tamil
                    self.phrases[cleaned_tanglish_no_punct] = tamil
                    
                    # Unsupervised word alignment heuristic to learn vocabulary
                    t_words = cleaned_tanglish_no_punct.split()
                    
                    # Clean punctuation from Tamil words
                    tamil_no_punct = re.sub(r'[.,!;:\"\'“”]', '', tamil).strip()
                    # Clean question mark/period from individual words
                    ta_words = [w.replace("?", "").replace(".", "").strip() for w in tamil_no_punct.split()]
                    
                    if len(t_words) == len(ta_words):
                        for i in range(len(t_words)):
                            t_w = t_words[i]
                            ta_w = ta_words[i]
                            if t_w and ta_w:
                                self.words[t_w] = ta_w

            # Build phonetic indexes based on learned vocabulary
            for tanglish, tamil in self.phrases.items():
                pkey = TanglishPhoneticNormalizer.get_phonetic_key(tanglish)
                if pkey not in self.phonetic_phrases:
                    self.phonetic_phrases[pkey] = []
                if (tanglish, tamil) not in self.phonetic_phrases[pkey]:
                    self.phonetic_phrases[pkey].append((tanglish, tamil))
                
            for tanglish, tamil in self.words.items():
                pkey = TanglishPhoneticNormalizer.get_phonetic_key(tanglish)
                if pkey not in self.phonetic_words:
                    self.phonetic_words[pkey] = []
                if (tanglish, tamil) not in self.phonetic_words[pkey]:
                    self.phonetic_words[pkey].append((tanglish, tamil))
                
        except Exception as e:
            print(f"Error loading conversational dataset from CSV: {e}")

    def save_dataset(self):
        """Saves current memory mappings back to the CSV dataset file."""
        os.makedirs(os.path.dirname(self.dataset_path), exist_ok=True)
        try:
            import csv
            with open(self.dataset_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["tanglish", "tamil"])
                for tanglish, tamil in self.phrases.items():
                    writer.writerow([tanglish, tamil])
            return True
        except Exception as e:
            print(f"Error saving dataset to CSV: {e}")
            return False

    def clean_text(self, text):
        """Normalizes spacing, casing, and basic formatting."""
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        return text

    def clean_punctuation(self, text):
        """Removes punctuation for matching purposes."""
        return re.sub(r'[^\w\s]', '', text).strip()

    def levenshtein_distance(self, s1, s2):
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    def lookup_phrase(self, phrase):
        """Checks if a full phrase matches our conversational phrases dict."""
        cleaned = self.clean_text(phrase)
        cleaned_no_punct = self.clean_punctuation(cleaned)
        
        # 1. Exact match
        if cleaned in self.phrases:
            return self.phrases[cleaned]
        if cleaned_no_punct in self.phrases:
            return self.phrases[cleaned_no_punct]
            
        # 2. Phonetic key match
        from transliteration.phonetic_normalizer import TanglishPhoneticNormalizer
        pkey = TanglishPhoneticNormalizer.get_phonetic_key(cleaned_no_punct)
        if pkey in self.phonetic_phrases:
            candidates = self.phonetic_phrases[pkey]
            best_cand = min(candidates, key=lambda c: self.levenshtein_distance(cleaned_no_punct, c[0]))
            return best_cand[1]

        # 3. Fuzzy phonetic match (distance on phonetic keys)
        best_cand = None
        min_dist = float('inf')
        for kkey, candidates in self.phonetic_phrases.items():
            dist = self.levenshtein_distance(pkey, kkey)
            if dist < min_dist:
                min_dist = dist
                best_cand = min(candidates, key=lambda c: self.levenshtein_distance(cleaned_no_punct, c[0]))

        max_allowed = 1 if len(pkey) >= 6 else 0
        if min_dist <= max_allowed and best_cand:
            return best_cand[1]

        return None

    def lookup_word(self, word):
        """Checks if a single word matches our conversational words dict."""
        cleaned = self.clean_text(word)
        cleaned_no_punct = self.clean_punctuation(cleaned)
        
        # 1. Exact match
        if cleaned in self.words:
            return self.words[cleaned]
        if cleaned_no_punct in self.words:
            return self.words[cleaned_no_punct]
            
        # 2. Phonetic key match
        from transliteration.phonetic_normalizer import TanglishPhoneticNormalizer
        pkey = TanglishPhoneticNormalizer.get_phonetic_key(cleaned_no_punct)
        if pkey in self.phonetic_words:
            candidates = self.phonetic_words[pkey]
            best_cand = min(candidates, key=lambda c: self.levenshtein_distance(cleaned_no_punct, c[0]))
            return best_cand[1]

        # 3. Fuzzy phonetic match (distance on phonetic keys)
        best_cand = None
        min_dist = float('inf')
        for kkey, candidates in self.phonetic_words.items():
            dist = self.levenshtein_distance(pkey, kkey)
            if dist < min_dist:
                min_dist = dist
                best_cand = min(candidates, key=lambda c: self.levenshtein_distance(cleaned_no_punct, c[0]))

        max_allowed = 1 if len(pkey) >= 6 else 0
        if min_dist <= max_allowed and best_cand:
            return best_cand[1]

        return None

    def add_phrase_pair(self, tanglish, tamil):
        """Dynamically adds a phrase pair to the dataset."""
        tanglish_clean = self.clean_text(tanglish)
        if tanglish_clean:
            self.phrases[tanglish_clean] = tamil.strip()
            from transliteration.phonetic_normalizer import TanglishPhoneticNormalizer
            pkey = TanglishPhoneticNormalizer.get_phonetic_key(tanglish_clean)
            if pkey not in self.phonetic_phrases:
                self.phonetic_phrases[pkey] = []
            if (tanglish_clean, tamil.strip()) not in self.phonetic_phrases[pkey]:
                self.phonetic_phrases[pkey].append((tanglish_clean, tamil.strip()))
            self.save_dataset()

    def add_word_pair(self, tanglish, tamil):
        """Dynamically adds a word pair to the dataset."""
        tanglish_clean = self.clean_text(tanglish)
        if tanglish_clean:
            self.words[tanglish_clean] = tamil.strip()
            from transliteration.phonetic_normalizer import TanglishPhoneticNormalizer
            pkey = TanglishPhoneticNormalizer.get_phonetic_key(tanglish_clean)
            if pkey not in self.phonetic_words:
                self.phonetic_words[pkey] = []
            if (tanglish_clean, tamil.strip()) not in self.phonetic_words[pkey]:
                self.phonetic_words[pkey].append((tanglish_clean, tamil.strip()))
            self.save_dataset()
