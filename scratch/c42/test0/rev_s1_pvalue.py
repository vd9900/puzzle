"""Empirical p-value for the best real run (FAED reversed, start 1): 1000 letter shuffles + 1000 block shuffles
(blocks of 19 letters, keeps faed's local non-stationarity such as the e/g-free tail). Calibration only."""
import random
from prime_a1z26_beam import *
src = FAED[::-1]; obs = search(src, 1)['per']; rng = random.Random(99)
for kind in ('letter', 'block19'):
    xs = []
    for _ in range(1000):
        if kind == 'letter':
            l = list(src); rng.shuffle(l); t = ''.join(l)
        else:
            b = [src[i:i+19] for i in range(0, 570, 19)]; rng.shuffle(b); t = ''.join(b)
        xs.append(search(t, 1)['per'])
    m = sum(xs)/len(xs); sd = (sum((x-m)**2 for x in xs)/len(xs))**.5
    print(f'{kind}: obs={obs:.3f} mean={m:.3f} sd={sd:.3f} max={max(xs):.3f} p(>=obs)={sum(x>=obs for x in xs)/len(xs):.3f}')
