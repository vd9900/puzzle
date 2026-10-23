# Deterministic check: does any prefix/suffix of dbbi/faed/residual decode with the page's own z-method
# (a..i=1..9 [o=0] -> decimal -> hex -> bytes) to mostly-printable text? Control: Z1/Z2 must decode.
import sys; sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import *
def zdec(s):
    d=letters_to_digits(s)
    if not d or d[0]=='0': return b''
    return zmethod_digits(d)
def score(b):
    if not b: return 0
    return sum(32<=x<127 for x in b)/len(b)
for name,s in [('Z1',Z1),('Z2',Z2)]:
    print(name, zdec(s))
best=[]
for name,s in [('dbbi',DBBI),('faed',FAED)]:
    for L in range(6,len(s)+1):
        for kind,sub in (('pre',s[:L]),('suf',s[-L:])):
            b=zdec(sub); sc=score(b)
            if len(b)>=3: best.append((sc,len(b),name,kind,L,b[:40]))
best.sort(reverse=True)
for r in best[:12]: print(r)
# baseline: expected best score for random digit strings of same lengths
import random
random.seed(1); mx=[]
for t in range(3):
    s=''.join(random.choice('abcdefghi') for _ in range(570)); m=(0,0)
    for L in range(6,571):
        for sub in (s[:L],s[-L:]):
            b=zdec(sub)
            if len(b)>=3: m=max(m,(score(b),len(b)))
    mx.append(m)
print('random baselines (score,len):',mx)
