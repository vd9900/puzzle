# Is faed ITSELF a chain-addition "sum list" (lagged-Fibonacci / linear recurrence) mod 10 or mod 9?
# Pairwise i.i.d. tests cannot see 3-way dependence x[n]=x[n-a]+-x[n-b]; this checks it directly.
# g is ambiguous {0,7} (mod 10) per the 0->g merge model. Score = fraction of positions where SOME
# assignment of ambiguous g's satisfies the relation. Chance ~0.1-0.2; a true chain-addition stream -> 1.0.
import sys, itertools
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import FAED, DBBI
import random
def vals(c, mod):
    d='abcdefghi'.index(c)+1
    if mod==10: return (7,0) if c=='g' else (d,)
    return (d%9,)
def score(s, a, b, mod, sgn, start=0):
    V=[vals(c,mod) for c in s]
    ok=n=0
    for i in range(max(a,b)+start, len(s)):
        n+=1
        if any((x-(y+sgn*z))%mod==0 for x in V[i] for y in V[i-a] for z in V[i-b]): ok+=1
    return ok/max(n,1)
def scan(s,name,maxlag=40):
    best=[]
    for mod in (10,9):
        for sgn in (1,-1):
            for a in range(1,maxlag+1):
                for b in range(a+1,maxlag+1):
                    best.append((score(s,a,b,mod,sgn),mod,sgn,a,b))
    best.sort(reverse=True)
    print(name,'top:',[(round(x[0],3),)+x[1:] for x in best[:4]])
    return best[0][0]
# planted self-test: chain addition mod 10 (VIC style x[n]=x[n-10]+x[n-9]), 0->g, 7->g
r=random.Random(1); x=[r.randrange(10) for _ in range(10)]
while len(x)<570: x.append((x[-10]+x[-9])%10)
plant=''.join('g' if d in (0,7) else 'abcdefghi'[d-1] for d in x)
scan(plant,'PLANT(chain add lags 10,9)')
scan(FAED,'faed'); scan(FAED[:538],'faed body')
sh=list(FAED); random.Random(2).shuffle(sh); scan(''.join(sh),'shuffled control')
