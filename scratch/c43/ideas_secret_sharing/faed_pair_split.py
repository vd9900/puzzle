"""H3: 'half and better half' as a 2-share split over the seven 77-digit faed chunks (H1 layout).
For every pair (a,b), partition (contig/stride7), digit order (fwd/rev): additive 2-of-2 (k = y_a + y_b) and Shamir 2-of-7
over Z_n with x = chunk index + 1 (k = (x_b*y_a - x_a*y_b)/(x_b - x_a)). Every g in BOTH chunks is 0 or 7: the key is
linear in the g-bits, so a meet-in-the-middle over x-coordinates covers all 2^(g_a+g_b) choices exactly. Planted control first."""
import sys, secrets, itertools
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch'); sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c43/ideas_secret_sharing')
from common import FAED
import ec
N = ec.N
M = {c: i + 1 for i, c in enumerate('abcdefghi')}
def lin(chunk):
    L = len(chunk); base = sum((0 if c == 'g' else M[c]) * 10 ** (L - 1 - p) for p, c in enumerate(chunk))
    return base, [7 * 10 ** (L - 1 - p) for p, c in enumerate(chunk) if c == 'g']
def gray(ws):
    Wp = [ec.mul(w) for w in ws]; pt = None; mask = 0
    yield 0, None
    for i in range(1, 1 << len(ws)):
        b = (i & -i).bit_length() - 1
        pt = ec.add(pt, ec.neg(Wp[b]) if mask >> b & 1 else Wp[b]); mask ^= 1 << b
        yield mask, pt
def mitm(base, ws, target):
    A, B = ws[:len(ws) // 2], ws[len(ws) // 2:]
    B0 = ec.mul(base); tab = {}
    for m, pt in gray(A):
        q = ec.add(B0, pt)
        if q: tab.setdefault(q[0], []).append(m)
    hits = []
    for m, pt in gray(B):
        q = ec.add(target, ec.neg(pt)) if pt else target
        if q and q[0] in tab:
            for ma in tab[q[0]]:
                k = (base + sum(w for j, w in enumerate(A) if ma >> j & 1) + sum(w for j, w in enumerate(B) if m >> j & 1)) % N
                for kk in (k, (-k) % N):
                    if ec.mul(kk) == target: hits.append(hex(kk))
    return hits
def combos(ca, cb, xa, xb):
    (ba, wa), (bb, wb) = lin(ca), lin(cb)
    yield 'add', (ba + bb) % N, [w % N for w in wa + wb]
    d = pow(xb - xa, -1, N); la, lb = xb * d % N, (-xa) * d % N
    yield 'shamir', (la * ba + lb * bb) % N, [la * w % N for w in wa] + [lb * w % N for w in wb]
# planted control: Shamir 2-of-7 share pair with digits 0/7 written as g
def enc(v): return ''.join('g' if d in '07' else 'abcdefghi'[int(d) - 1] for d in str(v))
while True:
    sec, a1 = secrets.randbelow(N), secrets.randbelow(N)
    y2, y5 = (sec + a1 * 2) % N, (sec + a1 * 5) % N
    if 10 ** 76 <= y2 < 10 ** 77 and 10 ** 76 <= y5 < 10 ** 77 and enc(y2).count('g') + enc(y5).count('g') <= 34: break
tgt = ec.mul(sec)
assert any(hex(sec) in mitm(b, w, tgt) for t, b, w in combos(enc(y2), enc(y5), 2, 5) if t == 'shamir'), 'control failed'
print('planted Shamir control OK')
body = FAED[:539]
parts = {'contig': [body[i * 77:(i + 1) * 77] for i in range(7)], 'stride7': [body[j::7] for j in range(7)]}
n = 0
for pn, chunks in parts.items():
    for on in ('fwd', 'rev'):
        cs = [c if on == 'fwd' else c[::-1] for c in chunks]
        for a, b in itertools.combinations(range(7), 2):
            for t, base, ws in combos(cs[a], cs[b], a + 1, b + 1):
                h = mitm(base, ws, ec.TGT); n += 1 << len(ws)
                if h: print('!!! HIT', pn, on, a, b, t, h)
        print(pn, on, 'done; cumulative keys covered', n, flush=True)
print('total keys covered exactly:', n, 'hits: see above (none if no !!! lines)')
