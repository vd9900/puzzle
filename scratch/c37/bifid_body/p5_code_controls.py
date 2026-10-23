"""P5: sensitivity of the P2 detectors to CODE-like payloads (not just English).  Plant 'btcseed' + a 563-letter body
whose digraphs are drawn uniformly from a K-subset of the 81 reachable digraph codes (K = 10 decimal, 16 hex,
32 base32, 58 base58, 64 base64, 81 = everything), Bifid-encrypt (must give a-i only; verified), and measure how often
each detector rejects at p<0.01 vs the whole-shuffle null.  Tells which payload alphabets the null body excludes."""
import sys, json
import numpy as np
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/bifid_body')
from bb_lib import *  # noqa
import p2_structure as P2  # noqa

REACH = [(e, o) for e in 'dbce' for o in SQ if POS[e][0] * 5 + POS[o][0] <= 8 and POS[e][1] * 5 + POS[o][1] <= 8]
assert len(REACH) == 81, len(REACH)
rng = np.random.default_rng(5)
null = P2.all_stats(shuffles(5000, 77, 'whole'))
keys = ['S1_odd_ioc', 'S2_odd_entropy', 'S3_even_entropy', 'S4_body_ioc', 'S5_distinct_digraphs', 'S7_chi2_pair',
        'S8_rep3gram', 'S9_rep4gram']
res = {}
for K in (10, 16, 32, 58, 64, 81):
    fa = []
    for t in range(30):
        sub = [REACH[i] for i in rng.choice(81, K, replace=False)]
        body = ''.join(''.join(sub[i]) for i in rng.integers(0, K, 282))
        pt = ('btcseed' + body[1:])[:570]   # keep even/odd alignment: 'btcseed'+odd letter starts digraph 3
        pt = 'btcseed' + body[1:564]
        assert len(pt) == 570
        ct = bifid.bifid_encrypt(pt, SQ, 570)
        assert set(ct) <= set(LET9) and dec_str(ct) == pt
        fa.append([LET9.index(c) for c in ct])
    st = P2.all_stats(np.array(fa))
    det = {k: float(np.mean([P2.empirical(x, null[k]) < 0.01 for x in st[k]])) for k in keys}
    anyd = float(np.mean([any(P2.empirical(st[k][i], null[k]) < 0.01 / len(keys) for k in keys) for i in range(30)]))
    res[K] = {'per_detector': det, 'any_bonferroni': anyd}
    print(K, 'any(Bonf):', anyd, det)
json.dump(res, open('/home/vin/bitcoin_puzzle/scratch/c37/bifid_body/p5_results.json', 'w'), indent=1)
