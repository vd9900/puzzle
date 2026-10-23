"""Cycle 37 digit_codecs, batch 3 (all with planted self-tests / shuffled controls).
I1  optional '0' insertion AFTER or BEFORE each letter at a prime INPUT position (1-based, counted from left or right)
    -> engine.Search byte-local DFS (exhaustive), charsets lower / printnl.
I2  optional '0' insertion at prime OUTPUT positions counted from the LEFT, for every total insertion count Z
    (output length n+Z fixed => left positions map to right positions), exhaustive DFS with exact-Z constraint.
PB  'prime basics' = prime BASES: digit string (a=1..i=9) read in every prime base 11..251 -> integer -> bytes
    (no byte-local pruning possible; printable / lowercase ratio vs 200-shuffle control per base).
MK  matrixsumlist bit-mask: BIN1 (the 104 bits that spell 'matrixsumlist') has 56 ones = exactly the 56 dbbi letters
    left after removing all 25 b/be tokens. Place those letters at 1-bits (or 0-bits) and '0' elsewhere -> decimal ->
    bytes; also with the 61/60-letter residuals at the first ones, and reversed orders.
"""
import sys, json, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from engine import Search, CHARSETS, to_bytes, text_to_digits, DIG, lowmasks
from common_dc import DBBI, FAED, R60, R61, P, BIN1
from h1b_markers import tokens

OUT = []
def rec(**kw):
    OUT.append(kw); print(json.dumps(kw)[:330], flush=True)
PR = set(range(0x20, 0x7f)) | {9, 10, 13}
def pratio(b): return sum(c in PR for c in b) / max(1, len(b))
def lratio(b): return sum(0x61 <= c <= 0x7a for c in b) / max(1, len(b))
R56 = ''.join(t for t, m, _ in tokens('G') if not m)
STRS = {'DBBI': DBBI, 'R60': R60, 'R61': R61, 'R56': R56, 'FAED': FAED}
STRS.update({k + '_rev': v[::-1] for k, v in list(STRS.items())})


# ---------- I1 ----------
def slots_I1(s, where, count_from):
    n = len(s); slots = []
    for i, c in enumerate(s):
        pos = i + 1 if count_from == 'L' else n - i
        if where == 'before' and pos in P: slots.append(('ind', ('', '0')))
        slots.append(('fix', DIG[c]))
        if where == 'after' and pos in P: slots.append(('ind', ('', '0')))
    return slots

def test_I1():
    # self-test: plant text whose zeros all sit right after letters at prime left positions
    rnd = random.Random(5); words = 'zero prime door basic seed matrix rabbit choice white blue yellow'.split()
    ok = 0; tries = 0
    while ok < 2 and tries < 500000:
        tries += 1
        T = ''.join(rnd.choice(words) for _ in range(3)); D = text_to_digits(T)
        if D.count('0') < 2: continue
        # every zero must directly follow the j-th nonzero digit with j prime (1-based), no adjacent zeros
        good = True; j = 0; prev0 = False
        for ch in D:
            if ch == '0':
                if prev0 or j not in P: good = False; break
                prev0 = True
            else:
                j += 1; prev0 = False
        if not good: continue
        s = ''.join('abcdefghi'[int(ch) - 1] for ch in D if ch != '0')
        # recompute: zero after letter index j (1-based) must be prime -> check via search
        se = Search(slots_I1(s, 'after', 'L'), {}, CHARSETS['lower'], max_nodes=2_000_000, max_solutions=500).run()
        hit = any(to_bytes(v) == T.encode() for v, a, c in se.solutions)
        if hit:
            ok += 1; rec(test='I1_selftest', text=T, recovered=True, nsol=len(se.solutions), nodes=se.nodes)
    assert ok == 2
    for name, s in STRS.items():
        for where in ('after', 'before'):
            for cf in ('L', 'R'):
                for csn in ('lower', 'printnl'):
                    se = Search(slots_I1(s, where, cf), {}, CHARSETS[csn], max_nodes=20_000_000, max_solutions=20, min_bytes=4).run()
                    rec(test='I1', s=name, where=where, count_from=cf, cs=csn, nsol=len(se.solutions), deepest=se.deepest,
                        nodes=se.nodes, trunc=se.truncated, sols=[to_bytes(v)[:60].decode('latin1') for v, a, c in se.solutions[:3]])


# ---------- I2 ----------
def dfs_I2(digs, Z, cs, base=1, max_nodes=5_000_000):
    """output length N = n+Z; zeros may be inserted only at output positions q (1-based from left, or 0-based if base=0)
    that are prime; exactly Z insertions. Processed from the right: right position r (0-based) <-> q = N - r (1-based)."""
    n = len(digs); N = n + Z; low = lowmasks(cs); st = dict(nodes=0, deepest=0, trunc=False); sols = []
    sys.setrecursionlimit(20000)
    def okp(val, p, k):
        while 8 * (k + 1) <= p:
            if ((val >> (8 * k)) & 255) not in cs: return -1
            k += 1
        r = p - 8 * k
        if r and ((val >> (8 * k)) & ((1 << r) - 1)) not in low[r]: return -1
        return k
    def go(i, val, p, k, zleft):
        st['nodes'] += 1
        if st['nodes'] > max_nodes: st['trunc'] = True; return
        st['deepest'] = max(st['deepest'], k)
        if i < 0 and zleft == 0:
            nb = (val.bit_length() + 7) // 8
            if val and all(((val >> (8 * j)) & 255) in cs for j in range(k, nb)): sols.append(val)
            return
        q = N - p - (1 - base)  # left position of the next output digit (1-based if base==1)
        if i >= 0 and (N - p - zleft) > 0:
            nv = val + int(digs[i]) * 10 ** p; nk = okp(nv, p + 1, k)
            if nk >= 0: go(i - 1, nv, p + 1, nk, zleft)
        if zleft > 0 and q in P and q != (1 if base == 1 else 0):
            nk = okp(val, p + 1, k)
            if nk >= 0: go(i, val, p + 1, nk, zleft - 1)
    go(n - 1, 0, 0, 0, Z)
    return sols, st

