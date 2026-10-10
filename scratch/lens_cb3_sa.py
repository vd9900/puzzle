# SA cryptogram over straddling-checkerboard tokenisations (unknown board, every escape pair over a0 digits), clean quadgram model.
import sys, re, random, json, itertools, statistics, math
from cb3lib import *
ALPHA = 'abcdefghijklmnopqrstuvwxyz'
def tokenize(d, esc):
    toks = []; i = 0
    while i < len(d):
        c = d[i]; i += 1
        if c in esc and i < len(d): c += d[i]; i += 1
        toks.append(c)
    return toks
def qsum(t): return sum(LOGP.get(t[i:i+4], FLOOR) for i in range(len(t) - 3))
def solve(idx, n, restarts, iters, rng, T0=1.5, T1=0.02):
    best = (-1e18, '')
    for _ in range(restarts):
        key = (list(ALPHA) + ['?'] * max(0, n - 26))[:max(n, 26)]; rng.shuffle(key)
        txt = lambda: ''.join(key[i] for i in idx).replace('?', '')
        cur = qsum(txt()); lbest = (cur, txt())
        for it in range(iters):
            T = T0 * (T1 / T0) ** (it / iters)
            a, b = rng.sample(range(len(key)), 2)
            key[a], key[b] = key[b], key[a]
            s = qsum(txt()); d = s - cur
            if d >= 0 or rng.random() < math.exp(d / T):
                cur = s
                if cur > lbest[0]: lbest = (cur, txt())
            else: key[a], key[b] = key[b], key[a]
        if lbest[0] > best[0]: best = lbest
    return best
def run(name, digits, pairs, restarts, iters, ctrl, out, seed=1):
    rng = random.Random(seed); res = []
    for esc in pairs:
        toks = tokenize(digits, esc); types = sorted(set(toks)); n = len(types)
        if n < 10 or n > 28: continue
        idx = [types.index(t) for t in toks]
        sc, txt = solve(idx, n, restarts, iters, rng); per = sc / max(1, len(txt) - 3)
        cs = []
        for _ in range(ctrl):
            sh = idx[:]; rng.shuffle(sh); c, _t = solve(sh, n, restarts, iters, rng); cs.append(c / max(1, len(_t) - 3))
        m = statistics.mean(cs); sd = (statistics.pstdev(cs) if len(cs) > 1 else 0.05) or 0.05; z = (per - m) / sd
        r = {'src': name, 'esc': ''.join(esc), 'ntok': len(toks), 'types': n, 'q': round(per, 3), 'ctrl_mean': round(m, 3), 'z': round(z, 2), 'frags': frags(txt), 'text': txt}
        res.append(r); print(json.dumps(r), flush=True)
        if out and not name.startswith('CTRL'): out.write(txt + '\n'); out.flush()
    return res
if __name__ == '__main__':
    pairs = list(itertools.combinations('012345678', 2))
    out = open('/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_classical_crypto_sa.txt', 'w')
    print('POSITIVE CONTROL vic esc14'); run('CTRL_vic', VIC, [('1', '4')], 3, 5000, 2, out)
    run('faed', FAED.translate(A0), pairs, 3, 5000, 2, out)
    run('faed_rev', FAED[::-1].translate(A0), pairs, 3, 5000, 1, out)
    run('dbbi', DBBI.translate(A0), pairs, 3, 4000, 2, out)
    run('res61', RES61.translate(A0), pairs, 3, 4000, 2, out)
