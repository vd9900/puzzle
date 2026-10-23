"""Re-check the top-z readings of ternary_read.py against structure-preserving nulls (faed is known to have lag-1 and
non-stationary structure, which letter-shuffles destroy): (a) first-order Markov surrogates of the same input,
(b) circular rotations of the input. Also prints the letters the quadgram score actually used."""
import sys, numpy as np
sys.argv=['x']; exec(open('/home/vin/bitcoin_puzzle/scratch/c40/ternary/ternary_read.py').read().split('# ---------- planted')[0])
rng2=np.random.default_rng(7)
def markov(x,n,R):
    T=np.ones((9,9))*1e-9
    for a,b in zip(x,x[1:]): T[a,b]+=1
    T/=T.sum(1,keepdims=True); out=np.zeros((R,n),int); out[:,0]=rng2.choice(x,R)
    for i in range(1,n):
        for r in range(R): out[r,i]=rng2.choice(9,p=T[out[r,i-1]])
    return out
TOP=[('faed_rev',('salphaseion_inv','cr','rows_then_cols',6,2,'little','bytes')),
     ('faed_rev',('dbbi_first_inv','cr','halves_interleave',6,4,'little','bytes')),
     ('faed_rev',('salphaseion_inv','rc','rows_then_cols',6,2,'little','bytes')),
     ('R56',('rowmajor','rc','plain',3,0,'big','a1z26_sp0'))]
for nm,cfg in TOP:
    x=np.array([L9.index(c) for c in INPUTS[nm]]); n=len(x)
    V,sym=read(x[None,:],cfg); s0,c0=qscore(sym)
    letters=''.join(chr(97+v) for v in sym[0] if v<26)
    for lab,X in (('markov1',markov(x,n,300)),('rotations',np.array([np.roll(x,k) for k in range(1,n)])),('shuffle',np.array([rng2.permutation(x) for _ in range(400)]))):
        V2,s2=read(X,cfg); sc,cnt=qscore(s2); sc=sc[~np.isnan(sc)]
        print('%s %s %-9s obs q=%.3f letters=%d | null n=%d mean %.3f sd %.3f -> z=%.2f, frac>=obs %.4f'%(nm,cfg[:6],lab,s0[0],c0[0],len(sc),sc.mean(),sc.std(),(s0[0]-sc.mean())/sc.std(),(sc>=s0[0]).mean()))
    print('   letters used:',letters[:120])
