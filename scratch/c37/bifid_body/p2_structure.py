"""P2: does the 563-letter body of the natural Bifid decode (dbbi-keyed square, period 570) carry structure beyond
what Bifid-decoding a structureless faed produces?

Identity used: decode digraph (2j,2j+1) <-> faed pair (faed[j], faed[j+285]) (bijective).  So every body statistic is a
statistic of the paired sequence; the nulls shuffle faed (exact multiset / within-halves) or draw i.i.d. from its unigram.
Statistics (computed on body = decode[7:], and on the even / odd sub-streams of the full decode):
  S1 odd-stream IoC, S2 odd-stream entropy, S3 even-stream entropy, S4 body IoC, S5 #distinct digraph codes,
  S6 max digraph count, S7 chi2 independence of (faed[j], faed[j+285]) 9x9, S8/9/10 repeated 3/4/5-gram counts in body,
  S11 max-over-lags 1..60 periodic-match z (body), S12 English quadgram score of the odd stream,
  S13 odd-stream repeated 3-grams.
Empirical two-sided p = 2*min(P(null>=obs), P(null<=obs)).
Positive control: plant English text in the odd stream (even letter chosen as the first reachable of d,b,c,e),
Bifid-encrypt to a planted faed (all cells 0..8, verified), decode, and check the detectors fire.
"""
import sys, math, pickle, json, time
from collections import Counter
import numpy as np
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/bifid_body')
from bb_lib import *  # noqa

OUT = '/home/vin/bitcoin_puzzle/scratch/c37/bifid_body/'
QG, QFLOOR = None, None
_q = pickle.load(open('/home/vin/bitcoin_puzzle/scratch/quadgrams_clean.pkl', 'rb'))
QG = _q[0]; QFLOOR = _q[1] if not isinstance(_q[1], dict) else min(QG.values()) - 1
QARR = np.full(26 ** 4, float(QFLOOR))
for k, v in QG.items():
    if len(k) == 4 and k.isalpha() and k.islower():
        QARR[((ord(k[0]) - 97) * 26 + ord(k[1]) - 97) * 26 * 26 + (ord(k[2]) - 97) * 26 + ord(k[3]) - 97] = v
SQ_ORD = np.array([ord(c) - 97 for c in SQ])


def stats_batch(dec):
    """dec: (M, 570) cells. returns dict of arrays (M,)"""
    M = dec.shape[0]
    body = dec[:, 7:]
    ev = dec[:, 0::2]; od = dec[:, 1::2]
    S = {}

    def ioc_b(x, K=25):
        n = x.shape[1]
        cnt = np.zeros((x.shape[0], K)); np.add.at(cnt, (np.repeat(np.arange(x.shape[0]), n), x.ravel()), 1)
        return (cnt * (cnt - 1)).sum(1) / (n * (n - 1)), cnt

    def ent(cnt):
        p = cnt / cnt.sum(1, keepdims=True)
        with np.errstate(divide='ignore', invalid='ignore'):
            return -np.nansum(np.where(p > 0, p * np.log2(p), 0), 1)
    S['S1_odd_ioc'], co = ioc_b(od)
    S['S2_odd_entropy'] = ent(co)
    _, ce = ioc_b(ev)
    S['S3_even_entropy'] = ent(ce)
    S['S4_body_ioc'], _ = ioc_b(body)
    code = ev * 25 + od  # digraph code
    cc = np.zeros((M, 625)); np.add.at(cc, (np.repeat(np.arange(M), code.shape[1]), code.ravel()), 1)
    S['S5_distinct_digraphs'] = (cc > 0).sum(1).astype(float)
    S['S6_max_digraph'] = cc.max(1)
    # chi2 of 9x9 contingency faed[j] x faed[j+285] (via digraph code bijection: count matrix of codes)
    obs = cc  # 81 used codes, independence via the inverse map is equivalent; compute directly from faed pairs below
    S['_cc'] = cc
    for n in (3, 4, 5):
        L = body.shape[1] - n + 1
        h = np.zeros((M, L), dtype=np.int64)
        for i in range(n):
            h = h * 25 + body[:, i:i + L]
        hs = np.sort(h, 1)
        dup = (hs[:, 1:] == hs[:, :-1]).sum(1)  # number of repeated occurrences beyond first
        S[f'S{5 + n}_rep{n}gram'] = dup.astype(float)
    # periodicity
    zs = []
    for k in range(1, 61):
        m = (body[:, :-k] == body[:, k:]).mean(1)
        zs.append(m)
    Z = np.stack(zs, 1)
    mu = Z.mean(0, keepdims=True); sd = Z.std(0, keepdims=True) + 1e-12
    S['_lagmatch'] = Z
    # odd stream English quadgram score (avg log10 per quadgram)
    ol = SQ_ORD[od]
    idx = ((ol[:, :-3] * 26 + ol[:, 1:-2]) * 26 + ol[:, 2:-1]) * 26 + ol[:, 3:]
    S['S12_odd_quadgram'] = QARR[idx].mean(1)
    L = od.shape[1] - 2
    h = (od[:, :L] * 25 + od[:, 1:L + 1]) * 25 + od[:, 2:L + 2]
    hs = np.sort(h, 1)
    S['S13_odd_rep3'] = (hs[:, 1:] == hs[:, :-1]).sum(1).astype(float)
    return S


