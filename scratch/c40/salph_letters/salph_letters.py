"""Cycle 40 / salph_letters: does mapping the page's 9 symbols a..i onto the 9 distinct letters of the heading
'SalPhaseIon' (or 'Cosmic Duality') produce readable text?

Deterministic maps (several orders) are applied to dbbi, R60, R61, R56, faed (+ reversals) and to dbbi/faed letters at
square positions. Each output is scored with
  * the clean Carroll-only quadgram model (c37/construction_forensics/quad_indep.py), mean log10 per quadgram;
  * dictionary segmentation coverage (fraction of letters covered by words of length >=3 / >=4 whose letters all lie in
    the map's target alphabet; words from /usr/share/dict/words + puzzle texts);
  * longest dictionary word found.
Each (map family, text) gets 300 seeded random-permutation controls from the SAME family (random bijections onto the
same 9 letters, or random arrangements of the same multiset for positional maps).
Self-tests: data derivations are asserted; planted English (only target letters, encoded through the inverse map) must
be detected; a shuffled-dbbi negative control is reported.
Run: python3 salph_letters.py  -> stdout + results.json
"""
import sys, re, json, random, statistics
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/construction_forensics')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from common import DBBI, FAED
from quad_indep import LOGP, FLOOR
import common_dc  # runs asserts: R60/R61 = dbbi minus prime-position markers (83/84-token segmentations)

OUT = '/home/vin/bitcoin_puzzle/scratch/c40/salph_letters/results.json'
NCTRL = 300
SRC9 = 'abcdefghi'

# ---------------------------------------------------------------- texts (self-verifying)
R60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
R61 = R60 + 'e'
assert common_dc.R60 == R60 and common_dc.R61 == R61


def res56(s):
    r = []; i = 0
    while i < len(s):
        if s[i] == 'b': i += 2 if (i + 1 < len(s) and s[i + 1] == 'e') else 1
        else: r.append(s[i]); i += 1
    return ''.join(r)


R56 = res56(DBBI)
assert len(DBBI) == 91 and len(FAED) == 570 and len(R56) == 56
assert DBBI.startswith('dbbi') and FAED.startswith('faed') and set(DBBI) | set(FAED) <= set(SRC9)
sq1 = lambda s: ''.join(s[k * k - 1] for k in range(1, int(len(s) ** .5) + 1))       # 1-based positions 1,4,9,...
sq0 = lambda s: ''.join(s[k * k] for k in range(0, int((len(s) - 1) ** .5) + 1))     # 0-based indices 0,1,4,9,...
TEXTS = {}
for k, v in (('dbbi', DBBI), ('R60', R60), ('R61', R61), ('R56', R56), ('faed', FAED)):
    TEXTS[k] = v; TEXTS[k + '_rev'] = v[::-1]
for k, v in (('dbbi', DBBI), ('faed', FAED)):
    TEXTS[k + '_sq1'] = sq1(v); TEXTS[k + '_sq0'] = sq0(v)
assert len(TEXTS['dbbi_sq1']) == 9 and len(TEXTS['faed_sq1']) == 23

# ---------------------------------------------------------------- maps
H = 'SalPhaseIon'


def first_occ(w):
    out = []
    for c in w.lower():
        if c.isalpha() and c not in out: out.append(c)
    return out


