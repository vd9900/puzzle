"""T4: is faed consistent with CyberChef 'To Charcode' (base 9, no delimiter) of text + Substitute 0-8 -> a-i?
Map-free test: compare faed's SORTED letter-frequency profile with sorted digit profiles of base-9 charcodes of
(a) English text (Carroll), (b) lowercase hex text, (c) base64 text, (d) uniform random base-9 digits (control).
Also the leading-digit constraint: every printable code 32..126 in base 9 is 35..150 -> 2-3 digits; with 3-digit
codes the top digit is always '1' -> one letter must be >= ~25-33%."""
import sys, random, re, base64, os
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import *
from collections import Counter
def b9(n):
    s = ''
    while n: s = '012345678'[n % 9] + s; n //= 9
    return s
def prof(s):
    c = sorted(Counter(s).values(), reverse=True); c += [0]*(9-len(c)); t = sum(c); return [x/t for x in c[:9]]
def chi(p, n, q):
    return sum((n*a - n*b)**2/(n*b) for a, b in zip(p, q) if b > 0)
rng = random.Random(9)
car = open('/home/vin/bitcoin_puzzle/scratch/corpora/carroll_public_domain.txt').read()
srcs = {
 'english': lambda k: car[(o := rng.randrange(len(car)-400)):o+k],
 'hexlower': lambda k: os.urandom(k).hex()[:k],
 'base64': lambda k: base64.b64encode(os.urandom(k)).decode()[:k],
}
F = prof(FAED); print('faed sorted profile:', [round(x, 3) for x in F])
for name, gen in srcs.items():
    ds = ''.join(''.join(b9(ord(ch)) for ch in gen(230)) for _ in range(40))
    P = prof(ds); print('%-9s base9-charcode sorted profile:' % name, [round(x, 3) for x in P], ' chi2(faed|model)=%.0f' % chi(F, 570, P))
U = prof(''.join(rng.choice('012345678') for _ in range(200000)))
# null distribution of chi2 for uniform model at n=570 (sorted profile), simulate
sims = sorted(chi(prof(''.join(rng.choice('012345678') for _ in range(570))), 570, U) for _ in range(500))
print('uniform-base9 model: chi2(faed)=%.0f; simulated 570-digit samples chi2 95%%=%.0f 99%%=%.0f max=%.0f' % (chi(F, 570, U), sims[475], sims[495], sims[-1]))
