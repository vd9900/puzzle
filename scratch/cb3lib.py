# Shared straddling-checkerboard decoder + readability scorer for lens classical_crypto (round 3).
import sys, re, pickle, random, math, os
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED, primes_upto
LOGP, FLOOR = pickle.load(open('/home/vin/bitcoin_puzzle/scratch/quadgrams_clean.pkl', 'rb'))
RES61 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeeae'
RES60 = RES61[:-1]
VIC = '15165943121972409169171213758951813141543131412428154191312181219433121171617137149110916631213131281491109166131412199114371612126021664313711154112'
A0 = str.maketrans('abcdefghi', '012345678'); A1 = str.maketrans('abcdefghi', '123456789')
P = set(primes_upto(1000))
TOP, ROW1, ROW2 = 'fubcdora', '/lethingky', 'mvpszjqwx.'
DBBI_ORDER = ''.join(dict.fromkeys(DBBI))      # dbifhcega
FAED_ORDER = ''.join(dict.fromkeys(FAED))      # faedgcbhi
WORDS = set()
for p in ('/usr/share/dict/words', '/usr/share/dict/american-english'):
    if os.path.exists(p):
        WORDS |= {w.strip().lower() for w in open(p, errors='ignore') if w.strip().isalpha() and len(w.strip()) >= 4}
WORDS |= {'bitcoin', 'private', 'key', 'seed', 'wallet', 'matrix', 'neo', 'door', 'prime', 'rabbit', 'white', 'password', 'phase', 'cosmic', 'duality', 'half', 'better', 'oracle', 'architect', 'merovingian', 'choice', 'source', 'zion', 'trinity', 'morpheus', 'smith', 'causality', 'puzzle', 'gsmg', 'btc', 'satoshi', 'nakamoto', 'hash', 'sha', 'cipher', 'brainwallet'}
def make_board(esc=('1', '4'), top=TOP, rows=(ROW1, ROW2), colperm='0123456789'):
    """colperm: string of 10 digits; column j of the physical board carries digit colperm[j]."""
    b = {}
    cols = list(colperm)
    non = [d for d in cols if d not in esc]
    for d, l in zip(non, top): b[d] = l
    for e, r in zip(esc, rows):
        for j, l in enumerate(r): b[e + cols[j]] = l
    return b
def decode(digits, board, esc):
    out = []; i = 0; n = len(digits)
    while i < n:
        c = digits[i]; i += 1
        if c in esc:
            if i == n: out.append('?'); break
            c += digits[i]; i += 1
        out.append(board.get(c, '?'))
    return ''.join(out)
def letters(t): return re.sub('[^a-z]', '', t)
def qscore(t):
    t = letters(t)
    if len(t) < 6: return FLOOR
    return sum(LOGP.get(t[i:i+4], FLOOR) for i in range(len(t) - 3)) / (len(t) - 3)
def frags(t, minlen=5):
    t = letters(t); found = set()
    for L in range(minlen, 13):
        for i in range(len(t) - L + 1):
            w = t[i:i+L]
            if w in WORDS: found.add(w)
    return sorted(found, key=len, reverse=True)[:8]
def zscore(digits, fn, trials=30, seed=0):
    """z of fn(digits) vs fn(shuffled digits)."""
    r = random.Random(seed); l = list(digits); vals = []
    for _ in range(trials):
        r.shuffle(l); vals.append(fn(''.join(l)))
    m = sum(vals) / trials; sd = (sum((v - m) ** 2 for v in vals) / trials) ** .5 or 1e-9
    return (fn(digits) - m) / sd
def prime_mode(sym, mode, zero='0'):
    """sym: symbol string (letters or digits). mode none/zero/drop on 1-based physical prime positions."""
    if mode == 'none': return sym
    if mode == 'zero': return ''.join(zero if (i + 1) in P else c for i, c in enumerate(sym))
    if mode == 'drop': return ''.join(c for i, c in enumerate(sym) if (i + 1) not in P)
    raise ValueError(mode)
