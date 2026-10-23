"""Is 'dbbi parses (straddling-checkerboard style) into exactly 64 tokens over exactly 16 symbols' surprising?
For every prefix set P (1-3 letters of a..i): letters in P consume the next letter as a 2-letter token.
Null: shuffles of dbbi (same multiset); statistic = does ANY prefix set give (64 tokens, 16 distinct)?"""
import sys, random, itertools
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import DBBI
L = 'abcdefghi'
SETS = [set(c) for k in (1, 2, 3) for c in itertools.combinations(L, k)]
def parse(s, P):
    toks, i = [], 0
    while i < len(s):
        if s[i] in P:
            if i + 1 >= len(s): return None
            toks.append(s[i:i+2]); i += 2
        else:
            toks.append(s[i]); i += 1
    return toks
def shapes(s):
    out = []
    for P in SETS:
        t = parse(s, P)
        if t is None: continue
        out.append((''.join(sorted(P)), len(t), len(set(t))))
    return out
real = [x for x in shapes(DBBI) if x[1] == 64 and x[2] == 16]
print('real dbbi: prefix sets giving 64 tokens / 16 symbols:', real)
print('real dbbi: any (n tokens, 16 symbols, n%2==0):', [x for x in shapes(DBBI) if x[2] == 16][:10])
r = random.Random(11); l = list(DBBI); N = 20000; hit_any = 0; hit_bg = 0
for _ in range(N):
    r.shuffle(l); s = ''.join(l)
    sh = shapes(s)
    if any(x[1] == 64 and x[2] == 16 for x in sh): hit_any += 1
    t = parse(s, {'b', 'g'})
    if t and len(t) == 64 and len(set(t)) == 16: hit_bg += 1
print(f'null (any prefix set of size 1-3 -> 64/16): {hit_any}/{N} = {hit_any/N:.4f}')
print(f'null (prefix set fixed to b,g -> 64/16):  {hit_bg}/{N} = {hit_bg/N:.4f}')

# --- marker-preserving null: keep the 23 prime-position b/be marker tokens fixed (L83 segmentation), shuffle residual letters
from exp05_prime_seg import segmentations
from common import primes_upto
P = set(primes_upto(200))
for seg in segmentations(DBBI):
    Ltok = len(seg)
    mark_idx = [i for i in range(Ltok) if (i + 1) in P]
    resid = [seg[i] for i in range(Ltok) if (i + 1) not in P]
    hits_any = hits_bg = 0; M = 20000; rr = random.Random(5)
    for _ in range(M):
        rs = resid[:]; rr.shuffle(rs); it = iter(rs)
        s = ''.join(seg[i] if (i + 1) in P else next(it) for i in range(Ltok))
        sh = shapes(s)
        if any(x[1] == 64 and x[2] == 16 for x in sh): hits_any += 1
        t = parse(s, {'b', 'g'})
        if t and len(t) == 64 and len(set(t)) == 16: hits_bg += 1
    print(f'marker-preserving null (L{Ltok}): any-set 64/16 {hits_any/M:.4f}   b,g 64/16 {hits_bg/M:.4f}')
