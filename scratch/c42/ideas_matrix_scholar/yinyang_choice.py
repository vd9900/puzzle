# 'the problem is choice': label bits (104) choose, at faed's 104 prime positions (pi(570)=104), between a digit and its
# yin-yang complement (d -> 10-d).  Read the 104 chosen digits (and the full 570 stream) via z-method int->bytes.
import sys; sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import FAED, BIN1
def isp(n): return n>1 and all(n%k for k in range(2,int(n**.5)+1))
def tob(x): return x.to_bytes((x.bit_length()+7)//8,'big')
def pr(b): return sum(32<=c<127 for c in b)/max(1,len(b))
bits=[1 if c=='b' else 0 for c in BIN1]
for base in (0,1):
    P=[p for p in range(base,570+base) if isp(p)]; assert len(P)==104, len(P)
    for pol in (0,1):
        for border in ('fwd','rev'):
            bb=bits if border=='fwd' else bits[::-1]
            sel=[]
            for p,b in zip(P,bb):
                d=ord(FAED[p-base])-96
                sel.append(10-d if (b^pol) else d)
            for name,ds in (('sel104',sel),):
                x=int(''.join(map(str,ds))); y=tob(x)
                print(base,pol,border,name,f'{pr(y):.2f}',y[:20] if pr(y)>0.7 else '')
