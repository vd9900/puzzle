#!/usr/bin/env python3
"""Brainwallet oracle: for each candidate string, derive private keys as sha256(s), sha256(sha256(s)),
sha256(sha256hex(s)) and (if s is 64 hex chars) int(s,16); compute compressed+uncompressed P2PKH addresses;
compare with the creator's on-chain breadcrumb recipients and the prize addresses.
Usage: python3 bw_oracle.py --file CANDS.txt [--label X] [--no-normalize]   or  --stdin
"""
import sys, os, re, hashlib, argparse, json
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
from tools.gsmg import CURVE_ORDER, base58check_encode
from cryptography.hazmat.primitives.asymmetric import ec
TARGETS = {
 '1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9': 'UNSPENT breadcrumb 2020-04-07 (no message)',
 '1GyT5WrLYpwFkuiVoPDJZa1Q6jtjbjuBff': 'breadcrumb "do you beleive me you need it?"',
 '18CchrjA3Uzfrzy4DFqao9ric6YfK4hjdc': 'breadcrumb "part of the cipher"',
 '13HGhjkmKUkP8sk9k63BLmhkxRjy7uK4Rp': 'breadcrumb "Good job, Neo!" (1)',
 '148XH2YBmLr4oAJXQcG84FpNYoBmqnVPHQ': 'breadcrumb "Good job, Neo!" (2)',
 '1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe': 'PRIZE ADDRESS',
 '17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa': 'secondary prize address',
 '1Jqq37KkZEt4F3Dt6qXdtyiMEFBBdawbkJ': 'control: causality',
 '1K23RS1y2fnuZRkhw5nUpFr5Jk5WN11Zeq': 'control: phase3.2 preimage',
}
HITLOG = '/home/vin/bitcoin_puzzle/scratch/wf/HITS.log'
def addrs(k):
    if not 0 < k < CURVE_ORDER: return {}
    pub = ec.derive_private_key(k, ec.SECP256K1()).public_key().public_numbers()
    x, y = pub.x, pub.y
    out = {}
    for kind, enc in (('compressed', bytes([2 + (y & 1)]) + x.to_bytes(32, 'big')), ('uncompressed', b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big'))):
        h = hashlib.new('ripemd160', hashlib.sha256(enc).digest()).digest()
        out[kind] = base58check_encode(b'\x00' + h)
    return out
def keys_for(s):
    b = s.encode('utf-8', 'surrogatepass'); h = hashlib.sha256(b).digest()
    yield 'sha256', int.from_bytes(h, 'big')
    yield 'sha256d', int.from_bytes(hashlib.sha256(h).digest(), 'big')
    yield 'sha256(hex)', int.from_bytes(hashlib.sha256(h.hex().encode()).digest(), 'big')
    if re.fullmatch(r'[0-9a-fA-F]{64}', s): yield 'hex-as-key', int(s, 16)
def forms(s, normalize=True):
    if not normalize: return {s}
    return {x for x in {s, s.strip(), s.lower(), s.upper(), re.sub(r'\s+', '', s), re.sub(r'[^A-Za-z0-9]', '', s), re.sub(r'[^a-z0-9]', '', s.lower())} if x}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--file'); ap.add_argument('--stdin', action='store_true'); ap.add_argument('--label', default=''); ap.add_argument('--no-normalize', action='store_true')
    a = ap.parse_args()
    lines = open(a.file, encoding='utf-8', errors='replace').read().split('\n') if a.file else sys.stdin.read().split('\n')
    cands = [l.rstrip('\r') for l in lines if l.strip() and not l.startswith('#')]
    seen = set(); n = 0; hits = []
    for c in cands:
        for f in forms(c, not a.no_normalize):
            if f in seen: continue
            seen.add(f)
            for kname, k in keys_for(f):
                n += 1
                for kind, ad in addrs(k).items():
                    if ad in TARGETS:
                        hit = {'candidate': c[:200], 'form': f[:120], 'derivation': kname, 'pubkey': kind, 'address': ad, 'meaning': TARGETS[ad]}
                        hits.append(hit); print('!!! BRAINWALLET MATCH', json.dumps(hit))
                        if 'control' not in TARGETS[ad]:
                            with open(HITLOG, 'a') as fh: fh.write(json.dumps({'label': a.label, 'type': 'brainwallet', **hit}) + '\n')
    print(f'[{a.label}] candidates={len(cands)} forms={len(seen)} keys={n} matches={len(hits)} (controls included)')
if __name__ == '__main__': main()
