"""faed / head538 / reversed: decimal (a..i=1..9, g=0|7) -> integer -> base 26 (a=0) or base 27 (0=space) letters.
Top-down beam over the g choices: after each digit, the output prefix fixed for every completion is the common prefix
of floor(lo/R^e) and floor((hi-1)/R^e). Quadgram-scored; planted English control must be recovered first."""
import sys, math, random, functools, builtins
print = functools.partial(builtins.print, flush=True)
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch'); sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/construction_forensics')
from common import FAED
from quad_indep import LOGP, FLOOR
V = {c: i + 1 for i, c in enumerate('abcdefghi')}
def beam(s, R, W=800):
    L = len(s); A = ('abcdefghijklmnopqrstuvwxyz' if R == 26 else ' abcdefghijklmnopqrstuvwxyz')
    lo_full = int(''.join('0' if c == 'g' else str(V[c]) for c in s)); K = 1
    while R ** K <= lo_full: K += 1   # approx output length (top may vary by 1; handled by e range)
    P10 = [10 ** k for k in range(L + 1)]
    states = [(0.0, 0, '')]  # (score, prefix value v, letters)
    for P in range(1, L + 1):
        c = s[P - 1]; digs = ('0', '7') if c == 'g' else (str(V[c]),)
        new = []
        for sc, v, t in states:
            for d in digs:
                v2 = v * 10 + int(d); lo = v2 * P10[L - P]; hi = (v2 + 1) * P10[L - P] - 1
                # how many leading letters are fixed?
                m = len(t); e = None
                # total letters of lo
                kl = K if R ** (K - 1) <= lo else K - 1
                if lo == 0 or (hi.bit_length() and (R ** kl <= hi)): new.append((sc, v2, t)); continue
                # extend fixed prefix greedily
                tt = t; scc = sc
                while len(tt) < kl:
                    e = kl - len(tt) - 1
                    a, b = lo // R ** e, hi // R ** e
                    if a != b: break
                    ch = A[a % R]; tt += ch
                    q = tt.replace(' ', '')
                    if len(q) >= 4 and ch != ' ': scc += LOGP.get(q[-4:], FLOOR)
                new.append((scc, v2, tt))
        new.sort(key=lambda x: x[0] / max(1, len(x[2].replace(' ', ''))), reverse=True)
        states = new[:W]
    best = states[0]; q = best[2].replace(' ', '')
    return best[0] / max(1, len(q) - 3), best[2]
if __name__ == '__main__':
    eng = ('theprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfundstolive' * 6)[:380]
    n = 0
    for ch in eng: n = n * 26 + (ord(ch) - 97)
    plant = ''.join('g' if d in '07' else 'abcdefghi'[int(d) - 1] for d in str(n))
    sc, t = beam(plant, 26); print('PLANT len', len(plant), 'g', plant.count('g'), 'score', round(sc, 2), t[:80])
    assert t[:60] == eng[:60], 'plant not recovered'
    rnd = ''.join(random.choice('abcdefghig') for _ in range(570))
    for R in (26, 27):
        print('CONTROL random R', R, [round(x, 2) if isinstance(x, float) else x[:60] for x in beam(rnd, R)])
    for label, s in (('faed', FAED), ('head538', FAED[:538]), ('faed_rev', FAED[::-1])):
        for R in (26, 27):
            sc, t = beam(s, R); print(label, 'R', R, 'score', round(sc, 2), repr(t[:90]))
