"""faed prefixes whose length permits z-method lowercase text (e.g. 540 -> 224 bytes = 7x32), motivated by the
independent change-point finding that faed's last ~30 letters are compositionally anomalous.
Families (all exhaustive top-down interval DFS from digit_codecs/h4_topdown.py):
  A identity a=1..i=9, each occurrence of letter M may be 0 (M in a..i, or none)
  B any bijection letters->1..9 with zero merged into M (td_perm), M in {g, i, e} (faed's over-represented letters)
Charsets lower / lowsp / printnl / textish. Self-test: planted 540-digit lowercase text recovered."""
import sys, time, json, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch'); sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from common import FAED
from h4_topdown import TD, td_perm, CHARSETS, to_bytes
from h7_length_feasibility import *  # noqa (only for reference)
def td_choices(choices, cs, max_nodes=5_000_000, max_sol=5):
    L = len(choices); T = TD(L, cs, max_nodes)
    sys.setrecursionlimit(20000)
    def go(t, A, kd):
        T.nodes += 1
        if T.nodes > max_nodes: T.trunc = True; return
        if t == L:
            if all(c in cs for c in to_bytes(A)): T.sols.append(A)
            return
        r = L - t - 1
        for v in choices[t]:
            if t == 0 and v == 0: continue
            nA = A + v * T.p10[r]; nk = T.check(nA, r, kd)
            if nk >= 0: go(t + 1, nA, nk)
            if T.trunc or len(T.sols) >= max_sol: return
    go(0, 0, 0)
    return T
def famA(s, M, cs):
    ch = [((ord(c) - 96, 0) if c == M else (ord(c) - 96,)) for c in s]
    return td_choices(ch, cs)
# self-test: plant a lowercase text, encode with zeros disguised as 'g'
r = random.Random(4)
while True:
    txt = bytes(r.choice(b'abcdefghijklmnopqrstuvwxyz ') for _ in range(224)); txt = b't' + txt[1:]
    d = str(int.from_bytes(txt, 'big'))
    if len(d) == 540: break
planted = ''.join('g' if c == '0' else chr(96 + int(c)) for c in d)
T = famA(planted, 'g', CHARSETS['lowsp']); assert any(to_bytes(a) == txt for a in T.sols), 'selftest failed'
print('selftest OK nodes', T.nodes)
out = []
for cut in (540, 536, 533, 531, 545, 548):
    s = FAED[:cut]
    for csn in ('lower', 'lowsp', 'printnl', 'textish'):
        cs = CHARSETS[csn]
        for M in [None] + list('abcdefghi'):
            t0 = time.time(); T = famA(s, M, cs)
            rec = dict(fam='A', cut=cut, cs=csn, M=M, nodes=T.nodes, trunc=T.trunc, deepest=T.deepest, nsol=len(T.sols),
                       sols=[to_bytes(a)[:80].decode('latin-1') for a in T.sols[:3]])
            out.append(rec)
            if T.sols or T.trunc or T.deepest >= 12: print(rec)
print('famA done', len(out), 'runs; solutions:', sum(r['nsol'] for r in out), 'truncated:', sum(r['trunc'] for r in out))
for cut in (540,):
    for M in 'gie':
        for csn in ('lowsp', 'printnl'):
            T = td_perm(FAED[:cut], M, CHARSETS[csn], max_nodes=30_000_000)
            rec = dict(fam='B', cut=cut, cs=csn, M=M, nodes=T.nodes, trunc=T.trunc, deepest=T.deepest, nsol=len(T.sols))
            out.append(rec); print(rec)
json.dump(out, open('/home/vin/bitcoin_puzzle/scratch/c37/faed540/results.json', 'w'))
