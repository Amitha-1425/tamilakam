import os
import csv
import random
import itertools

# Define categories and base sentences
BASE_TEMPLATES = {
    "Daily Conversations": [
        ("epdi iruka", "எப்படி இருக்க?"),
        ("epdi irukinga", "எப்படி இருக்கீங்க?"),
        ("naan nalla iruken", "நான் நல்லா இருக்கேன்"),
        ("nanba epdi iruka", "நண்பா எப்படி இருக்க?"),
        ("enna panra", "என்ன பண்ற?"),
        ("enna panringa", "என்ன பண்றீங்க?"),
        ("solren nalla ketuko", "சொல்றேன் நல்லா கேட்டுக்கோ."),
        ("romba nandri", "ரொம்ப நன்றி"),
        ("vaada machan", "வாடா மச்சான்"),
        ("enga pora", "எங்க போற?"),
        ("saptiya", "சாப்பிட்டியா?"),
        ("sapteengala", "சாப்பிட்டீங்களா?"),
        ("sari appram paarkalam", "சரி அப்புறம் பார்க்கலாம்."),
        ("inniku nalla naal", "இன்னைக்கு நல்ல நாள்."),
        ("vibe nalla iruku", "வைப் நல்லா இருக்கு."),
        ("solra macha", "சொல்றா மச்சா."),
        ("enna aachu", "என்ன ஆச்சு?"),
        ("kadhai sollu", "கதை சொல்லு."),
        ("nethu enga pona", "நேத்து எங்க போன?"),
        ("enaku puriyala", "எனக்கு புரியல."),
        ("unaku puriyudha", "உனக்கு புரியுதா?"),
        ("aama adhu dhaan", "ஆமா அது தான்."),
        ("illa illai", "இல்ல இல்லை."),
        ("romba kavalaiya iruku", "ரொம்ப கவலையா இருக்கு.")
    ],
    "Family Conversations": [
        ("amma saapadu readyaa", "அம்மா சாப்பாடு ரெடியா?"),
        ("appa eppo varraanga", "அப்பா எப்போ வர்றாங்க?"),
        ("thambi padikiriya", "தம்பி படிக்கிறியா?"),
        ("thangachi enga pona", "தங்கச்சி எங்க போன?"),
        ("veetla ellarum epdi irukaanga", "வீட்ல எல்லாரும் எப்படி இருக்காங்க?"),
        ("akkavuku kalyanam", "அக்காவுக்கு கல்யாணம்."),
        ("annave koopidu", "அண்ணாவை கூப்பிடு."),
        ("veetu velai mudinjadhu", "வீட்டு வேலை முடிஞ்சது."),
        ("vittuku epo vara", "வீட்டுக்கு எப்போ வர?"),
        ("veetuku va", "வீட்டுக்கு வா."),
        ("uravinargal vandhaanga", "உறவினர்கள் வந்தாங்க.")
    ],
    "Student Conversations": [
        ("college eppo mudiyum", "கல்லூரி எப்போ முடியும்?"),
        ("exam sema tough", "தேர்வு செம கடினம்."),
        ("assignment ezhudhitiya", "அசைன்மென்ட் எழுதிட்டியா?"),
        ("attendance vandhucha", "வருகைப்பதிவு வந்துச்சா?"),
        ("project ready panra", "புராஜெக்ட் ரெடி பண்றா."),
        ("palli koodam ponom", "பள்ளி கூடம் போனோம்."),
        ("friendu call panran", "பிரெண்டு கால் பண்றான்."),
        ("class eppo aarambam", "வகுப்பு எப்போ ஆரம்பம்?"),
        ("marks vandhuruchu", "மதிப்பெண்கள் வந்துருச்சு.")
    ],
    "Social Media Conversations": [
        ("inniku sema vibe", "இன்னைக்கு செம வைப்."),
        ("sema photo bro", "செம படம் ப்ரோ."),
        ("comment panunga makkale", "கமெண்ட் பண்ணுங்க மக்களே."),
        ("caption nalla iruku", "கேப்ஷன் நல்லா இருக்கு."),
        ("status paarthiya", "ஸ்டேட்டஸ் பார்த்தியா?"),
        ("trending video adhu", "டிரெண்டிங் வீடியோ அது."),
        ("thalaivare gethu", "தலைவரே கெத்து."),
        ("vibe pandrom", "வைப் பண்றோம்.")
    ],
    "Motivational and Quote Content": [
        ("vazhkaiyil vetri peruvom", "வாழ்க்கையில் வெற்றி பெறுவோம்."),
        ("nambikai dhaan ellam", "நம்பிக்கை தான் எல்லாம்."),
        ("anbe vazhi", "அன்பே வழி."),
        ("karunai kaatungal", "கருணை காட்டுங்கள்."),
        ("uyir nalla vazhum", "உயிர் நல்லா வாழும்."),
        ("uyaram thodu", "உயரம் தொடு."),
        ("dhrogam seyyadhe", "துரோகம் செய்யாதே."),
        ("santhosham perumai", "சந்தோஷம் பெருமை.")
    ],
    "Common Spoken Tamil": [
        ("ooruku poriya", "ஊருக்கு போறியா?"),
        ("panam vechirukiya", "பணம் வச்சிருக்கியா?"),
        ("thanni venum", "தண்ணி வேணும்."),
        ("kaasu illa", "காசு இல்ல."),
        ("inniku velai iruku", "இன்னைக்கு வேலை இருக்கு."),
        ("naalaiku paarkalam", "நாளைக்கு பார்க்கலாம்."),
        ("romba sandhosham", "ரொம்ப சந்தோஷம்."),
        ("kovam padadhe", "கோபம் படாதே."),
        ("bayam yen", "பயம் ஏன்?")
    ],
    "Public Place Conversations": [
        ("bus stand enga iruku", "பஸ் ஸ்டாண்ட் எங்க இருக்கு?"),
        ("railway station eppo varum", "ரயில்வே ஸ்டேஷன் எப்போ வரும்?"),
        ("hospital ponom", "ஆஸ்பத்திரி போனோம்."),
        ("bank openaa", "வங்கி திறந்திருக்கா?"),
        ("office poitu varren", "அலுவலகம் போயிட்டு வர்றேன்."),
        ("kadaiyila vangu", "கடையில வாங்கு.")
    ]
}

