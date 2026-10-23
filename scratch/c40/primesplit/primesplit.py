"""Cycle 40: 'primes split faed into two streams' family (and dbbi primes vs 24 colour bits). Self-verifying.
P = faed letters at prime positions (1-based / 0-based, 104), N = rest (466). Each stream fwd+rev:
 (1) z-method length feasibility, (2) exhaustive top-down DFS: single-letter zero disguise (free / only where label bit=1 /
 only where bit=0 / any letter optionally zero where bit=b) + free zero re-insertion (td_insert), (3) td_perm all 9! maps
 (+merged zero letter M, or no zero), (4) Phase 3.2 straddling checkerboard (esc 1,4) and Bifid (dbbi square) scored with
 the clean Carroll quadgram model vs shuffled controls. dbbi: 24 physical-prime letters vs 24 colour bits."""
import sys, time, json, random, math, re, itertools
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch'); sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/construction_forensics')
sys.setrecursionlimit(20000)
from common import DBBI, FAED, BIN1, Z1, Z2, primes_upto, letters_to_digits
from h4_topdown import TD, td_insert, td_perm, CHARSETS
from engine import to_bytes, text_to_digits
from bifid import bifid_decrypt, bifid_encrypt, CANON
from quad_indep import LOGP, FLOOR
OUT = {}
PR = set(primes_upto(1000))
assert len([p for p in PR if p <= 570]) == 104 and len([p for p in PR if p <= 91]) == 24
BITS = BIN1.translate(str.maketrans('ab', '01')); assert len(BITS) == 104
def split(s, base):
    P = ''.join(c for i, c in enumerate(s) if (i + base) in PR); N = ''.join(c for i, c in enumerate(s) if (i + base) not in PR)
    return P, N
P1, N1 = split(FAED, 1); P0, N0 = split(FAED, 0)
STREAMS = {'P1': P1, 'N1': N1, 'P0': P0, 'N0': N0}
STREAMS.update({k + '_rev': v[::-1] for k, v in list(STREAMS.items())})
OUT['sizes'] = {k: len(v) for k, v in STREAMS.items()}; print('sizes', OUT['sizes'])
print('P1', P1); print('P0', P0)
CS = {k: CHARSETS[k] for k in ('lower', 'printnl', 'textish')}
D1 = {c: i + 1 for i, c in enumerate('abcdefghi')}

# ---------- (1) length feasibility ----------
def top_bytes(lo, hi):
    out = set(); nb_lo = (lo.bit_length() + 7) // 8; nb_hi = ((hi - 1).bit_length() + 7) // 8
    for nb in range(nb_lo, nb_hi + 1):
        a = max(lo, 1 << (8 * (nb - 1))); b = min(hi - 1, (1 << (8 * nb)) - 1)
        if a <= b: out |= set(range(a >> (8 * (nb - 1)), (b >> (8 * (nb - 1))) + 1))
    return out
def feas(L, lead=None):
    lo, hi = (10 ** (L - 1), 10 ** L) if lead is None else (lead * 10 ** (L - 1), (lead + 1) * 10 ** (L - 1))
    tb = top_bytes(lo, hi); return {c: bool(tb & CS[c]) for c in CS}
for nm, s in (('Z1', letters_to_digits(Z1)), ('Z2', letters_to_digits(Z2))):
    assert feas(len(s), int(s[0]))['lower'], nm          # self-check: solved stages are feasible
feasrows = {}
for k, s in STREAMS.items():
    L = len(s)
    feasrows[k] = dict(L=L, any_map=feas(L), std_lead=feas(L, D1[s[0]]),
                       insert_Z_feasible_lower=[Z for Z in range(0, 150) if feas(L + Z, D1[s[0]])['lower']][:12])
    print('feas', k, feasrows[k])
OUT['feasibility'] = feasrows

# ---------- (2) zero-disguise top-down DFS ----------
def td_opts(opts, cs, max_nodes=5_000_000, max_sol=50):
    n = len(opts); T = TD(n, cs, max_nodes)
    def go(t, A, kd):
        T.nodes += 1
        if T.nodes > max_nodes: T.trunc = True; return
        if t == n:
            if all(c in cs for c in to_bytes(A)): T.sols.append(A)
            return
        r = n - t - 1
        for v in opts[t]:
            nA = A + v * T.p10[r]; nk = T.check(nA, r, kd)
            if nk >= 0: go(t + 1, nA, nk)
            if T.trunc or len(T.sols) >= max_sol: return
    go(0, 0, 0); return T
def make_opts(s, M, mode, bits=None):
    o = []
    for t, c in enumerate(s):
        d = D1[c]; ok = t > 0 and (M == '*' or c == M)
        if mode in ('bit1', 'bit0'): ok = ok and bits[t] == mode[-1]
        o.append((d, 0) if ok else (d,))
    return o
