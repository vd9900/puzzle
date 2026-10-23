"""'prime basics' (2,3,5,7 = b,c,e,g) 'zeroed out' -> faed as a bit stream? Generalised: every 2-class partition of a..i.
Detector: ASCII structure = fraction of 8-bit (or 7-bit) groups that are printable (8-bit: MSB=0 and 0x20..0x7e).
Self-verifying: real text gives ~100%; random bits give ~37% (8-bit) / ~74% (7-bit). Compare with shuffled-faed controls."""
import sys, random, itertools
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import FAED, DBBI
R61 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeeae'
L = 'abcdefghi'
parts = [set(c) for k in range(1, 5) for c in itertools.combinations(L, k)]  # 255 up to complement (k<=4 covers all since 9 odd)
def best(s):
    out = []
    for P in parts:
        for inv in (0, 1):
            bits = ''.join(('1' if (c in P) ^ inv else '0') for c in s)
            for g in (7, 8):
                for off in range(g):
                    b = bits[off:]; n = len(b) // g
                    if n < 8: continue
                    vals = [int(b[i*g:(i+1)*g], 2) for i in range(n)]
                    for rev in (0, 1):
                        vv = vals if not rev else [int(format(v, f'0{g}b')[::-1], 2) for v in vals]
                        pr = sum(32 <= v < 127 for v in vv) / n
                        out.append((pr, ''.join(sorted(P)), inv, g, off, rev, bytes(v for v in vv if v < 256)[:40]))
    out.sort(key=lambda r: -r[0]); return out
for name, s in (('faed', FAED), ('dbbi', DBBI), ('R61', R61)):
    o = best(s)
    pb = [r for r in o if r[1] == 'bceg']
    print(f'{name}: top={o[0][:6]} sample={o[0][6]!r}')
    print(f'   prime-digit partition bceg best={pb[0][:6]} sample={pb[0][6]!r}')
    rnd = random.Random(1); ctl = []
    for _ in range(3):
        sh = ''.join(rnd.sample(s, len(s))); ctl.append(round(best(sh)[0][0], 3))
    print(f'   shuffled controls (max printable frac): {ctl}')