def test_I2():
    # self-test: text whose zeros are at prime left positions
    rnd = random.Random(8); words = 'zero prime door basic seed matrix rabbit choice white blue yellow'.split(); ok = 0; tries = 0
    while ok < 2 and tries < 500000:
        tries += 1
        T = ''.join(rnd.choice(words) for _ in range(3)); D = text_to_digits(T)
        zs = [i + 1 for i, ch in enumerate(D) if ch == '0']
        if len(zs) >= 2 and all(z in P for z in zs):
            sols, st = dfs_I2(D.replace('0', ''), len(zs), CHARSETS['lower'])
            if T.encode() in [to_bytes(v) for v in sols]:
                ok += 1; rec(test='I2_selftest', text=T, Z=len(zs), recovered=True, nsol=len(sols), nodes=st['nodes'])
    assert ok == 2
    for name, s in STRS.items():
        digs = ''.join(DIG[c] for c in s)
        for base in (1, 0):
            for csn in ('lower', 'printnl'):
                tot_nodes = 0; found = []; deep = 0; trunc = False
                for Z in range(0, 41 if 'FAED' not in name else 121):
                    sols, st = dfs_I2(digs, Z, CHARSETS[csn], base=base)
                    tot_nodes += st['nodes']; deep = max(deep, st['deepest']); trunc |= st['trunc']
                    found += [(Z, to_bytes(v)[:60].decode('latin1')) for v in sols[:3]]
                rec(test='I2', s=name, base=base, cs=csn, Zmax=40 if 'FAED' not in name else 120, nsol=len(found), deepest=deep,
                    nodes=tot_nodes, trunc=trunc, sols=found[:3])


# ---------- PB ----------
def test_PB():
    primes = [p for p in range(11, 252) if p in P]
    rnd = random.Random(3)
    # self-test: text -> integer -> base-13 digits (only digits 1..9 survive?) : construct a plant guaranteed in digits 1..9
    # by brute choice of a text whose base-13 expansion avoids 0,10,11,12 is unrealistic; instead verify decode(encode(x)).
    for B in (11, 13):
        x = int.from_bytes(b'primebasics', 'big'); ds = []
        while x: ds.append(x % B); x //= B
        y = 0
        for d in reversed(ds): y = y * B + d
        assert to_bytes(y) == b'primebasics'
    rec(test='PB_selftest', ok=True)
    for name, s in STRS.items():
        dg = [ord(c) - 96 for c in s]
        best = []
        for B in primes:
            n = 0
            for d in dg: n = n * B + d
            b = to_bytes(n)
            best.append((pratio(b), lratio(b), B, b[:16].hex()))
        # control: shuffled strings, max pratio over all bases
        cmax = []
        for _ in range(100):
            l = dg[:]; rnd.shuffle(l); m = 0
            for B in primes:
                n = 0
                for d in l: n = n * B + d
                m = max(m, pratio(to_bytes(n)))
            cmax.append(m)
        cmax.sort()
        top = max(best)
        rec(test='PB', s=name, nbases=len(primes), best_pratio=round(top[0], 3), best_base=top[2], best_lratio=round(max(x[1] for x in best), 3),
            ctrl_max_pratio_p95=round(cmax[94], 3), ctrl_max=round(cmax[-1], 3))


# ---------- MK ----------
def test_MK():
    bits = BIN1.translate(str.maketrans('ab', '01'))
    assert bits.count('1') == 56 and len(R56) == 56
    # self-test: plant a text, mask by its zero pattern, then rebuild
    T = 'matrixsumlist'; D = text_to_digits(T)
    mask = ''.join('0' if ch == '0' else '1' for ch in D); letters = ''.join('abcdefghi'[int(ch) - 1] for ch in D if ch != '0')
    it = iter(letters); rebuilt = ''.join(DIG[next(it)] if m == '1' else '0' for m in mask)
    assert to_bytes(int(rebuilt)) == T.encode()
    rec(test='MK_selftest', ok=True, note='zero-mask reconstruction round-trips; BIN1 zero density 48/104 vs ~10% expected for decimal text')
    for rname, rs in (('R56', R56), ('R56_rev', R56[::-1])):
        for pol in ('ones', 'zeros'):
            for bname, bb in (('BIN1', bits), ('BIN1_rev', bits[::-1])):
                want = '1' if pol == 'ones' else '0'
                if bb.count(want) != len(rs):
                    # 48 zeros < 56 letters: fill the first 48 letters only, report
                    pass
                it = iter(rs); out = []
                for c in bb:
                    if c == want:
                        try: out.append(DIG[next(it)])
                        except StopIteration: out.append('0')
                    else: out.append('0')
                dg = ''.join(out).lstrip('0')
                b = to_bytes(int(dg)) if dg else b''
                rec(test='MK', resid=rname, letters_at=pol, mask=bname, ndig=len(dg), pratio=round(pratio(b), 3), lratio=round(lratio(b), 3), head=b[:20].hex())


if __name__ == '__main__':
    which = sys.argv[1]
    for w in which.split(','):
        globals()['test_' + w]()
    json.dump(OUT, open(f'/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs/h3_out_{which.replace(",", "_")}.json', 'w'), indent=0)
