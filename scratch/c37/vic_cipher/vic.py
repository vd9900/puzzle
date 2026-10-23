# Full VIC cipher (Hayhanen) per Wikipedia "VIC cipher" + quadibloc pp1324 worked example.
# Validated by selftest() on both published vectors.
import re

def seq_rank_key(vals):
    """vals: list of comparable values; returns list of ranks 1..n (ties left to right)."""
    order = sorted(range(len(vals)), key=lambda i: (vals[i], i))
    r = [0] * len(vals)
    for k, i in enumerate(order):
        r[i] = k + 1
    return r

def seq_letters(s):
    """VIC sequencing of a letter string; returns digits as ints (10 -> 0) for len<=10, ranks otherwise."""
    r = seq_rank_key(list(s))
    return [x % 10 for x in r] if len(s) <= 10 else r

def dval(d):
    return 10 if d == 0 else d

def seq_digits(ds):
    r = seq_rank_key([dval(d) for d in ds])
    return [x % 10 for x in r] if len(ds) <= 10 else r

def col_order(keydigits, zero_high=True):
    """order in which columns are read: sort by (value with 0=10, position)."""
    if zero_high:
        return sorted(range(len(keydigits)), key=lambda i: (dval(keydigits[i]), i))
    return sorted(range(len(keydigits)), key=lambda i: (keydigits[i], i))

def chain(seed, n):
    """chain addition: returns seed + n generated digits."""
    s = list(seed)
    i = 0
    while len(s) < len(seed) + n:
        s.append((s[i] + s[i + 1]) % 10)
        i += 1
    return s

def sub10(a, b): return [(x - y) % 10 for x, y in zip(a, b)]
def add10(a, b): return [(x + y) % 10 for x, y in zip(a, b)]

def digits(s): return [int(c) for c in s]
def dstr(ds): return ''.join(str(d) for d in ds)

def phrase20(phrase):
    p = re.sub('[^A-Za-z]', '', phrase).upper()
    if len(p) < 20:
        raise ValueError('phrase < 20 letters')
    return p[:20]

def derive(phrase, date, pnum, keygroup, zero_as_ten_width=False):
    """phrase: text (>=20 letters); date: digit string (>=5); pnum int; keygroup 5-digit string.
    Returns dict of all lines."""
    A = digits(keygroup)
    B = digits(date[:5])
    C = sub10(A, B)
    D = phrase20(phrase)
    E1 = seq_letters(D[:10]); E2 = seq_letters(D[10:])
    F1 = chain(C, 5)
    G = add10(E1, F1)
    # encode: digit d -> E2[pos], pos(1)=0..pos(0)=9
    H = [E2[(d - 1) % 10] for d in G]
    J = seq_digits(H)
    blk = chain(H, 50)[10:]
    K, L, M, N, P = [blk[i * 10:(i + 1) * 10] for i in range(5)]
    # last two non-equal digits of P
    last = P[-1]; i = 8
    while i >= 0 and P[i] == last: i -= 1
    prev = P[i]
    if zero_as_ten_width:
        wa, wb = pnum + dval(prev), pnum + dval(last)
    else:
        wa, wb = pnum + prev, pnum + last
    # read block by columns in order of J
    rows = [K, L, M, N, P]
    stream = []
    for j in col_order(J):
        for r in rows: stream.append(r[j])
    Q = stream[:wa]; R = stream[wa:wa + wb]
    S = seq_digits(P)
    return dict(A=A, B=B, C=C, D=D, E1=E1, E2=E2, F1=F1, G=G, H=H, J=J, K=K, L=L, M=M, N=N, P=P,
                Q=Q, R=R, S=S, wa=wa, wb=wb, H_str=dstr(H))

def derive_from_H(H, pnum):
    """Everything downstream of line H (H: list of 10 digits)."""
    J = seq_digits(H)
    blk = chain(H, 50)[10:]
    rows = [blk[i * 10:(i + 1) * 10] for i in range(5)]
    P = rows[4]
    last = P[-1]; i = 8
    while i >= 0 and P[i] == last: i -= 1
    prev = P[i]
    wa, wb = pnum + prev, pnum + last
    stream = []
    for j in col_order(J):
        for r in rows: stream.append(r[j])
    return stream[:wa], stream[wa:wa + wb], seq_digits(P)

