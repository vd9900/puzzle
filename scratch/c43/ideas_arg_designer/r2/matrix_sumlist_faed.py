"""'matrix sumlist' read literally: the Phase-0 14x14 bit MATRIX applied to 14-digit blocks of faed (and R60/dbbi).
(1) Hill mod 10 with K in {M, M^T, flips}: LLR vs a1z26-English digit model, g as erasure {0,7}.
(2) Row sums (M . block) -> letters (sum mod 26, a=1): English chi/IC for g=7 and g=0.
Controls: shuffled faed. Plant: text encoded so that M.block mod 26 = a1z26 letters is impossible to plant generally, so (2) uses IC calibration."""
import sys, itertools, random
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
import numpy as np
from common import FAED, DBBI, MATRIX
from collections import Counter
M=np.array(MATRIX,dtype=np.int64)
eng=''.join(c for c in open('/home/vin/bitcoin_puzzle/research/artifacts/phase32-beaufort.txt').read().lower() if c.isalpha())
a1z26=''.join(str(ord(ch)-96) for ch in eng); cnt=Counter(a1z26)
q=np.array([cnt[str(d)]+1 for d in range(10)],float); q/=q.sum()
EF=Counter(eng); ef=np.array([EF[chr(97+i)]+1 for i in range(26)],float); ef/=ef.sum()
def digs(s,gval): return np.array([gval if c=='g' else 'abcdefghi'.index(c)+1 for c in s],dtype=np.int64)
def ic(seq):
    c=Counter(seq); n=len(seq); return sum(v*(v-1) for v in c.values())/max(1,n*(n-1))
keys={'M':M,'MT':M.T,'Mlr':M[:,::-1],'Mud':M[::-1,:],'Mrot':np.rot90(M)}
def run(s,label):
    out=[]
    for kn,K in keys.items():
        for off in range(14):
            B=(len(s)-off)//14
            for gval in (7,0):
                d=digs(s,gval)[off:off+B*14].reshape(B,14)
                sums=(K@d.T).T.reshape(-1)          # raw row sums
                p10=sums%10
                llr=float(np.log(q[p10]/0.1).sum())
                letters=(sums-1)%26
                chi=float(np.log(ef[letters]*26).sum())  # LLR vs uniform letters
                out.append((llr,chi,ic(letters.tolist()),kn,off,gval))
    best_llr=max(out); best_chi=max(out,key=lambda x:x[1]); best_ic=max(out,key=lambda x:x[2])
    print(f'{label:10s} bestLLR(a1z26 mod10) {best_llr[0]:7.1f} {best_llr[3:]} | bestEnglishLLR(mod26) {best_chi[1]:7.1f} {best_chi[3:]} | bestIC {best_ic[2]:.4f} {best_ic[3:]}')
    return best_llr[0],best_chi[1],best_ic[2]
r=run(FAED,'faed'); run(FAED[::-1],'faed_rev')
rng=random.Random(3); C=[]
for t in range(10):
    l=list(FAED); rng.shuffle(l); C.append(run(''.join(l),'ctrl%d'%t))
C=np.array(C); print('controls max: LLR %.1f  EngLLR %.1f  IC %.4f'%tuple(C.max(0)))
# plant for (2): build blocks whose M-row-sums mod 26 spell English? Not generally solvable; instead sanity: English letters IC ~0.066, uniform ~0.038
print('ref IC english %.4f uniform %.4f'%(ic(list(eng[:500])),1/26))
