# Does faed (fwd/rev, base 0/1) admit a tokenization where prime logical positions carry a1z26 tokens
# spelling a known label, non-prime positions single letters? zeros dropped ('t'=20 -> 'b', 'j'=10 -> 'a').
import sys
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import *
P=set(primes_upto(5000))
def codes(ch):
    n=ord(ch)-96; s=str(n); out={s.replace('0','')}
    return {''.join(chr(96+int(d)) for d in x) for x in out}
def match(stream, target, base):
    # DFS: walk logical positions; at prime positions must consume code of next target letter
    best=[0]
    def rec(i, lp, k):
        best[0]=max(best[0],k)
        if k==len(target) or i>=len(stream): return
        if lp in P:
            for c in codes(target[k]):
                if stream.startswith(c,i): rec(i+len(c), lp+1, k+1)
        else:
            rec(i+1, lp+1, k)
    rec(0, base, 0); return best[0]
for tgt in ('matrixsumlist','lastwordsbeforearchichoice','thispassword','yellowblueprimes'):
    for name,s in [('faed',FAED),('faed_rev',FAED[::-1]),('faed_nohdr',FAED[4:]),('R60','difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea')]:
        print(tgt,name,[match(s,tgt,b) for b in (0,1)])
