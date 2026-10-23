"""dbbi carries the image colour bits (= LSB/parity of the chars of 'gsmg.io/theseedisplanted') at its prime positions.
Analogy test: do faed's 104 prime positions (pi(570)=104) carry the 104 label bits ('matrixsumlist') as LETTER PARITY?
Conventions: letter value a=1..i=9 (and a=0..i=8), primes 1-based (and 0-based index), label bit order fwd/rev,
bit sense direct/inverted. g is 0|7 (parity ambiguous) -> scored as wildcard. Oracle: agreement on non-g positions
(null ~ Binomial(n, 1/2)); planted control first."""
import sys, random
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import FAED, BIN1, DBBI, primes_upto
from math import comb
bits = [int(c == 'b') for c in BIN1]  # a=0 b=1 as used by b2a
assert len(bits) == 104
P1 = primes_upto(570)
assert len(P1) == 104
def score(s, positions, bitlist, a0, inv):
    agree = n = 0
    for p, b in zip(positions, bitlist):
        c = s[p]
        if c == 'g': continue
        v = ord(c) - 97 + (0 if a0 else 1)
        n += 1; agree += ((v & 1) ^ inv) == b
    return agree, n
def tail(k, n):
    return sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n
def scan(s, label):
    best = []
    for base in (1, 0):  # 1-based prime p -> index p-1 ; 0-based -> index p
        pos = [p - base for p in P1 if p - base < len(s)]
        for order in ('fwd', 'rev'):
            bl = bits if order == 'fwd' else bits[::-1]
            for a0 in (False, True):
                for inv in (0, 1):
                    k, n = score(s, pos, bl, a0, inv)
                    best.append((tail(max(k, n - k), n), k, n, base, order, a0, inv))
    best.sort()
    print(f'{label:10s} best p={best[0][0]:.3g} agree={best[0][1]}/{best[0][2]} cfg={best[0][3:]}')
    return best[0]
# planted control: overwrite faed's prime positions with letters whose parity = label bit
rnd = random.Random(7); s = list(FAED)
for p, b in zip(P1, bits):
    s[p - 1] = rnd.choice('acei' if b else 'bdfh')  # a=1 odd
r = scan(''.join(s), 'PLANT'); assert r[0] < 1e-20
scan(FAED, 'faed'); scan(FAED[::-1], 'faed_rev')
# same test applied to dbbi (control: its colour bits ARE there as tokens, not parity) and residual
