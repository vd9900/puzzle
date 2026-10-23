# Reconstruct L83 segmentation of dbbi (prime logical positions hold b/be) and the 23 residual segments between primes.
import sys; sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, primes_upto
P=set(primes_upto(200))
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
sols=[]
def rec(i,toks):
    if i==len(DBBI):
        sols.append(list(toks)); return
    L=len(toks)+1
    opts=[DBBI[i]]
    if DBBI[i:i+2]=='be': opts.append('be')
    for t in opts:
        if L in P and t not in('b','be'): continue
        toks.append(t); rec(i+len(t),toks); toks.pop()
rec(0,[])
good=[s for s in sols if ''.join(t for k,t in enumerate(s,1) if k not in P)==R60]
print(len(sols),'segmentations;',len(good),'reproduce R60; lengths',sorted(set(len(s) for s in good)))
S=good[0]
print(len(S))
segs=[];cur=''
for k,t in enumerate(S,1):
    if k in P: segs.append(cur); cur=''
    else: cur+=t
print('trailing',repr(cur))
print(segs, len(segs))
