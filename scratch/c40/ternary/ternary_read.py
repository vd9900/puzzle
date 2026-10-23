"""Cycle 40 ternary lens: each page letter a..i = one cell of a 3x3 matrix = 2 trits (row,col).
Regroup the trit stream into 3-trit symbols (27-alphabets: a1z26 with 0=space, a0z25 with 26=space) or 5/6-trit groups
(-> byte values), read, and score with the CLEAN Carroll quadgram model (c37/construction_forensics/quad_indep.py),
z against NCTRL shuffled-input controls (same reading applied to letter-shuffled input).
Self-verifying: planted English messages encoded through three different configurations must decode exactly and score high.
Family-wise calibration: max z over all readings for the real inputs vs the same max for K pseudo-observed control rows."""
import sys, json, math, hashlib
import numpy as np
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/construction_forensics')
from common import DBBI, FAED
import quad_indep as Q

OUT = '/home/vin/bitcoin_puzzle/scratch/c40/ternary/'
NCTRL = 400; KPSEUDO = 20
rng = np.random.default_rng(40)
QT = np.full(26 ** 4, Q.FLOOR)
for k, v in Q.LOGP.items():
    QT[((ord(k[0]) - 97) * 26 + ord(k[1]) - 97) * 26 * 26 + (ord(k[2]) - 97) * 26 + ord(k[3]) - 97] = v

L9 = 'abcdefghi'
R60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
R56 = 'difhccgihaihggegegehhehhfafdhffcdfcccgfeggecdcifffgigeea'
assert len(DBBI) == 91 and len(FAED) == 570 and len(R60) == 60 and len(R56) == 56
assert set(DBBI + FAED + R60 + R56) <= set(L9)
INPUTS = {'dbbi': DBBI, 'R60': R60, 'R61': R60 + 'e', 'R56': R56, 'faed': FAED}
INPUTS.update({k + '_rev': v[::-1] for k, v in list(INPUTS.items())})

def first_occ(s):
    o = []
    for c in s:
        if c in L9 and c not in o: o.append(c)
    return ''.join(o)
def keyed(w):
    k = first_occ(w); return k + ''.join(c for c in L9 if c not in k)
ORD = {'rowmajor': L9, 'dbbi_first': keyed(DBBI), 'faed_first': keyed(FAED),
       'matrixsumlist': keyed('matrixsumlist'), 'salphaseion': keyed('salphaseion')}
assert ORD['dbbi_first'] == 'dbifhcega', ORD['dbbi_first']
for k in list(ORD):  # inverse permutation variant: letter L9[j] -> cell L9.index(o[j])
    inv = ''.join(sorted(L9, key=lambda c: L9.index(ORD[k][L9.index(c)])))
    if inv not in ORD.values(): ORD[k + '_inv'] = inv
def cellmap(order):  # letter index 0..8 -> cell 0..8 ; order[k] sits in cell k (matrix filled row-major)
    return np.array([order.index(c) for c in L9])

def trits(X, order, to):  # X (R,n) letter idx -> t1,t2 (R,n)
    cell = cellmap(order)[X]; r, c = cell // 3, cell % 3
    return (r, c) if to == 'rc' else (c, r)
def stream(t1, t2, sv):
    R, n = t1.shape
    P = np.stack([t1, t2], 2).reshape(R, 2 * n)
    if sv == 'plain': return P
    if sv == 'rows_then_cols': return np.concatenate([t1, t2], 1)
    if sv == 'halves_interleave': return np.stack([P[:, :n], P[:, n:]], 2).reshape(R, 2 * n)
def group(S, g, off, en):
    S = S[:, off:]; m = S.shape[1] // g
    w = 3 ** np.arange(g)[::-1] if en == 'big' else 3 ** np.arange(g)
    return S[:, :m * g].reshape(S.shape[0], m, g) @ w
def alpha(V, a):  # -> symbols 0..25 letters, 26 = space / non-letter
    if a == 'a1z26_sp0': return np.where(V == 0, 26, V - 1)
    if a == 'a0z25_sp26': return V.copy()
    if a == 'bytes':
        return np.where((V >= 97) & (V <= 122), V - 97, np.where((V >= 65) & (V <= 90), V - 65, 26))
