"""Windowed composition dispersion: sum over non-overlapping windows of the chi-square of window counts
vs the global composition. Compared with shuffles (i.i.d. null). Also controls: the solved Phase 3.2.2
checkerboard digit stream (real encoded text, not transposed) and a columnar-transposed version of it."""
import sys, random
from collections import Counter
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import FAED, DBBI
def disp(s, w):
    g = Counter(s); n = len(s); tot = 0.0
    for i in range(0, n - w + 1, w):
        c = Counter(s[i:i+w])
        for ch in g:
            e = g[ch] * w / n
            tot += (c[ch] - e) ** 2 / e
    return tot
def test(name, s, ws=(15, 19, 25, 30, 38, 50, 57, 95), N=3000):
    r = random.Random(5); l = list(s)
    obs = {w: disp(s, w) for w in ws}
    ge = {w: 0 for w in ws}
    for _ in range(N):
        r.shuffle(l); t = ''.join(l)
        for w in ws:
            if disp(t, w) >= obs[w]: ge[w] += 1
    print(name, ' '.join(f'w{w}:p={ge[w]/N:.3f}' for w in ws))
VIC322 = '15165943121972409169171213758951813141543131412428154191312181219433121171617137149110916631213131281491109166131412199114371612126021664313711154112'
test('FAED      ', FAED)
test('FAED[:538]', FAED[:538])
test('3.2.2 stream (control, real encoded text)', VIC322, ws=(10, 15, 25, 30))
def columnar(s, k, rnd):
    order = list(range(k)); rnd.shuffle(order)
    return ''.join(s[c::k] for c in order)
test('3.2.2 transposed k=7 (control)', columnar(VIC322, 7, random.Random(2)), ws=(10, 15, 25, 30))
