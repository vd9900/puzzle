#!/usr/bin/env python3
"""Comprehensive sweep of the Cosmic Duality book text against SMALL_B64, INNER_B64, and COSMIC_B64.
Parses sentences, headings, captions, and key phrases from data/user_supplied/telegram/docs/export_files/cosmic-duality_compress.pdf.txt.
"""
import sys, os, re, time, json
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')

from systematic_solver import run_sweep, forms_of, check_password

BOOK_PATH = '/home/vin/bitcoin_puzzle/data/user_supplied/telegram/docs/export_files/cosmic-duality_compress.pdf.txt'
OUT_REPORT = '/home/vin/bitcoin_puzzle/scratch/cosmic_duality_results.json'

def extract_candidates():
    with open(BOOK_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        raw_text = f.read()

    cands = set()

    # 1. Structural titles & key headings
    headings = [
        "The Unity of Opposites",
        "Dualities As Old As Time",
        "The Dark Side of Fairy Tales",
        "The Battle of the Sexes",
        "Driving the Devil Out",
        "In the Grasp of Ageless Evil",
        "Paths of Righteousness",
        "The Triumph of Good",
        "Hark! Heaven's Winged Host",
        "Cosmic Duality",
        "Mysteries of the Unknown",
        "Time-Life Books",
        "Rob Wood",
        "Stansbury, Ronsaville and Wood",
        "Unity of Opposites",
        "sigmoid line",
        "sigmoid line curving in two directions",
        "curving in two directions like the letter s",
        "like the letter s",
        "two halves separated by a sigmoid line",
        "a seed of the other",
        "contains a seed of the other",
        "each side contains a seed of the other",
        "penetrates the other and contains a seed of the other",
        "half black and half white",
        "circle that is half black and half white",
        "the light half yang",
        "the dark half yin",
        "male principle and heaven",
        "female principle and earth",
        "joined inseparably and together form the whole",
        "ch'i", "qi", "Tao", "I Ching", "Book of Changes",
        "Shiva and Shakti", "Shiva without Shakti is a corpse",
        "Shiva without Shakti",
        "two poles of force",
        "positive and negative",
        "Fortuna", "wheel of fortune",
        "separate the opposites",
        "reconciliation of opposites",
        "two-headed dragon",
        "dual nature of mercury",
        "transform metal into gold",
        "golden perfection",
        "when opposites attract",
        "opposites attract",
        "harmony between fluctuating states of oppositeness",
        "polarity", "polos", "pivot",
        "spiritual salvation",
        "freedom of choice",
        "choice between good and evil",
    ]
    for h in headings:
        cands.add(h)

    # 2. Sentences from text
    # Clean up multi-space and line breaks to normalize sentences
    normalized = re.sub(r'\s+', ' ', raw_text)
    raw_sentences = re.split(r'(?<=[.!?])\s+', normalized)

    print(f"Total raw sentences found: {len(raw_sentences)}")
    
    # Filter sentences of interest (containing keywords or of concise length)
    keywords = [
        'yin', 'yang', 'opposite', 'duality', 'seed', 'flower', 'rose', 'door',
        'choice', 'half', 'salvation', 'circle', 'sigmoid', 'shiva', 'shakti',
        'dragon', 'mercury', 'gold', 'light', 'dark', 'balance', 'harmony',
        'beginning', 'end', 'flaw', 'truth', 'two', 'tao', 'ch\'i', 'qi'
    ]
    
    for s in raw_sentences:
        s_clean = s.strip()
        # Keep reasonably sized sentences (between 10 and 200 chars)
        if 10 <= len(s_clean) <= 150:
            words = s_clean.split()
            if any(k in s_clean.lower() for k in keywords):
                cands.add(s_clean)
                # Also add without trailing punctuation
                cands.add(s_clean.rstrip('.!?,"\''))

    # 3. Specific clauses around Yin-Yang (pp. 34-36)
    p34_clauses = [
        "The symbol is a circle that is half black and half white",
        "half black and half white, the two halves separated by a sigmoid line",
        "the two halves separated by a sigmoid line",
        "separated by a sigmoid line, curving in two directions like the letter s",
        "curving in two directions like the letter s",
        "each side of the symbol demonstrably penetrates the other",
        "contains a seed of the other",
        "The light half, yang, is thought of as the active side",
        "associated with the male principle and heaven",
        "The dark half, on the other hand, is considered passive",
        "associated with the female principle and earth",
        "these dualities are joined inseparably and together form the whole",
        "joined inseparably and together form the whole",
        "complementary opposites sprang from a single cosmic cell",
        "sprang from a single cosmic cell, called ch'i, or qi",
        "brought into existence by the creative force called Tao",
        "achieve harmony between fluctuating states of oppositeness",
        "harmony between fluctuating states of oppositeness",
        "Shiva without Shakti is a corpse",
        "Shiva without Shakti",
        "two parts of the same whole",
        "interconnectedness of life's dualities",
        "reconciliation of opposites",
    ]
    for c in p34_clauses:
        cands.add(c)

    print(f"Total deduplicated candidate phrases: {len(cands)}")
    return list(cands)

def main():
    print("Extracting candidates from Cosmic Duality book...")
    t0 = time.time()
    cands = extract_candidates()
    print(f"Extraction completed in {time.time() - t0:.2f}s.")
    
    print("\nRunning systematic sweep against SMALL_B64, INNER_B64, and COSMIC_B64...")
    hits = run_sweep(cands, label="COSMIC_DUALITY_BOOK_SWEEP")
    
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": BOOK_PATH,
        "candidate_count": len(cands),
        "hit_count": len(hits),
        "hits": hits
    }
    with open(OUT_REPORT, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {OUT_REPORT}.")

if __name__ == '__main__':
    main()
