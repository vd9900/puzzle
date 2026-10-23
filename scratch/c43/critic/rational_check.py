"""Critic quick check: is a g-resolved faed/dbbi/R60 the decimal expansion of a rational p/q with q <= 1e18 (any decimal point)?
40-digit prefix -> Fraction.limit_denominator(1e18) (exact recovery guaranteed since 1e-40 < 1/(2q^2)); verify all letters.
Plant control: 123456789/9876543211 (long-period) g-encoded."""
import sys, itertools
from fractions import Fraction
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import FAED, DBBI
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
def enc(digs): return ''.join('g' if d in '07' else chr(96+int(d)) for d in digs)
def matches(s, digs): return all((c=='g' and d in '07') or (c!='g' and d==str(ord(c)-96)) for c,d in zip(s,digs))
def check(s, m=40, Q=10**18):
    gi=[i for i,c in enumerate(s[:m]) if c=='g']; hits=[]
    for bits in itertools.product('07', repeat=len(gi)):
        d=[str(ord(c)-96) if c!='g' else None for c in s[:m]]
        for i,b in zip(gi,bits): d[i]=b
        D=int(''.join(d))
        f=Fraction(D,10**m).limit_denominator(Q)   # x = 0.d1d2...; decimal point shift = multiply by 10^L (q unchanged up to factors of 2,5)
        if f.denominator<2: continue
        tot=len(s)
        digs=str(f.numerator*10**tot//f.denominator).zfill(tot)
        if len(digs)==tot and matches(s,digs): hits.append((f.numerator,f.denominator))
    return hits
p=str(123456789*10**120//9876543211).zfill(120)
h=check(enc(p[:110])); print('control', h[:2]); assert h
for nm,s in (('faed',FAED),('faed_rev',FAED[::-1]),('dbbi',DBBI),('dbbi_rev',DBBI[::-1]),('R60',R60),('R60rev',R60[::-1])):
    print(nm,'hits',check(s), flush=True)
