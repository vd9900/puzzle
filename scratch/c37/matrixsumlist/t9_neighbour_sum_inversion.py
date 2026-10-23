"""T9: is a page digit string the NEIGHBOURHOOD-SUM MATRIX of a hidden small-integer image?
'matrix sum list' read literally on the page objects themselves: faed (570 = 19x30 = 15x38 ...), its halves (285 = 15x19),
dbbi (91 = 7x13) and residual60 could be the serialized list of window sums ("Minesweeper numbers") of a hidden
binary/digit matrix -- the same kind of 2-D bit matrix the puzzle opened with.  A 9-symbol alphabet a..i fits
Moore-8 counts (0..8, a=0) or 3x3 box sums (a=1..9 or a=0..8).
Deterministic decode: build the linear window-sum operator A for the layout (h x w, serialization order, boundary
= zero-padded or toroidal) and solve A x = v exactly (least squares + residual).  If the string really is such a
sum list, x is integral and (for an image) binary.  No guessing: one linear solve per layout.
Detector: fraction of x entries within 1e-6 of an integer, fraction within {0,1}; residual ||Ax-v||.
Control: same pipeline on 40 multiset shuffles of each source (max over all layouts).
Planted self-test: random binary 19x30 image -> 3x3 box sums -> letters -> recovered exactly."""
import sys, random, json, itertools
import numpy as np
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/matrixsumlist')
from msl_lib import *

KINDS = {
    'box3': [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)],
    'moore8': [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc],
    'vn5': [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)],
    'box2': [(0, 0), (0, 1), (1, 0), (1, 1)],
    'box2b': [(0, 0), (0, -1), (-1, 0), (-1, -1)],
}


def order(h, w, kind):
    if kind == 'row':
        return [(r, c) for r in range(h) for c in range(w)]
    if kind == 'snake':
        return [(r, c if r % 2 == 0 else w - 1 - c) for r in range(h) for c in range(w)]
    if kind in ('spiral_ccw', 'spiral_cw'):
        top, left, bottom, right = 0, 0, h - 1, w - 1
        out = []
        while top <= bottom and left <= right:
            if kind == 'spiral_ccw':   # down the left column first (the puzzle image's spiral)
                out += [(r, left) for r in range(top, bottom + 1)]; left += 1
                out += [(bottom, c) for c in range(left, right + 1)]; bottom -= 1
                if left <= right:
                    out += [(r, right) for r in range(bottom, top - 1, -1)]; right -= 1
                if top <= bottom:
                    out += [(top, c) for c in range(right, left - 1, -1)]; top += 1
            else:
                out += [(top, c) for c in range(left, right + 1)]; top += 1
                out += [(r, right) for r in range(top, bottom + 1)]; right -= 1
                if top <= bottom:
                    out += [(bottom, c) for c in range(right, left - 1, -1)]; bottom -= 1
                if left <= right:
                    out += [(r, left) for r in range(bottom, top - 1, -1)]; left += 1
        assert len(out) == h * w and len(set(out)) == h * w
        return out
    raise ValueError(kind)


def operator(h, w, kind, torus):
    n = h * w
    A = np.zeros((n, n))
    for r in range(h):
        for c in range(w):
            i = r * w + c
            for dr, dc in KINDS[kind]:
                rr, cc = r + dr, c + dc
                if torus:
                    rr %= h; cc %= w
                elif not (0 <= rr < h and 0 <= cc < w):
                    continue
                A[i, rr * w + cc] += 1
    return A


_cache = {}


def pinv(h, w, kind, torus):
    key = (h, w, kind, torus)
    if key not in _cache:
        A = operator(h, w, kind, torus)
        _cache[key] = (A, np.linalg.pinv(A), np.linalg.matrix_rank(A))
    return _cache[key]


def solve(vals, h, w, okind, kind, torus):
    """vals: serialized list; returns stats of x on the h x w grid (row-major)"""
    A, P, rank = pinv(h, w, kind, torus)
    grid = np.zeros(h * w)
    for v, (r, c) in zip(vals, order(h, w, okind)):
        grid[r * w + c] = v
    x = P @ grid
    res = float(np.abs(A @ x - grid).max())
    near_int = np.abs(x - np.round(x)) < 1e-6
    intf = float(near_int.mean())
    binf = float((near_int & ((np.round(x) == 0) | (np.round(x) == 1))).mean())
    digf = float((near_int & (np.round(x) >= 0) & (np.round(x) <= 9)).mean())
    return dict(res=res, intf=intf, binf=binf, digf=digf, rank=int(rank), n=h * w, x=x)


