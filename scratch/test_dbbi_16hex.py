#!/usr/bin/env python3
"""Test DBBI {b, g} 64-token / 16-symbol straddling checkerboard parse
as a 64-character hexadecimal string / 32-byte private key or AES password.
Evaluates:
  - Alphabetical token order
  - First appearance order
  - Frequency order
  - Checkerboard row-major order
  - be=0 anchored orders
Checks BOTH target Bitcoin addresses:
  - 1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe (Half)
  - 17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa (Better Half)
AND checks all 3 AES blobs (small, inner, cosmic).
Completely offline, deterministic, and self-auditing.
"""
import sys, os, hashlib, json, time, itertools
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, BLOBS, evp, sha256hex
from tools.gsmg import candidate_addresses, TARGET_ADDRESS, CURVE_ORDER as N
from systematic_solver import check_password, verify_body, run_sweep

ADDR_HALF = TARGET_ADDRESS # 1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe
ADDR_BETTER = '17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa'
TARGETS = {ADDR_HALF, ADDR_BETTER}

# Parse DBBI with prefixes b and g
toks = []
i = 0
while i < len(DBBI):
    if DBBI[i] in 'bg' and i + 1 < len(DBBI):
        toks.append(DBBI[i:i+2]); i += 2
    else:
        toks.append(DBBI[i]); i += 1

assert len(toks) == 64
distinct_toks = sorted(list(set(toks)))
assert len(distinct_toks) == 16

print(f"Parsed DBBI into 64 tokens with 16 distinct symbols.")

# Token orderings
orderings = {}

# 1. Alphabetical
orderings['alphabetical'] = distinct_toks

# 2. First occurrence
first_occ = []
for t in toks:
    if t not in first_occ: first_occ.append(t)
orderings['first_occ'] = first_occ

# 3. Frequency (most common first)
from collections import Counter
counts = Counter(toks)
orderings['freq_desc'] = [t for t, _ in counts.most_common()]
orderings['freq_asc'] = [t for t, _ in reversed(counts.most_common())]

# 4. Checkerboard row-major
row0 = [t for t in distinct_toks if len(t) == 1] # a, c, d, e, f, h, i
row1 = [t for t in distinct_toks if t.startswith('b')] # ba, bb, be, bf, bh
row2 = [t for t in distinct_toks if t.startswith('g')] # gb, ge, gg, gi
orderings['cb_rows'] = row0 + row1 + row2
orderings['cb_rows_b_g_single'] = row1 + row2 + row0

# 5. be=0 anchored: put 'be' at index 0, rest alphabetical / first_occ
orderings['be0_alpha'] = ['be'] + [t for t in distinct_toks if t != 'be']
orderings['be0_firstocc'] = ['be'] + [t for t in first_occ if t != 'be']

hex_chars_asc = '0123456789abcdef'
hex_chars_desc = 'fedcba9876543210'
hex_chars_rot = ['0123456789abcdef'[k:] + '0123456789abcdef'[:k] for k in range(16)]

candidate_hexes = set()

for ord_name, tok_list in orderings.items():
    # Forward and reversed token lists
    for rev in (False, True):
        tl = list(reversed(tok_list)) if rev else tok_list
        tag = f"{ord_name}{'_rev' if rev else ''}"
        
        # Test against all 16 rotations of hex chars (forward and backwards)
        for hex_pattern in (hex_chars_asc, hex_chars_desc):
            mapping = {t: h for t, h in zip(tl, hex_pattern)}
            hex_str = ''.join(mapping[t] for t in toks)
            candidate_hexes.add(hex_str)
            candidate_hexes.add(hex_str.upper())
            # Also reversed hex string
            candidate_hexes.add(hex_str[::-1])

print(f"Generated {len(candidate_hexes)} candidate 64-hex strings.")

# Direct private key check
direct_hits = 0
for hstr in candidate_hexes:
    try:
        raw_key = bytes.fromhex(hstr)
        k = int.from_bytes(raw_key, 'big')
        if 1 <= k < N:
            ads = candidate_addresses(raw_key)
            for ad in ads.values():
                if ad in TARGETS:
                    print(f"\n🔥🔥🔥 DIRECT PRIVATE KEY MATCH: {ad} (hex: {hstr}) 🔥🔥🔥\n")
                    direct_hits += 1
    except: pass

# Test against AES blobs
hits = run_sweep(candidate_hexes, label="DBBI_16Hex_Sweep")

print(f"\nFinal Summary: {len(candidate_hexes)} 64-hex candidates tested.")
print(f"Direct Address Matches: {direct_hits}")
print(f"Structured AES Hits: {len(hits)}")
