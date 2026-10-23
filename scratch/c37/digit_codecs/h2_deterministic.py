"""Cycle 37 digit_codecs: cheap deterministic / statistical codec tests (all with planted self-tests + controls).

A  bijective base-9 numeration (digits a..i = 1..9, NO zero digit) -> integer -> bytes  [z-method analogue];
   also the integer's standard base-9 digit string re-read as decimal -> bytes ("zeroes appear on conversion").
B  a1z26 reading (R=18 A=1 B=2 hint): digit-profile test vs English-a1z26 (best case over any letter<->digit map),
   and a1z26 segmentation beam search scored by quadgrams vs shuffled controls.
C  fixed-width chunk readings (2/3 digits, all phases, fwd/rev): mod-26 letters (quadgram z vs shuffles),
   3-digit chunks as decimal ASCII / mod 256 (printable ratio z vs shuffles).
D  z-method on the community Bifid output (a1z26 digits -> int; 5x5 coordinates -> base-10/base-5 int).
E  zeros inserted at prime output positions (deterministic, 4 conventions) and optional insertion at
   right-counted prime positions (byte-local DFS); R60/R61 optional zeroing at prime positions (zero_dfs.dfs).
F  structural feasibility of binary payloads (WIF 0x80.., Salted__) for the digit-length families.
Output: JSON lines to h2_out.json and a printed summary."""
import sys, json, random, math, re, hashlib
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from common_dc import DBBI, FAED, Z1, Z2, R60, R61, marked, P
from engine import CHARSETS, to_bytes, text_to_digits
import cleanq as textmodel
from zero_dfs import dfs as zdfs

OUT = []
def rec(**kw):
    OUT.append(kw); print(json.dumps(kw)[:400], flush=True)

D = lambda s: ''.join(str(ord(c) - 96) for c in s)       # a=1..i=9
STRS = {'DBBI': DBBI, 'R60': R60, 'R61': R61, 'FAED': FAED}
STRS.update({k + '_rev': v[::-1] for k, v in list(STRS.items())})
PR = set(range(0x20, 0x7f)) | {9, 10, 13}
def pratio(b): return sum(c in PR for c in b) / max(1, len(b))
def lratio(b): return sum(0x61 <= c <= 0x7a for c in b) / max(1, len(b))
def longest_print(b):
    best = cur = 0
    for c in b:
        cur = cur + 1 if c in PR else 0; best = max(best, cur)
    return best

# ---------------- A: bijective base-9 ----------------
def bij9_decode(digs):
    n = 0
    for d in digs: n = n * 9 + int(d)
    return n
def bij9_encode(n):
    out = []
    while n > 0:
        r = n % 9 or 9; out.append(str(r)); n = (n - r) // 9
    return ''.join(reversed(out))
def std9(n):
    out = []
    while n: out.append(str(n % 9)); n //= 9
    return ''.join(reversed(out)) or '0'

def test_A():
    # self-test: plant text -> bijective base 9 -> letters; decode must recover
    for t in ('lastwordsbeforearchichoice', 'thispassword'):
        n = int.from_bytes(t.encode(), 'big'); s = bij9_encode(n)
        assert '0' not in s and to_bytes(bij9_decode(s)) == t.encode()
        # and standard-base-9-reread variant: text -> decimal digits -> treat as base-9 value -> bijective digits
        dec = text_to_digits(t)
        if '9' not in dec:
            s2 = bij9_encode(int(dec, 9)); assert to_bytes(int(std9(bij9_decode(s2)))) == t.encode()
    rec(test='A_selftest', ok=True)
    rnd = random.Random(1)
    for name, s in STRS.items():
        n = bij9_decode(D(s)); b = to_bytes(n)
        n2 = int(std9(n)); b2 = to_bytes(n2)
        # control: 200 shuffles, max printable ratio
        ctrl = []
        for _ in range(200):
            l = list(s); rnd.shuffle(l); ctrl.append(pratio(to_bytes(bij9_decode(D(''.join(l))))))
        rec(test='A_bij9', s=name, nbytes=len(b), pratio=round(pratio(b), 3), lratio=round(lratio(b), 3),
            longest_print=longest_print(b), ctrl_pratio_max=round(max(ctrl), 3), head=b[:24].hex(),
            std9_as_dec_pratio=round(pratio(b2), 3), std9_longest=longest_print(b2))