fo = first_occ(H)
assert ''.join(fo) == 'salpheion' and len(fo) == 9
assert dict(zip(SRC9, fo)) == dict(a='s', b='a', c='l', d='p', e='h', f='e', g='i', h='o', i='n')  # community proposal
caps_pos = [i + 1 for i, c in enumerate(H) if c.isupper()]
assert caps_pos == [1, 4, 9] and all(int(p ** .5) ** 2 == p for p in caps_pos)
caps = [H[p - 1].lower() for p in caps_pos]                         # s p i
capsfirst = caps + [c for c in fo if c not in caps]                 # s p i a l h e o n
lower_d = first_occ(''.join(c for c in H if c.islower()))
lowerfirst = lower_d + [c for c in caps if c not in lower_d]        # a l h s e o n p i
lastocc = sorted(fo, key=lambda c: max(i for i, x in enumerate(H.lower()) if x == c))   # l p h a s e i o n
assert ''.join(lastocc) == H[-9:].lower()                           # == the last 9 chars 'lPhaseIon'
revword = first_occ(H[::-1])                                         # n o i e s a h p l
alpha = sorted(fo)                                                   # a e h i l n o p s
SAL = {'first_occ': fo, 'first_occ_rev': fo[::-1], 'alpha': alpha, 'alpha_rev': alpha[::-1],
       'capsfirst_SPI': capsfirst, 'capsfirst_rev': capsfirst[::-1], 'lowerfirst_then_PI': lowerfirst,
       'last_occ(=last9 lPhaseIon)': lastocc, 'last_occ_rev': lastocc[::-1], 'word_reversed_first_occ': revword}
for v in SAL.values(): assert sorted(v) == alpha
# positional: a..i -> first 9 characters 'SalPhaseI' (capitals exactly at 1,4,9), non-injective
POS9 = list(H[:9].lower())
assert ''.join(POS9) == 'salphasei'
SALPOS = {'pos_first9_SalPhaseI': POS9, 'pos_first9_rev': POS9[::-1]}
# Cosmic Duality: 11 distinct letters (premise of '9 letters' fails); use first 9 distinct and first 9 characters
CD = 'CosmicDuality'
cd_fo = first_occ(CD)
assert len(cd_fo) == 11
COS = {'cd_first9_distinct': cd_fo[:9], 'cd_first9_distinct_rev': cd_fo[:9][::-1], 'cd_alpha9': sorted(cd_fo[:9])}
COS2 = {'cd_last9_distinct': cd_fo[-9:], 'cd_last9_distinct_rev': cd_fo[-9:][::-1]}
COSPOS = {'cd_pos_first9_CosmicDua': list(CD[:9].lower()), 'cd_pos_first9_rev': list(CD[:9].lower())[::-1]}
FAMILIES = {'SAL_bijection': SAL, 'SAL_positional': SALPOS, 'COS_bijection_first9': COS, 'COS_bijection_last9': COS2,
            'COS_positional': COSPOS}

# ---------------------------------------------------------------- word list
dict_words = set()
for line in open('/usr/share/dict/words', encoding='utf-8', errors='ignore'):
    w = line.strip()
    if w.isalpha() and w.isascii() and w.islower(): dict_words.add(w)
beau = re.sub('[^a-z]', '', open('/home/vin/bitcoin_puzzle/research/artifacts/phase32-beaufort.txt').read().lower())
seg = open('/home/vin/bitcoin_puzzle/scratch/speech32_words.txt').read().lower()
assert re.sub('[^a-z]', '', seg) == beau     # segmented beaufort text is exactly the artifact
puzzle_words = set(re.findall('[a-z]+', seg))
for f in ('research/artifacts/phase2.txt', 'research/artifacts/phase3.txt', 'research/artifacts/phase32.txt',
          'scratch/corpora/puzzle_texts.txt'):
    puzzle_words |= set(re.findall('[a-z]+', open('/home/vin/bitcoin_puzzle/' + f, errors='ignore').read().lower()))
puzzle_words |= {'salphaseion', 'salphase', 'phase', 'ion', 'cosmic', 'duality'}
ALLW = {w for w in dict_words | puzzle_words if len(w) >= 3}


def wordsets(alphabet):
    al = set(alphabet); by = {}
    for w in ALLW:
        if set(w) <= al: by.setdefault(len(w), set()).add(w)
    return by


# ---------------------------------------------------------------- scoring
def quad(s):
    if len(s) < 4: return FLOOR
    return sum(LOGP.get(s[i:i + 4], FLOOR) for i in range(len(s) - 3)) / (len(s) - 3)


