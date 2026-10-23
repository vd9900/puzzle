# Diagnostic for idea 5 (a1z26 tokens at primes): under the model, 'a' is followed by d/e/h/i (N,O,R,S) and 'b' by a/c/e (U,W,Y)
# more often than filler would give. Compare faed to letter-shuffled controls (same unigram).
import sys, random
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import FAED
def stat(s):
    A=sum(1 for i in range(len(s)-1) if s[i]=='a' and s[i+1] in 'dehi')
    B=sum(1 for i in range(len(s)-1) if s[i]=='b' and s[i+1] in 'ace')
    return A,B
r=random.Random(7); obs=stat(FAED); ctrl=[]
for _ in range(5000):
    l=list(FAED); r.shuffle(l); ctrl.append(stat(''.join(l)))
for j,nm in enumerate(('a->dehi','b->ace')):
    c=[x[j] for x in ctrl]; m=sum(c)/len(c); sd=(sum((x-m)**2 for x in c)/len(c))**.5
    p=sum(1 for x in c if x>=obs[j])/len(c)
    print(nm,'obs',obs[j],'ctrl mean %.1f sd %.1f'%(m,sd),'p(>=obs)=%.3f'%p)
