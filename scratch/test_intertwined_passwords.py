#!/usr/bin/env python3
"""Test the 7 intertwined passwords hypothesis against SMALL_B64, INNER_B64, and COSMIC_B64."""
import sys, os, hashlib, itertools
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')

from systematic_solver import run_sweep, forms_of, check_password

# The 7 passwords across all phases:
P1 = "theseedisplanted"
P2 = "theflowerblossomsthroughwhatseemstobeaconcretesurface"
P3 = "causality"
P4_clean = "jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple"
P4_typo = "jacquefrescogivetitjustonesecondheisenbergsuncertaintyprinciple"
P5 = "thematrixhasyou"
P6 = "incaseyoumanagetocrackthistheprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfundstolive"
P7_text = "HASHTHETEXT"
P7_url = "89727c598b9cd1cf8873f27cb7057f050645ddb6a7a157a110239ac0152f6a32"

cands = []

for p4 in [P4_clean, P4_typo]:
    for p7 in [P7_text, P7_text.lower(), P7_url]:
        passwords = [P1, P2, P3, p4, P5, P6, p7]
        
        # 1. Direct concatenation
        cands.append(''.join(passwords))
        cands.append(' '.join(passwords))
        
        # 2. Acrostic (first letters)
        cands.append(''.join(p[0] for p in passwords))
        
        # 3. Last letters
        cands.append(''.join(p[-1] for p in passwords))
        
        # 4. XOR of 32-byte sha256 digests
        raw_digests = [hashlib.sha256(p.encode()).digest() for p in passwords]
        xor_digest = bytearray(32)
        for d in raw_digests:
            for i in range(32):
                xor_digest[i] ^= d[i]
        cands.append(bytes(xor_digest).hex())
        cands.append(bytes(xor_digest))
        
        # 5. Concatenation of SHA256 hexes
        cands.append(''.join(d.hex() for d in raw_digests))
        
        # 6. Sequential hash chain
        chain = b""
        for p in passwords:
            chain = hashlib.sha256(chain + p.encode()).digest()
        cands.append(chain.hex())
        cands.append(chain)
        
        # 7. Reverse sequential hash chain
        rchain = b""
        for p in reversed(passwords):
            rchain = hashlib.sha256(rchain + p.encode()).digest()
        cands.append(rchain.hex())
        cands.append(rchain)

# Also test short names of the 7 stages
short_names = ["seed", "flower", "causality", "fresco", "matrix", "half", "hash"]
cands.append(''.join(short_names))
cands.append(' '.join(short_names))

print(f"Testing {len(cands)} intertwined password candidates...")
run_sweep(cands, "7_INTERTWINED_PASSWORDS")
