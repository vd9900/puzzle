# Stage 2: beam (Viterbi) checkerboard decode with hidden-digit resolution for the top derivations of each target.
# Input: main_results.json from run_main.py. Same procedure on faed, shuffled controls and planted ciphertexts.
import sys, json, argparse
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/vic_cipher'); sys.path.insert(0, '.')
import numpy as np
import vic, vicfast as V, beam
from multiprocessing import Pool

def load_targets(setname):
    import run2 as R
    R.SET = setname
    return R.make_targets()

def job(args):
    name, s, rec = args
    (z, ez, _n, ptag, dtag, postag, gi, mp, rdesc, kgd, pnum, mode) = rec[:12]
    import cands
    phrase = dict(cands.usable_phrases())[ptag]
    date = dict(cands.DATES)[dtag]
    k = vic.derive(phrase, date, pnum, kgd)
    body = s[:5 * gi] + s[5 * gi + 5:]
    a = V.to_idx(body)
    u = a[V.untranspose_index(len(s) - 5, tuple(k['Q']), tuple(k['R']), mode)]
    best = None
    for bname, tab in (('atonesir', V.board_tables(k['S'], 'atonesir')), ('p32', V.board_tables(kind='p32')),
                       ('p32S', V.board_tables(k['S'], 'p32S'))):
        for X in [None] + list(range(9)):
            sc, txt = beam.beam_decode(u, mp, tab, X=X, B=300)
            if best is None or sc > best[0]:
                best = (sc, bname, X, txt)
    return name, rec, round(best[0], 4), best[1], best[2], best[3][:200]

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--main', default='results/main_results.json'); ap.add_argument('--procs', type=int, default=8)
    ap.add_argument('--out', default='stage2_results.json'); ap.add_argument('--set', default='main')
    a = ap.parse_args()
    M = json.load(open(a.main))
    T = load_targets(a.set)
    jobs = []
    for name, d in M['targets'].items():
        seen = set()
        for st in ['z', 'ez', 'lm_at', 'lm_p32', 'lm_p32S']:
            for rec in d['top_' + st][:20]:
                key = tuple(rec[3:12])
                if key in seen: continue
                seen.add(key); jobs.append((name, T[name], rec))
    print('jobs', len(jobs), flush=True)
    res = {}
    with Pool(a.procs) as pool:
        for name, rec, sc, bname, X, txt in pool.imap_unordered(job, jobs):
            res.setdefault(name, []).append(dict(score=sc, board=bname, X=X, rec=rec, text=txt))
    out = {}
    for name, L in res.items():
        L.sort(key=lambda r: -r['score'])
        out[name] = dict(n=len(L), best=L[0]['score'], top=L[:8])
        print(name, 'n', len(L), 'best %.3f' % L[0]['score'], L[0]['board'], L[0]['X'], L[0]['rec'][3:12], L[0]['text'][:70])
    json.dump(out, open(a.out, 'w'), indent=1)
