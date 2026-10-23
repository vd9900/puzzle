#!/usr/bin/env python3
"""Sweep Phase 3.2 inner blob (INNER_B64) and chained cross-stage candidates
against all three AES blobs and secp256k1 target addresses:
  - 1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe (Half)
  - 17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa (Better Half)
Completely offline, deterministic, and self-auditing.
"""
import sys, os, hashlib, json, time, itertools, re
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import BLOBS, evp, sha256hex, DBBI, FAED, BIN1, Z1, Z2, Z3
from tools.gsmg import candidate_addresses, TARGET_ADDRESS, CURVE_ORDER as N
from systematic_solver import check_password, verify_body, forms_of, run_sweep

ADDR_HALF = TARGET_ADDRESS # 1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe
ADDR_BETTER = '17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa'
TARGETS = {ADDR_HALF, ADDR_BETTER}

def check_direct_key(raw_bytes, desc):
    """Check if raw_bytes or its sha256 is directly a target private key."""
    for b in (raw_bytes, hashlib.sha256(raw_bytes).digest()):
        if len(b) == 32:
            k = int.from_bytes(b, 'big')
            if 1 <= k < N:
                try:
                    ads = candidate_addresses(b)
                    for ad in ads.values():
                        if ad in TARGETS:
                            print(f"\n🔥🔥🔥 JACKPOT PRIVATE KEY MATCH: {ad} ({desc}) 🔥🔥🔥\n")
                            return True
                except: pass
    return False

# Base components from Phase 3.2
M91 = "incaseyoumanagetocrackthistheprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfundstolive"
PREV32 = "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple"
CAUS = "causality"

# Subtracted / algebraic strings
sub1 = ''.join(chr((ord(d) - ord(m)) % 26 + ord('a')) for d, m in zip(DBBI, M91))
sub2 = ''.join(chr((ord(m) - ord(d)) % 26 + ord('a')) for d, m in zip(DBBI, M91))
add = ''.join(chr((ord(d) - 97 + ord(m) - 97) % 26 + ord('a')) for d, m in zip(DBBI, M91))

single_tokens = [
    # 1. Cipher & codepage clues
    "thematrixhasyou",
    "beaufort",
    "1141",
    "cp1141",
    "cp273",
    "beaufort1141",
    "thematrixhasyoubeaufort",
    "thematrixhasyoubeaufort1141",
    
    # 2. Checkerboard & riddle terms
    "straddle",
    "straddlingcheckerboard",
    "pokerstraddle",
    "fubcd",
    "oracle",
    "fubcdora",
    "thingky",
    "mvps",
    "fubcdking",
    "oraclequeen",
    "thingkymvps",
    "fubcdkingoraclequeen",
    "sadboard",
    "aswideasthefirstoneseen",
    "wideasthefirstoneseen",
    "sadboardwideasfirstone",
    
    # 3. Decoded checkerboard clauses
    M91,
    "incaseyoumanagetocrackthis",
    "theprivatekeysbelongtohalfandbetterhalf",
    "andtheyalsoneedfundstolive",
    "theyalsoneedfundstolive",
    "halfandbetterhalf",
    "halfandbetterhalfandtheyalsoneedfundstolive",
    "theprivatekeysbelongtohalf",
    "theprivatekeysbelongtobetterhalf",
    "half",
    "betterhalf",
    "privatekeysbelongtohalfandbetterhalf",
    
    # 4. Speech endings and Architect keywords
    "ciaobellao",
    "ciaobella",
    "goodluckneverthelessireallyhopeyouretheone",
    "bullshit",
    "denialisthemostpredictableofallhumanresponses",
    "twentythreeciphers",
    "sixteenencryptions",
    "sevenintertwinedpasswords",
    "twentythreecipherssixteenencryptionssevenintertwinedpasswords",
    "twentysixletters",
    "sourcecodes",
    "primebasics",
    "actualprivatekey",
    
    # 5. Algebraic / diff signals
    sub1,
    sub1.upper(),
    sub1[:21],
    sub1[21:27], # "youwon"
    sub1[27:],   # 64 chars
    sub1[:70],
    sub1[70:],
    "youwon",
    "YOUWON",
    "youwonbemodest",
    "YOUWONBEMODEST",
    "bemodest",
    "kmodest",
    "tsedomk",
    sub2,
    sub2.upper(),
    add,
    add.upper(),
    
    # 6. Cross-stage preimages
    PREV32,
    CAUS,
    CAUS + "thematrixhasyou",
    PREV32 + "thematrixhasyou",
    PREV32 + M91,
    PREV32 + "incaseyoumanagetocrackthis",
    PREV32 + "halfandbetterhalf",
    
    # 7. Target address literals & pairs
    ADDR_HALF,
    ADDR_BETTER,
    ADDR_HALF + ADDR_BETTER,
    ADDR_BETTER + ADDR_HALF,
    "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe:17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa",
    "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa:1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
]

# Generate compound preimages in page order
compounds = []

# Order of elements on Phase 3.2 page:
# [Intro/Beaufort] -> [Checkerboard] -> [Riddle]
seq_riddles = [
    ["thematrixhasyou", "beaufort", "1141"],
    ["thematrixhasyou", "1141"],
    ["thematrixhasyou", "straddlingcheckerboard"],
    ["thematrixhasyou", M91],
    ["thematrixhasyou", "incaseyoumanagetocrackthis"],
    ["thematrixhasyou", "beaufort", "1141", "straddlingcheckerboard"],
    ["thematrixhasyou", "beaufort", "1141", M91],
    ["thematrixhasyou", "beaufort", "1141", "straddlingcheckerboard", M91],
    ["thematrixhasyou", "beaufort", "1141", "straddle", M91],
    ["beaufort", "1141", "straddle"],
    ["straddle", "fubcd", "oracle", "thingky", "mvps"],
    ["straddlingcheckerboard", "fubcd", "oracle", "thingky", "mvps"],
    ["fubcd", "oracle", "thingky", "mvps", M91],
    ["straddle", M91],
    ["straddlingcheckerboard", M91],
    [M91, "ciaobellao"],
    ["thematrixhasyou", M91, "ciaobellao"],
    [PREV32, "thematrixhasyou", "beaufort", "1141", M91],
    [PREV32, "thematrixhasyou", M91],
    [CAUS, "thematrixhasyou", "beaufort", "1141", M91]
]

for seq in seq_riddles:
    compounds.append("".join(seq))
    compounds.append(" ".join(seq))
    compounds.append("_".join(seq))
    compounds.append("-".join(seq))

# Also pair key clauses with endings
clauses = [
    M91,
    "incaseyoumanagetocrackthis",
    "theprivatekeysbelongtohalfandbetterhalf",
    "halfandbetterhalf",
    "theyalsoneedfundstolive",
    "youwon",
    "youwonbemodest"
]
endings = [
    "ciaobellao",
    "enter",
    "matrixsumlist",
    "theseedisplanted"
]
for cl in clauses:
    for end in endings:
        compounds.append(cl + end)
        compounds.append(cl + " " + end)

all_cands = sorted(list(set(single_tokens + compounds)))
print(f"Generated {len(all_cands)} candidate preimages for Phase 3.2 inner sweep.")

# Direct key check
direct_hits = 0
for c in all_cands:
    if check_direct_key(c.encode(), c):
        direct_hits += 1

# Run sweep against all 3 blobs
hits = run_sweep(all_cands, label="Phase32_Inner_Sweep")

print(f"\nFinal Summary: {len(all_cands)} candidates tested.")
print(f"Direct Address Matches: {direct_hits}")
print(f"Structured AES Hits: {len(hits)}")
