# Fast locator: anchor index on 8-digit substrings (fewest-g sub-window of every 14-letter probe, g expanded to {0,7}),
# vectorised with numpy over each constant's digit string, then exact verification of the 14-letter window and maximal
# consecutive extension of the full source string. Usage: python3 scan.py probes.json const1.txt [const2.txt ...]
import sys, json, itertools, time, os
import numpy as np
P = json.load(open(sys.argv[1]))
sources = dict(P['sources'])
label_bits = P['label_bits'].replace('a', '0').replace('b', '1')
files = sys.argv[2:]
W, STEP, A = int(os.environ.get('W', 14)), 7, 8  # W<14 only for false-hit-rate calibration
DIG = {c: str(i + 1) for i, c in enumerate('abcdefghi')}
def ok(letter, digit):  # digit is int
    return (digit in (0, 7)) if letter == 'g' else (digit == 'abcdefghi'.index(letter) + 1)
def to_letters(digs):
    return ''.join('g' if ch in '07' else 'abcdefghi'[int(ch) - 1] for ch in digs)

# planted self-test: 120 digits of pi starting at fraction offset 73,000,000 (string index 73,000,001; index 0 is the '3')
PLANT_OFF = 73_000_001
pi_file = [f for f in files if f.endswith('pi.txt')]
if pi_file:
    with open(pi_file[0], 'rb') as fh:
        fh.seek(PLANT_OFF); planted_digits = fh.read(120).decode()
    if len(planted_digits) == 120: sources['PLANTED_pi_7.3e7'] = to_letters(planted_digits)

probes = []  # (source, window_start, pattern_letters)
for nm, s in sources.items():
    starts = list(range(0, len(s) - W + 1, STEP))
    if starts[-1] != len(s) - W: starts.append(len(s) - W)
    for st in starts: probes.append((nm, st, s[st:st + W]))
anchor = {}  # int -> list of (probe_idx, offset_in_window)
exp_false = {}
for pi_, (nm, st, w) in enumerate(probes):
    exp_false[nm] = exp_false.get(nm, 0) + 2 ** w.count('g')
    o = min(range(W - A + 1), key=lambda k: w[k:k + A].count('g'))
    sub = w[o:o + A]
    opts = [('0', '7') if c == 'g' else (DIG[c],) for c in sub]
    for combo in itertools.product(*opts):
        anchor.setdefault(int(''.join(combo)), []).append((pi_, o))
keys = np.array(sorted(anchor), dtype=np.int64)
print(f'probes={len(probes)} anchors={len(keys)}', flush=True)

results = {'probes': len(probes), 'exp_false_per_1e14_positions': exp_false, 'consts': {}}
for f in files:
    t = time.time()
    raw = open(f, 'rb').read()
    d = np.frombuffer(raw, dtype=np.uint8) - 48
    assert d.max() <= 9
    L = len(d)
    v = np.zeros(L - A + 1, dtype=np.int64)
    for j in range(A):
        v *= 10; v += d[j:L - A + 1 + j]
    pos = np.nonzero(np.isin(v, keys, kind='table'))[0]
    del v
    hits = []
    for p in pos.tolist():
        val = int(raw[p:p + A])
        for pi_, o in anchor[val]:
            q = p - o
            if q < 0 or q + W > L: continue
            nm, st, w = probes[pi_]
            if all(ok(w[k], d[q + k]) for k in range(W)):
                s = sources[nm]
                b = 0
                while st - b - 1 >= 0 and q - b - 1 >= 0 and ok(s[st - b - 1], d[q - b - 1]): b += 1
                fw = 0
                while st + W + fw < len(s) and q + W + fw < L and ok(s[st + W + fw], d[q + W + fw]): fw += 1
                run = b + W + fw
                # whole-source aligned agreement (random alignment ~ 0.12)
                s0 = q - st
                agree = sum(1 for k in range(len(s)) if 0 <= s0 + k < L and ok(s[k], d[s0 + k])) / len(s)
                hits.append({'src': nm, 'win': st, 'digit_index': q, 'src_start_digit_index': s0,
                             'run_len': run, 'run_src_range': [st - b, st + W + fw], 'aligned_agree': round(agree, 3)})
    # de-duplicate (overlapping windows of one alignment)
    uniq = {}
    for h in hits:
        key = (h['src'], h['src_start_digit_index'], h['run_src_range'][0])
        uniq[key] = h
    hits = sorted(uniq.values(), key=lambda h: -h['run_len'])
    # oracle for long runs: digits under g -> bits (0->0, 7->1), decode both bit orders, compare with label
    for h in hits:
        if h['run_len'] >= 100:
            s = sources[h['src']]; a0, a1 = h['run_src_range']; s0 = h['src_start_digit_index']
            bits = ''.join('0' if d[s0 + k] == 0 else '1' for k in range(a0, a1) if s[k] == 'g')
            h['g_bits'] = bits
            for inv in (0, 1):
                bb = bits if not inv else bits.translate(str.maketrans('01', '10'))
                for order in ('msb', 'lsb'):
                    chars = [bb[i:i + 8] if order == 'msb' else bb[i:i + 8][::-1] for i in range(0, len(bb) - 7, 8)]
                    h[f'ascii_{order}_inv{inv}'] = ''.join(chr(int(c, 2)) if 32 <= int(c, 2) < 127 else '.' for c in chars)
            h['label_prefix_match'] = bits[:len(label_bits)] == label_bits[:len(bits)]
            h['g_digits_true'] = ''.join(str(d[s0 + k]) for k in range(a0, a1) if s[k] == 'g')[:60]
    results['consts'][f] = {'ndigits': L, 'anchor_candidates': len(pos), 'hits14': hits, 'secs': round(time.time() - t, 1)}
    print(f, L, 'anchor-cands', len(pos), 'hits14', [(h['src'], h['digit_index'], h['run_len'], h['aligned_agree']) for h in hits],
          f'{time.time() - t:.1f}s', flush=True)
json.dump(results, open(f'scan_results_W{W}.json', 'w'), indent=1)
