#!/usr/bin/env python3
"""Evaluate the 540 non-prime characters of DBBI + FAED (661 - 121 = 540 = 36 * 15).
Analyzes frequency, IC, Bifid/Polybius decryptions across divisors (periods 15, 30, 36, 540),
transpositions, and tests derived strings against AES blobs and target addresses.
Completely offline, deterministic, and self-auditing.
"""
import sys, os, hashlib, json, time, math
from collections import Counter
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED, primes_upto, BLOBS
from systematic_solver import run_sweep, forms_of

COMBINED = DBBI + FAED
assert len(COMBINED) == 661

P_661 = set(primes_upto(661))
assert len(P_661) == 121

# Extract non-prime characters for both 1-based and 0-based indexing
np_1based = ''.join(c for i, c in enumerate(COMBINED) if (i + 1) not in P_661)
np_0based = ''.join(c for i, c in enumerate(COMBINED) if i not in P_661)
assert len(np_1based) == 540
assert len(np_0based) == 541

def calc_ic(s):
    n = len(s)
    if n <= 1: return 0.0
    cnt = Counter(s)
    return sum(f * (f - 1) for f in cnt.values()) / (n * (n - 1))

def calc_entropy(s):
    n = len(s)
    cnt = Counter(s)
    return -sum((f / n) * math.log2(f / n) for f in cnt.values())

print(f"NP 1-based (len={len(np_1based)}): IC={calc_ic(np_1based):.5f}, Entropy={calc_entropy(np_1based):.3f}")
print("NP 1-based top freq:", Counter(np_1based).most_common())
print(f"NP 0-based (len={len(np_0based)}): IC={calc_ic(np_0based):.5f}, Entropy={calc_entropy(np_0based):.3f}")
print("NP 0-based top freq:", Counter(np_0based).most_common())

# Bifid decryption helper for 3x3 Polybius square (9 symbols: a..i)
def bifid_decrypt(ct, square, period):
    # square: 9-char string representing 3x3 grid
    coords = {c: (i // 3, i % 3) for i, c in enumerate(square)}
    inv_coords = {(i // 3, i % 3): c for i, c in enumerate(square)}
    pt = []
    for block_start in range(0, len(ct), period):
        block = ct[block_start:block_start + period]
        k = len(block)
        # In Bifid encryption with period k:
        # row coords r[0..k-1] and col coords c[0..k-1] are written:
        # stream = r[0] r[1] ... r[k-1] c[0] c[1] ... c[k-1]
        # and paired two-by-two to form ciphertext.
        # So decrypting:
        # Read pairs from ciphertext block to reconstruct stream of length 2k:
        stream = []
        for ch in block:
            r, c = coords.get(ch, (0, 0))
            stream.append(r)
            stream.append(c)
        r_coords = stream[:k]
        c_coords = stream[k:]
        for r, c in zip(r_coords, c_coords):
            pt.append(inv_coords.get((r, c), '?'))
    return ''.join(pt)

# Squares to test
squares = {
    'canon': 'abcdefghi',
    'dbbi': ''.join(dict.fromkeys(DBBI)),
    'faed': ''.join(dict.fromkeys(FAED)),
    'salphaseion': 'salphione' # 9 unique letters of SalPhaseIon
}

candidates = []

for name, s in [('np_1based', np_1based), ('np_0based', np_0based)]:
    candidates.append(s)
    candidates.append(s[::-1])
    
    # Columnar transpositions for divisors of 540 (e.g. width 15, 18, 30, 36)
    for w in (15, 18, 30, 36):
        # Column-major read
        col_major = ''.join(s[col::w] for col in range(w))
        candidates.append(col_major)
        candidates.append(col_major[::-1])
    
    # Bifid decryptions
    for sq_name, sq in squares.items():
        if len(sq) != 9:
            # Pad or trim to 9 distinct chars
            sq = ''.join(dict.fromkeys(sq + 'abcdefghi'))[:9]
        for p in (15, 18, 30, 36, 540):
            dec = bifid_decrypt(s, sq, p)
            candidates.append(dec)

candidates = sorted(list(set(candidates)))
print(f"Generated {len(candidates)} candidate forms from 540 non-prime analysis.")

# Sweep against AES blobs and addresses
hits = run_sweep(candidates, label="540_NonPrimes_Sweep")

print(f"\nFinal Summary: {len(candidates)} candidates tested.")
print(f"Structured AES Hits: {len(hits)}")
