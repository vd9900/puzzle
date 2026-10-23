"""T1b: why does CyberChef/bifid.py Decode(faed, key=dbbi) score z=+21.8 vs shuffled-faed controls? Decompose."""
import sys, random, statistics, math
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import *
import bifid, textmodel, pickle
# NOTE: scratch/quadgrams.pkl is CONTAMINATED (chat transcript contains the btcseed decode 19x); use the clean model
sys.path.insert(0, "/home/vin/bitcoin_puzzle/scratch/c37/construction_forensics"); import quad_indep
# quadgrams_clean.pkl is ALSO contaminated -> independent Carroll-only model
textmodel.LOGP, textmodel.FLOOR = quad_indep.LOGP, quad_indep.FLOOR
from collections import Counter
sq = bifid.CANON; B = bifid.BIF
rng = random.Random(1)
def ctrl(f, n=300):
    v = []
    for _ in range(n):
        l = list(FAED); rng.shuffle(l); v.append(f(bifid.bifid_decrypt(''.join(l), sq, 570)))
    return statistics.mean(v), statistics.pstdev(v)
for name, f in [('quad full', textmodel.score), ('quad body[7:]', lambda t: textmodel.score(t[7:])),
                ('quad body[7:400]', lambda t: textmodel.score(t[7:400]))]:
    m, s = ctrl(f); x = f(B); print('%-18s real=%.3f ctrl=%.3f+-%.3f z=%+.1f' % (name, x, m, s, (x-m)/s))
# offset-285 pairing in faed: are row/col digits of ct[j] and ct[285+j] dependent? chi2 of letter pairs
pos = {c: (i//5, i%5) for i, c in enumerate(sq)}
pairs = Counter((FAED[j], FAED[285+j]) for j in range(285))
def chi2pairs(s):
    p = Counter((s[j], s[285+j]) for j in range(285)); a = Counter(s[:285]); b = Counter(s[285:])
    return sum((p[(x,y)] - a[x]*b[y]/285)**2/(a[x]*b[y]/285) for x in a for y in b)
real = chi2pairs(FAED); cs = []
for _ in range(300):
    l = list(FAED); rng.shuffle(l); cs.append(chi2pairs(''.join(l)))
print('offset-285 pair chi2 real=%.1f ctrl=%.1f+-%.1f p~%.3f' % (real, statistics.mean(cs), statistics.pstdev(cs), sum(c >= real for c in cs)/300))
print('decoded unigram top:', Counter(B).most_common(12))
