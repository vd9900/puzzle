"""P3: key look-elsewhere calibration.  The dbbi-keyed square puts a..i in cells 0..8 in dbbi first-occurrence order.
For ALL 9! orders of a..i in cells 0..8 (tail klmnopqrstuvwxyz fixed, as any a-i keyword gives), decode the first 16
letters of faed (period 570) and count orders whose decode starts with a vocabulary string (tiers from P1).
Self-check: the number of orders giving 'btcseed' must equal the community-reported 8, and the dbbi order must be one.
Also reports the expected count 9! * P_tier as a cross-check of the P1 analytic union (orders are not independent
samples, but the count is an exact enumeration over the real faed)."""
import sys, itertools, json
import numpy as np
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/bifid_body')
import p1_vocab_pvalue as P1  # noqa
from bb_lib import FAED, H, LET9, SQ  # noqa

TAIL = 'klmnopqrstuvwxyz'
L = 16
a_letters = FAED[:L // 2]; b_letters = FAED[H:H + L // 2]
perms = np.array(list(itertools.permutations(range(9))), dtype=np.int64)  # perms[k][cell] = letter index at cell
# cell of each letter under each perm
cell_of = np.argsort(perms, axis=1)  # (9!, 9): letter idx -> cell
ai = np.array([LET9.index(c) for c in a_letters]); bi = np.array([LET9.index(c) for c in b_letters])
ca = cell_of[:, ai]; cb = cell_of[:, bi]
ev = (ca // 5) * 5 + (cb // 5); od = (ca % 5) * 5 + (cb % 5)
out = np.empty((len(perms), L), dtype=np.int64); out[:, 0::2] = ev; out[:, 1::2] = od
# map cell -> letter per perm
letters = np.array(list(LET9 + TAIL))  # index 0..8 = a..i, 9.. = tail
# cell c<9 -> letter perms[k][c]; c>=9 -> TAIL[c-9]
cellletter = np.concatenate([perms, np.tile(np.arange(9, 25), (len(perms), 1))], axis=1)
outl = np.take_along_axis(cellletter, out, 1)
strs = [''.join(letters[r]) for r in outl]
dbbi_order = tuple(LET9.index(c) for c in SQ[:9])
k_dbbi = [i for i, p in enumerate(map(tuple, perms)) if p == dbbi_order][0]
assert strs[k_dbbi].startswith('btcseed'), strs[k_dbbi]
n_btc = sum(s.startswith('btcseed') for s in strs)
print('orders giving btcseed:', n_btc, '(community: 8)')
tiers = P1.build_tiers()
res = {'n_orders': len(strs), 'n_btcseed': n_btc}
for name in ('B_theme_1_2', 'B2_theme_1_2_3', 'C_english_word', 'C3_bip39', 'ALL'):
    mini = P1.minimal([w for w in set(tiers[name]) if P1.fits(w)])
    by7 = {}
    for w in mini:
        by7.setdefault(w[:7], []).append(w)
    hits = []
    for k, s in enumerate(strs):
        for w in by7.get(s[:7], []):
            if s.startswith(w):
                hits.append((k, w))
    uniq = sorted(set(w for _, w in hits))
    exp = len(strs) * sum(P1.p_iid(w) for w in mini)
    res[name] = {'orders_hit': len(hits), 'distinct_words': len(uniq), 'expected_iid': exp, 'words': uniq[:60]}
    print(f'{name:16s} orders with vocab prefix: {len(hits):6d} (iid-expected {exp:.1f}); distinct words {len(uniq)}: '
          f'{uniq[:30]}')
json.dump(res, open('/home/vin/bitcoin_puzzle/scratch/c37/bifid_body/p3_results.json', 'w'), indent=1)