# ---------------- B: a1z26 ----------------
def english_letters():
    t = open('/home/vin/bitcoin_puzzle/scratch/corpora/carroll_public_domain.txt', errors='ignore').read().lower()
    t += open('/home/vin/bitcoin_puzzle/scratch/corpora/puzzle_texts.txt', errors='ignore').read().lower()
    return re.sub('[^a-z]', '', t)

def test_B():
    E = english_letters()
    enc = ''.join(str(ord(c) - 96) for c in E[:200000])
    from collections import Counter
    ce = Counter(enc); tot = sum(ce.values())
    prof_e = sorted((v / tot for v in ce.values()), reverse=True)
    # a1z26 English with zeros removed (zero digits deleted) -> 9-symbol profile
    ce9 = Counter(c for c in enc if c != '0'); t9 = sum(ce9.values())
    prof_e9 = sorted((v / t9 for v in ce9.values()), reverse=True)
    for name in ('FAED', 'DBBI', 'R60'):
        s = STRS[name]; c = Counter(s); n = len(s)
        prof = sorted((v / n for v in c.values()), reverse=True)
        # best-case (sorted) chi-square of observed counts vs English-a1z26 9-symbol profile
        chi = sum((c_obs - n * p) ** 2 / (n * p) for c_obs, p in zip(sorted(c.values(), reverse=True), prof_e9))
        # null: same statistic for samples drawn from the English-a1z26 model (how large chi is typical)
        rnd = random.Random(5); nulls = []
        for _ in range(300):
            st = rnd.randrange(0, len(enc) - n * 3); sample = [ch for ch in enc[st:st + n * 3] if ch != '0'][:n]
            cs = Counter(sample)
            vals = sorted(cs.values(), reverse=True) + [0] * (9 - len(cs))
            nulls.append(sum((a - n * p) ** 2 / (n * p) for a, p in zip(vals, prof_e9)))
        nulls.sort()
        rec(test='B_profile', s=name, obs_sorted=[round(x, 3) for x in prof], eng_a1z26_sorted9=[round(x, 3) for x in prof_e9],
            chi_bestmap=round(chi, 1), null_chi_p99=round(nulls[int(0.99 * len(nulls))], 1), null_chi_max=round(nulls[-1], 1),
            rejected=chi > nulls[-1])
    # segmentation beam search
    L, F = textmodel.LOGP, textmodel.FLOOR
    BONUS = 4.4  # per-letter offset so English (Carroll model, ~-4.4 per quad) scores ~0
    def beam(digs, width=400, allow_zero=False):
        beams = {(0, ''): 0.0}  # (pos, last3) -> score ; keep text separately
        texts = {(0, ''): ''}
        n = len(digs)
        frontier = [(0, '', '', 0.0)]
        best_full = None
        layers = {0: {('', ''): (0.0, '')}}
        from collections import defaultdict
        states = defaultdict(dict)
        states[0][''] = (0.0, '')
        for pos in range(n):
            if pos not in states: continue
            cur = sorted(states[pos].items(), key=lambda kv: -kv[1][0])[:width]
            for last3, (sc, txt) in cur:
                opts = []
                d1 = digs[pos]
                if d1 != '0': opts.append((1, int(d1)))
                if pos + 1 < n:
                    v = int(digs[pos:pos + 2])
                    if 10 <= v <= 26 and (allow_zero or digs[pos + 1] != '0'): opts.append((2, v))
                for ln, v in opts:
                    ch = chr(96 + v); quad = last3 + ch
                    add = (L.get(quad, F) + BONUS) if len(quad) == 4 else 0.0
                    nl = quad[-3:]; np_ = pos + ln
                    nt = txt + ch; ns = sc + add
                    if nl not in states[np_] or states[np_][nl][0] < ns:
                        states[np_][nl] = (ns, nt)
            del states[pos]
        if n not in states or not states[n]: return None
        sc, txt = max(states[n].values())
        return sc / max(1, len(txt)), txt
    # planted self-test: English text (letters a..z) -> a1z26 digits -> must be recovered approximately
    plant = 'yourlifeisthesumofaremainderofanunbalancedequation'
    r = beam(''.join(str(ord(c) - 96) for c in plant), allow_zero=True)
    rec(test='B_beam_selftest', plant=plant, got=r[1], score=round(r[0], 3))
    rnd = random.Random(9)
    for name in ('DBBI', 'R60', 'R61', 'DBBI_rev', 'R60_rev', 'FAED', 'FAED_rev'):
        s = STRS[name]
        sc, txt = beam(D(s), width=200 if 'FAED' in name else 400)
        ctrl = []
        for _ in range(30 if 'FAED' in name else 100):
            l = list(s); rnd.shuffle(l); ctrl.append(beam(D(''.join(l)), width=200 if 'FAED' in name else 400)[0])
        mu = sum(ctrl) / len(ctrl); sd = (sum((x - mu) ** 2 for x in ctrl) / len(ctrl)) ** .5
        rec(test='B_beam', s=name, score=round(sc, 3), ctrl_mean=round(mu, 3), ctrl_sd=round(sd, 3), z=round((sc - mu) / sd, 2), text=txt[:80])

