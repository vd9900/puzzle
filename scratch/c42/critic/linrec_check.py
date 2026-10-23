# Critic quick check: is faed/dbbi/R60 (or a projection) a low-order linear recurrence?
# (1) Berlekamp-Massey over GF(3) on digits mod 3 (mod-9 chain addition with 9 written as 'i' needs no erasures).
# (2) Order-k affine recurrences over GF(p), p in {2,3,5}, g treated as erasure (g in {0,7}); solve on g-free windows.
# Planted controls: a mod-10 lagged-Fibonacci stream (0 and 7 written as g) and a mod-9 one.
import sys, random
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import FAED, DBBI
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
def bm(s,p):
    C=[1];B=[1];L=0;m=1;b=1
    for n in range(len(s)):
        d=s[n]
        for i in range(1,L+1): d=(d+C[i]*s[n-i])%p
        if d==0: m+=1; continue
        coef=d*pow(b,p-2,p)%p; T=C[:]
        C=C+[0]*(len(B)+m-len(C))
        for i in range(len(B)): C[i+m]=(C[i+m]-coef*B[i])%p
        if 2*L<=n: L=n+1-L; B=T; b=d; m=1
        else: m+=1
    return L
def rank_mod(M,p):
    M=[r[:] for r in M]; r=0; cols=len(M[0]) if M else 0
    for c in range(cols):
        piv=next((i for i in range(r,len(M)) if M[i][c]%p),None)
        if piv is None: continue
        M[r],M[piv]=M[piv],M[r]; inv=pow(M[r][c],p-2,p)
        M[r]=[x*inv%p for x in M[r]]
        for i in range(len(M)):
            if i!=r and M[i][c]%p:
                f=M[i][c]; M[i]=[(a-f*b)%p for a,b in zip(M[i],M[r])]
        r+=1
    return r
def affine_rec(vals,p,k):
    # vals: list of ints or None (erasure). Unknowns: c1..ck, c0, and coefficient on x[n] fixed to -1.
    # equation: x[n] - sum c_i x[n-i] - c0 = 0. Homogeneous system in (1,c1..ck,c0) -> check if nontrivial solution with first coord 1.
    rows=[]
    for n in range(k,len(vals)):
        w=vals[n-k:n+1]
        if any(v is None for v in w): continue
        rows.append([w[-1]%p]+[(-w[-1-i])%p for i in range(1,k+1)]+[(p-1)%p])
    if len(rows)<k+6: return None
    # system A*[1,c..] = 0  <=> rows[:,1:] * c = -rows[:,0]; consistent iff rank(A_aug)==rank(A_coeff)
    A=[r[1:] for r in rows]; Aug=[r[1:]+[(-r[0])%p] for r in rows]
    return len(rows), rank_mod(A,p)==rank_mod(Aug,p) and rank_mod(A,p)<= k+1
def digits(s,gval): return [None if c=='g' and gval is None else (gval if c=='g' else 'abcdefghi'.index(c)+1) for c in s]
def planted10(n,seed=1):
    r=random.Random(seed); x=[r.randrange(10) for _ in range(7)]
    while len(x)<n: x.append((x[-7]+x[-3])%10)
    return ''.join('g' if d in (0,7) else 'abcdefghi'[d-1] for d in x)
def planted9(n,seed=2):
    r=random.Random(seed); x=[r.randrange(1,10) for _ in range(9)]
    while len(x)<n: x.append(((x[-9]+2*x[-4]+x[-1]-1)%9)+1)
    return ''.join('abcdefghi'[d-1] for d in x)
tests=[('faed',FAED),('faed_body',FAED[:538]),('dbbi',DBBI),('R60',R60),('PLANT10',planted10(570)),('PLANT9',planted9(570))]
for name,s in tests:
    for rev in (False,True):
        t=s[::-1] if rev else s
        v3=[('abcdefghi'.index(c)+1)%3 for c in t]
        out=[f'BM_GF3(i=9->0)={bm(v3,3)}/{len(t)}']
        for p in (2,3,5):
            okk=[]
            for k in range(1,13):
                vals=[None if c=='g' else ('abcdefghi'.index(c)+1)%p for c in t]
                if p==3: vals=[('abcdefghi'.index(c)+1)%3 for c in t]  # mod-9 model: no erasure
                r=affine_rec(vals,p,k)
                if r and r[1]: okk.append(k)
            out.append(f'GF{p} consistent orders<=12: {okk}')
        print(name,'rev' if rev else 'fwd',' | '.join(out))
