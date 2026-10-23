"""Family-wise p for the max over the 9 runs: each FAED letter-shuffle goes through the same 9 (input x start)
transforms; standardise each run by its null mean/sd; compare max-z of real vs the null max-z distribution."""
import random
from prime_a1z26_beam import *
def nine(s):
    return [search(t, st)['per'] for t in (s, s[::-1], s[4:]) for st in (1, 188, 189)]
rng = random.Random(7); N = 600
null = []
for _ in range(N):
    l = list(FAED); rng.shuffle(l); null.append(nine(''.join(l)))
mu = [sum(r[k] for r in null)/N for k in range(9)]
sd = [(sum((r[k]-mu[k])**2 for r in null)/N)**.5 for k in range(9)]
obs = nine(FAED); zo = [(obs[k]-mu[k])/sd[k] for k in range(9)]
print('real z per run (fwd/rev/nohdr x s1/s188/s189):', [round(z, 2) for z in zo])
mz = [max((r[k]-mu[k])/sd[k] for k in range(9)) for r in null]
print(f'max z real={max(zo):.2f}; family-wise p={sum(m >= max(zo) for m in mz)/N:.3f}')
