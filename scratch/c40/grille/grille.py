"""Cycle 40: coloured cells of the 14x14 image as a TURNING GRILLE (Fleissner) applied to 14x14 letter windows.
Self-tests: (1) spiral reading of MATRIX == known phase-1 text; (2) grille is rotation-disjoint; (3) planted grille
message is recovered (English via speech-like scoring and z-method via direct decode + zero-disguise DFS).
Controls: random rotation-disjoint grilles with the same 15/9/1 composition, identical variant set and inputs."""
import sys, json, random, math, time, itertools
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/construction_forensics')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from common import DBBI, FAED, BIN1, MATRIX
import quad_indep as Q
from h4_topdown import td_insert, TD, CHARSETS
from engine import to_bytes
from PIL import Image

OUT = '/home/vin/bitcoin_puzzle/scratch/c40/grille/'
N = 14
LOWER = CHARSETS['lower']; PRINT = CHARSETS['printnl']

# ---------- grille from the image ----------
im = Image.open('/home/vin/bitcoin_puzzle/research/sources/gsmg-puzzle.png').convert('RGB')
from collections import Counter
COL = {}
for r in range(N):
    for c in range(N):
        cnt = Counter(im.getpixel((c * 75 + x, r * 75 + y)) for x in range(0, 75, 3) for y in range(0, 75, 3) if c * 75 + x < im.size[0])
        COL[(r, c)] = cnt.most_common(1)[0][0]
BLUE = [p for p in sorted(COL) if COL[p] == (63, 72, 204)]
YEL = [p for p in sorted(COL) if COL[p] == (255, 242, 0)]
WHT = [p for p in sorted(COL) if COL[p] == (254, 254, 254)]
assert len(BLUE) == 15 and len(YEL) == 9 and WHT == [(7, 4)], (len(BLUE), len(YEL), WHT)
# bit convention check: black/blue = 1, white/yellow = 0
for p, col in COL.items():
    exp = 1 if col in ((0, 0, 0), (63, 72, 204)) else 0
    assert MATRIX[p[0]][p[1]] == exp, p


def cw(p): return (p[1], N - 1 - p[0])


def rot(p, k):
    for _ in range(k % 4): p = cw(p)
    return p


def orbit(p): return frozenset(rot(p, k) for k in range(4))


def spiral(n):
    """decoding spiral: counter-clockwise inward from top-left, down first"""
    out = []; top, left, bot, right = 0, 0, n - 1, n - 1
    while top <= bot and left <= right:
        for r in range(top, bot + 1): out.append((r, left))
        for c in range(left + 1, right + 1): out.append((bot, c))
        if left < right:
            for r in range(bot - 1, top - 1, -1): out.append((r, right))
        if top < bot:
            for c in range(right - 1, left, -1): out.append((top, c))
        top += 1; left += 1; bot -= 1; right -= 1
    return out


SP = spiral(N); assert len(set(SP)) == 196
SPI = {p: i for i, p in enumerate(SP)}
bits = ''.join(str(MATRIX[r][c]) for r, c in SP)
phase1 = bytes(int(bits[i:i + 8], 2) for i in range(0, 192, 8))
assert phase1 == b'gsmg.io/theseedisplanted', phase1      # self-test 1: spiral convention

ALL24 = BLUE + YEL
assert len({orbit(p) for p in ALL24 + WHT}) == 25           # self-test 2: rotation-disjoint incl. near-white
GRILLES = {'all24': ALL24, 'all25': ALL24 + WHT, 'blue15': BLUE, 'blue16': BLUE + WHT, 'yel9': YEL, 'yel10': YEL + WHT}

ORDKEY = {'row': lambda p: p[0] * N + p[1], 'col': lambda p: p[1] * N + p[0], 'spiral': lambda p: SPI[p]}
FILLS = {'row': [(r, c) for r in range(N) for c in range(N)], 'spiral': SP}
VARIANTS = [(d, s, o, f) for d in ('cw', 'ccw') for s in range(4) for o in ORDKEY for f in FILLS]   # 48 per grille


def read_positions(G, d, s, o):
    pos = []
    for j in range(4):
        k = s + j if d == 'cw' else s - j
        pos += sorted((rot(h, k) for h in G), key=ORDKEY[o])
    return pos


def make_readers(grilles):
    """precompute index lists: for each (grille, variant) the list of text indices (fill applied)"""
    R = []
    for gname, G in grilles.items():
        for (d, s, o, f) in VARIANTS:
            fidx = {p: i for i, p in enumerate(FILLS[f])}
            R.append(((gname, d, s, o, f), [fidx[p] for p in read_positions(G, d, s, o)]))
    return R


def qscore(t):
    if len(t) < 4: return -99
    return sum(Q.LOGP.get(t[i:i + 4], Q.FLOOR) for i in range(len(t) - 3)) / (len(t) - 3)


DIG = {c: str(i + 1) for i, c in enumerate('abcdefghi')}; DIG['o'] = '0'


def zdirect(s):
    v = int(''.join(DIG[c] for c in s)); b = to_bytes(v)
    return b, sum(x in LOWER for x in b) / len(b), all(x in PRINT for x in b)


def lead_lower(s, cs=LOWER):
    """number of leading big-endian bytes in charset under direct z-method"""
    b = to_bytes(int(''.join(DIG[c] for c in s))); n = 0
    for x in b:
        if x in cs: n += 1
        else: break
    return n


def td_merged(s, M, cs, max_nodes=200000):
    """standard map a..i=1..9; each occurrence of letter M may be a disguised 0 (top-down DFS)."""
    n = len(s); T = TD(n, cs, max_nodes); dv = [int(DIG[c]) for c in s]
    def go(t, A, kd):
        T.nodes += 1
        if T.nodes > max_nodes: T.trunc = True; return
        if t == n:
            if all(c in cs for c in to_bytes(A)): T.sols.append(A)
            return
        r = n - t - 1
        for v in ((dv[t], 0) if (s[t] == M and t > 0) else (dv[t],)):
            nA = A + v * T.p10[r]; nk = T.check(nA, r, kd)
            if nk >= 0: go(t + 1, nA, nk)
            if T.trunc or len(T.sols) >= 5: return
    go(0, 0, 0); return T


def zero_dfs(s, Zmax=12):
    """returns (nsol, deepest_top_bytes, trunc, sols) over: zeros deleted (reinsert Z<=Zmax) + merged-zero letter M"""
    if any(c not in 'abcdefghi' for c in s): return (0, 0, False, [])
    digs = ''.join(DIG[c] for c in s); sols = []; deep = 0; trunc = False
    for Z in range(0, Zmax + 1):
        T = td_insert(digs, Z, LOWER, max_nodes=200000)
        deep = max(deep, T.deepest); trunc |= T.trunc; sols += [('ins', Z, to_bytes(v)) for v in T.sols]
    for M in 'abcdefghi':
        T = td_merged(s, M, LOWER)
        deep = max(deep, T.deepest); trunc |= T.trunc; sols += [('merge', M, to_bytes(v)) for v in T.sols]
    return len(sols), deep, trunc, sols[:3]


def random_grille(rnd):
    orbs = {}
    for r in range(N):
        for c in range(N): orbs.setdefault(orbit((r, c)), []).append((r, c))
    keys = list(orbs); rnd.shuffle(keys)
    cells = [rnd.choice(sorted(orbs[k])) for k in keys[:25]]
    b, y, w = cells[:15], cells[15:24], cells[24:]
    return {'all24': b + y, 'all25': b + y + w, 'blue15': b, 'blue16': b + w, 'yel9': y, 'yel10': y + w}
