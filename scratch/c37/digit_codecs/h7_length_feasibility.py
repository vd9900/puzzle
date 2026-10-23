"""Length/leading-digit feasibility of z-method decodes (exact integer arithmetic).
An L-digit decimal number N lies in [10^(L-1), 10^L); its big-endian top byte therefore lies in a fixed interval that
depends only on L (and, more tightly, on the leading digit d: N in [d*10^(L-1), (d+1)*10^(L-1))). If that interval
misses a charset, NO digit map / zeroing pattern of an L-digit string can decode to that charset.
Self-check: Z1 (63 digits, leading 1) and Z2 (29 digits, leading 3) must be feasible for 'lower'."""
import sys, json
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from h5_topdown_more import CHARSETS
from common_dc import DBBI, FAED, R60, R61, Z1, Z2
from engine import DIG


def top_bytes(lo, hi):
    """set of possible top bytes for integers in [lo, hi)"""
    out = set()
    nb_lo = (lo.bit_length() + 7) // 8; nb_hi = ((hi - 1).bit_length() + 7) // 8
    for nb in range(nb_lo, nb_hi + 1):
        a = max(lo, 1 << (8 * (nb - 1))); b = min(hi - 1, (1 << (8 * nb)) - 1)
        if a > b: continue
        out |= set(range(a >> (8 * (nb - 1)), (b >> (8 * (nb - 1))) + 1))
    return out


def feas(L, lead=None):
    if lead is None: lo, hi = 10 ** (L - 1), 10 ** L
    else: lo, hi = lead * 10 ** (L - 1), (lead + 1) * 10 ** (L - 1)
    tb = top_bytes(lo, hi)
    return {c: bool(tb & CHARSETS[c]) for c in ('lower', 'printnl', 'b64', 'hex', 'ebc_lower', 'ebc_text')}, (min(tb), max(tb))


rows = []
z1 = ''.join(DIG[c] for c in Z1); z2 = ''.join(DIG[c] for c in Z2)
for name, L, lead in (('Z1', len(z1), int(z1[0])), ('Z2', len(z2), int(z2[0]))):
    f, r = feas(L, lead); assert f['lower'], name
    rows.append(dict(s=name, L=L, lead=lead, any_map=feas(L)[0], any_map_topbyte=feas(L)[1], lead_fixed=f, lead_topbyte=r))
items = [('DBBI', DBBI), ('DBBI_rev', DBBI[::-1]), ('R60', R60), ('R60_rev', R60[::-1]), ('R61', R61), ('R61_rev', R61[::-1]),
         ('FAED', FAED), ('FAED_rev', FAED[::-1])]
for name, s in items:
    L = len(s); lead = int(DIG[s[0]])
    fa, ra = feas(L); fl, rl = feas(L, lead)
    rows.append(dict(s=name, L=L, lead=lead, any_map=fa, any_map_topbyte=ra, lead_fixed=fl, lead_topbyte=rl))
# lengths reachable by marker reinsertion families (L83/L84 residual 60/61 + 23 marker strings of 0..2 digits)
for L in (83, 84, 104, 106, 107, 661):
    fa, ra = feas(L); rows.append(dict(s=f'len{L}', L=L, any_map=fa, any_map_topbyte=ra))
for r in rows: print(json.dumps(r))
json.dump(rows, open('/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs/h7_feasibility.json', 'w'), indent=0)
