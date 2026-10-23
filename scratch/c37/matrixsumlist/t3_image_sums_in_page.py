"""T3: is any page digit string a serialization of a 'matrix sum' of the puzzle image?
A binary 14x14 matrix yields single decimal digits under neighbourhood sums: Moore-8 neighbour count (0..8 =
exactly nine symbols, matching the page's 9-letter a..i alphabet), 3x3 box sum incl. centre (0..9 = decimal digits
with o=0), 2x2 window sums (0..4), von-Neumann 5-cell sums (0..5); plus row/column prefix sums mod 10,
per-byte popcounts along the decoding spiral (24 values), coloured-cell row/col/r+c lists, row/col/diagonal sums.
Image variants: bits; bits with near-white cell = 1; inverted.  Serializations: row-major, column-major,
snake, decoding spiral (CCW) and its clockwise mirror, each forward/reversed.  Letter maps: a=1..i=9,o=0 and
a=0..i=8.  Statistic: longest common substring (LCS) between each serialized sequence and dbbi, res60, faed, BIF
(btcseed Bifid output), Z1, Z2.  Control: same statistic with the page strings multiset-shuffled (100 shuffles);
a hit needs real LCS above the control maximum.  Planted test: embed a 3x3-box-sum serialization inside a shuffled
faed and confirm detection."""
import sys, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/matrixsumlist')
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
from msl_lib import *
from tools.gsmg import extract_grid, SOURCES, spiral_coordinates
import bifid

G = extract_grid(SOURCES / 'gsmg-puzzle.png'); COL = G['colors']
N = 14
SP = spiral_coordinates(N)

def variants():
    M = [row[:] for row in MATRIX]
    yield 'bits', M
    M2 = [row[:] for row in MATRIX]; M2[7][4] = 1
    yield 'bits_nw1', M2
    yield 'inv', [[1 - x for x in row] for row in MATRIX]

def at(M, r, c):
    return M[r][c] if 0 <= r < N and 0 <= c < N else 0

def transforms(M):
    out = {}
    out['moore8'] = [[sum(at(M, r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr or dc)) for c in range(N)] for r in range(N)]
    out['box3'] = [[sum(at(M, r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)) for c in range(N)] for r in range(N)]
    out['box2'] = [[sum(at(M, r + dr, c + dc) for dr in (0, 1) for dc in (0, 1)) for c in range(N)] for r in range(N)]
    out['vn5'] = [[at(M, r, c) + at(M, r - 1, c) + at(M, r + 1, c) + at(M, r, c - 1) + at(M, r, c + 1) for c in range(N)] for r in range(N)]
    out['rowprefix10'] = [[sum(M[r][:c + 1]) % 10 for c in range(N)] for r in range(N)]
    out['colprefix10'] = [[sum(M[i][c] for i in range(r + 1)) % 10 for c in range(N)] for r in range(N)]
    # valid-only (no padding) 3x3 / moore over interior 12x12, as a 12x12 grid
    out['box3_valid'] = [[sum(M[r + dr][c + dc] for dr in (0, 1, 2) for dc in (0, 1, 2)) for c in range(N - 2)] for r in range(N - 2)]
    out['moore8_valid'] = [[sum(M[r + dr][c + dc] for dr in (0, 1, 2) for dc in (0, 1, 2)) - M[r + 1][c + 1] for c in range(N - 2)] for r in range(N - 2)]
    return out

def serials(T):
    n = len(T); m = len(T[0])
    allc = [(r, c) for r in range(n) for c in range(m)]
    orders = {'row': allc, 'col': [(r, c) for c in range(m) for r in range(n)],
              'snake': [(r, c if r % 2 == 0 else m - 1 - c) for r in range(n) for c in range(m)]}
    if n == m:
        sp = spiral_coordinates(n)
        orders['spiral'] = sp; orders['spiral_cw'] = [(c, r) for r, c in sp]
    for k, o in list(orders.items()):
        yield k, [T[r][c] for r, c in o]
        yield k + '_rev', [T[r][c] for r, c in o][::-1]

