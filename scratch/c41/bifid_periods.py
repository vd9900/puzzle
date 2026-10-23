"""Bifid decode of faed at every period 2..570 with natural square keys; clean English score vs shuffled-faed controls."""
import sys, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch'); sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/construction_forensics')
from common import FAED, DBBI
from bifid import square_from, bifid_decrypt, bifid_encrypt
from quad_indep import LOGP, FLOOR
R60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
def sc(t): return sum(LOGP.get(t[i:i+4], FLOOR) for i in range(len(t)-3)) / max(1, len(t)-3)
keys = {'dbbi': square_from(DBBI), 'R60': square_from(R60), 'matrixsumlist': square_from('matrixsumlist'),
        'salphaseion': square_from('salphaseion'), 'plain': square_from('')}
rnd = random.Random(1)
ctrl = []
for _ in range(3):
    l = list(FAED); rnd.shuffle(l); ctrl.append(''.join(l))
res = []
for kn, sq in keys.items():
    for p in range(2, 571):
        for d, f in (('dec', bifid_decrypt), ('enc', bifid_encrypt)):
            out = f(FAED, sq, p); s = sc(out)
            cmax = max(sc(f(c, sq, p)) for c in ctrl)
            res.append((s - cmax, s, cmax, kn, p, d, out[:50]))
res.sort(reverse=True)
for r in res[:12]: print(f'margin={r[0]:+.3f} real={r[1]:.3f} ctrlmax={r[2]:.3f} key={r[3]} period={r[4]} {r[5]} {r[6]}')
print('configs', len(res), ' planted-English reference score ~ -4.0, random ~ -6.5')
