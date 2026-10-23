# (1) period-P phase x letter dependence for P=2..12 (ASCII-decimal codes predict strong period 2/3), shuffle control,
#     with power check on simulated ASCII-decimal streams; (2) "uniform over K symbols merged into 9 classes" family.
import sys, itertools, math, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch'); sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/faed_provenance')
import numpy as np
from collections import Counter
from common import FAED, DBBI
import models as M
rnd = random.Random(5); LET = 'abcdefghi'
def phase_chi(s, P):
    T = np.zeros((P, 9))
    for i, ch in enumerate(s): T[i % P, ord(ch) - 97] += 1
    E = np.outer(T.sum(1), T.sum(0)) / T.sum(); return float(((T - E) ** 2 / np.maximum(E, 1e-9)).sum())
def ptest(s, P, n=400):
    o = phase_chi(s, P); l = list(s); c = 0
    for _ in range(n): rnd.shuffle(l); c += phase_chi(''.join(l), P) >= o
    return o, (1 + c) / (1 + n)
print('== period test on faed (shuffle control, 400 perms)')
for P in range(2, 13):
    o, p = ptest(FAED, P); print('P=%2d chi=%7.2f p=%.3f' % (P, o, p))
print('== power: ascii_lowervar / ascii_lower3 sims mapped with faed-best map, period 2,3 p-values')
for mode in ('lowervar', 'lower3', 'printvar'):
    pdist = M.digit_dist(lambda n: M.ascii_dec(n, mode)); ll, m = M.best_map(pdist, M.OBS)
    ps = []
    for t in range(5):
        s = M.to_letters(M.ascii_dec(700, mode), m)[:570]
        ps.append((round(ptest(s, 2, 100)[1], 3), round(ptest(s, 3, 100)[1], 3)))
    print(mode, ps)
print('== K-symbol uniform merged into 9 classes (all compositions), best ll and multinomial-sim p of G')
obs = M.OBS; SAT = M.sat_ll(obs); cs = np.sort(obs)[::-1]
def parts(K, k=9, mx=None):
    if mx is None: mx = K
    if k == 1:
        if 1 <= K <= mx: yield (K,)
        return
    for first in range(min(K - (k - 1), mx), 0, -1):
        for rest in parts(K - first, k - 1, first): yield (first,) + rest
for K in range(9, 21):
    best = max(((cs * np.log(np.array(pt) / K)).sum(), pt) for pt in parts(K))
    ll, pt = best; G = 2 * (SAT - ll)
    q = np.array(pt) / K; Gs = []
    for _ in range(500):
        c = np.random.default_rng(rnd.randrange(1 << 30)).multinomial(570, q); c2 = np.sort(c)[::-1]
        Gs.append(2 * (M.sat_ll(c) - max((c2 * np.log(np.array(pp) / K)).sum() for pp in parts(K))))
    print('K=%2d best composition %s ll=%.2f G=%.2f p=%.3f' % (K, pt, ll, G, (1 + sum(g >= G for g in Gs)) / 501))
