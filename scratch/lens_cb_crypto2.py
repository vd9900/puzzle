# Simulated-annealing cryptogram solver over straddling-checkerboard tokenizations, with positive controls.
import sys, re, random, json, itertools, statistics, math
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED
import pickle; LOGP, FLOOR = pickle.load(open("/home/vin/bitcoin_puzzle/scratch/quadgrams_clean.pkl", "rb"))
RES60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
VIC = '15165943121972409169171213758951813141543131412428154191312181219433121171617137149110916631213131281491109166131412199114371612126021664313711154112'
A0 = str.maketrans('abcdefghi', '012345678')
ALPHA = 'abcdefghijklmnopqrstuvwxyz'
BOARD = dict(zip('02356789', 'fubcdora')); BOARD.update({'1' + str(c): l for c, l in enumerate('/lethingky')}); BOARD.update({'4' + str(c): l for c, l in enumerate('mvpszjqwx.')})
ENC = {v: k for k, v in BOARD.items()}
def tokenize(d, esc):
    toks = []; i = 0
    while i < len(d):
        c = d[i]; i += 1
        if c in esc and i < len(d): c += d[i]; i += 1
        toks.append(c)
    return toks
def qsum(t): return sum(LOGP.get(t[i:i+4], FLOOR) for i in range(len(t) - 3))
def solve(idx, n, restarts, iters, rng, T0=2.0, T1=0.02):
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
def run(name, digits, pairs, restarts, iters, ctrl, out=None, seed=1):
    rng = random.Random(seed); res = []
    for esc in pairs:
        toks = tokenize(digits, esc); types = sorted(set(toks)); n = len(types)
        if n < 12 or n > 28: continue
        idx = [types.index(t) for t in toks]
        sc, txt = solve(idx, n, restarts, iters, rng); per = sc / max(1, len(txt) - 3)
        cs = []
        for _ in range(ctrl):
            sh = idx[:]; rng.shuffle(sh); c, _t = solve(sh, n, restarts, iters, rng); cs.append(c / max(1, len(_t) - 3))
        m = statistics.mean(cs) if cs else 0; sd = (statistics.pstdev(cs) if len(cs) > 1 else 1e-9) or 1e-9; z = (per - m) / sd
        r = {'src': name, 'esc': ''.join(esc), 'ntok': len(toks), 'types': n, 'q': round(per, 3), 'ctrl_mean': round(m, 3), 'z': round(z, 2), 'text': txt}
        res.append(r); print(json.dumps(r), flush=True)
        if out: out.write(txt + '\n'); out.flush()
    return res
if __name__ == '__main__':
    which = sys.argv[1]
    pairs = list(itertools.combinations('0123456789', 2))
    out = open(f'/home/vin/bitcoin_puzzle/scratch/wf/cands_lens_classical_crypto_cryptogram2_{which}.txt', 'w')
    if which == 'control':
        print('CONTROL A: vic 91 tokens'); run('vic', VIC, [('1', '4')], 8, 8000, 3)
        sp = re.sub('[^a-z]', '', open('/home/vin/bitcoin_puzzle/research/artifacts/phase32-beaufort.txt').read())[:300]
        enc = ''.join(ENC[c] for c in sp); print('CONTROL B: speech 300 letters ->', len(enc), 'digits'); run('speech300', enc, [('1', '4')], 5, 8000, 2)
    elif which == 'short':
        run('dbbi', DBBI.translate(A0), pairs, 6, 6000, 4, out=out)
        run('res60', RES60.translate(A0), pairs, 6, 6000, 4, out=out)
    else:
        run('faed', FAED.translate(A0), pairs, 4, 6000, 2, out=out)
