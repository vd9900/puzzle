from common import *
from serial import hcond
import random, math, sys, json
f=letters_to_digits(FAED); N=len(f)
def untranspose(ct, order):
    n=len(order); rows=N//n; extra=N%n
    lens=[rows+(1 if c<extra else 0) for c in range(n)]
    cols=[None]*n; pos=0
    for r in range(n):
        c=order.index(r); cols[c]=ct[pos:pos+lens[c]]; pos+=lens[c]
    return ''.join(cols[c][r] for r in range(rows+1) for c in range(n) if r<lens[c])
def anneal(ct, n, iters, seed):
    r=random.Random(seed)
    order=list(range(n)); r.shuffle(order)
    cur=hcond(untranspose(ct,order)); best=cur; bestorder=order[:]
    T0=0.05
    for it in range(iters):
        i,j=r.sample(range(n),2)
        order[i],order[j]=order[j],order[i]
        v=hcond(untranspose(ct,order))
        T=T0*(1-it/iters)+1e-4
        if v<cur or r.random()<math.exp((cur-v)/T):
            cur=v
            if v<best: best=v; bestorder=order[:]
        else:
            order[i],order[j]=order[j],order[i]
    return best,bestorder
results={}
shuf=[]
rr=random.Random(99)
for s in range(3):
    l=list(f); rr.shuffle(l); shuf.append(''.join(l))
for n in range(5,41):
    iters=max(3000, 400*n)
    real=min(anneal(f,n,iters,seed) for seed in range(2))
    ctrl=[min(anneal(sf,n,iters,seed) for seed in range(2))[0] for sf in shuf]
    results[n]={'real':real[0],'order':real[1],'ctrl':ctrl}
    print(f'n={n:2d} real={real[0]:.4f} ctrl={[round(c,4) for c in ctrl]} gap={min(ctrl)-real[0]:+.4f}',flush=True)
json.dump(results,open('exp21_results.json','w'))
