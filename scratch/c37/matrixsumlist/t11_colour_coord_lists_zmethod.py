"""T11: 'matrix sum list' = list of the coloured cells' coordinates/sums, decoded with the page z-method.
Selections: all 25 non-b/w cells, 24 (yellow+blue), yellow 9, blue 15.  Cell order: decoding spiral (CCW, the
order the image is read), row-major.  Per-cell quantity (base 0 and base 1): r+c, r, c, 'rc' (row digits then col
digits), r*14+c linear index, spiral position.  Serialization: concatenation / zero-pad 2 / 3, mod 10; list
forward and reversed; decimal -> integer -> big-endian bytes.  Also prints the near-white cell's index under each
indexing scheme (the community line says it is '101 010' under the right indexing) as a deterministic check.
Detector: full printable (>=6 bytes), lowercase ratio, longest printable run.  Control: 200 random placements of
the same coloured-cell multiset on the 14x14 grid (same pipeline)."""
import sys, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/matrixsumlist')
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
from msl_lib import *
from t10_image_sumlists_zmethod import COL, SP, N, feasible_lower, serials

SPI = {rc: i for i, rc in enumerate(SP)}

def quantities(r, c, base):
    return {'r+c': [r + c + 2 * base], 'r': [r + base], 'c': [c + base], 'rc': [r + base, c + base],
            'lin': [r * N + c + base], 'spos': [SPI[(r, c)] + base]}

def derivations(colmap):
    cells = {k: [] for k in ('all25', 'yb24', 'yellow', 'blue')}
    for order, seq in (('spiral', SP), ('row', [(r, c) for r in range(N) for c in range(N)])):
        sel = {'all25': [rc for rc in seq if colmap[rc] != 'bw'],
               'yb24': [rc for rc in seq if colmap[rc] in ('yellow', 'blue')],
               'yellow': [rc for rc in seq if colmap[rc] == 'yellow'],
               'blue': [rc for rc in seq if colmap[rc] == 'blue']}
        for sn, cl in sel.items():
            for base in (0, 1):
                for q in ('r+c', 'r', 'c', 'rc', 'lin', 'spos'):
                    L = [x for (r, c) in cl for x in quantities(r, c, base)[q]]
                    for dn, LL in (('fwd', L), ('rev', L[::-1])):
                        for ser, ds in serials(LL):
                            while ds and ds[0] == 0: ds = ds[1:]
                            if ds: yield (order, sn, base, q, dn, ser), ds

def evaluate(colmap, keep=False):
    n = nfull = 0; bl = 0.0; br = 0; hits = []; seen = set()
    for p, ds in derivations(colmap):
        t = tuple(ds)
        if t in seen: continue
        seen.add(t); n += 1
        b = zdec(ds)
        if len(b) >= 6:
            if pr(b) == 1.0:
                nfull += 1
                if keep: hits.append((p, b))
            bl = max(bl, lowr(b))
        br = max(br, longest_printable_run(b))
    return dict(n=n, full_printable=nfull, best_lower=round(bl, 3), best_run=br), hits

if __name__ == '__main__':
    colmap = {(r, c): (COL[r][c] if COL[r][c] in ('yellow', 'blue', 'near_white') else 'bw') for r in range(N) for c in range(N)}
    nw = [rc for rc, v in colmap.items() if v == 'near_white'][0]
    r, c = nw
    print('near-white cell (r,c) 0-based', nw, '| 1-based', (r + 1, c + 1), '| linear 0/1-based', r * N + c, r * N + c + 1,
          '| col-major', c * N + r, '| spiral pos 0/1-based', SPI[nw], SPI[nw] + 1,
          '| binary r,c', format(r, 'b'), format(c, 'b'), '| binary 1-based', format(r + 1, 'b'), format(c + 1, 'b'))
    real, hits = evaluate(colmap, keep=True)
    print('REAL', real)
    for p, b in hits: print('   full-printable', p, b)
    keys = list(colmap); vals = list(colmap.values())
    ctrl = []
    for t in range(200):
        rnd = random.Random(300 + t); v2 = vals[:]; rnd.shuffle(v2)
        ctrl.append(evaluate(dict(zip(keys, v2)))[0])
    for k in real:
        cc = sorted(x[k] for x in ctrl)
        print(f'{k:15s} real={real[k]} ctrl median={cc[100]} p95={cc[189]} max={cc[-1]}')
