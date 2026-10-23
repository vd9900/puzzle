"""T10: 'matrix sum list' -> page z-method.  The 14x14 image matrix's sum LISTS (rows, cols, both diagonal families,
per-byte sums along the decoding spiral, rows+cols) under a small principled set of colour weightings
(black=1, white=0; yellow weight Y, blue weight B in {0,1,2,3,5,7,9,15} -- 9 and 15 are the yellow/blue cell
counts, small primes for 'primes'; near-white weight in {0,1}), written as a decimal string (plain concatenation,
zero-padded width 2/3, one digit per sum mod 10; list forward and reversed) and decoded with the page's z-method
(decimal -> integer -> big-endian bytes).  Digits are fully determined (no free map), so each derivation is one
decode; the digit_codecs length-feasibility rule is reported (fraction of derivations whose length/leading digit
even admit a lowercase top byte).
Detector (structural, no AES): full-printable decodes with >= 6 bytes, max lowercase ratio (>= 6 bytes), longest
printable run.  Control: 40 random matrices = all 196 cells shuffled with colour labels attached (preserves bit
and colour counts), identical pipeline.  Planted test: a matrix-free list whose concat decodes to a known word."""
import sys
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/matrixsumlist')
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
from msl_lib import *
from tools.gsmg import extract_grid, SOURCES, spiral_coordinates
N = 14
COL = extract_grid(SOURCES / 'gsmg-puzzle.png')['colors']
SP = spiral_coordinates(N)
WS = (0, 1, 2, 3, 5, 7, 9, 15)
LOWER = set(range(97, 123))

def top_bytes(lo, hi):
    out = set()
    for nb in range((lo.bit_length() + 7) // 8, ((hi - 1).bit_length() + 7) // 8 + 1):
        a = max(lo, 1 << (8 * (nb - 1))); b = min(hi - 1, (1 << (8 * nb)) - 1)
        if a <= b: out |= set(range(a >> (8 * (nb - 1)), (b >> (8 * (nb - 1))) + 1))
    return out

_FEAS = {}
def feasible_lower(ds):
    key = (len(ds), ds[0])
    if key not in _FEAS:
        L, d = len(ds), ds[0]
        _FEAS[key] = bool(top_bytes(d * 10 ** (L - 1), (d + 1) * 10 ** (L - 1)) & LOWER) if d else False
    return _FEAS[key]

def lists(W):
    rows = [sum(W[r]) for r in range(N)]
    cols = [sum(W[r][c] for r in range(N)) for c in range(N)]
    diag = [sum(W[r][c] for r in range(N) for c in range(N) if r - c == k) for k in range(-(N - 1), N)]
    anti = [sum(W[r][c] for r in range(N) for c in range(N) if r + c == k) for k in range(2 * N - 1)]
    sp = [W[r][c] for r, c in SP]
    spb = [sum(sp[i:i + 8]) for i in range(0, 192, 8)]
    return {'rows': rows, 'cols': cols, 'diag': diag, 'anti': anti, 'spiral8': spb, 'rows+cols': rows + cols,
            'cols+rows': cols + rows}

def serials(L):
    yield 'cat', [int(ch) for x in L for ch in str(x)]
    for k in (2, 3):
        if all(x < 10 ** k for x in L): yield f'pad{k}', [int(ch) for x in L for ch in f'{x:0{k}d}']
    yield 'mod10', [x % 10 for x in L]

def derivations(M, C):
    seen = set()
    for Y in WS:
        for B in WS:
            for NW in (0, 1):
                W = [[(Y if C[r][c] == 'yellow' else B if C[r][c] == 'blue' else NW if C[r][c] == 'near_white' else M[r][c])
                      for c in range(N)] for r in range(N)]
                for ln, L in lists(W).items():
                    for dn, LL in (('fwd', L), ('rev', L[::-1])):
                        for sn, ds in serials(LL):
                            while ds and ds[0] == 0: ds = ds[1:]
                            t = tuple(ds)
                            if not ds or t in seen: continue
                            seen.add(t)
                            yield (Y, B, NW, ln, dn, sn), ds

def evaluate(M, C, keep=False):
    n = nfeas = nfull = 0; bestlow = 0.0; bestrun = 0; hits = []
    for p, ds in derivations(M, C):
        n += 1; nfeas += feasible_lower(ds)
        b = zdec(ds)
        if len(b) >= 6:
            if pr(b) == 1.0:
                nfull += 1
                if keep: hits.append((p, b))
            bestlow = max(bestlow, lowr(b))
        bestrun = max(bestrun, longest_printable_run(b))
    return dict(n=n, feas_lower=nfeas, full_printable=nfull, best_lower=round(bestlow, 3), best_run=bestrun), hits

if __name__ == '__main__':
    # planted: list [1, 9, 5, ...] built from the decimal of b'sumlist' split into 2-digit items
    ds = str(int.from_bytes(b'sumlist', 'big'))
    L = [int(ds[i:i + 2]) for i in range(0, len(ds), 2)]
    assert zdec([int(ch) for x in L for ch in f'{x:02d}']) == b'sumlist' or zdec([int(ch) for x in L for ch in str(x)]) == b'sumlist'
    print('planted self-test OK')
    real, hits = evaluate(MATRIX, COL, keep=True)
    print('REAL', real)
    for p, b in hits[:20]: print('   full-printable', p, b)
    cells = [(MATRIX[r][c], COL[r][c]) for r in range(N) for c in range(N)]
    import random
    ctrl = []
    for t in range(40):
        rnd = random.Random(1000 + t); cc = cells[:]; rnd.shuffle(cc)
        M2 = [[cc[r * N + c][0] for c in range(N)] for r in range(N)]
        C2 = [[cc[r * N + c][1] for c in range(N)] for r in range(N)]
        ctrl.append(evaluate(M2, C2)[0])
    for k in ('n', 'feas_lower', 'full_printable', 'best_lower', 'best_run'):
        c = sorted(x[k] for x in ctrl)
        print(f'{k:15s} real={real[k]} ctrl median={c[len(c)//2]} p95={c[int(.95*len(c))-1]} max={c[-1]}')
