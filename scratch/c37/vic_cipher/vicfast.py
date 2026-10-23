# Fast VIC derivation -> un-transposition -> serial-structure detector, for faed (570 symbols a-i).
# Builds on vic.py (validated against Wikipedia key-derivation vector and quadibloc full worked example).
import sys, math, random, re
import numpy as np
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/vic_cipher')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
import vic
from functools import lru_cache

LET = 'abcdefghi'

def col_perm(n, key):
    return np.array(vic.columnar_perm(n, list(key)), dtype=np.int32)

@lru_cache(maxsize=200000)
def _cp(n, key):
    return col_perm(n, key)

@lru_cache(maxsize=200000)
def _dp(n, key, gap):
    return np.array(vic.disrupted_perm(n, list(key), gap), dtype=np.int32)

def untranspose_index(n, Q, R, mode='disrupted'):
    """Return idx such that plain_stream = ct_body[idx].
    Encryption: t1 = st[pQ] (t1[k] = st[pQ[k]]); t2 = t1[pR]. So t2[k] = st[pQ[pR[k]]].
    Composite perm c = pQ[pR]; st[c[k]] = t2[k] -> st = t2[inv(c)]."""
    pQ = _cp(n, tuple(Q))
    if mode == 'disrupted':
        pR = _dp(n, tuple(R), 1)
    elif mode == 'disrupted0':          # variant: next triangle starts right after the previous one (no gap row)
        pR = _dp(n, tuple(R), 0)
    elif mode == 'plain':
        pR = _cp(n, tuple(R))
    elif mode == 'single':
        pR = np.arange(n, dtype=np.int32)
    else:
        raise ValueError(mode)
    c = pQ[pR]
    inv = np.empty(n, dtype=np.int32)
    inv[c] = np.arange(n, dtype=np.int32)
    return inv

def hcond_arr(a, k):
    """H(next|prev) in bits for int array a over alphabet size k."""
    pc = np.bincount(a[:-1] * k + a[1:], minlength=k * k).reshape(k, k).astype(float)
    rows = pc.sum(1)
    n = pc.sum()
    with np.errstate(divide='ignore', invalid='ignore'):
        t = np.where(pc > 0, pc * np.log2(pc / rows[:, None]), 0.0)
    return -t.sum() / n

def null_stats(a, k, trials=400, seed=0):
    r = np.random.default_rng(seed)
    b = a.copy(); vals = []
    for _ in range(trials):
        r.shuffle(b); vals.append(hcond_arr(b, k))
    vals = np.array(vals)
    return vals.mean(), vals.std()

# ---------- keygroup reading ----------
def kg_readings(kg_letters, mapname):
    """Return list of (desc, digit-string) readings of a 5-letter keygroup.
    a1: a..i = 1..9; the hidden digit 0 is merged into ONE letter X; any subset of X's occurrences may be 0.
    a0: a..i = 0..8; the hidden digit 9 merged into one letter X."""
    if mapname == 'a1':
        base = {c: str(i + 1) for i, c in enumerate(LET)}; hid = '0'
    else:
        base = {c: str(i) for i, c in enumerate(LET)}; hid = '9'
    d0 = ''.join(base[c] for c in kg_letters)
    outs = {d0: 'none'}
    for X in sorted(set(kg_letters)):
        pos = [i for i, c in enumerate(kg_letters) if c == X]
        for m in range(1, 1 << len(pos)):
            d = list(d0)
            for j, p in enumerate(pos):
                if m >> j & 1: d[p] = hid
            outs.setdefault(''.join(d), '%s->%s@%s' % (X, hid, ''.join(str(p) for j, p in enumerate(pos) if m >> j & 1)))
    return [(v, k) for k, v in outs.items()]

def kg_positions(date, ngroups):
    """Group index (0-based, in the full ciphertext of ngroups groups) of the keygroup.
    Standard (Wikipedia/quadibloc): inserted d6 groups from the end -> index ngroups-d6; d6=0 -> last group.
    Alternates: d6=0 read as 10; counted from the start."""
    d6 = int(date[5]) if len(date) > 5 else 0
    pos = []
    if d6 == 0:
        pos += [('end0', ngroups - 1), ('end10', ngroups - 10)]
    else:
        pos += [('end', ngroups - d6)]
        pos += [('start', d6 - 1)]
    return pos

def derive_keys(phrase20, date, pnum, kgdigits):
    k = vic.derive(phrase20, date, pnum, kgdigits)
    return k['Q'], k['R'], k['S']

