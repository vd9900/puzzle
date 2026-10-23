import sys, random
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import *
def expand(s,start=0):
    bits=[];b=start
    for c in s: bits+=[b]*(ord(c)-96); b^=1
    return bits
def peak(bits, lags=range(10,400)):
    n=len(bits); res=[]
    for L in lags:
        agree=sum(bits[i]==bits[i+L] for i in range(n-L))/(n-L)
        res.append((agree,L))
    res.sort(reverse=True); return res[:4]
print('faed', peak(expand(FAED)))
random.seed(7)
for k in range(4):
    f=list(FAED); random.shuffle(f); print('ctrl',peak(expand(''.join(f))))
# planted: a 40-wide bitmap with a big diagonal stripe pattern, RLE'd with run cap 9 -> check detection
W=40; img=[[1 if ((r//6)+(c//5))%2 else 0 for c in range(W)] for r in range(70)]
bits=[b for r in img for b in r]
runs=[];cur=bits[0];n=0
for b in bits:
    if b==cur and n<9:n+=1
    elif b==cur: runs.append(n);runs.append(0);n=1  # crude cap
    else: runs.append(n);cur=b;n=1
runs.append(n)
print('planted lag peak', peak(bits)[:2])
