"""T5: 'matrix sum list' read as a programmer would: a sparse matrix given as a LIST of (row, col, value) triples
(COO format) whose duplicate entries are SUMMED when the dense matrix is formed (scipy/Matlab sparse() semantics).
faed 570 = 190 x 3 exactly; residual60 = 20 x 3; a..i = 1..9 are natural 1-based 9x9 indices.
Dense 9x9 cell sums average ~12.6 for faed, i.e. inside the a1z26 letter range -> 81-letter message.
Also the pair version: (row, col) pairs with unit weight (count matrix) and (index, value) pairs -> 9-entry sum list.
Detector: English quadgram score (textmodel) of the dense matrix serialized row/col-major, values as a1z26,
mod 26, mod 27 (0=space); plus printable ratio of chr(values).  Control: 300 multiset shuffles of the source.
Planted self-test: random COO triples whose dense sums spell a known 81-letter text."""
import sys, random, itertools
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/matrixsumlist')
from msl_lib import *
A = 'abcdefghijklmnopqrstuvwxyz'

def dense_from_triples(d, roles, n=9):
    """d: list of ints 1..9; roles: permutation of ('r','c','v')"""
    M = [[0] * n for _ in range(n)]
    for i in range(0, len(d) - 2, 3):
        t = dict(zip(roles, d[i:i + 3]))
        M[t['r'] - 1][t['c'] - 1] += t['v']
    return M

def dense_from_pairs(d, n=9):
    M = [[0] * n for _ in range(n)]
    for i in range(0, len(d) - 1, 2):
        M[d[i] - 1][d[i + 1] - 1] += 1
    return M

def serials(M):
    n = len(M)
    yield 'row', [M[r][c] for r in range(n) for c in range(n)]
    yield 'col', [M[r][c] for c in range(n) for r in range(n)]
    yield 'row_rev', [M[r][c] for r in range(n) for c in range(n)][::-1]
    yield 'col_rev', [M[r][c] for c in range(n) for r in range(n)][::-1]

def letter_maps(vals):
    yield 'a1z26', ''.join(A[v - 1] if 1 <= v <= 26 else '' for v in vals), sum(1 <= v <= 26 for v in vals) / len(vals)
    yield 'mod26a1', ''.join(A[(v - 1) % 26] for v in vals if v > 0), 1.0
    yield 'mod26a0', ''.join(A[v % 26] for v in vals), 1.0
    yield 'mod27sp', ''.join(' ' if v % 27 == 0 else A[v % 27 - 1] for v in vals).replace(' ', ''), 1.0

def all_decodes(s):
    out = []
    d = dig(s)
    for off in (0, 1, 2):
        dd = d[off:]
        for roles in itertools.permutations('rcv'):
            M = dense_from_triples(dd, roles)
            for sn, vals in serials(M):
                for mn, txt, cov in letter_maps(vals):
                    if cov >= 0.8 and len(txt) >= 40:
                        out.append(((off, ''.join(roles), sn, mn), txt))
    for off in (0, 1):
        M = dense_from_pairs(d[off:])
        for sn, vals in serials(M):
            for mn, txt, cov in letter_maps(vals):
                if cov >= 0.8 and len(txt) >= 40:
                    out.append(((off, 'pairs', sn, mn), txt))
    return out

def best(out):
    if not out:
        return (-9, None, '')
    sc = [(textmodel.score(t), p, t) for p, t in out]
    return max(sc)

if __name__ == '__main__':
    # planted: build triples (r,c,v) whose dense sums give letters of an 81-letter text (a1z26)
    rnd = random.Random(3)
    text = ('thequickbrownfoxjumpsoverthelazydogwhilethearchitectwatchesfromhischairandsmiles')[:81]
    trip = []
    for idx, ch in enumerate(text):
        r, c = divmod(idx, 9); target = A.index(ch) + 1
        while target > 0:
            v = min(9, target) if target <= 9 else rnd.randint(1, 9)
            if target - v != 0 and target - v < 1: v = target
            trip.append((r + 1, c + 1, v)); target -= v
    rnd.shuffle(trip)
    planted = ''.join(chr(96 + x) for t in trip for x in t)
    P = [x for x in all_decodes(planted) if x[0] == (0, 'rcv', 'row', 'a1z26')]
    assert P and P[0][1] == text, P[:1]
    print('planted self-test OK; planted score %.2f' % textmodel.score(text))
    for name, s in (('faed', FAED), ('res60', RES60), ('dbbi', DBBI), ('faed_rev', FAED[::-1])):
        out = all_decodes(s)
        b = best(out)
        ctrl = sorted(best(all_decodes(shuffled(s, 900 + t)))[0] for t in range(300))
        print(f'{name:8s} decodes={len(out):4d} REAL best quadgram {b[0]:.3f} {b[1]} {b[2][:60]!r} | CTRL median {ctrl[150]:.3f} p99 {ctrl[297]:.3f} max {ctrl[-1]:.3f}')
    # also print the faed dense 9x9 (r,c,v) matrix for the record
    M = dense_from_triples(dig(FAED), ('r', 'c', 'v'))
    for row in M: print(' '.join(f'{x:3d}' for x in row))