def qscore(sym):
    R, m = sym.shape
    isl = sym < 26; cnt = isl.sum(1)
    comp = np.take_along_axis(sym, np.argsort(~isl, axis=1, kind='stable'), 1)
    if m < 4: return np.full(R, np.nan), cnt
    idx = ((comp[:, :-3] * 26 + comp[:, 1:-2]) * 26 + comp[:, 2:-1]) * 26 + comp[:, 3:]
    valid = np.arange(m - 3)[None, :] < (cnt - 3)[:, None]
    sc = np.where(valid, QT[np.where(valid, idx, 0)], 0).sum(1) / np.maximum(cnt - 3, 1)
    sc = sc.astype(float); sc[cnt < 8] = np.nan   # too few letters to score
    return sc, cnt
def text(symrow, V=None, a=None):
    if a == 'bytes': return bytes(int(v) for v in V if v < 256).decode('latin1').encode('unicode_escape').decode()
    return ''.join(' ' if s == 26 else chr(97 + s) for s in symrow)

CONFIGS = []
for on in ORD:
    for to in ('rc', 'cr'):
        for sv in ('plain', 'rows_then_cols', 'halves_interleave'):
            for g in (3, 5, 6):
                for off in range(g):
                    for en in ('big', 'little'):
                        for a in (('a1z26_sp0', 'a0z25_sp26') if g == 3 else ('bytes',)):
                            CONFIGS.append((on, to, sv, g, off, en, a))

def read(X, cfg):
    on, to, sv, g, off, en, a = cfg
    t1, t2 = trits(X, ORD[on], to)
    V = group(stream(t1, t2, sv), g, off, en)
    return V, alpha(V, a)

