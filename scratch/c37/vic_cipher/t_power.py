# Power of the stage-1 detectors (hcond z, adjacent-equal z) at the RIGHT key, for several plaintext types,
# full VIC (AT ONE SIR board, S-keyed), 0 hidden in letter g, compared with the observed null floor over ~1M derivations
# (control minima z: -5.93..-6.35, ez maxima 5.02..5.35).
import sys, re, random
sys.path.insert(0, '.')
import numpy as np, vic, vicfast as V
txt = re.sub('[^A-Z]', '', open('carroll.txt').read().upper())
bip = [w.strip().upper() for w in open('/home/vin/.venvs/open-crypto-puzzles/lib/python3.12/site-packages/mnemonic/wordlist/english.txt')]
B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
rnd = random.Random(11)
def ptext(kind):
    if kind == 'english': i = rnd.randrange(len(txt) - 2000); return txt[i:i + 900]
    if kind == 'bip39': return ''.join(rnd.choice(bip) for _ in range(150))
    if kind == 'random_letters': return ''.join(rnd.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(600))
    if kind in ('wif_base58', 'hex64'):
        alph = B58 if kind == 'wif_base58' else '0123456789ABCDEF'
        return ''.join(rnd.choice(alph) for _ in range(400))
def encode(text, enc):
    st = ''
    for run in re.findall('[0-9]+|[A-Za-z]+', text):
        if run[0].isdigit(): st += enc['/'] + ''.join(d * 3 for d in run) + enc['/']
        else: st += ''.join(enc[c.upper()] for c in run)
    return st
res = {}
for kind in ['english', 'bip39', 'random_letters', 'wif_base58', 'hex64']:
    zs, ezs = [], []
    for t in range(12):
        phrase = ''.join(rnd.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(20))
        kg = ''.join(rnd.choice('0123456789') for _ in range(5)); pn = rnd.randint(1, 16)
        k = vic.derive(phrase, '1192001', pn, kg)
        enc, dec, esc = vic.vic_board(k['S'])
        st = encode(ptext(kind), enc)[:565]
        while len(st) < 565: st += '0'
        u_true = V.to_idx(''.join({**{str(i + 1): c for i, c in enumerate(V.LET)}, '0': 'g'}[d] for d in st))
        mu, sd = V.null_stats(u_true, 9, trials=300)
        b = u_true.copy(); r = np.random.default_rng(1); eq = []
        for _ in range(300): r.shuffle(b); eq.append(int((b[1:] == b[:-1]).sum()))
        zs.append((V.hcond_arr(u_true, 9) - mu) / sd); ezs.append((int((u_true[1:] == u_true[:-1]).sum()) - np.mean(eq)) / np.std(eq))
    zs, ezs = np.array(zs), np.array(ezs)
    det = ((zs < -6.6) | (ezs > 5.4)).mean()
    print('%-15s right-key z: median %.2f min %.2f max %.2f | ez median %.2f | detected beyond null floor: %.2f' % (kind, np.median(zs), zs.min(), zs.max(), np.median(ezs), det))
