"""T1c: locate the source of the body's quadgram excess: cross-half alignment (j,285+j) vs within-half adjacency."""
import sys, random, statistics
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import *
import bifid, textmodel, pickle
# NOTE: scratch/quadgrams.pkl is CONTAMINATED (chat transcript contains the btcseed decode 19x); use the clean model
sys.path.insert(0, "/home/vin/bitcoin_puzzle/scratch/c37/construction_forensics"); import quad_indep
# quadgrams_clean.pkl is ALSO contaminated -> independent Carroll-only model
textmodel.LOGP, textmodel.FLOOR = quad_indep.LOGP, quad_indep.FLOOR
sq = bifid.CANON; F = FAED; h = 285; rng = random.Random(2)
S = lambda ct: textmodel.score(bifid.bifid_decrypt(ct, sq, 570)[7:])
real = S(F)
def rep(name, vals):
    m, s = statistics.mean(vals), statistics.pstdev(vals); print('%-55s ctrl=%.3f+-%.3f  z(real)=%+.1f' % (name, m, s, (real-m)/s))
print('real body score', round(real, 3))
rep('A: second half rotated k=1..120 (alignment broken)', [S(F[:h] + F[h:][k:] + F[h:][:k]) for k in range(1, 121)])
def joint():
    p = list(range(h)); rng.shuffle(p); return ''.join(F[i] for i in p) + ''.join(F[h+i] for i in p)
rep('B: same perm on both halves (pairs kept, adjacency broken)', [S(joint()) for _ in range(200)])
def blocks(L):  # shuffle blocks of length L in each half independently
    def bs(s):
        b = [s[i:i+L] for i in range(0, len(s), L)]; rng.shuffle(b); return ''.join(b)
    return bs(F[:h]) + bs(F[h:])
rep('C: each half shuffled in blocks of 5 (adjacency mostly kept)', [S(blocks(5)) for _ in range(200)])
# D: different square, same faed: random squares that keep a-i in the first 9 cells (order permuted)
def sqperm():
    a = list('abcdefghi'); rng.shuffle(a); rest = list('klmnopqrstuvwxyz'); return ''.join(a) + ''.join(rest)
vals = [textmodel.score(bifid.bifid_decrypt(F, sqperm(), 570)) for _ in range(200)]
print('D: faed decoded with 200 random a-i-first squares: mean=%.3f sd=%.3f max=%.3f (dbbi square full=%.3f)' % (statistics.mean(vals), statistics.pstdev(vals), max(vals), textmodel.score(bifid.BIF)))
