#!/usr/bin/env python3
"""Test FAED as a number, private key, or cipher password under all prime-zeroing rules,
scalar windows, and modular reductions, checking both target secp256k1 addresses:
  - 1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe (Half)
  - 17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa (Better Half)
AND checking decryption of all 3 AES blobs (small, inner, cosmic).
"""
import sys, os, hashlib, json, time, re
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import FAED, BIN1, DBBI, BLOBS, evp, printable_ratio
from tools.gsmg import candidate_addresses, TARGET_ADDRESS, CURVE_ORDER as N
from systematic_solver import check_password, verify_body

ADDR_HALF = TARGET_ADDRESS
ADDR_BETTER = '17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa'
TARGETS = {ADDR_HALF, ADDR_BETTER}

def is_prime(n):
    if n < 2: return False
    for d in range(2, int(n**0.5)+1):
        if n % d == 0: return False
    return True

P_570 = [p for p in range(1, 571) if is_prime(p)]
assert len(P_570) == 104 == len(BIN1)

# Generate digit variants of FAED
variants = {}

# 1. Raw FAED as digits a=1..i=9
variants['raw_1to9'] = ''.join(str(ord(c) - ord('a') + 1) for c in FAED)
variants['raw_0to8'] = ''.join(str(ord(c) - ord('a')) for c in FAED)

# 2. Prime zeroing (all primes -> '0')
for base in (1, 0):
    for zero_char in ('0', ''): # replace with '0' or delete
        mode = 'zero' if zero_char == '0' else 'del'
        s = []
        for i, c in enumerate(FAED):
            pos = i + 1 if base == 1 else i
            if is_prime(pos):
                if zero_char: s.append('0')
            else:
                s.append(str(ord(c) - ord('a') + 1))
        variants[f'all_primes_b{base}_{mode}'] = ''.join(s)

# 3. BIN1-guided prime zeroing
# BIN1 has 'a' and 'b'
for base in (1, 0):
    for trigger_bit in ('b', 'a'):
        for zero_char in ('0', ''):
            mode = 'zero' if zero_char == '0' else 'del'
            p_idx = [p - 1 if base == 1 else p for p in P_570 if (p - 1 if base == 1 else p) < len(FAED)]
            zero_set = set(idx for idx, b in zip(p_idx, BIN1) if b == trigger_bit)
            s = []
            for i, c in enumerate(FAED):
                if i in zero_set:
                    if zero_char: s.append('0')
                else:
                    s.append(str(ord(c) - ord('a') + 1))
            variants[f'bin1_{trigger_bit}_b{base}_{mode}'] = ''.join(s)

print(f'Total digit variants of FAED: {len(variants)}')

hits = []
checked_keys = 0
t0 = time.time()

for vname, digs in variants.items():
    if not digs: continue
    
    # Check 1: Digits string as password to AES blobs
    res = check_password(digs)
    if res:
        for r in res:
            print(f'!!! AES HIT with {vname} (digits): {r}')
            hits.append((vname, 'digits_pw', r))
            
    # Check 2: Big integer representation
    try:
        val = int(digs)
    except:
        continue
        
    # Check 2a: val % N as private key scalar
    k_mod = val % N
    if k_mod > 0:
        checked_keys += 1
        raw_key = k_mod.to_bytes(32, 'big')
        ads = candidate_addresses(raw_key)
        for ad in ads.values():
            if ad in TARGETS:
                print(f'!!! JACKPOT MATCH ({vname} % N): {ad} scalar: 0x{k_mod:064x}')
                hits.append((vname, 'mod_N', ad, hex(k_mod)))
                
    # Check 2b: Bytes representation of val
    n_bytes = (val.bit_length() + 7) // 8
    val_bytes = val.to_bytes(n_bytes, 'big')
    
    # Check val_bytes as password
    res_b = check_password(val_bytes)
    if res_b:
        for r in res_b:
            print(f'!!! AES HIT with {vname} (val_bytes): {r}')
            hits.append((vname, 'bytes_pw', r))
            
    # Check 2c: Sliding 32-byte windows across val_bytes
    if len(val_bytes) >= 32:
        for offset in range(len(val_bytes) - 31):
            window = val_bytes[offset : offset + 32]
            k_win = int.from_bytes(window, 'big')
            if 1 <= k_win < N:
                checked_keys += 1
                ads = candidate_addresses(window)
                for ad in ads.values():
                    if ad in TARGETS:
                        print(f'!!! JACKPOT MATCH ({vname} window offset {offset}): {ad} scalar: 0x{k_win:064x}')
                        hits.append((vname, f'window_{offset}', ad, hex(k_win)))

    # Check 2d: Sliding 64-hex / 78-digit decimal windows of digs
    if len(digs) >= 78:
        for offset in range(len(digs) - 77):
            chunk = digs[offset : offset + 78]
            try:
                k_chunk = int(chunk)
                if 1 <= k_chunk < N:
                    checked_keys += 1
                    raw_c = k_chunk.to_bytes(32, 'big')
                    ads = candidate_addresses(raw_c)
                    for ad in ads.values():
                        if ad in TARGETS:
                            print(f'!!! JACKPOT MATCH ({vname} dec chunk {offset}): {ad} scalar: 0x{k_chunk:064x}')
                            hits.append((vname, f'dec_chunk_{offset}', ad, hex(k_chunk)))
            except: pass

    # Check 2e: SHA256 of digs and val_bytes as key
    for obj in (digs.encode(), val_bytes):
        h_raw = hashlib.sha256(obj).digest()
        k_h = int.from_bytes(h_raw, 'big')
        if 1 <= k_h < N:
            checked_keys += 1
            ads = candidate_addresses(h_raw)
            for ad in ads.values():
                if ad in TARGETS:
                    print(f'!!! JACKPOT MATCH ({vname} sha256): {ad} scalar: 0x{k_h:064x}')
                    hits.append((vname, 'sha256_key', ad, hex(k_h)))

print(f'Completed check of FAED number variants: {checked_keys} keys checked in {time.time()-t0:.2f}s. Total hits: {len(hits)}')
