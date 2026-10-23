"""H1: faed[:539] = seven 77-digit decimal scalars (7*77 = 539 = start of the e/g-free tail), letters a..i = 1..9,
'g' = 0 OR 7 (zero disguised as g; 'brute forcing might be required'). Exhaustive over every g-choice per chunk via
meet-in-the-middle on secp256k1 x-coordinates (perfect oracle: prize pubkey). Partitions: contiguous and stride-7
('intertwined'); digit order forward and reversed. Planted control first. Usage: python3 faed7x77_mitm.py"""
import sys, secrets
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch'); sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c43/ideas_secret_sharing')
from common import FAED
import ec
M = {c: str(i + 1) for i, c in enumerate('abcdefghi')}
def subset_points(ws):
    """yield (mask, point) over all subsets of ws (Gray code), point = sum(w)*G"""
    Wp = [ec.mul(w) for w in ws]; pt = None; mask = 0
    yield 0, None
    for i in range(1, 1 << len(ws)):
        b = (i & -i).bit_length() - 1
        if mask >> b & 1: pt = ec.add(pt, ec.neg(Wp[b]))
        else: pt = ec.add(pt, Wp[b])
        mask ^= 1 << b
        yield mask, pt
def mitm(chunk, target):
    L = len(chunk)
    base = int(''.join('0' if c == 'g' else M[c] for c in chunk))
    ws = [7 * 10 ** (L - 1 - p) for p, c in enumerate(chunk) if c == 'g']
    A, B = ws[:len(ws) // 2], ws[len(ws) // 2:]
    tab = {}
    B0 = ec.mul(base)
    for m, pt in subset_points(A):
        q = ec.add(B0, pt)
        if q: tab.setdefault(q[0], []).append(m)
    hits = []
    for m, pt in subset_points(B):
        q = ec.add(target, ec.neg(pt)) if pt else target
        if q and q[0] in tab:
            for ma in tab[q[0]]:
                k = base + sum(w for j, w in enumerate(A) if ma >> j & 1) + sum(w for j, w in enumerate(B) if m >> j & 1)
                for kk in (k % ec.N, (-k) % ec.N):
                    if ec.mul(kk) == target: hits.append(kk)
    return hits, len(ws)
# planted control: random 77-digit key, 0 and 7 -> g
k0 = secrets.randbelow(9 * 10 ** 76) + 10 ** 76
s = str(k0); ch = ''.join('g' if d in '07' else 'abcdefghi'[int(d) - 1] for d in s)
h, ng = mitm(ch, ec.mul(k0)); assert k0 in h, 'control failed'
print(f'planted control OK ({ng} g positions)')
body = FAED[:539]
parts = {'contig': [body[i * 77:(i + 1) * 77] for i in range(7)], 'stride7': [body[j::7] for j in range(7)]}
total = 0
for pn, chunks in parts.items():
    for i, c in enumerate(chunks):
        for on, cc in (('fwd', c), ('rev', c[::-1])):
            h, ng = mitm(cc, ec.TGT); total += 1 << ng
            print(f'{pn} chunk{i} {on}: g={ng} keys covered={1 << ng} prize hits={len(h)}', h if h else '')
print('total candidate keys covered exactly:', total)
# aggregate yin-yang combinations with uniform g maps (sum mod n, digitwise mod-10 sum)
for pn, chunks in parts.items():
    for gm in '07':
        for on in ('fwd', 'rev'):
            nums = [''.join(gm if ch_ == 'g' else M[ch_] for ch_ in (c if on == 'fwd' else c[::-1])) for c in chunks]
            s1 = sum(int(x) for x in nums) % ec.N
            s2 = int(''.join(str(sum(int(x[p]) for x in nums) % 10) for p in range(77)))
            for lab, k in (('sum', s1), ('digitsum10', s2)):
                q = ec.mul(k); print(pn, gm, on, lab, 'HIT' if q and q[0] == ec.TGT[0] else '-')