def cover(s, by, minL):
    n = len(s); best = [0] * (n + 1); back = [None] * (n + 1); maxw = 0; maxL = max(by) if by else 0
    for i in range(1, n + 1):
        b = best[i - 1]; bk = None
        for L in range(minL, min(maxL, i) + 1):
            ws = by.get(L)
            if ws and s[i - L:i] in ws:
                if L > maxw: maxw = L
                v = best[i - L] + L
                if v > b: b = v; bk = L
        best[i] = b; back[i] = bk
    return best[n] / max(1, n), maxw, back


def seg_words(s, back):
    out = []; i = len(s)
    while i > 0:
        L = back[i]
        if L: out.append(s[i - L:i]); i -= L
        else: i -= 1
    return out[::-1]


def stats(s, by):
    c3, mw, _ = cover(s, by, 3)
    c4, _, _ = cover(s, by, 4)
    return {'quad': quad(s), 'cov3': c3, 'cov4': c4, 'maxword': mw}


STATS = ('quad', 'cov3', 'cov4', 'maxword')


def apply(m, s):
    return s.translate(str.maketrans(SRC9, ''.join(m)))


def controls(target, n, seed):
    rng = random.Random(seed); out = []
    for _ in range(n):
        t = list(target); rng.shuffle(t); out.append(t)
    return out


def compare(x, ctrl):
    mu = statistics.mean(ctrl); sd = statistics.pstdev(ctrl) or 1e-9
    return (x - mu) / sd, (1 + sum(c >= x for c in ctrl)) / (len(ctrl) + 1)


# ---------------------------------------------------------------- self-tests (planted positives)
PLANT = ('alonelionsleepsonaplainsheseeshisnosealishinesaspoonhehopessheisinpainhenapsinapale'
         'pinshopnosheshallsellapplesashelpsaninsanelionaspensionsnailspoilsapianoalone')
PLANT = ''.join(c for c in PLANT if c in set(fo))   # keep only target letters (drops the 'k','m' if any)
assert set(PLANT) <= set(fo)
by_sal = wordsets(fo)
inv = {v: k for k, v in zip(SRC9, fo)}
ctrl_sal = controls(fo, NCTRL, 4001)
selftest = {}
for name, plain in (('plant91', PLANT[:91]), ('plant60', PLANT[:60]), ('plant23', PLANT[:23]), ('plant9', PLANT[:9])):
    cipher = ''.join(inv[c] for c in plain)
    assert apply(fo, cipher) == plain
    st = stats(plain, by_sal); cs = [stats(apply(m, cipher), by_sal) for m in ctrl_sal]
    selftest[name] = {k: compare(st[k], [c[k] for c in cs]) for k in STATS}
    selftest[name]['values'] = st
rng = random.Random(7); shuf = list(DBBI); rng.shuffle(shuf); shuf = ''.join(shuf)
st = stats(apply(fo, shuf), by_sal); cs = [stats(apply(m, shuf), by_sal) for m in ctrl_sal]
selftest['neg_shuffled_dbbi'] = {k: compare(st[k], [c[k] for c in cs]) for k in STATS}
print('SELF-TEST (z, p) planted English encoded by inverse first_occ map, vs 300 random bijection controls:')
for k, v in selftest.items():
    print(f'  {k:18s}', '  '.join(f'{s}: z={v[s][0]:+.2f} p={v[s][1]:.4f}' for s in STATS))
assert selftest['plant91']['quad'][0] > 3 and selftest['plant91']['cov3'][1] <= 2 / (NCTRL + 1)
assert selftest['plant60']['quad'][0] > 3 and selftest['plant60']['cov3'][1] <= 2 / (NCTRL + 1)

