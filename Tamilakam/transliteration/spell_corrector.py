import re

class TanglishSpellCorrector:
    def __init__(self, known_words=None):
        self.known_words = set(known_words) if known_words else set()
        
    def add_known_words(self, words):
        self.known_words.update(words)

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

    def phonetic_normalize(self, word):
        from transliteration.phonetic_normalizer import TanglishPhoneticNormalizer
        return TanglishPhoneticNormalizer.get_phonetic_key(word)

    def correct_word(self, word):
        if not word:
            return ""
            
        cleaned = word.lower().strip()
        if cleaned in self.known_words:
            return cleaned

        pkey = self.phonetic_normalize(cleaned)
        
        # 1. Phonetic key matching (exact match on phonetic representation)
        candidates = [kw for kw in self.known_words if self.phonetic_normalize(kw) == pkey]
        if candidates:
            # Return the candidate with the smallest raw Levenshtein distance
            return min(candidates, key=lambda kw: self.levenshtein_distance(cleaned, kw))

        # 2. Fuzzy phonetic key matching (closest key based on distance of phonetic representations)
        best_kw = None
        min_p_dist = float('inf')
        
        for kw in self.known_words:
            if ' ' in kw:
                continue
            kw_pkey = self.phonetic_normalize(kw)
            p_dist = self.levenshtein_distance(pkey, kw_pkey)
            if p_dist < min_p_dist:
                min_p_dist = p_dist
                best_kw = kw
            elif p_dist == min_p_dist and best_kw:
                # Tie-breaker: raw distance to typed word
                if self.levenshtein_distance(cleaned, kw) < self.levenshtein_distance(cleaned, best_kw):
                    best_kw = kw

        max_allowed_p_dist = 1 if len(pkey) >= 6 else 0
        if min_p_dist <= max_allowed_p_dist and best_kw:
            return best_kw

        return cleaned

    def correct_sentence(self, sentence):
        if not sentence:
            return ""
            
        tokens = re.split(r'(\s+|[^\w\'])', sentence)
        corrected_tokens = []
        
        for token in tokens:
            if re.match(r'^[a-zA-Z\']+$', token):
                corrected_tokens.append(self.correct_word(token))
            else:
                corrected_tokens.append(token)
                
        return "".join(corrected_tokens)