def seqs():
    for vn, M in variants():
        for tn, T in transforms(M).items():
            for sn, s in serials(T):
                yield f'{vn}/{tn}/{sn}', s
        bits = ''.join(str(M[r][c]) for r, c in SP)
        pc = [bits[i:i + 8].count('1') for i in range(0, 192, 8)]
        yield f'{vn}/popcount_spiral', pc
        yield f'{vn}/popcount_spiral_rev', pc[::-1]
        rows = [sum(r) for r in M]; cols = [sum(M[r][c] for r in range(N)) for c in range(N)]
        for nm, L in (('rows', rows), ('cols', cols), ('rows+cols', rows + cols), ('cols+rows', cols + rows)):
            yield f'{vn}/{nm}_mod10', [x % 10 for x in L]
            yield f'{vn}/{nm}_digits', [int(ch) for x in L for ch in str(x)]
            yield f'{vn}/{nm}_digits_rev', [int(ch) for x in L[::-1] for ch in str(x)]
    cells = [(r, c) for r, c in SP if COL[r][c] in ('blue', 'yellow', 'near_white')]
    for base in (0, 1):
        yield f'colour_r_b{base}', [int(ch) for r, c in cells for ch in str(r + base)]
        yield f'colour_c_b{base}', [int(ch) for r, c in cells for ch in str(c + base)]
        yield f'colour_rc_b{base}', [int(ch) for r, c in cells for ch in str(r + base) + str(c + base)]
        yield f'colour_r+c_b{base}', [int(ch) for r, c in cells for ch in str(r + c + 2 * base)]

def to_letters(s, a0):
    if a0:
        return ''.join(chr(97 + x) if 0 <= x <= 8 else '#' for x in s)
    return ''.join(('o' if x == 0 else chr(96 + x)) if 0 <= x <= 9 else '#' for x in s)

def lcs_len(a, kset_by_k, maxk=40):
    """longest k such that some length-k substring of a is in target (kset_by_k[k])"""
    best = 0
    for k in range(1, maxk + 1):
        ks = kset_by_k[k]
        if any(a[i:i + k] in ks for i in range(len(a) - k + 1)):
            best = k
        else:
            break
    return best

def ksets(t, maxk=40):
    return {k: set(t[i:i + k] for i in range(len(t) - k + 1)) for k in range(1, maxk + 1)}

def run(targets, letter_seqs):
    ks = {tn: ksets(t) for tn, t in targets.items()}
    res = {}
    for tn in targets:
        best = (0, None)
        for name, L in letter_seqs:
            v = lcs_len(L, ks[tn])
            if v > best[0]:
                best = (v, name)
        res[tn] = best
    return res

if __name__ == '__main__':
    letter_seqs = []
    for name, s in seqs():
        for a0 in (False, True):
            L = to_letters(s, a0)
            letter_seqs.append((f'{name}/a0={a0}', L))
    print('image-derived sequences:', len(letter_seqs))
    targets = {'dbbi': DBBI, 'res60': RES60, 'faed': FAED, 'bif': bifid.BIF, 'Z1': Z1, 'Z2': Z2}
    # planted self-test: put 15 symbols of a box3 serialization inside a shuffled faed
    nm, L = [x for x in letter_seqs if x[0] == 'bits/box3/spiral/a0=False'][0]
    frag = L[40:55]
    fake = shuffled(FAED, 5); fake = fake[:200] + frag + fake[215:]
    r = run({'fake': fake}, letter_seqs)
    assert r['fake'][0] >= 15, r
    print('planted self-test OK:', r)
    real = run(targets, letter_seqs)
    print('REAL:', real)
    ctrl = {tn: [] for tn in targets}
    for t in range(100):
        sh = {tn: shuffled(s, 7000 + t) for tn, s in targets.items()}
        r = run(sh, letter_seqs)
        for tn in targets: ctrl[tn].append(r[tn][0])
    for tn in targets:
        c = sorted(ctrl[tn])
        print(f'{tn:6s} real LCS={real[tn][0]:2d} ({real[tn][1]})  control median={c[50]} p95={c[95]} max={c[-1]}')