# self-test: planted ~104-digit text, zeros disguised as letter M only where an (artificial) bit string has 1
rnd = random.Random(40)
for txt, M in (('raisingthestakeswithoutextrachancesofwin', 'g'), ('halfandbetterhalfmatrixsumlistpri', 'c')):
    D = text_to_digits(txt); s = ''.join('abcdefghi'[int(ch) - 1] if ch != '0' else M for ch in D)
    bits = ''.join('1' if (ch == '0' or rnd.random() < .5) else '0' for ch in D)
    for mode in ('free', 'bit1'):
        T = td_opts(make_opts(s, M, mode, bits), CS['lower'], max_sol=10 ** 4)
        assert any(to_bytes(v) == txt.encode() for v in T.sols), (txt, mode)
    T = td_opts(make_opts(s, '*', 'bit1', bits), CS['lower'], max_sol=10 ** 5)
    assert any(to_bytes(v) == txt.encode() for v in T.sols), (txt, 'anyletter-bit1')
    Tp = td_perm(s, M, CS['printnl'], max_nodes=50_000_000, max_sol=10 ** 4)
    assert any(to_bytes(v) == txt.encode() for v, a in Tp.sols), (txt, 'td_perm')   # std map is one of the 9! maps
    Ti = td_insert(D.replace('0', ''), D.count('0'), CS['lower'], max_sol=10 ** 4)
    assert any(to_bytes(v) == txt.encode() for v in Ti.sols), (txt, 'td_insert')
print('selftests (zero-disguise free/bit1/any-letter-bit1, td_perm, td_insert) OK', flush=True)

zrows = []
for k, s in STREAMS.items():
    isP = k.startswith('P'); bits = (BITS if not k.endswith('_rev') else BITS[::-1]) if isP else None
    modes = ['free'] + (['bit1', 'bit0'] if isP else [])
    for csn in ('lower', 'printnl'):
        for M in 'abcdefghi':
            for mode in modes:
                T = td_opts(make_opts(s, M, mode, bits), CS[csn])
                zrows.append(dict(s=k, M=M, mode=mode, cs=csn, nodes=T.nodes, trunc=T.trunc, deep=T.deepest, nsol=len(T.sols),
                                  sols=[to_bytes(v)[:60].decode('latin1') for v in T.sols[:3]]))
        if isP:
            for mode in ('bit1', 'bit0'):
                T = td_opts(make_opts(s, '*', mode, bits), CS[csn], max_nodes=20_000_000)
                zrows.append(dict(s=k, M='*any', mode=mode, cs=csn, nodes=T.nodes, trunc=T.trunc, deep=T.deepest, nsol=len(T.sols),
                                  sols=[to_bytes(v)[:60].decode('latin1') for v in T.sols[:3]]))
OUT['zero_disguise'] = dict(n=len(zrows), nsol=sum(r['nsol'] for r in zrows), ntrunc=sum(r['trunc'] for r in zrows),
                            max_deep=max(r['deep'] for r in zrows), hits=[r for r in zrows if r['nsol']],
                            trunc=[r for r in zrows if r['trunc']])
print('zero-disguise:', {k: v for k, v in OUT['zero_disguise'].items() if k not in ('hits', 'trunc')}, flush=True)
# free zero re-insertion
irows = []
for k, s in STREAMS.items():
    digs = ''.join(str(D1[c]) for c in s); Zmax = 40 if len(s) < 200 else 110
    for csn in ('lower', 'textish'):   # printnl+free insertion is supercritical for P (run1: 18 garbage sols, see run1 log)
        tot = 0; tr = False; sols = []; deep = 0
        for Z in range(0, Zmax + 1):
            T = td_insert(digs, Z, CS[csn], max_nodes=1_000_000)
            tot += T.nodes; tr |= T.trunc; deep = max(deep, T.deepest); sols += [(Z, to_bytes(v)[:60].decode('latin1')) for v in T.sols[:3]]
        irows.append(dict(s=k, cs=csn, Zmax=Zmax, nodes=tot, trunc=tr, deep=deep, nsol=len(sols), sols=sols[:5]))
        print('insert', irows[-1], flush=True)
OUT['td_insert'] = irows

# ---------- (3) td_perm: all 9! maps, merged zero letter M or none ----------
prows = []
for k, s in STREAMS.items():
    for csn in ('lower', 'textish', 'printnl'):
        for M in list('abcdefghi') + [None]:
            t0 = time.time(); T = td_perm(s, M, CS[csn], max_nodes=5_000_000)
            prows.append(dict(s=k, M=M, cs=csn, nodes=T.nodes, trunc=T.trunc, deep=T.deepest, nsol=len(T.sols),
                              sols=[(to_bytes(v)[:60].decode('latin1'), a) for v, a in T.sols[:3]], secs=round(time.time() - t0, 1)))
    print('perm', k, [(r['cs'], r['M'], r['nsol'], r['trunc'], r['deep']) for r in prows if r['s'] == k], flush=True)
OUT['td_perm'] = dict(n=len(prows), nsol=sum(r['nsol'] for r in prows), ntrunc=sum(r['trunc'] for r in prows),
                      hits=[r for r in prows if r['nsol']], trunc=[r for r in prows if r['trunc']])
json.dump(OUT, open('/home/vin/bitcoin_puzzle/scratch/c40/primesplit/zmethod_results.json', 'w'), indent=0, default=str)
print('td_perm summary', {k: v for k, v in OUT['td_perm'].items() if k not in ('hits', 'trunc')})
