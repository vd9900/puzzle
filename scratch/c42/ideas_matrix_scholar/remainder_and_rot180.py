# (1) "sum of a remainder of an unbalanced equation": faed = q*dbbi + r ; read r, q as bytes (z-method style int->hex->ASCII)
# (2) yin-yang = 180-degree rotation + colour inversion of the 14x14 matrix; XOR/AND/sum with original, read in the phase-0 spiral
import sys; sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import DBBI, FAED, MATRIX
R60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
v=lambda s:int(''.join(str(ord(c)-96) for c in s))
def pr(b): return sum(32<=x<127 for x in b)/max(1,len(b))
def tob(x): return x.to_bytes((x.bit_length()+7)//8,'big') if x else b''
A={'faed':v(FAED),'faed_rev':v(FAED[::-1])}; B={'dbbi':v(DBBI),'R60':v(R60),'dbbi_rev':v(DBBI[::-1]),'R60_rev':v(R60[::-1])}
for an,a in A.items():
    for bn,b in B.items():
        q,r=divmod(a,b)
        for lab,x in (('r',r),('q',q)):
            bb=tob(x); print(f'{an}/{bn} {lab}: {len(bb)}B printable={pr(bb):.2f}', bb[:24] if pr(bb)>0.8 else '')
# spiral: counter-clockwise inward, down first, from top-left
def spiral(n):
    top,left,bot,right=0,0,n-1,n-1; out=[]
    while top<=bot and left<=right:
        for r in range(top,bot+1): out.append((r,left))
        left+=1
        for c in range(left,right+1): out.append((bot,c))
        bot-=1
        if left<=right:
            for r in range(bot,top-1,-1): out.append((r,right))
            right-=1
        if top<=bot:
            for c in range(right,left-1,-1): out.append((top,c))
            top+=1
    return out
M=MATRIX; n=len(M); S=spiral(n)
def read(G,inv=False):
    bits=[G[r][c]^inv for r,c in S]; out=[]
    for i in range(0,len(bits)-7,8): out.append(int(''.join(map(str,bits[i:i+8])),2))
    return bytes(out)
for inv in (0,1):
    t=read(M,inv)
    if pr(t)>0.9: print('self-test phase0 inv',inv,t); base_inv=inv
R=[[M[n-1-r][n-1-c] for c in range(n)] for r in range(n)]
ops={'rot180':lambda r,c:R[r][c],'rot180inv':lambda r,c:1-R[r][c],'xor':lambda r,c:M[r][c]^R[r][c],
     'xnor':lambda r,c:1-(M[r][c]^R[r][c]),'and':lambda r,c:M[r][c]&R[r][c],'or':lambda r,c:M[r][c]|R[r][c],
     'tr':lambda r,c:M[c][r],'antitr':lambda r,c:M[n-1-c][n-1-r]}
for k,f in ops.items():
    G=[[f(r,c) for c in range(n)] for r in range(n)]
    for inv in (0,1):
        t=read(G,inv); print(k,inv,f'{pr(t):.2f}',t if pr(t)>0.7 else '')
print('symmetry: cells equal under rot180',sum(M[r][c]==R[r][c] for r in range(n) for c in range(n)),'of',n*n)
