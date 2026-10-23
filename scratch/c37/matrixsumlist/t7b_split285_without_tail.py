"""T7b: T7 found the fixed Bifid split k=285 mildly significant (perm p=0.019).  The main loop found an independent
unigram change point at 538 (last 32 letters lack e,g).  Is the k=285 signal just that tail?  Re-test the k=285
prefix/suffix chi-square on faed[:538] (tail removed) and on faed with the tail shuffled back in at random, 5000
multiset-shuffle permutations each.  Also the two halves' per-letter counts."""
import sys, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/matrixsumlist')
from msl_lib import *
from t7_changepoint import chi2
def perm_p(s, k, n=5000, seed=1):
    real = chi2(s[:k], s[k:]); r = random.Random(seed); l = list(s); ge = 0
    for _ in range(n):
        r.shuffle(l); t = ''.join(l)
        ge += chi2(t[:k], t[k:]) >= real
    return real, (ge + 1) / (n + 1)
for name, s in (('faed_full', FAED), ('faed[:538]', FAED[:538]), ('faed[:538] split at 269 (its own half)', FAED[:538])):
    k = 269 if 'own half' in name else 285
    c, p = perm_p(s, k)
    print(f'{name:40s} k={k} chi2={c:.2f} perm p={p:.4f}')
print('half1 counts', {x: FAED[:285].count(x) for x in 'abcdefghi'})
print('half2 counts', {x: FAED[285:].count(x) for x in 'abcdefghi'})
print('half2 w/o tail', {x: FAED[285:538].count(x) for x in 'abcdefghi'})
