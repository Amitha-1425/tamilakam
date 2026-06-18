import os
import csv
import sys
import re
from transliteration.pipeline import TransliterationPipeline
from app import clean_and_transliterate_word

def clean_comparable_tamil(text):
    if not text:
        return ""
    # Strip common punctuation and whitespaces
    t = text.strip()
    t = re.sub(r'[^\w\s]', '', t)
    return re.sub(r'\s+', ' ', t).strip()

def run_evaluation():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
        
    print("Initializing Transliteration Pipeline...")
    pipeline = TransliterationPipeline(local_transliterate_fn=clean_and_transliterate_word)
    
    # 1. Run core spelling variation benchmark cases
    benchmark_cases = [
        ("epdi iruka", "எப்படி இருக்க?"),
        ("naan nala iruken", "நான் நல்லா இருக்கேன்"),
        ("enga pora", "எங்க போற?"),
        ("saptiya", "சாப்பிட்டியா?"),
        ("yenna", "என்ன"),
        ("ennaa", "என்ன"),
        ("yeppo", "எப்போ"),
        ("yeppoo", "எப்போ"),
        ("eppidi irukinga", "எப்படி இருக்கீங்க?"),
        ("enna da thambi saptiya nalla irukiya vittuku epo vara", "என்ன டா தம்பி சாப்பிட்டியா நல்லா இருக்கியா வீட்டுக்கு எப்போ வர?")
    ]
    
    print("\n==================================================")
    print("Baseline Spelling Variation Benchmark")
    print("==================================================")
    
    bench_passed = 0
    for input_txt, expected_txt in benchmark_cases:
        steps = pipeline.process(input_txt)
        output_txt = steps["final_output"].strip()
        
        c_out = clean_comparable_tamil(output_txt)
        c_exp = clean_comparable_tamil(expected_txt)
        passed = (c_out == c_exp) or (output_txt == expected_txt)
        
        if passed:
            bench_passed += 1
        print(f"Input   : {input_txt}")
        print(f"Expected: {expected_txt}")
        print(f"Result  : {output_txt}")
        print(f"Status  : {'PASSED ✅' if passed else 'FAILED ❌'}")
        print("-" * 50)
        
    print(f"Benchmark Score: {bench_passed}/{len(benchmark_cases)} passed.")
    
    # 2. Run test dataset evaluation
    test_csv_path = os.path.join("dataset", "test.csv")
    if not os.path.exists(test_csv_path):
        print(f"Error: test dataset not found at {test_csv_path}")
        return 1
        
    print("\n==================================================")
    print("Test Dataset CSV Evaluation")
    print(f"File: {test_csv_path}")
    print("==================================================")
    
    total_sentences = 0
    correct_sentences = 0
    total_words = 0
    correct_words = 0
    
    failures = []
    
    with open(test_csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)  # Skip header
        
        for row in reader:
            if len(row) < 2:
                continue
            tanglish, expected_tamil = row[0].strip(), row[1].strip()
            
            steps = pipeline.process(tanglish)
            output_tamil = steps["final_output"].strip()
            
            c_out = clean_comparable_tamil(output_tamil)
            c_exp = clean_comparable_tamil(expected_tamil)
            
            # Sentence level metrics
            total_sentences += 1
            is_sentence_correct = (c_out == c_exp)
            if is_sentence_correct:
                correct_sentences += 1
            else:
                if len(failures) < 15:
                    failures.append((tanglish, expected_tamil, output_tamil))
            
            # Word level metrics
            out_words = c_out.split()
            exp_words = c_exp.split()
            
            total_words += len(exp_words)
            # Simple alignment word-match counter
            matched = sum(1 for w1, w2 in zip(out_words, exp_words) if w1 == w2)
            correct_words += matched
            
    sentence_accuracy = (correct_sentences / total_sentences) * 100 if total_sentences > 0 else 0
    word_accuracy = (correct_words / total_words) * 100 if total_words > 0 else 0
    
    print(f"Evaluated Sentences : {total_sentences}")
    print(f"Sentence Accuracy   : {sentence_accuracy:.2f}% ({correct_sentences}/{total_sentences})")
    print(f"Evaluated Words     : {total_words}")
    print(f"Word Accuracy       : {word_accuracy:.2f}% ({correct_words}/{total_words})")
    
    if failures:
        print("\n--- Sample Failure Cases (First 15) ---")
        for idx, (t, exp, got) in enumerate(failures, 1):
            print(f"{idx}. Input   : {t}")
            print(f"   Expected: {exp}")
            print(f"   Got     : {got}")
            print()
            
    # Return exit code based on test performance
    if sentence_accuracy >= 85.0:
        print("EVALUATION SUCCESSFUL! Accuracy is above 85% threshold. 🎉")
        return 0
    else:
        print("EVALUATION FAILED. Accuracy is below 85% threshold. Retuning phonetic heuristics recommended.")
        return 1

if __name__ == "__main__":
    sys.exit(run_evaluation())
