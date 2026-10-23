"""CyberChef-natural variant: text -> 'From Base' radix 36 (a..z = 10..35) -> decimal -> letters a..i (g = 0|7).
Inverse: faed digits -> integer -> base 36; a pure-letter source must give ONLY a..z (random: (26/36)^~366 ~ 1e-52).
Top-down beam with digit outputs penalised hard + quadgram score; planted control first. Also small strings exhaustive."""
import sys, functools, builtins, random
print = functools.partial(builtins.print, flush=True)
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch'); sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/construction_forensics')
from common import FAED, DBBI
from quad_indep import LOGP, FLOOR
V = {c: i + 1 for i, c in enumerate('abcdefghi')}
A = '0123456789abcdefghijklmnopqrstuvwxyz'; R = 36; PEN = -40.0
def beam(s, W=800):
    L = len(s); lo_full = int(''.join('0' if c == 'g' else str(V[c]) for c in s)); K = 1
    while R ** K <= lo_full: K += 1
    P10 = [10 ** k for k in range(L + 1)]; states = [(0.0, 0, '')]
    for P in range(1, L + 1):
        c = s[P - 1]; digs = ('0', '7') if c == 'g' else (str(V[c]),); new = []
        for sc, v, t in states:
            for d in digs:
                v2 = v * 10 + int(d); lo = v2 * P10[L - P]; hi = (v2 + 1) * P10[L - P] - 1
                kl = K if R ** (K - 1) <= lo else K - 1
                if lo == 0 or R ** kl <= hi: new.append((sc, v2, t)); continue
                tt, scc = t, sc
                while len(tt) < kl:
                    e = kl - len(tt) - 1; a, b = lo // R ** e, hi // R ** e
                    if a != b: break
                    ch = A[a % R]; tt += ch
                    if ch.isdigit(): scc += PEN
                    elif len(tt) >= 4 and not any(x.isdigit() for x in tt[-4:]): scc += LOGP.get(tt[-4:], FLOOR)
                new.append((scc, v2, tt))
        new.sort(key=lambda x: x[0] / max(1, len(x[2])), reverse=True); states = new[:W]
    sc, _, t = states[0]
    return round(sc / max(1, len(t)), 2), sum(ch.isdigit() for ch in t), len(t), t
if __name__ == '__main__':
    eng = ('theprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfundstolive' * 6)[:360]
    n = 0
    for ch in eng: n = n * 36 + A.index(ch)
    plant = ''.join('g' if d in '07' else 'abcdefghi'[int(d) - 1] for d in str(n))
    r = beam(plant); print('PLANT', len(plant), 'g', plant.count('g'), r[:3], r[3][:60]); assert r[3][:60] == eng[:60]
    rnd = ''.join(random.choice('abcdefghig') for _ in range(570)); r = beam(rnd); print('CONTROL random', r[:3], r[3][:60])
    R60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
    for label, s in (('faed', FAED), ('head538', FAED[:538]), ('faed_rev', FAED[::-1]), ('R60', R60), ('R60rev', R60[::-1]),
                     ('dbbi', DBBI), ('dbbi_rev', DBBI[::-1]), ('tail32', FAED[538:]), ('tail32rev', FAED[538:][::-1])):
        r = beam(s, W=2000 if len(s) < 100 else 800); print(label, 'score/len', r[0], 'digit-chars', r[1], 'of', r[2], repr(r[3][:80]))
