import re

class TanglishPhoneticNormalizer:
    @staticmethod
    def get_phonetic_key(word):
        if not word:
            return ""
        
        w = word.lower().strip()
        
        # 1. Initial vowel/glide normalization
        if w.startswith("ye") or w.startswith("yae") or w.startswith("yey"):
            w = "e" + w[2:] if w.startswith("ye") else "e" + w[3:]
        elif w.startswith("ya"):
            w = "a" + w[2:] if w.startswith("yaa") else "a" + w[1:]
        elif w.startswith("yo"):
            w = "o" + w[2:] if w.startswith("yoo") else "o" + w[1:]
        elif w.startswith("wa") or w.startswith("wo"):
            w = "v" + w[1:]

        # 2. Vowel mapping & collapsing
        # Order matters to avoid partial matching issues
        w = w.replace("aa", "a")
        w = w.replace("ee", "i")
        w = w.replace("ii", "i")
        w = w.replace("uu", "u")
        w = w.replace("oo", "o")  # informal: oo often maps to o (e.g. yeppoo -> yeppo)
        w = w.replace("oa", "o")
        w = w.replace("ae", "e")
        w = w.replace("ey", "e")
        w = w.replace("ai", "i")
        w = w.replace("ay", "i")

        # 3. Consonant grouping (mapping phonetically similar characters together)
        w = w.replace("th", "t")
        w = w.replace("dh", "t")
        w = w.replace("d", "t")
        w = w.replace("kh", "k")
        w = w.replace("gh", "k")
        w = w.replace("g", "k")
        w = w.replace("bh", "p")
        w = w.replace("ph", "p")
        w = w.replace("b", "p")
        w = w.replace("sh", "s")
        w = w.replace("ch", "s")
        w = w.replace("c", "s")
        w = w.replace("zh", "l")
        w = w.replace("lh", "l")
        w = w.replace("nj", "n")
        w = w.replace("ng", "n")
        w = w.replace("w", "v")
        
        # Remove any lingering silent 'h' (e.g. rombha -> romba)
        w = w.replace("h", "")

        # 4. Collapse adjacent identical characters (consonants and vowels)
        w = re.sub(r'([a-z])\1+', r'\1', w)

        # 5. Standardize final vowels/glides
        if len(w) > 1:
            if w.endswith("y"):
                w = w[:-1] + "i"
            elif w.endswith("a") or w.endswith("e") or w.endswith("o") or w.endswith("u") or w.endswith("i"):
                # Ensure simple single vowel ending
                pass

        return w