# Programmatic spelling variation generator rules
def get_word_variations(word):
    # Strip punctuation
    w_clean = "".join([c for c in word.lower() if c.isalnum() or c == "'"])
    if not w_clean:
        return [word]
    
    # Generate variations for segments of the word
    variations = {w_clean}
    
    # Rule 1: Initial glides
    if w_clean.startswith("e"):
        variations.add("ye" + w_clean[1:])
        variations.add("ena" if w_clean == "enna" else "e" + w_clean[1:])
    elif w_clean.startswith("a"):
        variations.add("ya" + w_clean[1:])
    elif w_clean.startswith("o"):
        variations.add("yo" + w_clean[1:])
    elif w_clean.startswith("v"):
        variations.add("w" + w_clean[1:])

    # Rule 2: Consonant clusters
    curr = list(variations)
    for v in curr:
        # th/dh/d/t mappings
        v_mod = v.replace("th", "t").replace("dh", "t").replace("d", "t")
        variations.add(v_mod)
        v_mod2 = v.replace("t", "th")
        variations.add(v_mod2)
        v_mod3 = v.replace("t", "dh")
        variations.add(v_mod3)
        v_mod4 = v.replace("t", "d")
        variations.add(v_mod4)
        
        # g/k/kh/gh mappings
        g_mod = v.replace("kh", "k").replace("gh", "k").replace("g", "k").replace("kk", "k")
        variations.add(g_mod)
        g_mod2 = v.replace("k", "g")
        variations.add(g_mod2)
        
        # p/b/bh/ph mappings
        p_mod = v.replace("bh", "p").replace("ph", "p").replace("b", "p").replace("pp", "p")
        variations.add(p_mod)
        p_mod2 = v.replace("p", "b")
        variations.add(p_mod2)
        
        # sh/ch/c/s mappings
        s_mod = v.replace("sh", "s").replace("ch", "s").replace("c", "s")
        variations.add(s_mod)
        
        # l/zh/lh/ll mappings
        l_mod = v.replace("zh", "l").replace("lh", "l").replace("ll", "l")
        variations.add(l_mod)
        l_mod2 = v.replace("l", "zh")
        variations.add(l_mod2)
        
        # n/nn/nh mappings
        n_mod = v.replace("nn", "n").replace("nh", "n")
        variations.add(n_mod)
        
        # r/rr mappings
        r_mod = v.replace("rr", "r")
        variations.add(r_mod)
        r_mod2 = v.replace("r", "rr")
        variations.add(r_mod2)

    # Rule 3: Vowel variations
    curr = list(variations)
    for v in curr:
        # aa/a
        variations.add(v.replace("aa", "a"))
        variations.add(v.replace("a", "aa"))
        
        # ee/ii/i/ey/ae/e
        variations.add(v.replace("ee", "i").replace("ii", "i"))
        variations.add(v.replace("ee", "e").replace("ey", "e").replace("ae", "e"))
        variations.add(v.replace("e", "ee"))
        variations.add(v.replace("i", "ee"))
        
        # oo/uu/u/oa/o
        variations.add(v.replace("oo", "u").replace("uu", "u"))
        variations.add(v.replace("oo", "o").replace("oa", "o"))
        variations.add(v.replace("o", "oo"))
        variations.add(v.replace("u", "oo"))

    # Deduplicate and clean
    res = list(set(variations))
    # Return at most 8 random variations to avoid exponential growth
    if len(res) > 8:
        res = random.sample(res, 8)
    return res

