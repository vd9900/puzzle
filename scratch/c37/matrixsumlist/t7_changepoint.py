"""T7: structural test of the 'matrix sum list = Bifid fractionation (concatenate row list + col list)' reading.
Under Bifid with period 570 the first 285 faed letters carry plaintext ROW coordinates and the last 285 carry
COLUMN coordinates, so faed's composition should change exactly at 285.  Statistic: chi-square (9 letters)
between prefix [0,k) and suffix [k,570) for every k in 60..510; report the arg-max k and its permutation p-value
(10000 shuffles, max-over-k statistic).  Also the 2-coordinate decomposition at k=285: square-row (row 0/1) and
square-col composition in each half."""
import sys, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/matrixsumlist')
from msl_lib import *
import bifid
L = 'abcdefghi'
def chi2(a, b):
    ca = [a.count(x) for x in L]; cb = [b.count(x) for x in L]
    n1, n2 = len(a), len(b); s = 0.0
    for x, y in zip(ca, cb):
        t = x + y
        if t == 0: continue
        e1 = t * n1 / (n1 + n2); e2 = t * n2 / (n1 + n2)
        s += (x - e1) ** 2 / e1 + (y - e2) ** 2 / e2
    return s
def scan(s):
    best = (0, None)
    for k in range(60, 511):
        c = chi2(s[:k], s[k:])
        if c > best[0]: best = (c, k)
    return best
if __name__ == '__main__':
    real = scan(FAED); at285 = chi2(FAED[:285], FAED[285:])
    print('REAL max chi2 %.2f at k=%d ; chi2 at k=285: %.2f' % (real[0], real[1], at285))
    rnd = random.Random(11); NS = 2000
    mx = []; c285 = []
    for t in range(NS):
        sh = shuffled(FAED, 10000 + t)
        mx.append(scan(sh)[0]); c285.append(chi2(sh[:285], sh[285:]))
    p_max = sum(m >= real[0] for m in mx) / NS; p285 = sum(m >= at285 for m in c285) / NS
    print('perm p (max-over-k) = %.4f ; perm p (fixed k=285) = %.4f  [n=%d]' % (p_max, p285, NS))
    pos = {ch: divmod(bifid.CANON.index(ch), 5) for ch in L}
    for nm, h in (('first', FAED[:285]), ('second', FAED[285:])):
        rows = [sum(1 for ch in h if pos[ch][0] == r) for r in (0, 1)]
        cols = [sum(1 for ch in h if pos[ch][1] == c) for c in range(5)]
        print(nm, 'square-row counts', rows, 'square-col counts', cols, 'letters', [h.count(x) for x in L])
