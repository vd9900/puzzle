# Idea: 23 marker primes (<=83) are the minimal prime-modulus set for a 104-bit (13-byte) payload (79# < 2^104 < 83#).
# Residues = per-prime residual segment (number or digit-sum), reduced mod p; CRT -> integer -> bytes. Oracle: printable 13-14 B.
import sys, math; sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import primes_upto
ps=primes_upto(83)
print('log2 79#',math.log2(math.prod(ps[:-1])),'log2 83#',math.log2(math.prod(ps)))
segs=['d','','i','f','hcc','g','iha','e','eih','ggege','b','gehhe','hhf','a','fdh','ffcdb','fcccg','f','eggec','dci','f','ffgig','eea']
num=lambda s:int(''.join(str(ord(c)-96) for c in s)) if s else 0
dsum=lambda s:sum(ord(c)-96 for c in s)
dsum0=lambda s:sum(ord(c)-97 for c in s)  # a=0 variant
def crt(rs,ms):
    M=math.prod(ms); x=0
    for r,m in zip(rs,ms):
        Mi=M//m; x+=r*Mi*pow(Mi,-1,m)
    return x%M
M=math.prod(ps); out=[]
for vname,f in (('num',num),('dsum',dsum),('dsum_a0',dsum0),('len',len)):
    for pair in ('preceding','following'):
        vals=[f(s) for s in segs]
        if pair=='following': vals=vals[1:]+[0]
        rs=[v%p for v,p in zip(vals,ps)]
        x=crt(rs,ps)
        for order in ('fwd','rev'):
            y=x if order=='fwd' else crt([v%p for v,p in zip(vals[::-1],ps)],ps)
            b=y.to_bytes((y.bit_length()+7)//8 or 1,'big')
            pr=sum(32<=c<127 for c in b)/len(b)
            out.append((pr,vname,pair,order,b))
for o in sorted(out,key=lambda t:-t[0]): print(f'{o[0]:.2f}',o[1:4],o[4])
