# Continue the 23 marker primes into faed but read faed[p] as a RESIDUE mod p (CRT), primes>=11 so residues 0..9 < p.
import sys, math; sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import FAED, DBBI, primes_upto
def crt(rs,ms):
    M=math.prod(ms); x=0
    for r,m in zip(rs,ms): Mi=M//m; x+=r*Mi*pow(Mi,-1,m)
    return x%M
out=[]
for S,nm in ((FAED,'faed'),(FAED[::-1],'faed_rev'),(DBBI,'dbbi')):
    for lo in (2,11):
        ps=[p for p in primes_upto(83) if p>=lo]
        for one in (0,1):
            for base in (0,1):
                rs=[(ord(S[p-one])-97+base)%p for p in ps]
                x=crt(rs,ps); b=x.to_bytes((x.bit_length()+7)//8 or 1,'big')
                out.append((sum(32<=c<127 for c in b)/len(b),nm,lo,one,base,b))
out.sort(key=lambda t:-t[0]); [print(o) for o in out[:4]]
