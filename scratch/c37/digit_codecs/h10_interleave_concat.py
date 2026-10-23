"""Deterministic leftovers: (a) residual digits interleaved with matrixsumlist bits / marker bits (alternating, both
phases, both orders); (b) concatenations dbbi+faed, faed+dbbi, Z1+Z2+dbbi+faed (o=0), reversed. Oracle: printable /
lowercase ratio of decimal->bytes vs 200 shuffled-residual controls; plus exact top-byte feasibility of each length."""
import sys, json, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from common_dc import DBBI, FAED, R60, R61, Z1, Z2, BIN1, marked
from h7_length_feasibility import feas
from engine import to_bytes, text_to_digits
D = lambda s: s.translate(str.maketrans('abcdefghio', '1234567890'))
PR = set(range(0x20, 0x7f)) | {9, 10, 13}
pr = lambda b: sum(c in PR for c in b) / max(1, len(b))
bits = BIN1.translate(str.maketrans('ab', '01'))
mbits = {L: ''.join('1' if tok == 'b' else '0' for tok, mk, _, _ in marked(L) if mk) for L in (83, 84)}
R56 = 'difhccgihaihggegegehhehhfafdhffcdfcccgfeggecdcifffgigeea'
def inter(a, b, first):
    out = []
    for x, y in zip(a, b): out += [x, y] if first == 'a' else [y, x]
    return ''.join(out)
# self-test: interleaving round-trip
t = text_to_digits('matrixsumlist'); a, b = t[0::2], t[1::2]
assert inter(a, b, 'a')[:2 * len(b)] == t[:2 * len(b)]
rows = []; rnd = random.Random(1)
for rn, r in (('R60', R60), ('R61', R61), ('R56', R56)):
    for bn, bb in (('BIN1', bits), ('BIN1_rev', bits[::-1]), ('M83', mbits[83]), ('M84', mbits[84])):
        for first in ('a', 'b'):
            dg = inter(D(r), bb, first).lstrip('0'); b = to_bytes(int(dg))
            ctrl = []
            for _ in range(200):
                l = list(r); rnd.shuffle(l); d2 = inter(D(''.join(l)), bb, first).lstrip('0'); ctrl.append(pr(to_bytes(int(d2))))
            ctrl.sort()
            rows.append(dict(test='interleave', resid=rn, bits=bn, first=first, ndig=len(dg), pratio=round(pr(b), 3),
                             ctrl_p95=round(ctrl[189], 3), ctrl_max=round(ctrl[-1], 3), feasible_any_map=feas(len(dg))[0]))
cat = {'DBBI+FAED': D(DBBI + FAED), 'FAED+DBBI': D(FAED + DBBI), 'Z1Z2DBBIFAED': D(Z1 + Z2 + DBBI + FAED),
       'DBBIFAEDZ1Z2': D(DBBI + FAED + Z1 + Z2)}
cat.update({k + '_rev': v[::-1] for k, v in list(cat.items())})
for k, dg in cat.items():
    dg = dg.lstrip('0'); b = to_bytes(int(dg))
    rows.append(dict(test='concat', s=k, ndig=len(dg), pratio=round(pr(b), 3), top_byte=b[0], feasible_any_map=feas(len(dg))[0]))
for r in rows: print(json.dumps(r))
print('max interleave pratio - ctrl_p95:', max(r['pratio'] - r['ctrl_p95'] for r in rows if r['test'] == 'interleave'))
json.dump(rows, open('/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs/h10_interleave_concat.json', 'w'), indent=0)
