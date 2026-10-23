"""P1: honest p-value for the 'btcseed' prefix of the natural dbbi-keyed Bifid decode of faed (period 570).

Event family: decode starts with ANY vocabulary string of length >= 7 that is reachable under the forced pattern.
Forced pattern (from faed using square cells 0..8 only):
  * even output letters in {d,b,c,e} (cells 0,1,5,6)
  * digraph (even e, odd o) maps to the faed pair (faed[j], faed[j+285]) = (cell(r_e1, r_o1), cell(r_e2, r_o2)) where
    (r_e1, r_e2) = coords(e), (r_o1, r_o2) = coords(o); both cells must be in 0..8.
Nulls: iid (global unigram), half-iid (first-half unigram for faed[j], second-half for faed[j+285]),
       exact multiset shuffle (computed exactly by falling factorials).
Union over the prefix-minimal set of fitting strings (events for prefix-incomparable strings are disjoint) = exact.
Validation: Monte-Carlo with a trie on 2e6 iid / shuffled nulls must agree with the analytic numbers;
            planted check: the real faed must register 'btcseed' as a hit.
"""
import sys, json, itertools, math, re, time
from collections import Counter
import numpy as np
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/bifid_body')
from bb_lib import *  # noqa

OUT = '/home/vin/bitcoin_puzzle/scratch/c37/bifid_body/'
EVEN = set('dbce')
FIRST = Counter(FAED[:H]); SECOND = Counter(FAED[H:])


def norm(w):
    w = w.strip().lower().replace('j', 'i')
    return w if re.fullmatch('[a-z]+', w) else None


def pair_cells(e, o):
    """digraph (e,o) -> (cell of faed[j], cell of faed[j+285]) or None if unreachable"""
    if e not in EVEN:
        return None
    (ra, rb), (ca, cb) = POS[e], POS[o]
    x, y = ra * 5 + ca, rb * 5 + cb
    if x > 8 or y > 8:
        return None
    return SQ[x], SQ[y]


def fits(w):
    for i in range(0, len(w) - 1, 2):
        if pair_cells(w[i], w[i + 1]) is None:
            return False
    if len(w) % 2 and w[-1] not in EVEN:
        return False
    return True


ROW0 = [c for c in LET9 if CELL[c] < 5]
ROW1 = [c for c in LET9 if CELL[c] >= 5]


def requirement(w):
    """list of (first-half letter set, second-half letter set) per pair index j"""
    req = []
    for i in range(0, len(w) - 1, 2):
        x, y = pair_cells(w[i], w[i + 1])
        req.append(({x}, {y}))
    if len(w) % 2:
        ra, rb = POS[w[-1]]
        req.append((set(ROW0 if ra == 0 else ROW1), set(ROW0 if rb == 0 else ROW1)))
    return req


def p_iid(w, first=None, second=None):
    first = first or {c: P_IID[c] for c in LET9}
    second = second or first
    p = 1.0
    for A, B in requirement(w):
        p *= sum(first[c] for c in A) * sum(second[c] for c in B)
    return p


def p_shuffle(w):
    """exact probability under a uniformly random permutation of the faed multiset"""
    req = requirement(w)
    fixed = []; loose = None
    for A, B in req:
        if len(A) == 1 and len(B) == 1:
            fixed += [next(iter(A)), next(iter(B))]
        else:
            loose = (A, B)
    cnt = Counter(UNI); p = 1.0; n = N
    for ch in fixed:
        if cnt[ch] <= 0:
            return 0.0
        p *= cnt[ch] / n; cnt[ch] -= 1; n -= 1
    if loose:
        A, B = loose; s = 0.0
        for x in A:
            for y in B:
                s += cnt[x] * (cnt[y] - (x == y))
        p *= s / (n * (n - 1))
    return p


def minimal(strings):
    s = sorted(set(strings))
    out = []
    S = set(s)
    for w in s:
        if not any(w[:k] in S for k in range(7, len(w))):
            out.append(w)
    return out


# ---------------- vocabulary -----------------
def load(path, maxn=None):
    out = []
    with open(path, errors='ignore') as f:
        for i, l in enumerate(f):
            if maxn and i >= maxn:
                break
            w = norm(l.split()[0]) if l.strip() else None
            if w:
                out.append(w)
    return out


DICT_AM = load('/usr/share/dict/american-english')
DICT_BR = load('/usr/share/dict/british-english')
WIKI = load('/home/vin/.config/google-chrome/ZxcvbnData/3/english_wikipedia.txt')
TVF = load('/home/vin/.config/google-chrome/ZxcvbnData/3/us_tv_and_film.txt')
BIG = load('/home/vin/.cache/uv/archive-v0/Qa4J3g65DjkMHxrG/unstructured/nlp/english-words.txt')
BIP39 = load('/home/vin/working/venv/lib/python3.12/site-packages/eth_account/hdaccount/wordlist/english.txt')
assert len(BIP39) == 2048

