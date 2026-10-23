"""Show the deepest partial top-down solutions (determined top bytes) for a family, to eyeball for language."""
import sys
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from h5_topdown_more import CHARSETS, STRS
from h4_topdown import TD
from engine import to_bytes

def deep_partials(digs, cs, Kmax, keep=8, max_nodes=5_000_000):
    n = len(digs); T = TD(n, cs, max_nodes); dv = [int(c) for c in digs]; best = []
    def go(t, A, kd, K, zs):
        T.nodes += 1
        if T.nodes > max_nodes: return
        if kd >= 20:
            r = n - t; nb = ((A + 10 ** r - 1).bit_length() + 7) // 8
            best.append((kd, A.to_bytes(nb, 'big')[:kd], list(zs)))
        if t == n: return
        r = n - t - 1
        nA = A + dv[t] * T.p10[r]; nk = T.check(nA, r, kd)
        if nk >= 0: go(t + 1, nA, nk, K, zs)
        if t > 0 and K < Kmax:
            nk = T.check(A, r, kd)
            if nk >= 0: go(t + 1, A, nk, K + 1, zs + [t])
    go(0, 0, 0, 0, [])
    best.sort(key=lambda x: -x[0])
    seen = set(); out = []
    for kd, b, zs in best:
        if b in seen: continue
        seen.add(b); out.append((kd, b, zs))
        if len(out) >= keep: break
    return out, T.nodes

for name in ('DBBI', 'DBBI_rev'):
    digs = ''.join(str(ord(c) - 96) for c in STRS[name])
    out, nodes = deep_partials(digs, CHARSETS['printnl'], 12)
    print(name, 'nodes', nodes)
    for kd, b, zs in out: print('  ', kd, b, zs)
