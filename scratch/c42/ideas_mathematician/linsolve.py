# "zeroed out" = Gaussian elimination; "sum list" = RHS column. 56 = 7x8 augmented system [A|b].
# Oracle: exact rational solve gives ALL-INTEGER solution (random 7x7 digit systems essentially never do).
import sys, re, random; sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from fractions import Fraction
from common import DBBI
toks=re.findall(r'be|[a-i]',DBBI)
R56=[t for t in toks if t not in('b','be')]
print(len(R56), ''.join(R56))
def solve(M):  # M: n x (n+1) Fractions
    n=len(M); M=[r[:] for r in M]
    for c in range(n):
        p=next((r for r in range(c,n) if M[r][c]!=0),None)
        if p is None: return None
        M[c],M[p]=M[p],M[c]
        for r in range(n):
            if r!=c and M[r][c]!=0:
                f=M[r][c]/M[c][c]; M[r]=[x-f*y for x,y in zip(M[r],M[c])]
    return [M[i][n]/M[i][i] for i in range(n)]
def variants(seq,n):
    vals=[ord(t)-96 for t in seq]
    for base in (0,1):
        v=[x-1+base for x in vals]
        for layout in ('row','col'):
            if layout=='row': rows=[v[i*(n+1):(i+1)*(n+1)] for i in range(n)]
            else: rows=[[v[j*n+i] for j in range(n+1)] for i in range(n)]
            for rhs in ('last','first'):
                R=[r if rhs=='last' else r[1:]+r[:1] for r in rows]
                yield (base,layout,rhs),[[Fraction(x) for x in r] for r in R]
def score(seq,n):
    out=[]
    for k,M in variants(seq,n):
        x=solve(M)
        if x is None: out.append((k,'singular')); continue
        out.append((k,sum(xi.denominator==1 for xi in x),[str(xi) for xi in x]))
    return out
for k,*r in score(R56,7): print(k,r[0], r[1][:7] if len(r)>1 else '')
random.seed(0); c=[]
for _ in range(300):
    s=R56[:]; random.shuffle(s)
    c.append(max(r[1] for k,*r in [(k,*rest) for k,*rest in score(s,7)] if r[0]!='singular'))
print('control: max #integer components over 8 variants, distribution', {i:c.count(i) for i in sorted(set(c))})
