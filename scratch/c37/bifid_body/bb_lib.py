"""Shared helpers for the bifid_body lens (cycle 37).
Square = dbbi first-occurrence order 'dbifhcegaklmnopqrstuvwxyz'; faed uses cells 0..8 only.
Natural decode = Bifid decrypt, period 570 (one block)."""
import sys, math, random
from collections import Counter
import numpy as np
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import FAED, DBBI  # noqa: E402
import bifid  # noqa: E402

SQ = bifid.CANON
assert SQ == 'dbifhcegaklmnopqrstuvwxyz'
N = len(FAED)
H = N // 2
POS = {ch: divmod(i, 5) for i, ch in enumerate(SQ)}
CELL = {ch: i for i, ch in enumerate(SQ)}
LET9 = 'abcdefghi'
# faed letter -> square cell
F2CELL = np.array([CELL[c] for c in LET9])
FAED_IDX = np.array([LET9.index(c) for c in FAED])
SQ_ARR = np.array(list(SQ))
UNI = Counter(FAED)
P_IID = {c: UNI[c] / N for c in LET9}


def bifid_dec_np(idx_batch, period=None):
    """idx_batch: (M, n) array of faed letter indices 0..8 (a..i).  Returns (M, n) array of square cells (0..24)
    for the Bifid decrypt with SQ at the given period (default full length)."""
    idx_batch = np.atleast_2d(idx_batch)
    M, n = idx_batch.shape
    period = period or n
    cells = F2CELL[idx_batch]
    r, c = cells // 5, cells % 5
    out = np.empty((M, n), dtype=np.int64)
    for s in range(0, n, period):
        e = min(n, s + period); L = e - s
        seq = np.empty((M, 2 * L), dtype=np.int64)
        seq[:, 0::2] = r[:, s:e]; seq[:, 1::2] = c[:, s:e]
        out[:, s:e] = seq[:, :L] * 5 + seq[:, L:]
    return out


def cells_to_str(row):
    return ''.join(SQ[x] for x in row)


def dec_str(s, period=None):
    idx = np.array([[LET9.index(ch) for ch in s]])
    return cells_to_str(bifid_dec_np(idx, period)[0])


assert dec_str(FAED) == bifid.BIF and bifid.BIF.startswith('btcseed')


def shuffles(M, seed, mode='whole'):
    """null-model faed index arrays: 'whole' = exact multiset shuffle, 'half' = shuffle within each half,
    'iid' = i.i.d. from the global unigram."""
    rng = np.random.default_rng(seed)
    if mode == 'iid':
        p = np.array([P_IID[c] for c in LET9])
        return rng.choice(9, size=(M, N), p=p)
    base = np.tile(FAED_IDX, (M, 1))
    if mode == 'whole':
        return rng.permuted(base, axis=1)
    if mode == 'half':
        a = rng.permuted(base[:, :H], axis=1); b = rng.permuted(base[:, H:], axis=1)
        return np.concatenate([a, b], axis=1)
    raise ValueError(mode)


def entropy(counts):
    n = sum(counts.values())
    return -sum(v / n * math.log2(v / n) for v in counts.values() if v)


def ioc(seq):
    c = Counter(seq); n = len(seq)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1))