# ---------------- checkerboard ----------------
def vic_board(S, top='AT ONE SIR', rows=('BCDFGHJKLM', 'PQUVWXYZ./')):
    """S: 10 header digits. top: 10-char row with 2 blanks. Returns enc dict letter->digitstring, dec dict."""
    top = top.replace(' ', '_') if len(top) == 10 else None
    assert top is not None and len(top) == 10
    esc = [S[i] for i, ch in enumerate(top) if ch == '_']
    enc = {}
    for i, ch in enumerate(top):
        if ch != '_': enc[ch] = str(S[i])
    for e, row in zip(esc, rows):
        for i, ch in enumerate(row): enc[ch] = str(e) + str(S[i])
    dec = {v: k for k, v in enc.items()}
    return enc, dec, [str(e) for e in esc]

def cb_encode(text, enc):
    return ''.join(enc[c] for c in text)

def cb_decode(ds, dec, esc):
    out = []; i = 0
    while i < len(ds):
        c = ds[i]; i += 1
        if c in esc:
            if i >= len(ds): out.append('?'); break
            c += ds[i]; i += 1
        out.append(dec.get(c, '?'))
    return ''.join(out)

# ---------------- transpositions ----------------
def columnar_enc(s, key):
    w = len(key); order = col_order(key)
    return ''.join(s[j::w] for j in order)

def columnar_perm(n, key):
    """perm such that ct[k] = pt[perm[k]]"""
    w = len(key); order = col_order(key)
    perm = []
    for j in order:
        perm.extend(range(j, n, w))
    return perm

def columnar_dec(ct, key):
    perm = columnar_perm(len(ct), key)
    pt = [None] * len(ct)
    for k, p in enumerate(perm): pt[p] = ct[k]
    return ''.join(pt)

def disrupted_layout(n, key, gap=1):
    """returns (cells_plain, cells_tri): lists of (row, col) in row-major fill order."""
    w = len(key); order = col_order(key)
    nrows = (n + w - 1) // w
    exists = lambda r, c: r * w + c < n
    tri = set()
    r = 0; t = 0
    while r < nrows and t < len(order):
        c0 = order[t]
        for k in range(w - c0):
            rr = r + k
            if rr >= nrows: break
            for c in range(c0 + k, w): tri.add((rr, c))
        r = r + (w - c0) + gap
        t += 1
    plain = [(r, c) for r in range(nrows) for c in range(w) if exists(r, c) and (r, c) not in tri]
    tric = [(r, c) for r in range(nrows) for c in range(w) if exists(r, c) and (r, c) in tri]
    return plain, tric

def disrupted_perm(n, key, gap=1):
    """perm such that ct[k] = pt[perm[k]]"""
    w = len(key); order = col_order(key)
    plain, tric = disrupted_layout(n, key, gap)
    pos = {}
    for idx, cell in enumerate(plain + tric): pos[cell] = idx
    perm = []
    nrows = (n + w - 1) // w
    for j in order:
        for r in range(nrows):
            if (r, j) in pos: perm.append(pos[(r, j)])
    return perm

def disrupted_enc(s, key, gap=1):
    perm = disrupted_perm(len(s), key, gap)
    return ''.join(s[p] for p in perm)

def disrupted_dec(ct, key, gap=1):
    perm = disrupted_perm(len(ct), key, gap)
    pt = [None] * len(ct)
    for k, p in enumerate(perm): pt[p] = ct[k]
    return ''.join(pt)

# ---------------- full system ----------------
def encrypt(plaintext, phrase, date, pnum, keygroup, top='AT ONE SIR', null='0', gap=1, pad_before=True):
    k = derive(phrase, date, pnum, keygroup)
    enc, dec, esc = vic_board(k['S'], top)
    st = cb_encode(re.sub('[^A-Z./]', '', plaintext.upper()), enc)
    if pad_before:
        while len(st) % 5: st += null
    t1 = columnar_enc(st, k['Q'])
    while len(t1) % 5: t1 += null
    t2 = disrupted_enc(t1, k['R'], gap)
    groups = [t2[i:i + 5] for i in range(0, len(t2), 5)]
    d6 = int(date[5]) if len(date) > 5 else 0
    pos = len(groups) - d6 + 1 if d6 else len(groups)
    groups.insert(pos, keygroup)
    return ' '.join(groups), dict(keys=k, st=st, t1=t1, t2=t2)

def decrypt(ct, phrase, date, pnum, top='AT ONE SIR', gap=1, msglen=None):
    groups = ct.split()
    d6 = int(date[5]) if len(date) > 5 else 0
    pos = len(groups) - d6 if d6 else len(groups) - 1
    kg = groups.pop(pos)
    k = derive(phrase, date, pnum, kg)
    t2 = ''.join(groups)
    t1 = disrupted_dec(t2, k['R'], gap)
    if msglen is not None: t1 = t1[:msglen]
    st = None
    # strip nulls: try 0..4 trailing nulls; return all
    outs = []
    for nn in range(0, 5):
        body = t1[:len(t1) - nn] if nn else t1
        st = columnar_dec(body, k['Q'])
        enc, dec, esc = vic_board(k['S'], top)
        outs.append((nn, st, cb_decode(st, dec, esc)))
    return kg, k, outs

