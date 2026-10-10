#!/usr/bin/env python3
"""Multiprocess wrapper around bw_oracle.py (identical derivations, targets and HITLOG format;
uses bw_oracle.keys_for / bw_oracle.addrs). Adds form/derivation subsetting for very large files.
--mode full    : bw_oracle.forms() normalization set (7 forms)
--mode reduced : forms {raw, alnum-lower} only
--mode alnum   : form alnum-lower only
--derivs       : comma subset of sha256,sha256d,sha256(hex),hex-as-key (default all)
--max-words N  : only candidates with <= N whitespace-separated words
Usage: bw_fast.py --file F --label L [--procs 3] [--mode M] [--derivs ...] [--max-words N]
"""
import sys, os, re, json, time, argparse
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from multiprocessing import Pool
import bw_oracle as bw

def forms_for(s, mode):
    if mode == 'full': return bw.forms(s)
    if mode == 'reduced': return {x for x in {s, re.sub(r'[^a-z0-9]', '', s.lower())} if x}
    return {x for x in {re.sub(r'[^a-z0-9]', '', s.lower())} if x}

def work(args):
    chunk, mode, derivs = args
    seen = set(); n = 0; hits = []
    for c in chunk:
        for f in forms_for(c, mode):
            if f in seen: continue
            seen.add(f)
            for kname, k in bw.keys_for(f):
                if kname not in derivs: continue
                n += 1
                for kind, ad in bw.addrs(k).items():
                    if ad in bw.TARGETS:
                        hits.append({'candidate': c[:200], 'form': f[:120], 'derivation': kname, 'pubkey': kind, 'address': ad, 'meaning': bw.TARGETS[ad]})
    return n, hits

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--file', required=True); ap.add_argument('--label', default=''); ap.add_argument('--procs', type=int, default=3)
    ap.add_argument('--mode', default='full'); ap.add_argument('--derivs', default='sha256,sha256d,sha256(hex),hex-as-key'); ap.add_argument('--max-words', type=int, default=0)
    a = ap.parse_args(); t0 = time.time(); derivs = set(a.derivs.split(','))
    cands = [l.rstrip('\n').rstrip('\r') for l in open(a.file, encoding='utf-8', errors='replace') if l.strip() and not l.startswith('#')]
    if a.max_words: cands = [c for c in cands if len(c.split()) <= a.max_words]
    cands = list(dict.fromkeys(cands))
    if a.mode != 'full':  # global dedup on the (cheap) form set to avoid repeated EC work across chunks
        seen = set(); keep = []
        for c in cands:
            fs = forms_for(c, a.mode) - seen
            if fs: seen |= fs; keep.append(c)
        cands = keep
    B = 1000
    chunks = [(cands[i:i+B], a.mode, derivs) for i in range(0, len(cands), B)]
    total = 0; hits = []
    with Pool(a.procs) as pool:
        for i, (n, h) in enumerate(pool.imap_unordered(work, chunks)):
            total += n; hits += h
            for x in h:
                print('!!! BRAINWALLET MATCH', json.dumps(x), flush=True)
                if 'control' not in x['meaning']:
                    with open(bw.HITLOG, 'a') as fh: fh.write(json.dumps({'label': a.label, 'type': 'brainwallet', **x}) + '\n')
            if i % 100 == 0: print(f'  progress {i+1}/{len(chunks)} chunks, {total} keys, {time.time()-t0:.0f}s', flush=True)
    print(f'[{a.label}] candidates={len(cands)} keys={total} matches={len(hits)} (controls included) mode={a.mode} derivs={sorted(derivs)} max_words={a.max_words} time={time.time()-t0:.0f}s')
if __name__ == '__main__': main()
