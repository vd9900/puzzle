"""Shared material for the digit_codecs lens: dbbi tokenizations, marker colours, residuals."""
import sys
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from common import DBBI, FAED, Z1, Z2, primes_upto, BIN1
from engine import DIG

P = set(primes_upto(5000))


def segmentations(s=DBBI, marker='b', suffix='e', base=1):
    out = []
    def rec(i, lp, toks):
        if i == len(s):
            out.append(list(toks)); return
        if lp in P:
            if s[i] == marker:
                rec(i + 1, lp + 1, toks + [marker])
                if i + 1 < len(s) and s[i + 1] == suffix:
                    rec(i + 2, lp + 1, toks + [marker + suffix])
        else:
            rec(i + 1, lp + 1, toks + [s[i]])
    rec(0, base, [])
    return out

SEGS = {len(t): t for t in segmentations()}   # {84: [...], 83: [...]}
# colour of the k-th prime marker (spiral order): B=blue, Y=yellow, W=near-white (event index 20 = prime 73)
COLOURS = 'BBBBYBBBYYBBBBYBBYYBWYYBY'
R60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
R61 = R60 + 'e'


def marked(seg_len):
    """list of (token, is_marker, logical_pos, marker_index)"""
    t = SEGS[seg_len]
    out = []; m = 0
    for i, tok in enumerate(t):
        if (i + 1) in P:
            out.append((tok, True, i + 1, m)); m += 1
        else:
            out.append((tok, False, i + 1, None))
    return out

assert ''.join(tok for tok, mk, _, _ in marked(83) if not mk) == R60
assert ''.join(tok for tok, mk, _, _ in marked(84) if not mk) == R61