def selftest(verbose=True):
    # Wikipedia key derivation vector
    k = derive('Twas the night before Christmas', '139195', 6, '72401')
    exp = dict(C='69592', E1='8017942653', E2='6013589427', F1='6959254417', G='4966196060', H='3288628787',
               J='3178429506', K='5064805552', L='5602850077', M='1620350748', N='7823857125', P='5051328370',
               Q='0668005552551', R='758838', S='5961328470')
    for key, v in exp.items():
        assert dstr(k[key]) == v, (key, dstr(k[key]), v)
    assert k['wa'] == 13 and k['wb'] == 6
    enc, dec, esc = vic_board(k['S'])
    assert enc['A'] == '5' and enc['T'] == '9' and enc['O'] == '1' and enc['R'] == '0' and enc['B'] == '65' and enc['/'] == '80', enc
    # quadibloc full vector
    pt = ('We are pleased to hear of your success in establishing your false identity. You will be sent some money '
          'to cover expenses within a month.')
    pt_letters = re.sub('[^A-Z]', '', pt.upper())
    k = derive('I dream of Jeannie with t', '741776', 8, '77651')
    assert dstr(k['C']) == '03584' and dstr(k['E1']) == '6203189574' and dstr(k['E2']) == '1674205839'
    assert dstr(k['G']) == '6551517891' and dstr(k['H']) == '0221215831', dstr(k['H'])
    assert dstr(k['P']) == '1204339669' and dstr(k['S']) == '1205348679'
    assert k['wa'] == 14 and k['wb'] == 17
    assert dstr(k['Q']) == '36534693233928' and dstr(k['R']) == '94735236270398134', (dstr(k['Q']), dstr(k['R']))
    enc, dec, esc = vic_board(k['S'])
    st = cb_encode(pt_letters, enc)
    exp_st = ('834194810741640025044195058858096800202466734621010776047303'
              '88580905107647004327288885808370707014643265094095348825025'
              '854948481436468372047310953204')
    assert st == exp_st, st
    t1 = columnar_enc(st, k['Q']) + '9'
    exp_t1 = ('09200274534 6860181384 80577786883 15963702539 11018309880 75079700479 4027027992 90628086065 '
              '42040483240 30833654811 44818035243 4864084447 84005470562 1546580540').replace(' ', '')
    # quadibloc appends the null to the message before transposition? check both
    t1b = columnar_enc(st + '9', k['Q'])
    assert t1 == exp_t1 or t1b == exp_t1, (t1, t1b, exp_t1)
    which = 'after' if t1 == exp_t1 else 'before'
    t1 = exp_t1
    t2 = disrupted_enc(t1, k['R'])
    exp_t2 = ('36178054 289959253 507014400 011342004 746845842 675048425 03100846 918177284 83603475 035007668 '
              '483882424 283890960 350713758 689914050 008042900 873786014 472544860').replace(' ', '')
    assert t2 == exp_t2, (t2, exp_t2)
    full, info = encrypt(pt_letters, 'I dream of Jeannie with t', '741776', 8, '77651', null='9', pad_before=(which == 'before'))
    exp_full = ('36178 05428 99592 53507 01440 00113 42004 74684 58426 75048 42503 10084 69181 77284 83603 47503 '
                '50076 68483 88242 42838 90960 35071 37586 89914 05000 77651 80429 00873 78601 44725 44860')
    assert full == exp_full, (full, exp_full)
    kg, kk, outs = decrypt(exp_full, 'I dream of Jeannie with t', '741776', 8)
    assert kg == '77651'
    dec_ok = [o for o in outs if o[2].startswith(pt_letters)]
    assert dec_ok, outs
    # inverse consistency on random data
    import random
    rnd = random.Random(5)
    for _ in range(200):
        n = rnd.randint(20, 600); w = rnd.randint(2, 29)
        key = [rnd.randrange(10) for _ in range(w)]
        s = ''.join(rnd.choice('0123456789') for _ in range(n))
        assert disrupted_dec(disrupted_enc(s, key), key) == s
        assert columnar_dec(columnar_enc(s, key), key) == s
        p = disrupted_perm(n, key); assert sorted(p) == list(range(n))
    if verbose:
        print('VIC selftest OK: Wikipedia key-derivation lines A..S, quadibloc full vector (null', which,
              'transposition), decrypt recovers plaintext; disrupted/columnar inverses OK')
    return True

if __name__ == '__main__':
    selftest()