# ---------------------------------------------------------------- main run
results = {'n_controls': NCTRL, 'texts': {k: v for k, v in TEXTS.items()}, 'families': {}, 'selftest': selftest}
cells = []
for fi, (fam, maps) in enumerate(FAMILIES.items()):
    target = next(iter(maps.values()))
    by = wordsets(set(target))
    ctrl = controls(target, NCTRL, 1000 + fi)
    ctrl_stats = {t: [stats(apply(m, s), by) for m in ctrl] for t, s in TEXTS.items()}
    famres = {'target_letters': ''.join(sorted(set(target))), 'n_words_ge3': sum(len(v) for v in by.values()),
              'maps': {}}
    # null for 'max z over the 10 non-square texts' for a single map (controls vs their own distribution)
    for mname, m in maps.items():
        assert sorted(m) == sorted(target)
        mres = {'map': ''.join(m), 'texts': {}}
        for t, s in TEXTS.items():
            out = apply(m, s); st = stats(out, by)
            cmp = {k: compare(st[k], [c[k] for c in ctrl_stats[t]]) for k in STATS}
            _, _, back = cover(out, by, 3)
            mres['texts'][t] = {'out': out, 'stats': st, 'z_p': cmp, 'words3': seg_words(out, back)}
            for k in STATS: cells.append((cmp[k][1], cmp[k][0], fam, mname, t, k, st[k]))
        famres['maps'][mname] = mres
    results['families'][fam] = famres

# ---------------------------------------------------------------- report
print(f'\nword-list sizes (len>=3, letters within target): ' +
      ', '.join(f"{f}={r['n_words_ge3']}" for f, r in results['families'].items()))
for fam, fr in results['families'].items():
    print(f'\n=== {fam} (target {fr["target_letters"]}) ===')
    for mname, mr in fr['maps'].items():
        print(f' map {mname:28s} a..i -> {mr["map"]}')
        for t, r in mr['texts'].items():
            zp = r['z_p']
            print(f'   {t:9s} quad={r["stats"]["quad"]:.3f} z={zp["quad"][0]:+.2f} p={zp["quad"][1]:.3f} | '
                  f'cov3={r["stats"]["cov3"]:.2f} p={zp["cov3"][1]:.3f} | cov4={r["stats"]["cov4"]:.2f} '
                  f'p={zp["cov4"][1]:.3f} | maxw={r["stats"]["maxword"]} p={zp["maxword"][1]:.3f}')

print('\nCommunity map (first_occ a->s b->a c->l d->p e->h f->e g->i h->o i->n) outputs:')
for t in ('dbbi', 'R60', 'R61', 'R56', 'dbbi_sq1', 'dbbi_sq0', 'faed_sq1', 'faed_sq0'):
    r = results['families']['SAL_bijection']['maps']['first_occ']['texts'][t]
    print(f'  {t:9s} {r["out"]}\n            words>=3: {" ".join(r["words3"])}')
print('  faed[:120]', results['families']['SAL_bijection']['maps']['first_occ']['texts']['faed']['out'][:120])

cells.sort()
ncell = len(cells)
print(f'\nmultiple testing: {ncell} cells (family x map x text x stat), {NCTRL} controls each')
for thr in (0.01, 0.05):
    print(f'  cells with p<={thr}: {sum(c[0] <= thr for c in cells)} (expected under null ~{thr * ncell:.0f}; '
          f'cells are correlated and maxword is discrete, so p is conservative)')
print('  10 smallest p:')
for c in cells[:10]:
    print(f'    p={c[0]:.4f} z={c[1]:+.2f} {c[2]}/{c[3]}/{c[4]}/{c[5]} value={c[6]:.3f}')
best_q = max(cells, key=lambda c: c[1] if c[5] == 'quad' else -9)
print(f'  best quad z: {best_q[1]:+.2f} at {best_q[2]}/{best_q[3]}/{best_q[4]} (Bonferroni over {ncell} cells: '
      f'smallest resolvable p 1/{NCTRL + 1} x {ncell} >> 0.05)')
results['smallest_p_cells'] = [list(c) for c in cells[:25]]
json.dump(results, open(OUT, 'w'), indent=1)
print('wrote', OUT)
