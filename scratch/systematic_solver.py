#!/usr/bin/env python3
"""Systematic solver testing concrete cryptographic and contextual leads for GSMG Meganigma.
Checks BOTH readable plaintext (>80% printable) AND exact secp256k1 target addresses:
  - 1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe (~1.25 BTC, Half)
  - 17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa (~3.75 BTC, Better Half)
Zero network calls, completely offline.
"""
import sys, os, hashlib, json, time, itertools, re
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from Crypto.Cipher import AES
from common import BLOBS, evp, sha256hex, printable_ratio, DBBI, FAED, BIN1, Z1, Z2, Z3
from tools.gsmg import candidate_addresses, TARGET_ADDRESS, CURVE_ORDER as N

ADDR_HALF = TARGET_ADDRESS # 1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe
ADDR_BETTER = '17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa'
TARGETS = {ADDR_HALF, ADDR_BETTER}

HITS_FILE = '/home/vin/bitcoin_puzzle/scratch/wf/HITS.log'

def verify_body(body):
    """Checks if body is readable plaintext or matches target secp256k1 addresses."""
    # 1. Address match for 64-byte raw keys
    if len(body) == 64:
        for chunk in (body[:32], body[32:]):
            try:
                k = int.from_bytes(chunk, 'big')
                if 1 <= k < N:
                    ads = candidate_addresses(chunk)
                    for ad in ads.values():
                        if ad in TARGETS:
                            return True, f'MATCH_RAW_KEY: {ad} (scalar: 0x{k:064x})'
            except: pass
    elif len(body) == 32:
        try:
            k = int.from_bytes(body, 'big')
            if 1 <= k < N:
                ads = candidate_addresses(body)
                for ad in ads.values():
                    if ad in TARGETS:
                        return True, f'MATCH_RAW_KEY: {ad} (scalar: 0x{k:064x})'
        except: pass
        
    # 2. Address match for 64-hex string
    try:
        txt = body.decode('ascii', errors='ignore').strip()
        if len(txt) == 64 and all(c in '0123456789abcdefABCDEF' for c in txt):
            raw = bytes.fromhex(txt)
            ads = candidate_addresses(raw)
            for ad in ads.values():
                if ad in TARGETS:
                    return True, f'MATCH_HEX_KEY: {ad} (scalar: 0x{txt})'
    except: pass

    # 3. High printable ratio (textual solution / next stage instruction)
    pr = printable_ratio(body)
    if pr > 0.82 or b'Salted__' in body or b'U2FsdGVk' in body:
        return True, f'PRINTABLE_TEXT (ratio={pr:.2f}): {body[:100]!r}'

    return False, None

def check_password(pw_str, blobs=BLOBS, digests=('sha256', 'md5')):
    """Decrypts blobs using pw_str under both EVP digests."""
    pb = pw_str.encode('utf-8', 'surrogatepass') if isinstance(pw_str, str) else pw_str
    results = []
    for bname, (salt, ct) in blobs.items():
        for dg in digests:
            k, iv = evp(pb, salt, dg)
            pt = AES.new(k, AES.MODE_CBC, iv).decrypt(ct)
            pad = pt[-1]
            if 1 <= pad <= 16 and pt.endswith(bytes([pad]) * pad):
                body = pt[:-pad]
                ok, reason = verify_body(body)
                if ok:
                    results.append((bname, dg, reason, body))
    return results

def forms_of(c):
    c_str = str(c)
    s_clean = re.sub(r'[^A-Za-z0-9]', '', c_str)
    s_lower_clean = re.sub(r'[^a-z0-9]', '', c_str.lower())
    base_set = {
        c_str,
        c_str.lower(),
        c_str.upper(),
        c_str.strip(),
        c_str.lower().strip(),
        s_clean,
        s_lower_clean
    }
    base_set = {x for x in base_set if x}
    hashes = {sha256hex(x) for x in base_set}
    raw_hashes = {hashlib.sha256(x.encode('utf-8', 'surrogatepass')).digest() for x in base_set}
    return base_set | hashes | raw_hashes

def run_sweep(cands, label=''):
    t0 = time.time()
    seen = set()
    n_forms = 0
    hits = []
    for c in cands:
        for pw in forms_of(c):
            if pw in seen: continue
            seen.add(pw)
            n_forms += 1
            res = check_password(pw)
            if res:
                for bname, dg, reason, body in res:
                    hit_info = {
                        'label': label,
                        'candidate': c,
                        'password': pw[:80],
                        'blob': bname,
                        'kdf': dg,
                        'reason': reason
                    }
                    hits.append(hit_info)
                    print(f'\n!!! HIT FOUND [{label}]: {hit_info}')
                    with open(HITS_FILE, 'a') as f:
                        f.write(json.dumps(hit_info) + '\n')
    dt = time.time() - t0
    print(f'[{label:35s}] cands={len(cands):5d} forms={n_forms:6d} hits={len(hits):2d} ({dt:.2f}s)')
    return hits

if __name__ == '__main__':
    print('Systematic solver module ready.')