THEME = """bitcoin bitcoins btc xbt sat sats satoshi satoshis nakamoto coin coins crypto wallet wallets address addr key keys
privkey privatekey private public pubkey secret secrets seed seeds seedphrase mnemonic mnemonics phrase passphrase password
passwords pass passwd pwd word words wif hex base bip xprv xpub master root entropy hash hashes sha shaabef shabef ripemd
ecdsa curve block blocks chain blockchain ledger mine miner mining nonce sig signature sign txid utxo hodl prize reward bounty
treasure gold money cash fund funds code codes cipher ciphers decode decoded decrypt decrypted encrypt encrypted encode encoded
aes salt puzzle puzzles gsmg gsmgio solve solved solution answer clue clues hint hints door doors enter token tokens vault
safe lock unlock bank deposit electrum trezor ledgerwallet paper brain brainwallet cold storage backup recovery recover restore
matrix neo morpheus trinity oracle architect keymaker merovingian persephone smith agent zion nebuchadnezzar source rabbit
white red blue pill redpill bluepill choice illusion spoon seraph causality anomaly prime primes cosmic duality yin yang yinyang
salphaseion salvation phase matrixsumlist lastwords thispassword theseedisplanted seedisplanted planted plant flower blossom
concrete heisenberg fresco giveit logic warning robot mrrobot fsociety elliot whiterose rose roses sum list last first final
one two three four five six seven eight nine ten zero half better life death love truth light dark the is a an of to your this
my here it its his you we our next step stage level""".split()
THEME = sorted(set(norm(t) for t in THEME if norm(t)))
ENG = sorted(set(w for w in DICT_AM + DICT_BR + WIKI + TVF))   # curated-ish English
ENG_BIG = sorted(set(BIG))
COMMON = [w for w in WIKI[:5000] if len(w) >= 2] + ['a', 'i']   # common words for two-word compounds


def compounds(firsts, seconds, minlen=7):
    """all a+b (a in firsts, b in seconds) with len>=minlen whose full string fits; prune on fits(a)."""
    out = []
    by_len = {}
    for b in seconds:
        by_len.setdefault(len(b), []).append(b)
    fa = [a for a in firsts if fits(a)]
    for a in fa:
        for b in seconds:
            s = a + b
            if len(s) >= minlen and fits(s):
                out.append(s)
    return out


def build_tiers():
    tiers = {}
    tiers['A_btcseed'] = ['btcseed']
    T1 = [t for t in THEME if len(t) >= 7]
    T2 = compounds(THEME, THEME)
    tiers['B_theme_1_2'] = T1 + T2
    T2all = sorted(set(a + b for a in THEME for b in THEME))
    T3 = compounds(T2all, THEME)
    tiers['B2_theme_1_2_3'] = tiers['B_theme_1_2'] + T3
    tiers['C_english_word'] = [w for w in ENG if len(w) >= 7]
    tiers['C2_english_big'] = [w for w in ENG_BIG if len(w) >= 7]
    tiers['C3_bip39'] = [w for w in BIP39 if len(w) >= 7] + compounds(BIP39, BIP39)
    eng3 = [w for w in ENG if len(w) >= 3]
    D = compounds(THEME, eng3) + compounds(eng3, THEME)
    tiers['D_theme+english'] = tiers['B2_theme_1_2_3'] + D
    E = compounds(COMMON, COMMON)
    tiers['E_two_common_words'] = E
    tiers['ALL'] = sorted(set(tiers['D_theme+english'] + tiers['C_english_word'] + tiers['C2_english_big'] + tiers['C3_bip39'] + E))
    return tiers


def evaluate(tiers):
    half_first = {c: FIRST[c] / H for c in LET9}; half_second = {c: SECOND[c] / H for c in LET9}
    res = {}
    for name, words in tiers.items():
        fit = [w for w in set(words) if fits(w)]
        mini = minimal(fit)
        # 7-prefix (truncation-tolerant) event: first 7 letters equal the first 7 letters of a vocab string of length>=7
        # whose first 7 letters fit
        pre7 = sorted(set(w[:7] for w in set(words) if fits(w[:7])))
        r = {
            'n_vocab': len(set(words)), 'n_fit_full': len(fit), 'n_fit_minimal': len(mini),
            'p_iid': sum(p_iid(w) for w in mini),
            'p_halfiid': sum(p_iid(w, half_first, half_second) for w in mini),
            'p_shuffle': sum(p_shuffle(w) for w in mini),
            'n_prefix7': len(pre7),
            'p7_iid': sum(p_iid(w) for w in pre7),
            'p7_shuffle': sum(p_shuffle(w) for w in pre7),
            'top': sorted(((p_iid(w), w) for w in mini), reverse=True)[:25],
        }
        res[name] = r
    return res


