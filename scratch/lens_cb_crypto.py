# Cryptogram hill-climb over straddling-checkerboard tokenizations (escape pair unknown, board unknown).
import sys, re, random, json, itertools, statistics
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED
from textmodel import LOGP, FLOOR
RES60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
VIC = '15165943121972409169171213758951813141543131412428154191312181219433121171617137149110916631213131281491109166131412199114371612126021664313711154112'
A0 = str.maketrans('abcdefghi', '012345678')
ALPHA = 'abcdefghijklmnopqrstuvwxyz'
def tokenize(d, esc):
    toks = []; i = 0
    while i < len(d):
        c = d[i]; i += 1
        if c in esc and i < len(d): c += d[i]; i += 1
        toks.append(c)
    return toks
def qsum(t): return sum(LOGP.get(t[i:i+4], FLOOR) for i in range(len(t) - 3))
def solve(idx, n, restarts, iters, rng):
    best = (-1e18, '')
    for _ in range(restarts):
        key = list(ALPHA) + ['?'] * max(0, n - 26); key = key[:n] if n <= 26 else key; rng.shuffle(key)
        txt = lambda: ''.join(key[i] for i in idx).replace('?', '')
        cur = qsum(txt()); stale = 0
        for _ in range(iters):
            a, b = rng.sample(range(n), 2)
            key[a], key[b] = key[b], key[a]
            s = qsum(txt())
            if s >= cur: cur = s; stale = 0
            else: key[a], key[b] = key[b], key[a]; stale += 1
            if stale > 500: break
        if cur > best[0]: best = (cur, txt())
    return best
def run(name, digits, pairs, restarts=4, iters=4000, ctrl=6, out=None):
    rng = random.Random(1); res = []
    for esc in pairs:
        toks = tokenize(digits, esc); types = sorted(set(toks)); n = len(types)
        if n < 12 or n > 28: continue
        idx = [types.index(t) for t in toks]
        sc, txt = solve(idx, n, restarts, iters, rng); per = sc / max(1, len(txt) - 3)
        cs = []
        for _ in range(ctrl):
            sh = idx[:]; rng.shuffle(sh); c, _t = solve(sh, n, max(2, restarts - 1), iters, rng); cs.append(c / max(1, len(_t) - 3))
        m = statistics.mean(cs); sd = statistics.pstdev(cs) or 1e-9; z = (per - m) / sd
        r = {'src': name, 'esc': ''.join(esc), 'ntok': len(toks), 'types': n, 'q': round(per, 3), 'ctrl_mean': round(m, 3), 'z': round(z, 2), 'text': txt}
        res.append(r); print(json.dumps(r), flush=True)
        if out: out.write(txt + '\n'); out.flush()
    return res
if __name__ == '__main__':
    which = sys.argv[1]
    pairs = list(itertools.combinations('0123456789', 2))
    out = open(f'/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_classical_crypto_cryptogram_{which}.txt', 'w')
    if which == 'short':
        print('POSITIVE CONTROL (vic, esc 14):'); run('vic', VIC, [('1', '4')], out=out)
        run('dbbi', DBBI.translate(A0), pairs, out=out)
        run('res60', RES60.translate(A0), pairs, out=out)
    else:
        run('faed', FAED.translate(A0), pairs, restarts=3, iters=4000, ctrl=5, out=out)
