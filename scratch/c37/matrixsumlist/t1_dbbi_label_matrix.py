"""T1: dbbi (91 = 13x7) combined cell-wise with the 7-bit matrix of its own label 'matrixsumlist'
(13 chars x 7 bits = 91 bits, an exact size match), then read with the page's z-method
(decimal -> integer -> big-endian bytes).  'matrix sum' = element-wise matrix addition/subtraction;
'zeroed out' = subtraction / masking produces the 0 digits dbbi lacks.
Detector: printable ratio / lowercase ratio / English quadgram score of the decoded bytes.
Control: same pipeline with 2000 random 91-bit masks (max statistic distribution) + planted self-test."""
import itertools, random, sys
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/matrixsumlist')
from msl_lib import *

def label_bits(variant):
    if variant == 'msb7':
        return [int(b) for c in LABEL for b in format(ord(c), '07b')]
    if variant == 'lsb7':
        return [int(b) for c in LABEL for b in format(ord(c), '07b')[::-1]]
    if variant == 'bin1_first91':
        return [int(b) for b in BIN1.translate(str.maketrans('ab', '01'))[:91]]
    if variant == 'bin1_last91':
        return [int(b) for b in BIN1.translate(str.maketrans('ab', '01'))[-91:]]
    if variant == 'msb7_colmajor':  # 7x13 laid column-wise: bit k of char j at position k*13+j
        b = [[int(x) for x in format(ord(c), '07b')] for c in LABEL]
        return [b[j][k] for k in range(7) for j in range(13)]
    if variant == 'msb7_rev':
        return [int(b) for c in LABEL for b in format(ord(c), '07b')][::-1]
    raise ValueError

OPS = {
    'add': lambda d, b: d + b,
    'add_mod10': lambda d, b: (d + b) % 10,
    'sub': lambda d, b: d - b,
    'sub_mod10': lambda d, b: (d - b) % 10,
    'zero_where1': lambda d, b: 0 if b else d,
    'zero_where0': lambda d, b: d if b else 0,
}

def combine(dg, bits, op):
    out = []
    for d, b in zip(dg, bits):
        v = OPS[op](d, b)
        if v < 0 or v > 9:
            return None
        out.append(v)
    return out

def decode_all(dg, bits, op):
    res = []
    c = combine(dg, bits, op)
    if c is None:
        return res
    for base in (10, 9, 8):
        if max(c) >= base:
            continue
        for rev in (False, True):
            seq = c[::-1] if rev else c
            b = zdec(seq, base)
            res.append((base, rev, b))
    # also 'delete' readings (keep digits where bit==1 / ==0) -> z-method
    return res

def stats(b):
    return pr(b), lowr(b), eng(b), longest_printable_run(b)

def run(srcs):
    rows = []
    for sname, s in srcs:
        for a0 in (False, True):
            dg = dig(s, a0)
            for bv in ('msb7', 'lsb7', 'bin1_first91', 'bin1_last91', 'msb7_colmajor', 'msb7_rev'):
                bits = label_bits(bv)
                for op in OPS:
                    for base, rev, b in decode_all(dg, bits, op):
                        rows.append(((sname, a0, bv, op, base, rev), b, stats(b)))
                # deletion readings
                for keep in (0, 1):
                    kept = [d for d, x in zip(dg, bits) if x == keep]
                    for base in (10, 9):
                        if max(kept) >= base: continue
                        b = zdec(kept, base)
                        rows.append(((sname, a0, bv, f'keep{keep}', base, False), b, stats(b)))
    return rows

if __name__ == '__main__':
    # planted self-test: text -> decimal digits; dbbi-like letters = digit + bit (so 'sub' recovers)
    T = 'plantedtestmessagefortheonetwothree'
    digits = [int(x) for x in str(int.from_bytes(T.encode(), 'big'))]
    bits = label_bits('msb7')[-len(digits):]
    fake = ''.join(chr(96 + d + b) if d + b > 0 else 'o' for d, b in zip(digits, bits))
    dg = dig(fake)
    rec = zdec(combine(dg, bits, 'sub'))
    assert rec == T.encode(), rec
    print('planted self-test OK (sub recovers planted text)')

    srcs = [('dbbi', DBBI), ('dbbi_rev', DBBI[::-1])]
    rows = run(srcs)
    print('real decodes:', len(rows))
    rows.sort(key=lambda r: (-r[2][0], -r[2][2]))
    for p, b, st in rows[:12]:
        print(p, 'pr=%.2f low=%.2f eng=%.2f run=%d' % st, b[:40])
    best_pr = max(r[2][0] for r in rows); best_run = max(r[2][3] for r in rows)
    best_eng = max(r[2][2] for r in rows if r[2][1] > 0.5) if any(r[2][1] > 0.5 for r in rows) else -9
    # control: random 91-bit masks in place of the label bits (same ops/bases/directions)
    rnd = random.Random(37)
    ctrl_pr = []; ctrl_run = []
    for t in range(300):
        rb = [rnd.randint(0, 1) for _ in range(91)]
        mx = 0; mr = 0
        for a0 in (False, True):
            dg = dig(DBBI, a0)
            for op in OPS:
                for base, rev, b in decode_all(dg, rb, op):
                    s = stats(b); mx = max(mx, s[0]); mr = max(mr, s[3])
        ctrl_pr.append(mx); ctrl_run.append(mr)
    ctrl_pr.sort(); ctrl_run.sort()
    print('REAL best printable ratio %.3f, longest printable run %d' % (best_pr, best_run))
    print('CONTROL (per random mask, max over same ops) printable ratio median %.3f p95 %.3f max %.3f; run median %d p95 %d max %d' % (
        ctrl_pr[150], ctrl_pr[285], ctrl_pr[-1], ctrl_run[150], ctrl_run[285], ctrl_run[-1]))
