"""Ciphertext-only Hill row attack on faed (mod 10), g = erasure {0,7}.
Plaintext model: a1z26 digit stream of English (the page's own dbbi encoding style).
Score every inverse row r in Z10^n by LLR vs uniform; compare max to shuffled-faed controls.
Plant control: encrypt an a1z26 English digit stream with a random invertible Hill key, map digits->letters with 0,7->g, attack."""
import sys, itertools, random
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
import numpy as np
from common import FAED
from collections import Counter
eng=open('/home/vin/bitcoin_puzzle/research/artifacts/phase32-beaufort.txt').read().strip().lower()
eng=''.join(ch for ch in eng if ch.isalpha())
a1z26=''.join(str(ord(ch)-96) for ch in eng)
cnt=Counter(a1z26); q=np.array([cnt[str(d)]+1 for d in range(10)],float); q/=q.sum()
print('a1z26 digit model', np.round(q,3))
L2D={**{ch:i+1 for i,ch in enumerate('abcdefghi')}}
def to_digits(s):  # g -> -1 (erasure: 0 or 7)
    return [(-1 if ch=='g' else L2D[ch]) for ch in s]
def rows(n): return np.array(list(itertools.product(range(10),repeat=n))[1:],dtype=np.int64)
def score(dig,n,off,R):
    B=(len(dig)-off)//n; blocks=[dig[off+j*n:off+(j+1)*n] for j in range(B)]
    combos=[];bid=[];w=[]
    for j,b in enumerate(blocks):
        gi=[k for k,x in enumerate(b) if x==-1]
        for ch in itertools.product((0,7),repeat=len(gi)):
            v=list(b)
            for k,c in zip(gi,ch): v[k]=c
            combos.append(v); bid.append(j); w.append(1/2**len(gi))
    C=np.array(combos,dtype=np.int64).T; P=(R@C)%10; lik=q[P]*np.array(w)  # rows x combos
    per=np.zeros((R.shape[0],B))
    np.add.at(per.T, np.array(bid), lik.T)
    return (np.log(per/0.1)).sum(1)  # LLR per row
def attack(s,n):
    R=rows(n); dig=to_digits(s); best=-1e9; arg=None
    for off in range(n):
        sc=score(dig,n,off,R); i=int(sc.argmax())
        if sc[i]>best: best=sc[i]; arg=(off,tuple(R[i]))
    return best,arg
rng=random.Random(5)
# plant: random invertible key mod 10, plaintext = a1z26 of a different English slice
def inv_ok(K):
    d=int(round(np.linalg.det(K)))%10; return d%2==1 and d%5!=0
for n in (2,3,4):
    while True:
        K=np.array([[rng.randrange(10) for _ in range(n)] for _ in range(n)])
        if inv_ok(K): break
    pt=[int(c) for c in a1z26[300:300+570-570%n]]
    ct=[]
    for j in range(len(pt)//n): ct+=list((K@np.array(pt[j*n:(j+1)*n]))%10)
    plant=''.join('g' if d in (0,7) else 'abcdefghi'[d-1] for d in ct)
    pb,parg=attack(plant,n)
    real,rarg=attack(FAED,n)
    ctrl=[]
    for t in range(6):
        l=list(FAED); rng.shuffle(l); ctrl.append(attack(''.join(l),n)[0])
    print(f'n={n}: PLANT best LLR {pb:.1f} {parg} | REAL best {real:.1f} {rarg} | shuffled controls max {max(ctrl):.1f} mean {np.mean(ctrl):.1f}')
