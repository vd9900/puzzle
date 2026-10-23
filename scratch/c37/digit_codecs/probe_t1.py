"""Eyeball the deepest partial top-down decodes of faed under free zero reinsertion (T1) for a charset."""
import sys
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from h5_topdown_more import CHARSETS, STRS
from h4_topdown import TD
import cleanq
csn = sys.argv[1]; codec = sys.argv[2]
digs = ''.join(str(ord(c) - 96) for c in STRS['FAED']); n = len(digs); dv = [int(c) for c in digs]
cs = CHARSETS[csn]
for Z in range(39, 91):
    L = n + Z; T = TD(L, cs, 2_000_000); best = [0, None]
    def go(i, z, A, kd):
        T.nodes += 1
        if T.nodes > T.max_nodes: return
        if kd > best[0]:
            r = L - i - z; nb = ((A + 10 ** r - 1).bit_length() + 7) // 8
            best[0] = kd; best[1] = A.to_bytes(nb, 'big')[:kd]
        t = i + z
        if t == L: return
        r = L - t - 1
        if i < n:
            nA = A + dv[i] * T.p10[r]; nk = T.check(nA, r, kd)
            if nk >= 0: go(i + 1, z, nA, nk)
        if z < Z and t > 0:
            nk = T.check(A, r, kd)
            if nk >= 0: go(i, z + 1, A, nk)
    sys.setrecursionlimit(10000); go(0, 0, 0, 0)
    if best[0] >= 40:
        txt = best[1].decode(codec, 'replace')
        print(Z, best[0], T.nodes, round(cleanq.score(txt), 2), repr(txt[:90]))
