# Yin-yang = 180-degree point reflection with colour swap. On a digit stream: x[i] <-> 10 - x[n-1-i] (a<->i,b<->h,c<->g,d<->f,e).
# Structural test: is faed (or dbbi/R60) anti-symmetric under this map more/less than a permutation null?  Also half-shift form.
import sys, random; sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
def stat(d, mode):
    n=len(d)
    if mode=='fold': pairs=[(d[i],d[n-1-i]) for i in range(n//2)]
    else: h=n//2; pairs=[(d[i],d[i+h]) for i in range(h)]
    return sum(a+b==10 for a,b in pairs), sum(a==b for a,b in pairs)
random.seed(1)
for name,s in [('faed',FAED),('dbbi',DBBI),('R60',R60)]:
    d=[ord(c)-96 for c in s]
    for mode in ('fold','half'):
        obs=stat(d,mode); null=[]
        for _ in range(4000):
            e=d[:]; random.shuffle(e); null.append(stat(e,mode))
        for j,lab in enumerate(('sum10','equal')):
            vals=sorted(x[j] for x in null); m=sum(vals)/len(vals)
            p=sum(v>=obs[j] for v in vals)/len(vals); q=sum(v<=obs[j] for v in vals)/len(vals)
            print(f'{name:5s} {mode:4s} {lab:5s} obs={obs[j]:3d} null_mean={m:6.1f} p_hi={p:.3f} p_lo={q:.3f}')
