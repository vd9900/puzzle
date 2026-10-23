"""dbbi (91) vs the decoded Phase 3.2 checkerboard sentence (91). Deterministic masks and element-wise
'matrix sums'; oracle = quadgram score per char vs random controls of identical size."""
import sys, random, statistics
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, primes_upto
from textmodel import score
from exp05_prime_seg import segmentations
PT = 'incaseyoumanagetocrackthistheprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfundstolive'
assert len(PT) == len(DBBI) == 91
P = set(primes_upto(200))
R = random.Random(7)
def per(t): return score(t) / max(1, len(t))
def null_mask(k, n=3000):
    xs = []
    for _ in range(n):
        idx = sorted(R.sample(range(91), k)); xs.append(per(''.join(PT[i] for i in idx)))
    return statistics.mean(xs), statistics.pstdev(xs), max(xs)
masks = {}
for t in segmentations(DBBI):
    L = len(t); pos = 0; mk = []; tokstart = []; res = []
    for li, tok in enumerate(t, 1):
        span = list(range(pos, pos + len(tok)))
        if li in P: mk += span; tokstart.append(pos)
        else: res += span
        pos += len(tok)
    masks[f'L{L}_marker_letters'] = mk
    masks[f'L{L}_marker_tokstart'] = tokstart
    masks[f'L{L}_residual'] = res
masks['phys_prime_1based'] = [i for i in range(91) if (i + 1) in P]
masks['phys_prime_0based'] = [i for i in range(91) if i in P]
for L in 'abcdefghi':
    masks[f'letter_{L}'] = [i for i in range(91) if DBBI[i] == L]
    masks[f'not_{L}'] = [i for i in range(91) if DBBI[i] != L]
masks['b_or_e'] = [i for i in range(91) if DBBI[i] in 'be']
cache = {}
rows = []
for name, idx in masks.items():
    if not idx: continue
    sel = ''.join(PT[i] for i in idx)
    k = len(idx)
    if k not in cache: cache[k] = null_mask(k)
    mu, sd, mx = cache[k]
    z = (per(sel) - mu) / sd if sd else 0
    rows.append((z, name, k, sel, mx))
rows.sort(reverse=True)
print('MASKS (z of quadgram/char vs 3000 random same-size masks; higher = more English-like)')
for z, name, k, sel, mx in rows: print(f'{z:6.2f} {name:22} k={k:2} {sel}')
# element-wise matrix sums
print('\nELEMENTWISE dbbi (+/-) sentence mod 26, markers kept / zeroed; vs 2000 dbbi-shuffle controls')
segL84 = [t for t in segmentations(DBBI)]
zero_sets = {'none': set()}
for t in segL84:
    pos = 0; z = set()
    for li, tok in enumerate(t, 1):
        if li in P: z |= set(range(pos, pos + len(tok)))
        pos += len(tok)
    zero_sets[f'L{len(t)}'] = z
def combos(d):
    out = {}
    for zname, zs in zero_sets.items():
        dd = [0 if i in zs else x for i, x in enumerate(d)]
        for pa in (0, 1):
            p = [ord(c) - 97 + pa for c in PT]
            for op in ('p+d', 'p-d', 'd-p'):
                v = [(a + b) if op == 'p+d' else (a - b) if op == 'p-d' else (b - a) for a, b in zip(p, dd)]
                out[(zname, pa, op)] = ''.join(chr((x - pa) % 26 + 97) for x in v)
    return out
for dmap in ('a1', 'a0'):
    d = [ord(c) - 96 - (dmap == 'a0') for c in DBBI]
    real = combos(d)
    ctrl = {k: [] for k in real}
    for _ in range(300):
        sh = d[:]; R.shuffle(sh)
        for k, v in combos(sh).items(): ctrl[k].append(per(v))
    best = sorted(((per(v) - statistics.mean(ctrl[k])) / statistics.pstdev(ctrl[k]), k, v) for k, v in real.items())[::-1][:5]
    for z, k, v in best: print(f'{dmap} z={z:5.2f} {k} {v}')
