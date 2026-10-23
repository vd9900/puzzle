# faed provenance: rank generative models by unigram profile likelihood (best digit->letter map incl. merges),
# calibrated by parametric bootstrap that includes source-text variability, plus posterior-predictive checks of the
# non-stationarity statistics (change point, w30 dispersion, pair-avoiding run) and lag-1 dependence.
import sys, re, random, itertools, json, math
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
import numpy as np
from collections import Counter
from common import FAED

NSIM = int(sys.argv[1]) if len(sys.argv) > 1 else 400
L = len(FAED); LET = 'abcdefghi'
rnd = random.Random(37); nrng = np.random.default_rng(37)
TXT = re.sub('[^A-Z]', '', open('/home/vin/bitcoin_puzzle/scratch/corpora/carroll_public_domain.txt').read().upper())
RAW = open('/home/vin/bitcoin_puzzle/scratch/corpora/carroll_public_domain.txt').read()
RAW = re.sub(r'\s+', ' ', RAW)

def counts9(s): c = Counter(s); return np.array([c.get(x, 0) for x in LET])
OBS = counts9(FAED)

# ---------- generators: return a digit string (symbols '0'-'9') of length n -------------
def board_p32():
    esc = ('1', '4'); singles = [d for d in '0123456789' if d not in esc]; b = {}
    for d, l in zip(singles, 'FUBCDORA'): b[l] = d
    for j, l in enumerate('/LETHINGKY'): b[l] = '1' + str(j)
    for j, l in enumerate('MVPSZJQWX.'): b[l] = '4' + str(j)
    return b
def board_atonesir():  # classic: top row ATONESIR in 8 cols, escapes 2,6
    esc = ('2', '6'); singles = [d for d in '0123456789' if d not in esc]; b = {}
    for d, l in zip(singles, 'ATONESIR'): b[l] = d
    for j, l in enumerate('BCDFGHJKLM'): b[l] = '2' + str(j)
    for j, l in enumerate('PQUVWXYZ./'): b[l] = '6' + str(j)
    return b
def board9(top='ESTONIA'):  # 9-column board over symbols 1..9, escapes '7' (g) and '9' (i)
    esc = ('7', '9'); singles = [d for d in '123456789' if d not in esc]; b = {}
    rest = [c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if c not in top and c != 'J']  # 18 letters, J->I
    for d, l in zip(singles, top): b[l] = d
    for j, l in enumerate(rest[:9]): b[l] = '7' + '123456789'[j]
    for j, l in enumerate(rest[9:]): b[l] = '9' + '123456789'[j]
    b['J'] = b['I']; return b
def text_stream(enc, n, src=TXT):
    st = []; i = rnd.randrange(len(src) - 5000); tot = 0
    while tot < n:
        c = enc.get(src[i]); i += 1
        if c: st.append(c); tot += len(c)
    return ''.join(st)[:n]
def uniform_digits(n, k=10): return ''.join(str(x) for x in nrng.integers(0, k, n))
def ascii_dec(n, mode):
    st = []; tot = 0; i = rnd.randrange(len(RAW) - 5000)
    while tot < n:
        ch = RAW[i]; i += 1
        if mode == 'lower3':
            if not ch.isalpha(): continue
            c = '%03d' % ord(ch.lower())
        elif mode == 'lowervar':
            if not ch.isalpha(): continue
            c = str(ord(ch.lower()))
        elif mode == 'printvar':
            if not (32 <= ord(ch) < 127): continue
            c = str(ord(ch))
        elif mode == 'upper2':
            if not ch.isalpha(): continue
            c = str(ord(ch.upper()))
        st.append(c); tot += len(c)
    return ''.join(st)[:n]
def numblock_mix(n, frac, board):  # checkerboard text whose plaintext contains ONE contiguous number block
    nb = int(round(frac * n)); pos = rnd.randrange(0, n - nb + 1)
    t = text_stream(board, n - nb); return t[:pos] + uniform_digits(nb) + t[pos:]
def transpose(s):  # random-key columnar transposition (key length 7..20)
    k = rnd.randint(7, 20); order = list(range(k)); rnd.shuffle(order)
    return ''.join(s[c::k] for c in order)

