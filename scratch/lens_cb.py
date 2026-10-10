# Lens classical_crypto: straddling-checkerboard decodes of dbbi / residual / faed with the solved Phase 3.2 board.
import sys, re, random, json, itertools
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED, primes_upto, sha256hex
from textmodel import score as qscore
from collections import Counter

RES60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
RES61 = RES60 + 'e'
SOURCES = {'dbbi': DBBI, 'res60': RES60, 'res61': RES61, 'faed': FAED}
MAPS = {'a0': str.maketrans('abcdefghi', '012345678'), 'a1': str.maketrans('abcdefghi', '123456789')}
P = set(primes_upto(600))
WORDS = set(w.strip().lower() for w in open('/usr/share/dict/words') if re.fullmatch(r'[a-z]{3,}', w.strip()))
MAXW = 12

def make_board(row0, row1, row4, esc=('1', '4')):
    singles = [d for d in '0123456789' if d not in esc]
    assert len(row0) == 8 and len(row1) == 10 and len(row4) == 10, (row0, row1, row4)
    b = dict(zip(singles, row0))
    b.update({esc[0] + str(c): l for c, l in enumerate(row1)})
    b.update({esc[1] + str(c): l for c, l in enumerate(row4)})
    return b, esc

def decode(digits, board):
    b, esc = board
    out = []; i = 0; n = len(digits)
    while i < n:
        c = digits[i]; i += 1
        if c in esc:
            if i < n: c += digits[i]; i += 1
            else: out.append('?'); break
        out.append(b.get(c, '?'))
    return ''.join(out)

def zero_primes(d): return ''.join('0' if (i + 1) in P else c for i, c in enumerate(d))
def drop_primes(d): return ''.join(c for i, c in enumerate(d) if (i + 1) not in P)

def coverage(t):
    """greedy longest dictionary-word coverage (letters only) and list of words len>=5 found as substrings"""
    t = re.sub('[^a-z]', '', t)
    n = len(t); i = 0; cov = 0; words = []
    while i < n:
        for L in range(min(MAXW, n - i), 2, -1):
            if t[i:i + L] in WORDS:
                cov += L; words.append(t[i:i + L]); i += L; break
        else: i += 1
    frags = sorted({t[i:i + L] for i in range(n) for L in range(5, min(MAXW, n - i) + 1) if t[i:i + L] in WORDS}, key=len, reverse=True)
    return cov / max(1, n), frags

def zscore(t, trials=100, seed=0):
    letters = re.sub('[^a-z]', '', t)
    if len(letters) < 8: return 0.0
    s = qscore(letters); r = random.Random(seed); l = list(letters); vals = []
    for _ in range(trials):
        r.shuffle(l); vals.append(qscore(''.join(l)))
    m = sum(vals) / trials; sd = (sum((v - m) ** 2 for v in vals) / trials) ** .5 or 1e-9
    return (s - m) / sd

# ---- boards ----
STD = make_board('fubcdora', '/lethingky', 'mvpszjqwx.')
order = ''.join(dict.fromkeys(DBBI))            # first-occurrence order
assert order == 'dbifhcega', order
keyed26 = order + ''.join(c for c in 'abcdefghijklmnopqrstuvwxyz' if c not in order)
assert len(keyed26) == 26
perm_a0 = [int(c) for c in order.translate(MAPS['a0'])] + [9]      # 3,1,8,5,7,2,4,6,0,9
perm_a1 = [int(c) for c in order.translate(MAPS['a1'])] + [0]      # 4,2,9,6,8,3,5,7,1,0
def permute(row, perm): return ''.join(row[p] for p in perm)
def permute_inv(row, perm):
    out = [''] * 10
    for k, p in enumerate(perm): out[p] = row[k]
    return ''.join(out)