def chi2_pairs(fidx):
    a = fidx[:, :H]; b = fidx[:, H:]
    M = fidx.shape[0]
    T = np.zeros((M, 81)); np.add.at(T, (np.repeat(np.arange(M), H), (a * 9 + b).ravel()), 1)
    T = T.reshape(M, 9, 9)
    E = T.sum(2, keepdims=True) * T.sum(1, keepdims=True) / H
    return ((T - E) ** 2 / np.where(E > 0, E, 1)).sum((1, 2))


def all_stats(fidx):
    dec = bifid_dec_np(fidx)
    S = stats_batch(dec)
    S['S7_chi2_pair'] = chi2_pairs(fidx)
    return S


def empirical(obs, null):
    ge = (np.sum(null >= obs) + 1) / (len(null) + 1); le = (np.sum(null <= obs) + 1) / (len(null) + 1)
    return min(1.0, 2 * min(ge, le))


def lag_maxz(Zobs, Znull):
    mu = Znull.mean(0); sd = Znull.std(0) + 1e-12
    zo = ((Zobs - mu) / sd).max(1); zn = ((Znull - mu) / sd).max(1)
    return zo, zn


def planted_faed(seed=0):
    """English text in the odd stream; even letter = first reachable of d,b,c,e (always 'd' works)."""
    import re
    txt = open('/home/vin/bitcoin_puzzle/scratch/speech32_words.txt', errors='ignore').read().lower()
    txt = re.sub('[^a-z]', '', txt).replace('j', 'i')
    if len(txt) < 300:
        txt = (txt * 10)
    rng = np.random.default_rng(seed)
    st = rng.integers(0, max(1, len(txt) - 290))
    odd = txt[st:st + 285]
    pt = []
    for o in odd:
        opts = [e for e in 'dbce' if (POS[e][0] * 5 + POS[o][0] <= 8 and POS[e][1] * 5 + POS[o][1] <= 8)]
        pt += [opts[rng.integers(len(opts))], o]
    pt = ''.join(pt)
    ct = bifid.bifid_encrypt(pt, SQ, 570)
    assert set(ct) <= set(LET9), set(ct)
    assert dec_str(ct) == pt
    return np.array([LET9.index(c) for c in ct])


if __name__ == '__main__':
    t0 = time.time()
    M = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    real = all_stats(FAED_IDX[None, :])
    planted = np.stack([planted_faed(s) for s in range(20)])
    pl = all_stats(planted)
    results = {}
    for mode in ('whole', 'half', 'iid'):
        nul = all_stats(shuffles(M, 1234, mode))
        res = {}
        for k in sorted(real):
            if k.startswith('_'):
                continue
            res[k] = {'obs': float(real[k][0]), 'null_mean': float(nul[k].mean()), 'null_sd': float(nul[k].std()),
                      'p': empirical(real[k][0], nul[k]),
                      'planted_median': float(np.median(pl[k])),
                      'planted_frac_p<0.01': float(np.mean([empirical(x, nul[k]) < 0.01 for x in pl[k]]))}
        zo, zn = lag_maxz(real['_lagmatch'], nul['_lagmatch'])
        zp, _ = lag_maxz(pl['_lagmatch'], nul['_lagmatch'])
        res['S11_lag_maxz'] = {'obs': float(zo[0]), 'null_mean': float(zn.mean()), 'null_sd': float(zn.std()),
                               'p': float((np.sum(zn >= zo[0]) + 1) / (M + 1)),
                               'best_lag': int(np.argmax((real['_lagmatch'][0] - nul['_lagmatch'].mean(0)) /
                                                         (nul['_lagmatch'].std(0) + 1e-12))) + 1,
                               'planted_median': float(np.median(zp)),
                               'planted_frac_p<0.01': float(np.mean([(np.sum(zn >= x) + 1) / (M + 1) < 0.01 for x in zp]))}
        # digraph-code usage table for the real decode vs null mean
        cc_real = real['_cc'][0]; cc_null = nul['_cc'].mean(0)
        top = np.argsort(-cc_real)[:10]
        res['top_digraphs'] = [(SQ[c // 25] + SQ[c % 25], int(cc_real[c]), round(float(cc_null[c]), 2)) for c in top]
        results[mode] = res
        print(f'== null mode {mode}  M={M}')
        for k, r in res.items():
            print(' ', k, r)
    nonmin = [min(results[m][k]['p'] for m in results) for k in results['whole'] if k.startswith('S')]
    print('number of statistics:', len(nonmin), ' min p over all stats/modes:', min(nonmin),
          ' Bonferroni-adjusted:', min(1, min(nonmin) * len(nonmin) * 3))
    json.dump(results, open(OUT + 'p2_results.json', 'w'), indent=1)
    print('done', round(time.time() - t0, 1), 's')