GENS = {
 'uniform10_merge': lambda n: uniform_digits(n, 10),
 'uniform9': lambda n: uniform_digits(n, 9),
 'P32board_english': lambda n: text_stream(board_p32(), n),
 'P32board_english_transposed': lambda n: transpose(text_stream(board_p32(), n)),
 'ATONESIR_english_transposed': lambda n: transpose(text_stream(board_atonesir(), n)),
 'board9_ESTONIA_g_i_transposed': lambda n: transpose(text_stream(board9(), n)),
 'board9_ESTONIA_g_i_plain': lambda n: text_stream(board9(), n),
 'ascii_lower3': lambda n: ascii_dec(n, 'lower3'),
 'ascii_lowervar': lambda n: ascii_dec(n, 'lowervar'),
 'ascii_printvar': lambda n: ascii_dec(n, 'printvar'),
 'ascii_upper2': lambda n: ascii_dec(n, 'upper2'),
}
for f in (0.3, 0.5, 0.7):
    GENS['P32_numblock%.1f' % f] = (lambda f: (lambda n: numblock_mix(n, f, board_p32())))(f)
    GENS['P32_numblock%.1f_transposed' % f] = (lambda f: (lambda n: transpose(numblock_mix(n, f, board_p32()))))(f)

for f in (0.3, 0.5):
    GENS['board9_numblock%.1f_plain' % f] = (lambda f: (lambda n: numblock_mix(n, f, board9())))(f)
    GENS['board9_numblock%.1f_transposed' % f] = (lambda f: (lambda n: transpose(numblock_mix(n, f, board9()))))(f)

# ---------- profile likelihood: best map from model symbols -> 9 letters ---------------
def merge_profiles(p):
    """all ways to reduce a symbol distribution to 9 classes by merging pairs / dropping near-empty symbols."""
    p = np.asarray(p, float); k = len(p); out = []
    if k == 9: return [np.sort(p)[::-1]]
    if k == 10:
        for i, j in itertools.combinations(range(10), 2):
            q = np.delete(p, j).copy(); q[i if i < j else i - 1] += p[j]; out.append(np.sort(q)[::-1])
        for j in range(10):  # drop symbol j (never emitted): renormalize
            q = np.delete(p, j); s = q.sum()
            if s > 0 and p[j] < 0.005: out.append(np.sort(q / s)[::-1])
    return out
def best_ll(counts, profiles):
    c = np.sort(counts)[::-1]; best = -1e18
    for q in profiles:
        q = np.maximum(q, 1e-12); v = float((c * np.log(q)).sum())
        if v > best: best = v
    return best
def sat_ll(counts):
    c = counts[counts > 0]; return float((c * np.log(c / c.sum())).sum())