def mc_validate(min_words, M=2_000_000, seed=7, mode='iid', L=16):
    """Monte-Carlo: decode prefix of length L from null faed (only positions 0..7 and 285..292 matter)."""
    rng = np.random.default_rng(seed)
    S = set(min_words); maxL = max(len(w) for w in min_words)
    assert maxL <= L
    hits = 0; done = 0; CH = 200_000 if mode == "iid" else 20_000
    while done < M:
        m = min(CH, M - done)
        if mode == 'iid':
            p = np.array([P_IID[c] for c in LET9])
            a = rng.choice(9, size=(m, L // 2), p=p); b = rng.choice(9, size=(m, L // 2), p=p)
        else:  # exact shuffle: sample L positions w/o replacement via random keys over the multiset
            keys = rng.random((m, N))
            sel = np.argpartition(keys, L, axis=1)[:, :L]
            order = np.take_along_axis(keys, sel, 1).argsort(axis=1)
            sel = np.take_along_axis(sel, order, 1)
            v = FAED_IDX[sel]; a, b = v[:, :L // 2], v[:, L // 2:]
        ca, cb = F2CELL[a], F2CELL[b]
        ev = (ca // 5) * 5 + (cb // 5); od = (ca % 5) * 5 + (cb % 5)
        out = np.empty((m, L), dtype=np.int64); out[:, 0::2] = ev; out[:, 1::2] = od
        # filter: even letters forced; quick check by 7-letter prefix code set
        pre = set(w[:7] for w in S)
        codes7 = np.zeros(m, dtype=np.int64)
        for i in range(7):
            codes7 = codes7 * 25 + out[:, i]
        pre_codes = np.array(sorted(sum(CELL[ch] * 25 ** (6 - i) for i, ch in enumerate(w)) for w in pre))
        cand = np.nonzero(np.isin(codes7, pre_codes))[0]
        for k in cand:
            s = ''.join(SQ[x] for x in out[k])
            if any(s[:len(w)] == w for w in S if s.startswith(w[:7])):
                hits += 1
        done += m
    return hits, M


if __name__ == '__main__':
    t0 = time.time()
    # sanity: the real decode
    assert fits('btcseed') and requirement('btcseed')[0] == ({'f'}, {'a'})
    print('real natural decode prefix:', bifid.BIF[:16])
    print('P(btcseed) iid=%.4g halfiid=%.4g shuffle=%.4g' % (
        p_iid('btcseed'), p_iid('btcseed', {c: FIRST[c] / H for c in LET9}, {c: SECOND[c] / H for c in LET9}),
        p_shuffle('btcseed')))
    tiers = build_tiers()
    print('tiers built', {k: len(v) for k, v in tiers.items()}, round(time.time() - t0, 1), 's', flush=True)
    res = evaluate(tiers)
    for k, r in res.items():
        print(f"{k:22s} vocab={r['n_vocab']:9d} fit={r['n_fit_full']:7d} minimal={r['n_fit_minimal']:7d} "
              f"P_iid={r['p_iid']:.3e} P_half={r['p_halfiid']:.3e} P_shuf={r['p_shuffle']:.3e} | "
              f"prefix7 n={r['n_prefix7']} P7_iid={r['p7_iid']:.3e} P7_shuf={r['p7_shuffle']:.3e}")
        print('    top:', ', '.join(f'{w}({p:.1e})' for p, w in r['top'][:15]))
    # MC validation of the analytic union on the ALL tier restricted to length<=16 strings
    allmin = minimal([w for w in tiers['ALL'] if fits(w)])
    short = [w for w in allmin if len(w) <= 16]
    ana = sum(p_iid(w) for w in short); ana_s = sum(p_shuffle(w) for w in short)
    h, M = mc_validate(short, M=2_000_000, mode='iid')
    print(f'MC iid  (ALL, len<=16, {len(short)} strings): {h}/{M} = {h/M:.3e} vs analytic {ana:.3e} '
          f'(expected {ana*M:.1f} +- {math.sqrt(ana*M):.1f})')
    h2, M2 = mc_validate(short, M=1_000_000, mode='shuffle', seed=11)
    print(f'MC shuf (ALL, len<=16): {h2}/{M2} = {h2/M2:.3e} vs analytic {ana_s:.3e} '
          f'(expected {ana_s*M2:.1f} +- {math.sqrt(ana_s*M2):.1f})')
    # planted check: real faed registers as a hit
    real_hit = [w for w in allmin if bifid.BIF.startswith(w)]
    print('real faed hits in ALL minimal set:', real_hit)
    json.dump({k: {kk: vv for kk, vv in r.items()} for k, r in res.items()} | {
        'mc_iid': [h, M, ana], 'mc_shuffle': [h2, M2, ana_s], 'real_hits': real_hit},
        open(OUT + 'p1_results.json', 'w'), indent=1, default=str)
    print('done', round(time.time() - t0, 1), 's')