# ---------- planted self-tests (encode = exact inverse of the reading) ----------
def encode(msg, cfg):
    on, to, sv, g, off, en, a = cfg
    if a == 'a1z26_sp0': vals = [0 if ch == ' ' else ord(ch) - 96 for ch in msg]
    elif a == 'a0z25_sp26': vals = [26 if ch == ' ' else ord(ch) - 97 for ch in msg]
    else: vals = list(msg.encode())
    S = [0] * off
    for v in vals:
        d = [(v // 3 ** j) % 3 for j in range(g)]
        S += d[::-1] if en == 'big' else d
    if len(S) % 2: S.append(0)
    S = np.array(S); n = len(S) // 2
    if sv == 'plain': t1, t2 = S[0::2], S[1::2]
    elif sv == 'rows_then_cols': t1, t2 = S[:n], S[n:]
    else: P = np.concatenate([S[0::2], S[1::2]]); t1, t2 = P[0::2], P[1::2]
    r, c = (t1, t2) if to == 'rc' else (t2, t1)
    order = ORD[on]
    return ''.join(order[3 * ri + ci] for ri, ci in zip(r, c))
PLANT_MSG = 'meet me at the old mill when the bells ring and bring the second half of the key with you'
PLANTS = [('rowmajor', 'rc', 'plain', 3, 0, 'big', 'a1z26_sp0'),
          ('dbbi_first', 'cr', 'rows_then_cols', 3, 1, 'little', 'a0z25_sp26'),
          ('salphaseion', 'rc', 'halves_interleave', 5, 2, 'big', 'bytes')]
plant_inputs = {}
for i, pc in enumerate(PLANTS):
    s = encode(PLANT_MSG, pc)
    X = np.array([[L9.index(c) for c in s]])
    V, sym = read(X, pc)
    got = text(sym[0], V[0], pc[6])
    ok = PLANT_MSG in got.replace('\\x00', '') or PLANT_MSG.replace(' ', '') in got.replace(' ', '')
    print('PLANT', i, pc, 'len', len(s), 'decodes_exactly', ok, '|', got[:60])
    assert ok
    plant_inputs['PLANT%d' % i] = s

# ---------- main run ----------
def run(inputs, tag):
    rows = []
    for nm, s in inputs.items():
        x = np.array([L9.index(c) for c in s])
        X = np.vstack([x] + [rng.permutation(x) for _ in range(NCTRL)])
        seen = set()
        for cfg in CONFIGS:
            V, sym = read(X, cfg)
            key = hashlib.md5(sym[0].tobytes() + cfg[6].encode()).hexdigest()
            if key in seen: continue
            seen.add(key)
            sc, cnt = qscore(sym)
            pr = ((V >= 32) & (V <= 126)).mean(1) if cfg[6] == 'bytes' else None
            ctrl = sc[1:]; okc = ~np.isnan(ctrl)
            if np.isnan(sc[0]) or okc.sum() < 200: z = float('nan'); pz = np.full(KPSEUDO, np.nan)
            else:
                mu, sd = ctrl[okc].mean(), ctrl[okc].std()
                z = (sc[0] - mu) / sd; pz = (sc[1:1 + KPSEUDO] - mu) / sd
            p_emp = (1 + int((ctrl[okc] >= sc[0]).sum())) / (1 + int(okc.sum())) if not np.isnan(sc[0]) else float('nan')
            row = dict(input=nm, cfg=cfg, n_sym=int(sym.shape[1]), letters=int(cnt[0]), q=float(sc[0]), z=float(z),
                       p_emp=p_emp, pseudo_z=[float(t) for t in pz], text=text(sym[0], V[0], cfg[6])[:200])
            if pr is not None:
                row['printable'] = float(pr[0]); row['printable_z'] = float((pr[0] - pr[1:].mean()) / (pr[1:].std() + 1e-12))
                row['printable_ctrl_max'] = float(pr[1:].max())
            rows.append(row)
    return rows

prow = run(plant_inputs, 'plant')
for i, pc in enumerate(PLANTS):
    r = [r for r in prow if r['input'] == 'PLANT%d' % i and tuple(r['cfg']) == pc][0]
    print('PLANT', i, 'z=%.1f p_emp=%.4f' % (r['z'], r['p_emp']))
    assert r['z'] > 5
rows = run(INPUTS, 'real')
ok = [r for r in rows if not math.isnan(r['z'])]
ok.sort(key=lambda r: -r['z'])
print('readings', len(rows), 'scored', len(ok), 'distinct configs', len(CONFIGS))
# family-wise: max z per input family for observed vs pseudo-observed control rows
fam = {}
for r in ok:
    f = r['input']
    fam.setdefault(f, {'obs': -9e9, 'pseudo': [-9e9] * KPSEUDO})
    fam[f]['obs'] = max(fam[f]['obs'], r['z'])
    fam[f]['pseudo'] = [max(a, b) if not math.isnan(b) else a for a, b in zip(fam[f]['pseudo'], r['pseudo_z'])]
allmax_obs = max(v['obs'] for v in fam.values())
allmax_pseudo = [max(v['pseudo'][k] for v in fam.values()) for k in range(KPSEUDO)]
print('GLOBAL max z observed %.2f ; pseudo-observed max z: median %.2f range %.2f..%.2f ; frac pseudo >= obs %.2f' % (
    allmax_obs, float(np.median(allmax_pseudo)), min(allmax_pseudo), max(allmax_pseudo),
    float(np.mean([p >= allmax_obs for p in allmax_pseudo]))))
for f, v in fam.items():
    print('  %-9s max z %.2f | pseudo max median %.2f, max %.2f' % (f, v['obs'], np.median(v['pseudo']), max(v['pseudo'])))
print('TOP 12 by z:')
for r in ok[:12]:
    print('  z=%.2f p=%.4f q=%.3f %s %s n=%d | %s' % (r['z'], r['p_emp'], r['q'], r['input'], r['cfg'], r['n_sym'], r['text'][:90]))
by = [r for r in rows if 'printable' in r]
by.sort(key=lambda r: -r['printable'])
print('BYTES: top printable fractions (control max shown):')
for r in by[:8]:
    print('  pr=%.3f (ctrl max %.3f, z %.2f) %s %s | %s' % (r['printable'], r['printable_ctrl_max'], r['printable_z'], r['input'], r['cfg'], r['text'][:70]))
json.dump(dict(n_ctrl=NCTRL, configs=len(CONFIGS), orders=ORD, readings=len(rows), top=ok[:60],
               bytes_top=by[:30], family=fam, global_max_obs=allmax_obs, global_max_pseudo=allmax_pseudo),
          open(OUT + 'ternary_read_results.json', 'w'), indent=1, default=str)
