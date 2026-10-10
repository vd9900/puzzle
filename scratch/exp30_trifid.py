"""Trifid-style fractionation test: each faed letter = pair of trits (3x3 square), stream of 1140 trits,
blocks of 3p trits -> 3 rows of p -> plaintext letter i = (row1[i],row2[i],row3[i]) in a 27-symbol alphabet.
Score each (assignment, period, direction) by bigram IoC, then confirm top ones with serial-structure z."""
import itertools, sys, time, json
from collections import Counter
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import FAED, DBBI
from serial import hcond_z
def trits_of(s, assign):   # assign: dict letter->(t1,t2)
    out=[]
    for c in s: out+=assign[c]
    return out
def regroup(tr, p):        # tr: list of trits, length multiple of 3p
    out=[]
    for b in range(0,len(tr),3*p):
        blk=tr[b:b+3*p]
        if len(blk)<3*p: break
        r1,r2,r3=blk[:p],blk[p:2*p],blk[2*p:]
        out+=[r1[i]*9+r2[i]*3+r3[i] for i in range(p)]
    return out
def bigram_ioc(seq):
    c=Counter(zip(seq,seq[1:])); n=len(seq)-1
    return sum(v*(v-1) for v in c.values())/(n*(n-1))
letters='abcdefghi'
# reduced assignments: fix canonical relabeling of trit values within each coordinate by requiring first-occurrence order
def canonical(assign):
    m1={};m2={}
    for c in letters:
        t1,t2=assign[c]
        if t1 not in m1: m1[t1]=len(m1)
        if t2 not in m2: m2[t2]=len(m2)
    return tuple((m1[assign[c][0]],m2[assign[c][1]]) for c in letters)
pairs=[(i,j) for i in range(3) for j in range(3)]
seen=set(); assigns=[]
for perm in itertools.permutations(pairs):
    a=dict(zip(letters,perm)); key=canonical(a)
    if key in seen: continue
    seen.add(key); assigns.append(dict(zip(letters,key)))
print('reduced assignments',len(assigns),flush=True)
streams={'faed':FAED,'faed_rev':FAED[::-1]}
periods=[2,4,10,20,38,76,190,380]
t0=time.time(); results=[]
for sn,s in streams.items():
    for ai,a in enumerate(assigns):
        tr=trits_of(s,a)
        for p in periods:
            seq=regroup(tr,p)
            if len(seq)<100: continue
            results.append((bigram_ioc(seq),sn,ai,p))
    print(sn,'done',round(time.time()-t0),'s',flush=True)
results.sort(reverse=True)
print('evaluated',len(results),'; top 20 by bigram IoC:')
# control: random-like baseline = median
import statistics
print('median ioc',statistics.median(r[0] for r in results))
top=results[:150]
conf=[]
for ioc,sn,ai,p in top:
    seq=regroup(trits_of(streams[sn],assigns[ai]),p)
    txt=''.join(chr(97+x) for x in seq)   # 27 symbols -> a..z + '{'
    z=hcond_z(txt,trials=40)
    conf.append((z,ioc,sn,ai,p,txt[:60]))
conf.sort()
for z,ioc,sn,ai,p,t in conf[:20]: print(f'z={z:6.2f} ioc={ioc:.4f} {sn} assign#{ai} p={p} {t}')
json.dump({'top':[(z,ioc,sn,ai,p,assigns[ai]) for z,ioc,sn,ai,p,t in conf[:20]]},open('exp30_trifid_top.json','w'))
