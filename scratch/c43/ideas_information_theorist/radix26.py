"""Length-barrier escape: decimal (a..i=1..9, g=0|7) -> ONE integer -> base-26 letters (a=0 / bijective a=1) or base 27
(0=space). Unlike the z-method (base 256), these outputs are always letters, so the length-feasibility fact does not
exclude text. Small strings (R60, dbbi, tail32, Z-controls): exhaustive over g. faed/head538: top-down beam over g
(base-26 conversion is top-down causal: leading output letters depend only on leading digits + carry).
Oracle: clean quadgram mean log-prob per letter vs English threshold, planted controls."""
import sys, math, itertools, random, functools, builtins
print = functools.partial(builtins.print, flush=True)
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch'); sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch/c37/construction_forensics')
from common import FAED, DBBI
from quad_indep import LOGP, FLOOR
R60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
V = {c: i + 1 for i, c in enumerate('abcdefghi')}
def to_radix(n, mode):
    A = 'abcdefghijklmnopqrstuvwxyz'
    if mode == 'b26':
        s = ''
        while n: n, r = divmod(n, 26); s = A[r] + s
        return s
    if mode == 'bij26':
        s = ''
        while n: n, r = divmod(n - 1, 26); s = A[r] + s
        return s
    if mode == 'b27':
        s = ''
        while n: n, r = divmod(n, 27); s = (' ' + A)[r] + s
        return s
def score(t):
    t = t.replace(' ', '')
    if len(t) < 4: return -9
    return sum(LOGP.get(t[i:i + 4], FLOOR) for i in range(len(t) - 3)) / (len(t) - 3)
def to_letters(digs): return ''.join('g' if d in '07' else 'abcdefghi'[int(d) - 1] for d in digs)
def exhaustive(s, label):
    gp = [i for i, c in enumerate(s) if c == 'g']; best = []
    for bits in range(1 << len(gp)):
        d = list(''.join('0' if c == 'g' else str(V[c]) for c in s))
        for j, p in enumerate(gp):
            if bits >> j & 1: d[p] = '7'
        n = int(''.join(d))
        for mode in ('b26', 'bij26', 'b27'):
            t = to_radix(n, mode); best.append((score(t), mode, t))
    best.sort(reverse=True); print(f'[{label}] g={len(gp)} cands={len(best)} top:', [(round(a, 2), m, t[:50]) for a, m, t in best[:3]])
    return best[0][0]
if __name__ == '__main__':
    # calibration: English text scores ~ -4.5..-5; random letters ~ -6.5+
    eng = 'theprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfunds'
    print('english score', round(score(eng), 2), 'random score', round(score(''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(60))), 2))
    # planted control: english -> base26 int -> decimal -> letters with g, then exhaustive must recover
    n = 0
    for ch in eng[:40]: n = n * 26 + (ord(ch) - 97)
    plant = to_letters(str(n)); print('plant len', len(plant), 'g', plant.count('g'))
    assert exhaustive(plant, 'PLANT') > -5.0, 'plant failed'
    for label, s in (('R60', R60), ('R60rev', R60[::-1]), ('tail32', FAED[538:]), ('tail32rev', FAED[538:][::-1]), ('dbbi', DBBI), ('dbbi_rev', DBBI[::-1])):
        if s.count('g') <= 16: exhaustive(s, label)
        else: print(label, 'skip g=', s.count('g'))