# ---------- planted encryption (for self-tests) ----------
def plant(text, phrase, date, pnum, kg, total=570, mode='disrupted', top='AT ONE SIR', zero_letter='g',
          mapname='a1', numeric=False, rng=None):
    """Encrypt English text with full VIC so that the final ciphertext has exactly `total` digits, then map to letters
    (a1: 1..9 -> a..i, 0 -> zero_letter). Returns (letters, plain_digit_stream, keys)."""
    k = vic.derive(phrase, date, pnum, kg)
    enc, dec, esc = vic.vic_board(k['S'], top)
    body_len = total - 5
    st = ''
    for ch in text:
        c = enc.get(ch)
        if c is None: continue
        if len(st) + len(c) > body_len: break
        st += c
    while len(st) < body_len: st += '0'
    n = body_len
    pQ = _cp(n, tuple(k['Q']))
    t1 = ''.join(st[i] for i in pQ)
    if mode == 'disrupted': pR = _dp(n, tuple(k['R']), 1)
    elif mode == 'disrupted0': pR = _dp(n, tuple(k['R']), 0)
    elif mode == 'plain': pR = _cp(n, tuple(k['R']))
    else: pR = np.arange(n)
    t2 = ''.join(t1[i] for i in pR)
    groups = [t2[i:i + 5] for i in range(0, len(t2), 5)]
    ng = len(groups) + 1
    pos = kg_positions(date, ng)[0][1]
    groups.insert(pos, kg)
    ct = ''.join(groups)
    if mapname == 'a1':
        m = {str(i + 1): c for i, c in enumerate(LET)}; m['0'] = zero_letter
    else:
        m = {str(i): c for i, c in enumerate(LET)}; m['9'] = zero_letter
    return ''.join(m[d] for d in ct), st, k

def to_idx(s):
    return np.frombuffer(s.encode(), dtype=np.uint8).astype(np.int32) - 97

# ---------- checkerboard decoding + quadgram scoring ----------
import pickle as _pk
QL, QF = _pk.load(open('quadgrams_clean.pkl' if __import__('os').path.exists('quadgrams_clean.pkl')
                        else '/home/vin/bitcoin_puzzle/scratch/quadgrams_clean.pkl', 'rb'))

def board_tables(S=None, kind='atonesir'):
    """Return (single[10], esc[10] bool, double[10][10]) char tables (lowercase letters, '.', '/')."""
    single = [None] * 10; isesc = [False] * 10; double = [[None] * 10 for _ in range(10)]
    if kind == 'atonesir':
        enc, dec, esc = vic.vic_board(list(S))
        for code, ch in dec.items():
            if len(code) == 1: single[int(code)] = ch.lower()
            else: double[int(code[0])][int(code[1])] = ch.lower()
        for e in esc: isesc[int(e)] = True
    elif kind == 'p32S':  # Phase 3.2 alphabet with VIC S-line header: blanks at header positions 1 and 4
        hdr = list(S)
        top = ['f', None, 'u', 'b', None, 'c', 'd', 'o', 'r', 'a']
        escd = [hdr[1], hdr[4]]
        for j, l in enumerate(top):
            if l: single[hdr[j]] = l
        for e, row in zip(escd, ('/lethingky', 'mvpszjqwx.')):
            isesc[e] = True
            for j, l in enumerate(row): double[e][hdr[j]] = l
    elif kind == 'p32':   # solved Phase 3.2 board: escapes 1,4; columns in natural order
        sing = [d for d in range(10) if d not in (1, 4)]
        for d, l in zip(sing, 'fubcdora'): single[d] = l
        for j, l in enumerate('/lethingky'): double[1][j] = l
        for j, l in enumerate('mvpszjqwx.'): double[4][j] = l
        isesc[1] = isesc[4] = True
    return single, isesc, double

def cb_decode_digits(ds, tables):
    single, isesc, double = tables
    out = []; i = 0; n = len(ds)
    while i < n:
        d = ds[i]; i += 1
        if isesc[d]:
            if i >= n: break
            out.append(double[d][ds[i]]); i += 1
        else:
            out.append(single[d])
    return ''.join(out)

def qscore(t):
    t = ''.join(c for c in t if 'a' <= c <= 'z')
    if len(t) < 8: return QF
    L = QL; F = QF
    return sum(L.get(t[i:i + 4], F) for i in range(len(t) - 3)) / (len(t) - 3)

def letters_to_digit_list(u_idx, mapname):
    # u_idx: int array of letter indices 0..8; a1 -> digit idx+1, a0 -> idx
    return (u_idx + 1).tolist() if mapname == 'a1' else u_idx.tolist()