def layouts(n):
    return [(h, n // h) for h in range(3, n // 3 + 1) if n % h == 0]


def scan(src, maps=(False, True), keep_best=5):
    out = []
    for a0 in maps:
        v = dig(src, a0)
        for h, w in layouts(len(src)):
            for ok in ('row', 'snake', 'spiral_ccw', 'spiral_cw'):
                for kind in KINDS:
                    if max(v) > len(KINDS[kind]):
                        continue   # value range impossible for this window
                    for torus in (False, True):
                        s = solve(v, h, w, ok, kind, torus)
                        exact = s['res'] < 1e-6
                        out.append(((a0, h, w, ok, kind, torus), exact, s['intf'] if exact else 0.0,
                                    s['binf'] if exact else 0.0, s['digf'] if exact else 0.0, s['rank'], s['n']))
    return out


def summary(rows):
    if not rows:
        return dict(n=0)
    ex = [r for r in rows if r[1]]
    return dict(n=len(rows), exact_consistent=len(ex),
                best_intf=max((r[2] for r in rows), default=0), best_binf=max((r[3] for r in rows), default=0),
                best_digf=max((r[4] for r in rows), default=0),
                best=max(rows, key=lambda r: (r[3], r[2]))[0] if ex else None)


if __name__ == '__main__':
    # planted self-test: binary 19x30 image -> box3 sums (values 0..9 -> a=0 map needs <=8; use a=1..9 offset: shift by 1?)
    rnd = random.Random(5)
    h, w = 19, 30
    img = np.array([rnd.random() < 0.5 for _ in range(h * w)], dtype=float)
    A = operator(h, w, 'moore8', False)
    sums = (A @ img).astype(int)
    letters = ''.join(chr(97 + s) for s in sums)          # a=0 map, Moore counts 0..8
    s = solve(dig(letters, True), h, w, 'row', 'moore8', False)
    assert s['res'] < 1e-6, s['res']
    print('planted moore8 19x30 rank', s['rank'], 'of', h * w, 'binf=%.3f intf=%.3f' % (s['binf'], s['intf']))
    # planted 2: box3 on 19x30 spiral, a=1 map requires sums>=1: use dense image.
    # NOTE (fix after interrupted run): zero-padded box3 = T_h (x) T_w with T_n tridiagonal-ones, singular iff n = 2 mod 3;
    # 15x38 is singular (38 = 2 mod 3), so pinv returns the min-norm solution, not the planted image. Use 19x30 (nonsingular).
    h, w = 19, 30
    while True:
        img = np.array([rnd.random() < 0.6 for _ in range(h * w)], dtype=float)
        A = operator(h, w, 'box3', False); sums = (A @ img).astype(int)
        if sums.min() >= 1: break
    seq = [0] * (h * w)
    for (r, c), i in zip(order(h, w, 'spiral_ccw'), range(h * w)):
        seq[i] = sums[r * w + c]
    letters = ''.join(chr(96 + s) for s in seq)
    rows = scan(letters, maps=(False,))
    sm = summary(rows)
    print('planted box3 19x30 spiral scan:', sm)
    assert sm['best_binf'] == 1.0 and sm['best'][4] == 'box3'
    print('PLANTED SELF-TESTS OK')

    RES61 = RES60 + 'e'
    sources = {'faed': FAED, 'faed_h1': FAED[:285], 'faed_h2': FAED[285:], 'dbbi': DBBI, 'res60': RES60,
               'faed_tail_cut538': FAED[:538], 'dbbi_res56': ''.join(c for c in DBBI if c not in 'b')}
    report = {}
    for name, src in sources.items():
        rows = scan(src)
        sm = summary(rows)
        # control: shuffles
        NS = 40 if len(src) < 400 else 12
        cs = [summary(scan(shuffled(src, 77 + t))) for t in range(NS)]
        ctrl = dict(exact_consistent_med=sorted(c.get('exact_consistent', 0) for c in cs)[NS // 2],
                    best_intf_max=max(c.get('best_intf', 0) for c in cs), best_binf_max=max(c.get('best_binf', 0) for c in cs),
                    best_digf_max=max(c.get('best_digf', 0) for c in cs))
        report[name] = dict(real=sm, control=ctrl, NS=NS)
        print(name, len(src), 'REAL', sm, '| CTRL', ctrl, flush=True)
    json.dump(report, open('/home/vin/bitcoin_puzzle/scratch/c37/matrixsumlist/logs/t9.json', 'w'), indent=1, default=str)
