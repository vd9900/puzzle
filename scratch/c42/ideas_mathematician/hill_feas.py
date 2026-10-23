# Feasibility: dbbi with all 10 'be' tokenized = 81 tokens = 9x9. Is it invertible mod 9 / 10 / 26 (Hill key)?
import sys, re; sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import DBBI
from fractions import Fraction
from math import gcd
toks=re.findall(r'be|[a-i]',DBBI); assert len(toks)==81
def det(M):
    M=[[Fraction(x) for x in r] for r in M]; n=len(M); d=Fraction(1)
    for c in range(n):
        p=next((r for r in range(c,n) if M[r][c]!=0),None)
        if p is None: return 0
        if p!=c: M[c],M[p]=M[p],M[c]; d=-d
        d*=M[c][c]
        for r in range(c+1,n):
            f=M[r][c]/M[c][c]; M[r]=[x-f*y for x,y in zip(M[r],M[c])]
    return int(d)
for bev in (25,7,5):         # be = 25 (a1z26 'y'), or mod-reduced
    for base in (1,0):
        v=[(bev if t=='be' else ord(t)-97+base) for t in toks]
        K=[v[9*i:9*i+9] for i in range(9)]
        D=det(K)
        print(f'be={bev} base={base} det={D}', {m:gcd(D,m)==1 for m in (9,10,26)})
