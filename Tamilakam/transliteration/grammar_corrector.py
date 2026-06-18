import re

class TamilGrammarCorrector:
    def __init__(self):
        self.question_endings = [
            'யா', 'ஆ', 'தானே', 'இல்லையா', 'ல', 'வா', 'போறியா', 'இருக்கியா', 'பண்றியா'
        ]

    def clean_orthography(self, text):
        if not text:
            return ""

        t = text.strip()
        
        if not t.endswith('?'):
            words = re.findall(r'\w+', t)
            if words:
                last_word = words[-1]
                for ending in self.question_endings:
                    if last_word.endswith(ending):
                        t = t + '?'
                        break

        t = re.sub(r'\?+', '?', t)
        t = re.sub(r'!+', '!', t)
        t = re.sub(r'\s+([,.?!=])', r'\1', t)
        t = re.sub(r'([்])+', r'\1', t)
        
        # Suffix conversions (e.g., "சரி அஹ்" -> "சரியா?")
        t = re.sub(r'(?<!\w)சரி\s+(அஹ்|ஆ|அ)(?!\w)', 'சரியா?', t)
        
        return t

    def correct_sentence(self, sentence):
        return self.clean_orthography(sentence)