def generate_sentence_pairs():
    pairs = []
    
    # 1. Generate sentence-level variations
    for category, base_pairs in BASE_TEMPLATES.items():
        print(f"Generating variations for category: {category}...")
        for tanglish_base, tamil in base_pairs:
            words = tanglish_base.split()
            # Generate variations for each word
            word_options = [get_word_variations(w) for w in words]
            # Get cartesian product of word variations to make sentences
            for word_comb in itertools.product(*word_options):
                tanglish_variant = " ".join(word_comb)
                pairs.append((tanglish_variant, tamil))
                
    # 2. Add baseline word-level variations to ensure core vocab mapping
    BASE_WORDS = [
        ("da", "டா"),
        ("daa", "டா"),
        ("di", "டி"),
        ("dii", "டி"),
        ("irukiya", "இருக்கியா"),
        ("irukiyaa", "இருக்கியா"),
        ("vittuku", "வீட்டுக்கு"),
        ("veetuku", "வீட்டுக்கு"),
        ("vara", "வர"),
        ("varra", "வர்ற"),
        ("naalaiku", "நாளைக்கு"),
        ("nalaiku", "நாளைக்கு"),
        ("nalaki", "நாளைக்கு"),
        ("naalaiki", "நாளைக்கு"),
        ("nalaikki", "நாளைக்கு"),
        ("seri", "சரி"),
        ("sari", "சரி"),
        ("sariya", "சரியா"),
        ("seriya", "சரியா"),
        ("enga", "எங்க"),
        ("yenga", "எங்க"),
        ("ooruku", "ஊருக்கு"),
        ("oorukku", "ஊருக்கு"),
        ("vaa", "வா"),
        ("va", "வா"),
        ("iruka", "இருக்க"),
        ("irukka", "இருக்க"),
        ("irukinga", "இருக்கீங்க")
    ]
    for tanglish_base, tamil in BASE_WORDS:
        variations = get_word_variations(tanglish_base)
        for v in variations:
            pairs.append((v, tamil))
            
    # Deduplicate pairs
    unique_pairs = list(set(pairs))
    print(f"Total unique pairs generated: {len(unique_pairs)}")
    return unique_pairs

def save_splits(pairs):
    random.seed(42)
    random.shuffle(pairs)
    
    total = len(pairs)
    train_idx = int(total * 0.8)
    val_idx = int(total * 0.9)
    
    train_data = pairs[:train_idx]
    val_data = pairs[train_idx:val_idx]
    test_data = pairs[val_idx:]
    
    dataset_dir = r"c:\Users\midhu\OneDrive\Desktop\Tamilakam\dataset"
    os.makedirs(dataset_dir, exist_ok=True)
    
    def write_csv(filename, data):
        path = os.path.join(dataset_dir, filename)
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["tanglish", "tamil"])
            writer.writerows(data)
        print(f"Wrote {len(data)} rows to {path}")
        
    write_csv("train.csv", train_data)
    write_csv("validation.csv", val_data)
    write_csv("test.csv", test_data)

if __name__ == "__main__":
    generated_pairs = generate_sentence_pairs()
    save_splits(generated_pairs)