# ---------------- C: chunk readings ----------------
def test_C():
    rnd = random.Random(11)
    sc = textmodel.score
    def readings(s):
        d = D(s); out = {}
        for w in (2, 3):
            for off in range(w):
                ch = [int(d[i:i + w]) for i in range(off, len(d) - w + 1, w)]
                out[f'w{w}o{off}_mod26'] = ('txt', ''.join(chr(97 + v % 26) for v in ch))
                out[f'w{w}o{off}_m1mod26'] = ('txt', ''.join(chr(97 + (v - 1) % 26) for v in ch))
                if w == 3:
                    out[f'w3o{off}_ascii'] = ('bytes', bytes(v % 256 for v in ch))
        return out
    # self-test: plant English as homophonic 2-digit mod-26 code without zeros -> score must exceed controls
    plant = english_letters()[5000:5300]
    digs = ''
    for c in plant:
        k = ord(c) - 97
        opts = [v for v in range(11, 100) if v % 26 == k and '0' not in str(v)]
        digs += str(rnd.choice(opts))
    plant_s = ''.join(chr(96 + int(x)) for x in digs)
    names = dict(STRS); names['PLANT'] = plant_s
    for name, s in names.items():
        R = readings(s)
        ctrlR = []
        for _ in range(40):
            l = list(s); rnd.shuffle(l); ctrlR.append(readings(''.join(l)))
        for key, (kind, val) in R.items():
            f = sc if kind == 'txt' else pratio
            v = f(val); cv = [f(c[key][1]) for c in ctrlR]
            mu = sum(cv) / len(cv); sd = (sum((x - mu) ** 2 for x in cv) / len(cv)) ** .5 or 1e-9
            z = (v - mu) / sd
            if abs(z) > 3 or name == 'PLANT':
                rec(test='C_chunk', s=name, reading=key, value=round(v, 3), z=round(z, 2), head=(val[:40] if kind == 'txt' else val[:20].hex()))
    rec(test='C_done')

