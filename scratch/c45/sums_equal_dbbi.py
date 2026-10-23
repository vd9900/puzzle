"""Literal 'matrix sum list': is dbbi / its residual exactly the concatenated MULTI-DIGIT row or column sums of faed laid out as a
matrix?  Digits 1-9 -> a-i; a digit 0 in a sum is treated as a wildcard (dbbi has no 'o').  Every width 2..285, row/column sums,
letter values a=1..i=9 or a=0..i=8, g possibly worth 0 (merged-zero model), forward/reversed, both read orders.
Oracle: longest exact (wildcard-0) match vs shuffled-faed controls; full equality would be decisive."""
import sys, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import FAED, DBBI
R60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
R56 = ''.join(c for c in DBBI.replace('be', '') if c != 'b')
TARGETS = {'DBBI': DBBI, 'R60': R60, 'R61': R60 + 'e', 'R56': R56, 'DBBIrev': DBBI[::-1], 'R60rev': R60[::-1]}
def sumlists(s):
    out = {}
    for a0 in (0, 1):
        for gzero in (False, True):
            v = [0 if (gzero and c == 'g') else ord(c) - 96 - a0 for c in s]
            n = len(v)
            for w in range(2, 286):
                rows = [sum(v[i:i+w]) for i in range(0, n, w)]
                cols = [sum(v[j::w]) for j in range(w)]
                for kind, L in (('rows', rows), ('cols', cols), ('rows+cols', rows + cols), ('cols+rows', cols + rows)):
                    digs = ''.join(str(x) for x in L)
                    out[(a0, gzero, w, kind)] = digs
    return out
def lcs_wild(d, t):
    # longest common substring where digit '0' in d matches anything; d digits 1-9 must equal letter a-i
    best = (0, 0, 0)
    td = [ord(c) - 96 for c in t]
    dd = [int(c) for c in d]
    for i in range(len(dd)):
        for j in range(len(td)):
            L = 0
            while i + L < len(dd) and j + L < len(td) and (dd[i+L] == 0 or dd[i+L] == td[j+L]): L += 1
            if L > best[0]: best = (L, i, j)
    return best
def run(src):
    res = []
    sl = sumlists(src)
    for key, d in sl.items():
        for tn, t in TARGETS.items():
            L, i, j = lcs_wild(d, t)
            pref = 0
            while pref < min(len(d), len(t)) and (d[pref] == '0' or int(d[pref]) == ord(t[pref]) - 96): pref += 1
            res.append((L, pref, tn, key, len(d)))
    return res
real = run(FAED)
real.sort(reverse=True)
print('REAL top by longest match:')
for r in real[:8]: print('  ', r)
print('REAL best prefix match:', max(real, key=lambda r: r[1]))
rnd = random.Random(7); cmax = []
for _ in range(3):
    c = run(''.join(rnd.sample(FAED, len(FAED))))
    cmax.append((max(r[0] for r in c), max(r[1] for r in c)))
print('CONTROL (longest, prefix) maxima over 3 shuffles:', cmax)
