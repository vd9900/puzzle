"""T6: page order 'dbbi | matrixsumlist | faed' read as an equation: dbbi (or its 60/61-symbol residual after the
prime colour markers) IS the matrix sum list of faed.  (570 = 91*6 + 24: width-91 column sums use every faed digit.)
For every width w in 2..285, row-sum and column-sum lists of faed (a=1..9 and a=0..8), reduced to one digit by
digital root (1..9), mod 9 (0..8), mod 10; compared with dbbi / res60 / res61 (forward and reversed) at every
relative offset (overlap >= 20).  Statistic: max fraction of agreeing positions (chance ~1/9); and longest exact run.
Control: identical scan on 100 multiset shuffles of faed.  Planted test: replace dbbi by the width-91 column digital
roots of faed and confirm full agreement is found."""
import sys
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/matrixsumlist')
from msl_lib import *
import numpy as np

RES61 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeeae'

def reduce(L, mode):
    if mode == 'droot':
        return [((x - 1) % 9) + 1 if x > 0 else 0 for x in L]
    if mode == 'mod9':
        return [x % 9 for x in L]
    return [x % 10 for x in L]

def target_digits(t, a0):
    return dig(t, a0)

def best_align(a, b, minov=20):
    """max agreement fraction over all offsets (numpy correlate per symbol); longest run at the best offset"""
    a = np.asarray(a); b = np.asarray(b)
    la, lb = len(a), len(b)
    tot = np.zeros(la + lb - 1)
    for s in set(a.tolist()) & set(b.tolist()):
        tot += np.correlate((a == s).astype(float), (b == s).astype(float), 'full')
    # full index k corresponds to offset off = k - (lb - 1): b[j] aligned with a[off + j]
    offs = np.arange(la + lb - 1) - (lb - 1)
    ov = np.minimum(la, offs + lb) - np.maximum(0, offs)
    ok = ov >= minov
    if not ok.any():
        return 0, 0, None
    frac = np.where(ok, tot / np.maximum(ov, 1), 0)
    k = int(frac.argmax()); off = int(offs[k])
    run = best = 0
    for j in range(lb):
        i = off + j
        if 0 <= i < la and a[i] == b[j]:
            run += 1; best = max(best, run)
        else:
            run = 0
    return float(frac[k]), best, (off, int(ov[k]))

def scan(fs, targets):
    out = {}
    for a0 in (False, True):
        v = dig(fs, a0)
        for w in range(2, 286):
            for axis in ('rows', 'cols'):
                L = grid_sums(v, w, axis)
                if len(L) < 20:
                    continue
                for mode in ('droot', 'mod9', 'mod10'):
                    R = reduce(L, mode)
                    for tn, tv in targets.items():
                        for ta0 in (False, True):
                            if mode == 'droot' and ta0: continue      # droot gives 1..9 -> a=1 map only
                            if mode == 'mod9' and not ta0: continue   # mod9 gives 0..8 -> a=0 map only
                            T = dig(tv, ta0)
                            for rev in (False, True):
                                f, run, arg = best_align(R[::-1] if rev else R, T)
                                key = tn
                                cur = out.get(key, (0, 0, None))
                                if f > cur[0] or (f == cur[0] and run > cur[1]):
                                    out[key] = (f, run, (a0, w, axis, mode, ta0, rev, arg))
                                if run > out.get(key + '_run', (0, 0, None))[1]:
                                    out[key + '_run'] = (f, run, (a0, w, axis, mode, ta0, rev, arg))
    return out

if __name__ == '__main__':
    import random
    targets = {'dbbi': DBBI, 'res60': RES60, 'res61': RES61}
    # planted: target = width-91 column digital roots of faed
    L = reduce(grid_sums(dig(FAED), 91, 'cols'), 'droot')
    planted = ''.join(chr(96 + x) for x in L)
    r = scan(FAED, {'planted': planted})
    assert r['planted'][0] == 1.0, r['planted']
    print('planted self-test OK', r['planted'])
    real = scan(FAED, targets)
    for k, v in sorted(real.items()): print('REAL', k, round(v[0], 3), v[1], v[2])
    import time; t0 = time.time()
    ctrl = {k: [] for k in real}
    NS = 12
    for t in range(NS):
        c = scan(shuffled(FAED, 4242 + t), targets)
        for k in real: ctrl[k].append(c[k][0] if not k.endswith('_run') else c[k][1])
    for k in sorted(real):
        c = sorted(ctrl[k]); val = real[k][0] if not k.endswith('_run') else real[k][1]
        print(f'{k:10s} real={val:.3f} control median={c[NS//2]:.3f} max={c[-1]:.3f}  (n={NS}, {time.time()-t0:.0f}s)')
