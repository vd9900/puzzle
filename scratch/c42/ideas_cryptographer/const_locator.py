# Feasibility: is faed (body) a window of a famous constant's decimal digits, with 0 and 7 both written as 'g'?
# Oracle: any >=14-digit exact match (expected false hits per 1e6 positions ~ 1e6*1e-14*2^k ~ 0).
import sys, re
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import FAED, DBBI
from math import isqrt
sys.set_int_max_str_digits(0)
N=int(sys.argv[1]) if len(sys.argv)>1 else 300000
S=10**(N+10)
def arctan_inv(x):
    tot=t=S//x; x2=x*x; k=1; sgn=-1
    while t:
        t//=x2; tot+=sgn*(t//(2*k+1)); sgn=-sgn; k+=1
    return tot
def e_digits():
    tot=0; t=S; k=0
    while t: tot+=t; k+=1; t//=k
    return tot
consts={'pi':str(4*(4*arctan_inv(5)-arctan_inv(239))),'e':str(e_digits()),
 'sqrt2':str(isqrt(2*S*S)),'sqrt3':str(isqrt(3*S*S)),'phi':str((S+isqrt(5*S*S))//2)}
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
def pat(s): return ''.join('[07]' if c=='g' else str('abcdefghi'.index(c)+1) for c in s)
probes={}
for nm,s in (('faed',FAED),('R60',R60),('faedtail',FAED[-32:])):
    for st in range(0,len(s)-14,7):
        probes[(nm,st)]=re.compile(pat(s[st:st+14]))
for cn,c in consts.items():
    d=c[:N]
    hits=[(k,m.start()) for k,p in probes.items() for m in p.finditer(d)]
    print(cn,len(d),'hits:',hits[:10])
