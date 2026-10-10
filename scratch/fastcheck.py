#!/usr/bin/env python3
"""Multiprocess bulk checker. Reads candidate strings (one per line) from --file, applies
the normalization set {raw, lower, nospace-lower, alnum-lower, UPPER} and both password forms
{plain, sha256hex}, and tests all three blobs under sha256 and md5 EVP KDFs using a last-block
padding pre-check followed by full decrypt + printable test. Reports only structured hits.
Usage: python3 fastcheck.py --file cands.txt [--procs 4] [--label X] [--no-normalize]
"""
import sys, os, re, hashlib, argparse, json, time
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BLOBS, printable_ratio
from Crypto.Cipher import AES

PRE = []  # (name, salt, ct_last2blocks, ct_full)
for name, (salt, ct) in BLOBS.items():
    PRE.append((name, salt, ct[-32:], ct))
HITLOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wf', 'HITS.log')

def evp(pb, salt, dg):
    m = b''; prev = b''
    while len(m) < 48:
        prev = hashlib.new(dg, prev + pb + salt).digest(); m += prev
    return m[:32], m[32:48]

def test_pw(pb):
    out = []
    for name, salt, last2, ct in PRE:
        for dg in ('sha256', 'md5'):
            k, iv = evp(pb, salt, dg)
            prev = last2[:16] if len(ct) > 16 else iv
            last = AES.new(k, AES.MODE_ECB).decrypt(last2[16:])
            pt = bytes(a ^ b for a, b in zip(last, prev))
            p = pt[-1]
            if 1 <= p <= 16 and pt.endswith(bytes([p]) * p):
                full = AES.new(k, AES.MODE_CBC, iv).decrypt(ct)[:-p]
                if printable_ratio(full) > 0.8 or b'Salted__' in full or b'U2FsdGVk' in full:
                    out.append((name, dg, full[:120]))
    return out

def forms(c, normalize=True):
    if normalize:
        s = {c, c.lower(), re.sub(r'\s+', '', c.lower()), re.sub(r'[^a-z0-9]', '', c.lower()), c.upper()}
    else:
        s = {c}
    s = {x for x in s if x}
    return s | {hashlib.sha256(x.encode()).hexdigest() for x in s}

def work(args):
    chunk, normalize = args
    hits = []; n = 0; seen = set()
    for c in chunk:
        for pw in forms(c, normalize):
            if pw in seen: continue
            seen.add(pw); n += 1
            for name, dg, head in test_pw(pw.encode('utf-8', 'surrogatepass')):
                hits.append({'candidate': c[:200], 'password_form': pw[:80], 'blob': name, 'kdf': dg, 'plaintext_head': head.decode('latin-1')})
    return n, hits

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--file', required=True); ap.add_argument('--procs', type=int, default=4); ap.add_argument('--label', default=''); ap.add_argument('--no-normalize', action='store_true')
    a = ap.parse_args()
    t0 = time.time()
    cands = [l.rstrip('\n') for l in open(a.file, encoding='utf-8', errors='replace') if l.strip() and not l.startswith('#')]
    cands = list(dict.fromkeys(cands))
    B = 2000
    chunks = [(cands[i:i + B], not a.no_normalize) for i in range(0, len(cands), B)]
    total = 0; hits = []
    with Pool(a.procs) as pool:
        for i, (n, h) in enumerate(pool.imap_unordered(work, chunks)):
            total += n; hits += h
            for x in h:
                print('!!! STRUCTURED HIT', json.dumps(x), flush=True)
                with open(HITLOG, 'a') as f: f.write(json.dumps({'label': a.label, **x}) + '\n')
            if i % 50 == 0: print(f'  progress {i+1}/{len(chunks)} chunks, {total} forms, {time.time()-t0:.0f}s', flush=True)
    print(f'[{a.label}] candidates={len(cands)} password_forms={total} structured_hits={len(hits)} time={time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()