esc_keyed = ''.join(dict.fromkeys(c for c in order + 'lethingkymvpszjqwx' if c in 'lethingkymvpszjqwx'))
assert len(esc_keyed) == 18, esc_keyed
BOARDS = {
    'STD': STD,
    'ESC25naive': make_board('fubcdora', '/lethingky', 'mvpszjqwx.', esc=('2', '5')),
    'RK1_keyed26_slash_first': make_board(keyed26[:8], '/' + keyed26[8:17], keyed26[17:] + '.'),
    'RK2_keyed26_fillers_last': make_board(keyed26[:8], keyed26[8:18], keyed26[18:] + '/.'),
    'RK3_keyed26_fillers_first': make_board(keyed26[:8], '/.' + keyed26[8:16], keyed26[16:]),
    'RK4a_escrows_perm_a0': make_board('fubcdora', permute('/lethingky', perm_a0), permute('mvpszjqwx.', perm_a0)),
    'RK4b_escrows_perminv_a0': make_board('fubcdora', permute_inv('/lethingky', perm_a0), permute_inv('mvpszjqwx.', perm_a0)),
    'RK4c_escrows_perm_a1': make_board('fubcdora', permute('/lethingky', perm_a1), permute('mvpszjqwx.', perm_a1)),
    'RK4d_escrows_perminv_a1': make_board('fubcdora', permute_inv('/lethingky', perm_a1), permute_inv('mvpszjqwx.', perm_a1)),
    # escape rows keyed by dbbi order letters directly (order letters then rest), singles untouched
    'RK5_escrows_from_order': make_board('fubcdora', '/' + esc_keyed[:9], esc_keyed[9:] + '.'),
}

# ---- positive control ----
vic = '15165943121972409169171213758951813141543131412428154191312181219433121171617137149110916631213131281491109166131412199114371612126021664313711154112'
ctrl = decode(vic, STD)
assert ctrl.startswith('incaseyoumanage'), ctrl
print('CONTROL vic decode q=%.2f z=%.1f cov=%.2f' % (qscore(ctrl), zscore(ctrl), coverage(ctrl)[0]))

rows = []
cands = []
for bname, board in BOARDS.items():
    for sname, s in SOURCES.items():
        for mname, mp in MAPS.items():
            d0 = s.translate(mp)
            for zname, zf in (('none', lambda x: x), ('zero', zero_primes), ('drop', drop_primes)):
                d1 = zf(d0)
                for rd in (False, True):
                    d2 = d1[::-1] if rd else d1
                    dec = decode(d2, board)
                    for rt in (False, True):
                        txt = dec[::-1] if rt else dec
                        tag = f'{bname}|{sname}|{mname}|{zname}|revdig={int(rd)}|revtxt={int(rt)}'
                        cov, frags = coverage(txt)
                        rows.append({'tag': tag, 'q': round(qscore(txt), 3), 'z': round(zscore(txt), 2), 'cov': round(cov, 3),
                                     'len': len(txt), 'qmarks': txt.count('?'), 'frags': frags[:8], 'text': txt})
                        cands.append((tag, txt))
                        cands.append((tag + '|letters', re.sub('[^a-z]', '', txt)))
                        if not rt: cands.append((tag + '|digits', d2))

rows.sort(key=lambda r: -r['q'])
json.dump(rows, open('/home/vin/bitcoin_puzzle/scratch/wf/lens_classical_crypto_rows.json', 'w'), indent=0)
seen = set()
with open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_classical_crypto.txt', 'w') as fh:
    for tag, c in cands:
        if c and c not in seen:
            seen.add(c); fh.write(c + '\n')
print('candidates written:', len(seen))
print('\nTOP 25 by quadgram score:')
for r in rows[:25]:
    print(f"{r['q']:7.3f} z={r['z']:5.1f} cov={r['cov']:.2f} ?={r['qmarks']:2d} {r['tag']}\n        {r['text'][:100]}\n        frags={r['frags']}")
print('\nSTD board, all variants (sorted):')
for r in [r for r in rows if r['tag'].startswith('STD|')][:16]:
    print(f"{r['q']:7.3f} z={r['z']:5.1f} cov={r['cov']:.2f} {r['tag']}  {r['text'][:90]}")
import statistics
print('\nscore distribution: n=%d median q=%.2f max q=%.2f ; z>3: %d ; cov>0.5: %d' % (
    len(rows), statistics.median(r['q'] for r in rows), max(r['q'] for r in rows), sum(r['z'] > 3 for r in rows), sum(r['cov'] > .5 for r in rows)))
