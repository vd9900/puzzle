#!/usr/bin/env python3
"""Which uniform wallet alphabet, projected onto 9 symbols a-i, reproduces faed's letter histogram?
Mappings: digital root of the char value (digits = value, letters = a1z26) [the puzzle's own 'a=1..i=9' family]."""
import sys, math, string
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import FAED, DBBI
from collections import Counter
import math
class chi2:
    @staticmethod
    def sf(x,k):
        # regularized upper gamma Q(k/2, x/2) via series for lower gamma
        a=k/2; z=x/2
        if z<=0: return 1.0
        term=1/a; s=term; i=1
        while i<500:
            term*=z/(a+i); s+=term; i+=1
        P=s*math.exp(-z+a*math.log(z)-math.lgamma(a))
        return max(0.0,1-P)
L='abcdefghi'
obs=Counter(FAED); n=len(FAED)
print('faed counts',[obs[c] for c in L], n)
def dr(v): return 0 if v==0 else 1+(v-1)%9
def chval(c):
    if c.isdigit(): return int(c)
    return ord(c.lower())-96
alphs={
 'hex':'0123456789abcdef',
 'base58':'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz',
 'base64':string.ascii_uppercase+string.ascii_lowercase+string.digits+'+/',
 'base32rfc':string.ascii_uppercase+'234567',
 'bech32':'qpzry9x8gf2tvdw0s3jn54khce6mua7l',
 'alnum_lower':string.ascii_lowercase+string.digits,
 'lower':string.ascii_lowercase,
 'decimal':'0123456789',
}
def test(name,probs):
    exp=[probs.get(c,0)*n for c in L]
    if any(e==0 for e in exp): print(name,'zero-exp',[round(e,1) for e in exp]); return
    x=sum((obs[c]-e)**2/e for c,e in zip(L,exp))
    print(f'{name:28s} chi2={x:7.2f} p={chi2.sf(x,8):.3g}  exp=',[round(e,1) for e in exp])
for name,a in alphs.items():
    for zero in ('9','drop'):
        cnt=Counter()
        for ch in a:
            v=dr(chval(ch))
            if v==0:
                if zero=='drop': continue
                v=9
            cnt[L[v-1]]+=1
        tot=sum(cnt.values())
        test(f'{name} dr0->{zero}',{c:cnt[c]/tot for c in L})
# decimal with g double (cycle-42 model)
test('decimal g=0|7',{c:(0.2 if c=='g' else 0.1) for c in L})
test('32nds g6 i4 e4 rest3',{c:{'g':6,'i':4,'e':4}.get(c,3)/32 for c in L})