def digit_dist(gen, n=200000):
    s = ''.join(gen(5000) for _ in range(n // 5000)); c = Counter(s)
    syms = '0123456789'; v = np.array([c.get(x, 0) for x in syms], float)
    if 'uniform9' in str(gen): pass
    return v / v.sum()
def best_map(p, counts):
    """explicit digit->letter map achieving best_ll (for converting sims to letters)."""
    p = np.asarray(p, float); syms = list('0123456789'); best = (-1e18, None)
    order_obs = [LET[i] for i in np.argsort(-counts, kind='stable')]
    cands = []
    for i, j in itertools.combinations(range(10), 2):
        groups = [[syms[t]] for t in range(10) if t != j]; gi = i if i < j else i - 1; groups[gi].append(syms[j])
        cands.append(groups)
    for j in range(10):
        if p[j] < 0.005: cands.append([[syms[t]] for t in range(10) if t != j])
    for groups in cands:
        q = np.array([sum(p[int(x)] for x in g) for g in groups]); q = q / q.sum()
        idx = np.argsort(-q, kind='stable'); qs = np.maximum(q[idx], 1e-12)
        v = float((np.sort(counts)[::-1] * np.log(qs)).sum())
        if v > best[0]:
            m = {}
            for rank, gidx in enumerate(idx):
                for x in groups[gidx]: m[x] = order_obs[rank]
            best = (v, m)
    return best

# ---------- non-stationarity / dependence statistics (label-invariant) ------------------
def onehot(s):
    a = np.frombuffer(s.encode(), dtype=np.uint8) - 97; M = np.zeros((len(s), 9)); M[np.arange(len(s)), a] = 1; return M
def cp_stat(s, mn=20):
    M = onehot(s); n = len(s); cs = np.cumsum(M, 0); tot = cs[-1]; best = 0
    for k in range(mn, n - mn):
        a = cs[k - 1]; b = tot - a
        ea = tot * k / n; eb = tot * (n - k) / n
        g = 2 * (np.where(a > 0, a * np.log(np.maximum(a, 1e-12) / np.maximum(ea, 1e-12)), 0).sum()
                 + np.where(b > 0, b * np.log(np.maximum(b, 1e-12) / np.maximum(eb, 1e-12)), 0).sum())
        best = max(best, g)
    return best
def wdisp(s, w=30):
    nw = len(s) // w; M = onehot(s[:nw * w]).reshape(nw, w, 9).sum(1); tot = M.sum(0)
    E = np.outer(np.full(nw, w), tot / tot.sum()); return float(((M - E) ** 2 / np.maximum(E, 1e-9)).sum())
def pairrun(s):
    c = Counter(s); n = len(s); best = 0
    for x, y in itertools.combinations(LET, 2):
        q = (c[x] + c[y]) / n
        if q == 0: continue
        run = mx = 0
        for ch in s:
            if ch == x or ch == y: run = 0
            else: run += 1; mx = max(mx, run)
        best = max(best, -mx * math.log(1 - q))
    return best
def lag1mi(s):
    a = np.frombuffer(s.encode(), dtype=np.uint8) - 97; T = np.zeros((9, 9))
    np.add.at(T, (a[:-1], a[1:]), 1); P = T / T.sum(); r = P.sum(1); c = P.sum(0)
    nz = P > 0; return float((P[nz] * np.log(P[nz] / np.outer(r, c)[nz])).sum())
def to_letters(d, m): return ''.join(m.get(x, '') for x in d)

if __name__ == '__main__':
    obs_stats = dict(cp=cp_stat(FAED), w30=wdisp(FAED), pairrun=pairrun(FAED), lag1mi=lag1mi(FAED))
    print('observed', {k: round(v, 3) for k, v in obs_stats.items()}, 'counts', dict(zip(LET, OBS.tolist())))
    SAT = sat_ll(OBS); res = {}
    names = sys.argv[2].split(',') if len(sys.argv) > 2 else list(GENS)
    for name in names:
        gen = GENS[name]
        p = digit_dist(gen)
        profs = merge_profiles(p)
        ll, m = best_map(p, OBS)
        G = 2 * (SAT - ll)
        Gs = []; st = {k: [] for k in obs_stats}
        for t in range(NSIM):
            d = gen(L + 40)
            s = to_letters(d, m)[:L]
            if len(s) < L: s = to_letters(gen(2 * L), m)[:L]
            cs = counts9(s); Gs.append(2 * (sat_ll(cs) - best_ll(cs, profs)))
            if t < min(NSIM, 300):
                st['cp'].append(cp_stat(s)); st['w30'].append(wdisp(s)); st['pairrun'].append(pairrun(s)); st['lag1mi'].append(lag1mi(s))
        pG = (1 + sum(g >= G for g in Gs)) / (1 + len(Gs))
        pst = {k: (1 + sum(v >= obs_stats[k] for v in st[k])) / (1 + len(st[k])) for k in st}
        res[name] = dict(ll=ll, G=G, pG=pG, p_cp=pst['cp'], p_w30=pst['w30'], p_pairrun=pst['pairrun'],
                         p_lag1mi=pst['lag1mi'], map=m, dist=[round(x, 4) for x in p])
        print('%-34s ll=%9.2f G=%7.2f pG=%.4f  p_cp=%.3f p_w30=%.3f p_pair=%.3f p_lag1=%.3f  map=%s' % (
            name, ll, G, pG, pst['cp'], pst['w30'], pst['pairrun'], pst['lag1mi'],
            ''.join(m.get(x, '-') for x in '0123456789')), flush=True)
    json.dump(dict(observed=obs_stats, sat_ll=SAT, models=res), open(
        '/home/vin/bitcoin_puzzle/scratch/c37/faed_provenance/models_%s.json' % (sys.argv[3] if len(sys.argv) > 3 else 'all'), 'w'), indent=1)
