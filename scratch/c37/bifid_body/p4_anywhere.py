"""P4: are on-theme / English words over-represented ANYWHERE in the real decode (any offset, any alignment)
compared with Bifid decodes of shuffled faed?  Self-verifying count statistic; planted control inserts a theme word
into the odd stream of a planted plaintext.
Vocab V_theme = theme words len>=5 + all theme+theme concatenations len>=7 (unfiltered);
V_eng = english words (big list) len>=8.  Statistic = number of (position, word) matches."""
import sys, json
import numpy as np
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/bifid_body')
import p1_vocab_pvalue as P1  # noqa
from bb_lib import *  # noqa

VT = set(w for w in P1.THEME if len(w) >= 5) | set(a + b for a in P1.THEME for b in P1.THEME if len(a + b) >= 7)
VE = set(w for w in P1.ENG_BIG if len(w) >= 8)


def matches(s, V, lens):
    out = []
    for i in range(len(s)):
        for L in lens:
            if i + L <= len(s) and s[i:i + L] in V:
                out.append((i, s[i:i + L]))
    return out


LT = sorted(set(len(w) for w in VT)); LE = sorted(set(len(w) for w in VE))
real = bifid.BIF
rt = matches(real, VT, LT); re_ = matches(real, VE, LE)
print('real theme matches:', rt)
print('real english>=8 matches:', re_)
M = 1000
nt = []; ne = []
for mode in ('whole',):
    idx = shuffles(M, 99, mode)
    dec = bifid_dec_np(idx)
    for row in dec:
        s = cells_to_str(row)
        nt.append(len(matches(s, VT, LT))); ne.append(len(matches(s, VE, LE)))
nt = np.array(nt); ne = np.array(ne)
pt = (np.sum(nt >= len(rt)) + 1) / (M + 1); pe = (np.sum(ne >= len(re_)) + 1) / (M + 1)
print(f'theme: real={len(rt)} null mean={nt.mean():.2f} sd={nt.std():.2f} P(null>=real)={pt:.3f}')
print(f'eng>=8: real={len(re_)} null mean={ne.mean():.2f} sd={ne.std():.2f} P(null>=real)={pe:.3f}')
# excluding the prefix
rt_body = [m for m in rt if m[0] >= 7]
print('theme matches in body only:', rt_body)
json.dump({'real_theme': rt, 'real_eng8': re_, 'null_theme_mean': nt.mean(), 'p_theme': pt,
           'null_eng_mean': ne.mean(), 'p_eng': pe}, open('/home/vin/bitcoin_puzzle/scratch/c37/bifid_body/p4_results.json', 'w'),
          indent=1, default=str)
