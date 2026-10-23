"""Cycle 40 (4): straddling checkerboard (Phase 3.2 board, escapes 1,4) and Bifid (dbbi square) on the prime-split
streams, clean Carroll quadgram score vs shuffled-letter controls (same composition; max over variants to control
multiplicity). Plus dbbi physical-prime letters vs the 24 colour bits. Self-tests: planted English recovered and scored."""
import sys, json, random, re, math
from collections import Counter
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch'); sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/construction_forensics')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/digit_codecs')
from common import DBBI, FAED, BIN1, primes_upto
from bifid import bifid_decrypt, bifid_encrypt, CANON
from quad_indep import LOGP, FLOOR
PR = set(primes_upto(1000))
def split(s, base):
    return (''.join(c for i, c in enumerate(s) if (i + base) in PR), ''.join(c for i, c in enumerate(s) if (i + base) not in PR))
P1, N1 = split(FAED, 1); P0, N0 = split(FAED, 0)
ST = {'P1': P1, 'N1': N1, 'P0': P0, 'N0': N0}; ST.update({k + '_rev': v[::-1] for k, v in list(ST.items())})
def q(t):
    t = re.sub('[^a-z]', '', t)
    return FLOOR if len(t) < 6 else sum(LOGP.get(t[i:i+4], FLOOR) for i in range(len(t) - 3)) / (len(t) - 3)
TOP, ROW1, ROW2 = 'fubcdora', '/lethingky', 'mvpszjqwx.'
def board(esc=('1', '4')):
    b = {}; non = [d for d in '0123456789' if d not in esc]
    for d, l in zip(non, TOP): b[d] = l
    for e, r in zip(esc, (ROW1, ROW2)):
        for j, l in enumerate(r): b[e + str(j)] = l
    return b
B = board()
def cb_decode(dig, esc=('1', '4')):
    out = []; i = 0
    while i < len(dig):
        c = dig[i]; i += 1
        if c in esc:
            if i == len(dig): break
            c += dig[i]; i += 1
        out.append(B.get(c, '?'))
    return ''.join(out)
def cb_encode(txt):
    inv = {v: k for k, v in B.items()}; return ''.join(inv[ch] for ch in txt)
MAPS = {'a0': 'abcdefghi', 'a1': None, 'dbbiord0': ''.join(dict.fromkeys(DBBI)), 'faedord0': ''.join(dict.fromkeys(FAED))}
def to_dig(s, m):
    if m == 'a1': return s.translate(str.maketrans('abcdefghi', '123456789'))
    return s.translate(str.maketrans(MAPS[m], '012345678'))
def cb_best(s):
    best = (-99, None)
    for m in MAPS:
        sc = q(cb_decode(to_dig(s, m)))
        if sc > best[0]: best = (sc, m)
    return best
PERIODS = [0] + list(range(2, 26))
def bf_best(s):
    best = (-99, None)
    for p in PERIODS:
        sc = q(bifid_decrypt(s, CANON, p or len(s)))
        if sc > best[0]: best = (sc, p)
    return best
# self-tests: planted English through each pipeline must decode and score far above controls
ENG = ('itwasthebestoftimesitwastheworstoftimesitwastheageofwisdomitwastheageoffoolishnessitwastheepochofbelief'
       'itwastheepochofincredulityitwastheseasonoflightitwastheseasonofdarkness')
dg = cb_encode(ENG); assert cb_decode(dg) == ENG
amap = str.maketrans('012345678', 'abcdefghi'); planted_cb = dg.replace('9', '')[:104].translate(amap)  # imperfect plant (digit 9 dropped)
ct = bifid_encrypt(ENG[:104].replace('j', 'i'), CANON, 7); assert bifid_decrypt(ct, CANON, 7) == ENG[:104].replace('j', 'i')
print('plant check: english q =', round(q(ENG), 3), ' bifid-plant best', bf_best(ct))
R = random.Random(7); NC = 200; res = {}
def control(fn, s, n=NC):
    l = list(s); v = []
    for _ in range(n): R.shuffle(l); v.append(fn(''.join(l))[0])
    return v
for k, s in ST.items():
    for name, fn in (('checkerboard', cb_best), ('bifid', bf_best)):
        obs = fn(s); ctrl = control(fn, s); m = sum(ctrl) / len(ctrl); sd = (sum((x - m) ** 2 for x in ctrl) / len(ctrl)) ** .5
        p = (1 + sum(x >= obs[0] for x in ctrl)) / (1 + len(ctrl))
        dec = (cb_decode(to_dig(s, obs[1])) if name == 'checkerboard' else bifid_decrypt(s, CANON, obs[1] or len(s)))
        res[f'{k}/{name}'] = dict(score=round(obs[0], 3), variant=obs[1], ctrl_mean=round(m, 3), ctrl_sd=round(sd, 3),
                                  z=round((obs[0] - m) / sd, 2), p_emp=round(p, 3), sample=dec[:70])
        print(k, name, res[f'{k}/{name}'], flush=True)
# detector power: plant English-bifid of same length in a stream slot; must beat all controls
pw = bf_best(bifid_encrypt((ENG * 3)[:104].replace('j', 'i'), CANON, 0 or 104))
ctrlP = control(bf_best, P1, 100); print('bifid power: plant score', round(pw[0], 3), 'vs max ctrl', round(max(ctrlP), 3)); assert pw[0] > max(ctrlP)
pc = cb_best(cb_encode((ENG * 3)[:60]).translate(amap) if '9' not in cb_encode((ENG * 3)[:60]) else planted_cb)
print('cb plant (a0 map) score', round(pc[0], 3))
# ---------- dbbi physical primes vs 24 colour bits ----------
COL = 'BBBBYBBBYYBBBBYBBYYBWYYBY'; COL24 = COL.replace('W', ''); assert len(COL24) == 24
dres = {}
for base in (1, 0):
    Pd, Nd = split(DBBI, base); assert len(Pd) == 24
    for cname, cb in (('Y=1', COL24.translate(str.maketrans('BY', '01'))),):
        def mi(a, b):
            n = len(a); ca = Counter(a); cb_ = Counter(b); cab = Counter(zip(a, b))
            return sum(v / n * math.log2((v / n) / (ca[x] / n * cb_[y] / n)) for (x, y), v in cab.items())
        def consistent(a, b): return all(len({y for x2, y in zip(a, b) if x2 == x}) == 1 for x in set(a))
        obs = mi(Pd, cb); l = list(cb); ctrl = []; cons = 0
        for _ in range(20000):
            R.shuffle(l); ctrl.append(mi(Pd, ''.join(l))); cons += consistent(Pd, ''.join(l))
        dres[f'base{base}'] = dict(Pd=Pd, bits=cb, letter_counts=Counter(Pd).most_common(), MI=round(obs, 3),
                                    p_MI=round((1 + sum(x >= obs for x in ctrl)) / 20001, 4), letter_to_bit_consistent=consistent(Pd, cb),
                                    p_consistent_null=cons / 20000,
                                    bit_by_letter={x: ''.join(y for x2, y in zip(Pd, cb) if x2 == x) for x in sorted(set(Pd))})
        print('dbbi', base, dres[f'base{base}'], flush=True)
json.dump(dict(streams=res, dbbi_colour=dres), open('/home/vin/bitcoin_puzzle/scratch/c40/primesplit/cb_bifid_results.json', 'w'), indent=0)
