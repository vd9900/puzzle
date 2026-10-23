#!/usr/bin/env python3
"""Related-nonce check over the 6 creator signatures: is k_j = +/-k_i + delta for |delta| <= 2^20 (counter/offset nonce bug)?
Lift each r to both points R=(r,+/-y); D = R_j -/+ R_i; look up x(D) in a table of x(delta*G). Hit => k recoverable => verify d*G = prize pubkey.
Control: plant R2 = R1 + 12345*G and require a hit."""
import json, importlib.util
spec=importlib.util.spec_from_file_location('rc','rcheck.py')
src=open('rcheck.py').read().split('# small-nonce scan')[0]
ns={}; exec(src,ns)
add,G,P,N,sigs=ns['add'],ns['G'],ns['P'],ns['N'],ns['sigs']
def lift(x):
    y2=(pow(x,3,P)+7)%P; y=pow(y2,(P+1)//4,P); assert y*y%P==y2; return (x,y)
def neg(Q): return (Q[0],(-Q[1])%P)
tab={}; Q=None
for d in range(1,(1<<20)+1):
    Q=add(Q,G); tab[Q[0]]=d
Rs=[lift(s[2]) for s in sigs]
# control
plant=add(Rs[0], None); Qd=None
for _ in range(12345): Qd=add(Qd,G)
ctrlR=add(Rs[0],Qd)
D=add(ctrlR,neg(Rs[0])); print('control delta found:',tab.get(D[0]))
hits=[]
for i in range(len(Rs)):
    for j in range(i+1,len(Rs)):
        for a in (Rs[i],neg(Rs[i])):
            for b in (Rs[j],neg(Rs[j])):
                D=add(b,neg(a))
                if D and D[0] in tab: hits.append((i,j,tab[D[0]]))
                S=add(b,a)
                if S and S[0] in tab: hits.append((i,j,'sum',tab[S[0]]))
print('related-nonce hits:',hits)