# ---------------- D: Bifid output z-method ----------------
def test_D():
    import bifid
    B = bifid.BIF; sq = bifid.CANON
    from collections import Counter
    c = Counter(B); share = sum(c[x] for x in 'abcdefghio') / len(B)
    rec(test='D_bifid_letters', n=len(B), share_a_to_i_plus_o=round(share, 3), expected_uniform=round(10 / 25, 3))
    body = B[7:]
    cands = {}
    cands['a1z26_all'] = ''.join(str(ord(x) - 96) for x in B)
    cands['a1z26_body'] = ''.join(str(ord(x) - 96) for x in body)
    cands['zmethod_body_aito_only'] = ''.join({**{ch: str(i + 1) for i, ch in enumerate('abcdefghi')}, 'o': '0'}.get(x, '') for x in body)
    pos = {ch: (i // 5, i % 5) for i, ch in enumerate(sq)}
    cands['coords1_body'] = ''.join(f'{pos[x][0] + 1}{pos[x][1] + 1}' for x in body)
    cands['coords0_body'] = ''.join(f'{pos[x][0]}{pos[x][1]}' for x in body)
    for k, dg in cands.items():
        b = to_bytes(int(dg)) if dg.strip('0') else b''
        rec(test='D_bifid_dec', cand=k, ndig=len(dg), pratio=round(pratio(b), 3), lratio=round(lratio(b), 3), longest_print=longest_print(b))
    for k in ('coords0_body',):
        dg = cands[k]
        b = to_bytes(int(dg, 5)); rec(test='D_bifid_base5', cand=k, pratio=round(pratio(b), 3), longest_print=longest_print(b), head=b[:16].hex())
    idx = ''.join(chr(sq.index(x)) for x in body)
    n = 0
    for ch in idx: n = n * 25 + ord(ch)
    b = to_bytes(n); rec(test='D_bifid_base25', pratio=round(pratio(b), 3), longest_print=longest_print(b))

# ---------------- E: prime zero insertion ----------------
def insert_zero_full(digs, base, from_right):
    """build output where every prime output position (1-based if base==1 else 0-based) is '0'."""
    out = []; it = iter(digs if not from_right else digs[::-1]); pos = base
    remaining = len(digs)
    while remaining:
        if pos in P:
            out.append('0')
        else:
            out.append(next(it)); remaining -= 1
        pos += 1
    s = ''.join(out)
    return s[::-1] if from_right else s

def opt_insert_dfs(digs, cs, base=1, max_nodes=3_000_000, max_sol=20):
    """optional '0' insertion at right-counted prime output positions; byte-local pruning."""
    low = [set(c & ((1 << m) - 1) for c in cs) for m in range(9)]
    n = len(digs); nodes = [0]; sols = []; deepest = [0]
    sys.setrecursionlimit(20000)
    def ok(val, p, k):
        while 8 * (k + 1) <= p:
            if ((val >> (8 * k)) & 255) not in cs: return -1
            k += 1
        r = p - 8 * k
        if r and ((val >> (8 * k)) & ((1 << r) - 1)) not in low[r]: return -1
        return k
    def go(i, val, p, k, nz):
        nodes[0] += 1
        if nodes[0] > max_nodes or len(sols) >= max_sol: return
        deepest[0] = max(deepest[0], k)
        if i < 0:
            nb = (val.bit_length() + 7) // 8
            if val and all(((val >> (8 * j)) & 255) in cs for j in range(k, nb)): sols.append((val, nz))
            return
        outpos = p + base  # position (counted from the right) of the next output digit
        # option 1: consume next letter digit
        nv = val + int(digs[i]) * 10 ** p; nk = ok(nv, p + 1, k)
        if nk >= 0: go(i - 1, nv, p + 1, nk, nz)
        if outpos in P:
            nk = ok(val, p + 1, k)
            if nk >= 0: go(i, val, p + 1, nk, nz + 1)
    go(n - 1, 0, 0, 0, 0)
    return sols, deepest[0], nodes[0], nodes[0] > max_nodes

def test_E():
    # self-test for optional insertion: plant text whose decimal has zeros only at right-counted prime positions
    rnd = random.Random(2)
    planted_ok = 0
    for t in ('lastwordsbeforearchichoice', 'thispassword', 'aprimeexample', 'zeroedoutcharacters'):
        dg = text_to_digits(t)
        zr = [len(dg) - i for i, c in enumerate(dg) if c == '0']  # right-counted 1-based positions of zeros
        if all(z in P for z in zr):
            stripped = dg.replace('0', '')
            sols, deep, nodes, tr = opt_insert_dfs(stripped, CHARSETS['lower'])
            hit = any(to_bytes(v) == t.encode() for v, _ in sols)
            planted_ok += hit
            rec(test='E_selftest', text=t, zeros_at=zr, recovered=hit, nsol=len(sols), nodes=nodes)
        else:
            rec(test='E_selftest_skip', text=t, zeros_at=zr)
    # synthetic plant guaranteed to qualify: search texts until zeros sit only at right-counted primes
    words = 'the prime basics are required zero out some characters to proceed another door'.split()
    tries = 0
    while planted_ok == 0 and tries < 200000:
        tries += 1
        t = ''.join(rnd.choice(words) for _ in range(3)); dg = text_to_digits(t)
        zr = [len(dg) - i for i, c in enumerate(dg) if c == '0']
        if zr and all(z in P for z in zr):
            sols, deep, nodes, tr = opt_insert_dfs(dg.replace('0', ''), CHARSETS['lower'], max_sol=1000)
            hit = any(to_bytes(v) == t.encode() for v, _ in sols)
            rec(test='E_selftest_synth', text=t, zeros_at=zr, recovered=hit, nsol=len(sols), nodes=nodes, tries=tries)
            planted_ok += hit
    assert planted_ok
    for name, s in STRS.items():
        dg = D(s)
        for base in (0, 1):
            for fr in (False, True):
                o = insert_zero_full(dg, base, fr); b = to_bytes(int(o))
                rec(test='E_full_insert', s=name, base=base, from_right=fr, pratio=round(pratio(b), 3), longest_print=longest_print(b))
            for csn in ('lower', 'printnl'):
                sols, deep, nodes, tr = opt_insert_dfs(dg, CHARSETS[csn], base=base)
                rec(test='E_opt_insert_right', s=name, base=base, cs=csn, nsol=len(sols), deepest=deep, nodes=nodes, trunc=tr,
                    sols=[to_bytes(v)[:60].decode('latin1') for v, _ in sols[:3]])
    # R60/R61 optional zero replacement at prime positions (zero_dfs2 only covered DBBI/FAED)
    for name in ('R60', 'R61'):
        for rev in (False, True):
            s = STRS[name][::-1] if rev else STRS[name]; n = len(s)
            allows = {'p1L': {i for i in range(n) if (i + 1) in P}, 'p0L': {i for i in range(n) if i in P},
                      'p1R': {i for i in range(n) if (n - i) in P}, 'p0R': {i for i in range(n) if (n - 1 - i) in P}}
            for an, al in allows.items():
                for csn in ('lower', 'printnl', 'hex', 'b58', 'b64'):
                    sols, best, nodes = zdfs(s, 'abcdefghi', CHARSETS[csn], max_nodes=2_000_000, allow=al)
                    rec(test='E_R_prime_zero', s=name, rev=rev, allow=an, cs=csn, nsol=len(sols), deepest=best[0], nodes=nodes,
                        sols=[to_bytes(v)[:60].decode('latin1') for v, _ in sols[:3]])

# ---------------- F: binary payload feasibility ----------------
def test_F():
    for name, s in STRS.items():
        dg = D(s); n = int(dg); nb = (n.bit_length() + 7) // 8
        top = n >> (8 * (nb - 1))
        rec(test='F_len', s=name, ndig=len(dg), nbytes=nb, top_byte=top,
            wif_len_ok=nb in (37, 38), salted_len_ok=(nb - 16) % 16 == 0 and nb >= 32)

if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'ABCDEF'
    for w in which:
        globals()['test_' + w]()
    json.dump(OUT, open(f'/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs/h2_out_{which}.json', 'w'), indent=0)
